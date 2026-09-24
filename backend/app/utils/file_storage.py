"""Provide file storage components for the application."""

from pathlib import Path
import shutil
import uuid


BASE_STORAGE = Path("storage")

TEMP_STORAGE = BASE_STORAGE / "temporary"
UPLOAD_STORAGE = BASE_STORAGE / "uploads"
PROCESSED_STORAGE = BASE_STORAGE / "processed"


def create_storage_directories():

    """Create storage directories."""

    TEMP_STORAGE.mkdir(
        parents=True,
        exist_ok=True,
    )

    UPLOAD_STORAGE.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROCESSED_STORAGE.mkdir(
        parents=True,
        exist_ok=True,
    )


def generate_storage_filename(
    extension: str,
) -> str:

    """Generate storage filename."""

    return f"{uuid.uuid4()}{extension}"


def get_upload_path(
    filename: str,
) -> Path:

    """Get upload path."""

    return UPLOAD_STORAGE / filename


def save_upload_file(
    file,
    destination: Path,
):

    """Save upload file."""

    with destination.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )


def delete_file(path: Path):

    """Delete file."""

    if path.exists():
        path.unlink()
