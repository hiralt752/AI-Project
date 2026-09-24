"""Provide document service components for the application."""

# # pylint: disable=import-error
# # pylint: disable=import-error

# from pathlib import Path

# from app.utils.file_validation import (
#     validate_extension,
# )

# from app.utils.pdf_processor import (
#     extract_pdf_content,
# )

# from app.utils.docx_processor import (
#     extract_docx_content,
# )

# from app.utils.txt_processor import (
#     extract_txt_content,
# )

# from app.utils.doc_processor import (
#     extract_doc_content,
# )


# def process_document(
#     file_path: str | Path,
# ) -> dict:

#     file_path = Path(file_path)

#     extension = validate_extension(
#         file_path.name
#     )

#     if extension == ".pdf":

#         return extract_pdf_content(
#             file_path
#         )

#     if extension == ".docx":

#         return extract_docx_content(
#             file_path
#         )

#     if extension == ".txt":

#         return extract_txt_content(
#             file_path
#         )

#     if extension == ".doc":

#         return extract_doc_content(
#             file_path
#         )

#     raise ValueError(
#         "Unsupported document format"
#     )




# pylint: disable=import-error

from pathlib import Path

from app.utils.pdf_processor import extract_pdf_content
from app.utils.docx_processor import extract_docx_content
from app.utils.txt_processor import extract_txt_content
from app.utils.doc_processor import extract_doc_content


SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".doc",
}


def process_document(
    file_path: str | Path,
) -> dict:
    """
    Process a document based on its actual file extension.

    Supported:
        - PDF
        - DOCX
        - TXT
        - DOC
    """

    # Convert to Path object
    file_path = Path(file_path)

    # Check physical file
    if not file_path.exists():
        raise FileNotFoundError(
            f"Document file not found: {file_path}"
        )

    # Get actual extension from stored file
    extension = file_path.suffix.lower()

    print("========== DOCUMENT SERVICE ==========")
    print("File path:", file_path)
    print("File name:", file_path.name)
    print("Extension:", extension)
    print("File exists:", file_path.exists())
    print("======================================")

    # Check supported format
    if extension not in SUPPORTED_DOCUMENT_EXTENSIONS:
        raise ValueError(
            f"Unsupported document format: {extension}"
        )

    # PDF
    if extension == ".pdf":
        return extract_pdf_content(file_path)

    # DOCX
    if extension == ".docx":
        return extract_docx_content(file_path)

    # TXT
    if extension == ".txt":
        return extract_txt_content(file_path)

    # DOC
    if extension == ".doc":
        return extract_doc_content(file_path)

    # Safety fallback
    raise ValueError(
        f"Unsupported document format: {extension}"
    )

