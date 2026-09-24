"""Provide doc processor components for the application."""

from pathlib import Path
import subprocess
import tempfile

from app.utils.docx_processor import extract_docx_content


SOFFICE_PATH = (
    r"C:\Program Files\LibreOffice\program\soffice.exe"
)


def convert_doc_to_docx(
    file_path: str | Path,
) -> Path:

    """Convert doc to docx."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"DOC file not found: {file_path}"
        )

    output_directory = Path(
        tempfile.mkdtemp(
            prefix="doc_conversion_"
        )
    )

    command = [
        SOFFICE_PATH,
        "--headless",
        "--convert-to",
        "docx",
        "--outdir",
        str(output_directory),
        str(file_path),
    ]

    try:

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

    except subprocess.CalledProcessError as exc:

        raise RuntimeError(
            f"DOC to DOCX conversion failed: "
            f"{exc.stderr}"
        ) from exc

    converted_file = (
        output_directory
        / f"{file_path.stem}.docx"
    )

    if not converted_file.exists():

        raise RuntimeError(
            "DOCX conversion completed but "
            "converted file was not found."
        )

    return converted_file


def extract_doc_content(
    file_path: str | Path,
) -> dict:

    """Extract doc content."""

    converted_docx = convert_doc_to_docx(
        file_path
    )

    result = extract_docx_content(
        converted_docx
    )

    result["file_type"] = "doc"

    result["converted_from"] = "doc"

    return result
