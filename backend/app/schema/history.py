"""Provide history API schemas for the application."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


HistoryType = Literal[
    "image",
    "document",
]


class HistoryListItem(BaseModel):
    """Define a single history item."""

    id: int
    file_id: int

    file_name: str
    file_type: str

    analysis_type: HistoryType
    status: str

    # =========================================================
    # IMAGE ANALYSIS
    # =========================================================

    description: str | None = None

    ocr_text: str | None = None

    ocr_confidence: float | None = None

    ocr_word_count: int | None = None

    detected_objects: list | dict | None = None

    # =========================================================
    # DOCUMENT ANALYSIS
    # =========================================================

    summary_mode: str | None = None

    summary: str | None = None

    key_points: list | None = None

    entities: list | None = None

    decisions: list | None = None

    action_items: list | None = None

    chunk_count: int | None = None

    chunk_summaries: list | None = None

    # =========================================================
    # COMMON ANALYSIS FIELDS
    # =========================================================

    model_used: str | None = None

    processing_time: float | None = None

    warnings: list | None = None


class HistoryListResponse(BaseModel):
    """Define paginated history response."""

    items: list[HistoryListItem]

    page: int

    page_size: int

    total: int

    total_pages: int


class HistoryDetailResponse(BaseModel):
    """Define detailed history result."""

    id: int
    file_id: int

    # =========================================================
    # FILE INFORMATION
    # =========================================================

    file_name: str
    file_type: str
    file_size: int
    storage_reference: str
    checksum: str

    # =========================================================
    # ANALYSIS INFORMATION
    # =========================================================

    analysis_type: HistoryType

    status: str

    # =========================================================
    # IMAGE ANALYSIS
    # =========================================================

    description: str | None = None

    ocr_text: str | None = None

    ocr_confidence: float | None = None

    ocr_word_count: int | None = None

    detected_objects: list | dict | None = None

    # =========================================================
    # DOCUMENT ANALYSIS
    # =========================================================

    summary_mode: str | None = None

    summary: str | None = None

    key_points: list | None = None

    entities: list | None = None

    decisions: list | None = None

    action_items: list | None = None

    chunk_count: int | None = None

    chunk_summaries: list | None = None

    # =========================================================
    # COMMON ANALYSIS FIELDS
    # =========================================================

    model_used: str | None = None

    processing_time: float | None = None

    warnings: list | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class HistoryDeleteResponse(BaseModel):
    """Define history deletion response."""

    message: str

    id: int

    file_id: int