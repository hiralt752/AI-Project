"""Provide file components for the application."""

from datetime import datetime
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    """Define the FileUploadResponse API schema."""

    id: int
    file_name: str
    file_type: str
    size: int
    storage_reference: str
    checksum: str
    retention_status: str
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }

class AdminFileResponse(BaseModel):
    """Define the AdminFileResponse API schema."""

    id: int
    owner_id: int
    file_name: str
    file_type: str
    size: int
    storage_reference: str
    checksum: str
    retention_status: str
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
