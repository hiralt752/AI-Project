"""Provide file validation components for the application."""

from pathlib import Path
import io
import re
import zipfile

import fitz
from fastapi import HTTPException, UploadFile
from PIL import Image


# ============================================================================
# ALLOWED FILE TYPES
# ============================================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".docx",
    ".doc",
    ".txt",
    ".pptx",
    ".xlsx",
    ".csv",
}


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


# ============================================================================
# FILE SIZE LIMIT
# ============================================================================

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ============================================================================
# PDF LIMITS
# ============================================================================

MAX_PDF_PAGES = 100


# ============================================================================
# IMAGE LIMITS
# ============================================================================

MAX_IMAGE_PIXELS = 25_000_000  # 25 megapixels
MAX_IMAGE_WIDTH = 10_000
MAX_IMAGE_HEIGHT = 10_000


# ============================================================================
# TEXT LIMITS
# ============================================================================

MAX_TEXT_CHARACTERS = 2_000_000
MAX_TEXT_WORDS = 300_000


# ============================================================================
# OFFICE DOCUMENT LIMITS
# ============================================================================

MAX_ARCHIVE_UNCOMPRESSED_SIZE = 100 * 1024 * 1024  # 100 MB


# ============================================================================
# EXTENSION ↔ MIME TYPE
# ============================================================================

EXTENSION_MIME_MAP = {
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
    ".csv": {
        "text/csv",
        "text/plain",
    },
    ".doc": {"application/msword"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    ".pptx": {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    },
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
}


# ============================================================================
# MAGIC BYTES
# ============================================================================

FILE_SIGNATURES = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".pdf": (b"%PDF-",),
    ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    ".docx": (b"PK\x03\x04",),
    ".pptx": (b"PK\x03\x04",),
    ".xlsx": (b"PK\x03\x04",),
}


