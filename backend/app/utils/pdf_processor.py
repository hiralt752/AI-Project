"""Provide pdf processor components for the application."""

from pathlib import Path
import io

import fitz
from PIL import Image
import pymupdf

from app.utils.ocr import extract_text_with_confidence


def render_pdf_page(page) -> Image.Image:
    """
    Render a PDF page into a PIL image.
    Used for image-only/scanned PDF pages.
    """

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        alpha=False,
    )

    image_bytes = pixmap.tobytes("png")

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    image.load()

    return image.convert("RGB")


def extract_pdf_content(
    file_path: str | Path,
) -> dict:
    """
    Extract PDF content page-by-page.

    Native PDF text is extracted first.
    If a page contains no native text,
    the page is rendered and processed using OCR.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Selected file is not a PDF"
        )

    document = fitz.open(file_path)

    pages = []

    try:

        for page_index in range(len(document)):

            page = document[page_index]

            page_number = page_index + 1

            # 1. Extract native PDF text

            native_text = page.get_text("text").strip()

            if native_text:

                pages.append(
                    {
                        "page_number": page_number,
                        "text": native_text,
                        "source": "native",
                        "ocr_used": False,
                        "ocr_confidence": None,
                        "ocr_word_count": None,
                    }
                )

                continue

            # 2. Image-only / scanned page

            image = render_pdf_page(page)

            # 3. Run Tesseract OCR

            ocr_result = extract_text_with_confidence(
                image=image,
                language="eng",
            )

            pages.append(
                {
                    "page_number": page_number,
                    "text": ocr_result["text"],
                    "source": "ocr",
                    "ocr_used": True,
                    "ocr_confidence": ocr_result[
                        "confidence"
                    ],
                    "ocr_word_count": ocr_result[
                        "word_count"
                    ],
                }
            )

    finally:

        document.close()

    # 4. Combine page text

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    return {
        "file_type": "pdf",
        "page_count": len(pages),
        "pages": pages,
        "text": full_text,
    }
