from pathlib import Path
import re

from fastapi import HTTPException, UploadFile


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".docx",
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
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def sanitize_filename(filename: str) -> str:
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


def validate_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file extension",
        )

    return extension


def validate_mime_type(content_type: str | None):
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


async def validate_file_size(file: UploadFile) -> int:

    total_size = 0

    while True:

        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 20 MB limit",
            )

    await file.seek(0)

    return total_size