# ============================================================================
# FILENAME
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename."""

    filename = Path(filename).name

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename,
    )

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    return filename


# ============================================================================
# EXTENSION
# ============================================================================

def validate_extension(filename: str) -> str:
    """Validate file extension."""

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file extension",
        )

    return extension


# ============================================================================
# MIME TYPE
# ============================================================================

def validate_mime_type(
    content_type: str | None,
) -> str:
    """Validate MIME type."""

    if not content_type:
        raise HTTPException(
            status_code=400,
            detail="Missing MIME type",
        )

    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported MIME type",
        )

    return content_type


# ============================================================================
# EXTENSION + MIME
# ============================================================================

def validate_extension_mime(
    extension: str,
    content_type: str,
) -> None:
    """Validate extension and MIME type combination."""

    allowed_mime_types = EXTENSION_MIME_MAP.get(
        extension,
    )

    if not allowed_mime_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file extension",
        )

    if content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "File extension and MIME type do not match"
            ),
        )


# ============================================================================
# FILE SIZE
# ============================================================================

async def validate_file_size(
    file: UploadFile,
) -> int:
    """Validate uploaded file size."""

    total_size = 0

    while True:

        chunk = await file.read(
            1024 * 1024,
        )

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > MAX_FILE_SIZE:
            await file.seek(0)

            raise HTTPException(
                status_code=413,
                detail="File size exceeds 20 MB limit",
            )

    await file.seek(0)

    if total_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    return total_size


# ============================================================================
# EMPTY FILE
# ============================================================================

def validate_not_empty(
    content: bytes,
) -> None:
    """Reject empty file content."""

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )


# ============================================================================
# MAGIC BYTES
# ============================================================================

def validate_magic_bytes(
    content: bytes,
    extension: str,
) -> None:
    """Validate actual file signature."""

    # TXT and CSV don't have reliable fixed signatures.
    if extension in {".txt", ".csv"}:
        return

    # WebP requires RIFF + WEBP validation.
    if extension == ".webp":

        if len(content) < 12:
            raise HTTPException(
                status_code=400,
                detail="Invalid WebP file",
            )

        if (
            content[:4] != b"RIFF"
            or content[8:12] != b"WEBP"
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid WebP file signature",
            )

        return

    signatures = FILE_SIGNATURES.get(
        extension,
    )

    if not signatures:
        raise HTTPException(
            status_code=400,
            detail="File signature validation is not supported",
        )

    if not any(
        content.startswith(signature)
        for signature in signatures
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "File content does not match "
                "the declared file type"
            ),
        )


# ============================================================================
# IMAGE VALIDATION
# ============================================================================

def validate_image(
    content: bytes,
) -> None:
    """Validate image structure and dimensions."""

    try:
        with Image.open(
            io.BytesIO(content),
        ) as image:

            width, height = image.size

            if width <= 0 or height <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image dimensions",
                )

            if width > MAX_IMAGE_WIDTH:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Image width exceeds "
                        "10,000 pixels"
                    ),
                )

            if height > MAX_IMAGE_HEIGHT:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Image height exceeds "
                        "10,000 pixels"
                    ),
                )

            total_pixels = width * height

            if total_pixels > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Image exceeds the "
                        "25 megapixel limit"
                    ),
                )

            image.verify()

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image file",
        ) from exc


# ============================================================================
# PDF VALIDATION
# ============================================================================

def validate_pdf(
    content: bytes,
) -> None:
    """Validate PDF structure and page count."""

    document = None

    try:
        document = fitz.open(
            stream=content,
            filetype="pdf",
        )

        page_count = document.page_count

        if page_count == 0:
            raise HTTPException(
                status_code=400,
                detail="PDF contains no pages",
            )

        if page_count > MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "PDF exceeds the "
                    "100 page limit"
                ),
            )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted PDF file",
        ) from exc

    finally:
        if document is not None:
            document.close()


# ============================================================================
# TEXT VALIDATION
# ============================================================================

def validate_text_file(
    content: bytes,
) -> None:
    """Validate TXT/CSV content."""

    try:
        text = content.decode(
            "utf-8",
            errors="strict",
        )

    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Text file must use UTF-8 encoding",
        ) from exc

    character_count = len(text)

    if character_count > MAX_TEXT_CHARACTERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Text file exceeds the "
                "2,000,000 character limit"
            ),
        )

    word_count = len(
        re.findall(
            r"\S+",
            text,
        )
    )

    if word_count > MAX_TEXT_WORDS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Text file exceeds the "
                "300,000 word limit"
            ),
        )


# ============================================================================
# OFFICE ZIP VALIDATION
# ============================================================================

def validate_office_archive(
    content: bytes,
    extension: str,
) -> None:
    """Validate Office Open XML archive."""

    try:
        with zipfile.ZipFile(
            io.BytesIO(content),
        ) as archive:

            if archive.testzip() is not None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Office document contains "
                        "corrupted archive data"
                    ),
                )

            total_uncompressed_size = sum(
                info.file_size
                for info in archive.infolist()
            )

            if (
                total_uncompressed_size
                > MAX_ARCHIVE_UNCOMPRESSED_SIZE
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Office document uncompressed "
                        "content exceeds the 100 MB limit"
                    ),
                )

            names = set(
                archive.namelist()
            )

            if extension == ".docx":
                required_prefix = "word/"

            elif extension == ".pptx":
                required_prefix = "ppt/"

            elif extension == ".xlsx":
                required_prefix = "xl/"

            else:
                return

            if not any(
                name.startswith(required_prefix)
                for name in names
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Invalid Office document structure"
                    ),
                )

    except HTTPException:
        raise

    except zipfile.BadZipFile as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted Office document",
        ) from exc


# ============================================================================
# COMPLETE CONTENT VALIDATION
# ============================================================================

def validate_file_content(
    content: bytes,
    extension: str,
) -> None:
    """Perform complete file-content validation."""

    # 1. Empty file
    validate_not_empty(
        content,
    )

    # 2. Magic bytes / file signature
    validate_magic_bytes(
        content,
        extension,
    )

    # 3. Format-specific validation
    if extension in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:
        validate_image(
            content,
        )

    elif extension == ".pdf":
        validate_pdf(
            content,
        )

    elif extension in {
        ".txt",
        ".csv",
    }:
        validate_text_file(
            content,
        )

    elif extension in {
        ".docx",
        ".pptx",
        ".xlsx",
    }:
        validate_office_archive(
            content,
            extension,
        )

    # .doc is validated using its OLE magic bytes.