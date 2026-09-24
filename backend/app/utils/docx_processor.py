"""Provide docx processor components for the application."""

from pathlib import Path

from docx import Document


def extract_docx_content(
    file_path: str | Path,
) -> dict:
    """
    Extract DOCX paragraphs, headings and tables
    while preserving document order/structure.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"DOCX file not found: {file_path}"
        )

    if file_path.suffix.lower() != ".docx":
        raise ValueError(
            "Selected file is not a DOCX file"
        )

    document = Document(file_path)

    elements = []

    # Paragraphs + headings

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if not text:
            continue

        style_name = paragraph.style.name

        if style_name.startswith("Heading"):
            element_type = "heading"
        else:
            element_type = "paragraph"

        elements.append(
            {
                "type": element_type,
                "text": text,
                "style": style_name,
            }
        )

    # Tables

    tables = []

    for table_index, table in enumerate(
        document.tables
    ):

        rows = []

        for row in table.rows:

            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            rows.append(cells)

        tables.append(
            {
                "table_number": table_index + 1,
                "rows": rows,
            }
        )

    # Full text

    text_parts = []

    for element in elements:

        text_parts.append(
            element["text"]
        )

    for table in tables:

        for row in table["rows"]:

            text_parts.append(
                " | ".join(row)
            )

    full_text = "\n\n".join(text_parts)

    return {
        "file_type": "docx",
        "text": full_text,
        "elements": elements,
        "tables": tables,
    }
