"""Provide document cleaning service components for the application."""

import re
import unicodedata
from typing import Any


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters while preserving readable text.
    """

    if not text:
        return ""

    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    """
    Remove unnecessary whitespace while preserving paragraphs.
    """

    if not text:
        return ""

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove spaces/tabs at line boundaries
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)

    # Remove trailing spaces
    text = re.sub(r"[ \t]+\n", "\n", text)

    return text.strip()


def fix_ocr_errors(text: str) -> str:
    """
    Apply conservative OCR cleanup.

    Only performs transformations that are generally safe.
    """

    if not text:
        return ""

    # Fix words broken by line-ending hyphenation.
    #
    # Example:
    # summa-
    # rization
    #
    # becomes:
    # summarization
    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1\2",
        text,
    )

    # Convert remaining single line breaks inside a sentence
    # into spaces when they are clearly not paragraph boundaries.
    text = re.sub(
        r"(?<=[a-z0-9,.;:])\n(?=[a-z])",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    return text


def clean_text(text: str) -> str:
    """
    Complete text cleaning pipeline.
    """

    text = normalize_unicode(text)

    text = fix_ocr_errors(text)

    text = normalize_whitespace(text)

    return text


def clean_document(document: dict[str, Any]) -> dict[str, Any]:
    """
    Clean extracted document content while preserving
    page and structural metadata.
    """

    cleaned_pages = []

    for page in document.get("pages", []):

        cleaned_text = clean_text(
            page.get("text", "")
        )

        cleaned_page = {
            **page,
            "text": cleaned_text,
        }

        cleaned_pages.append(cleaned_page)

    cleaned_elements = []

    for element in document.get("elements", []):

        cleaned_element = {
            **element,
            "text": clean_text(
                element.get("text", "")
            ),
        }

        cleaned_elements.append(
            cleaned_element
        )

    cleaned_document = {
        **document,
        "text": clean_text(
            document.get("text", "")
        ),
        "pages": cleaned_pages,
        "elements": cleaned_elements,
    }

    return cleaned_document
