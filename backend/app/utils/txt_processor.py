"""Provide txt processor components for the application."""

from pathlib import Path


def extract_txt_content(
    file_path: str | Path,
) -> dict:

    """Extract txt content."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"TXT file not found: {file_path}"
        )

    if file_path.suffix.lower() != ".txt":
        raise ValueError(
            "Selected file is not a TXT file"
        )

    text = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    return {
        "file_type": "txt",
        "text": text,
        "page_count": 1,
        "pages": [
            {
                "page_number": 1,
                "text": text,
            }
        ],
    }
