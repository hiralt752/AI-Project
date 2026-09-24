"""Provide document components for the application."""


from datetime import datetime
from typing import Literal

from pydantic import BaseModel


SummaryMode = Literal[
    "Brief",
    "Standard",
    "Detailed",
    "Key Points",
    "Action Items",
]


class DocumentAnalysisRequest(BaseModel):
    """Define the DocumentAnalysisRequest API schema."""

    file_id: int

    summary_mode: SummaryMode = "Standard"

    extract_structured: bool = True


class DocumentAnalysisResponse(BaseModel):
    """Define the DocumentAnalysisResponse API schema."""

    id: int
    file_id: int

    summary_mode: str
    summary: str | None

    key_points: list | None
    #section_summaries: list | None

    entities: list | None
    decisions: list | None
    action_items: list | None

    chunk_count: int | None
    chunk_summaries: list | None

    #section_count: int | None

    model_used: str | None
    status: str
    processing_time: float | None
    warnings: list | None

    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }

