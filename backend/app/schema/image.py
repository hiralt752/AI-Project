from datetime import datetime

from pydantic import BaseModel


class ImageDescriptionResponse(BaseModel):
    id: int
    file_id: int
    description: str | None
    model_used: str | None
    status: str
    processing_time: float | None
    warnings: list | None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class ImageOCRResponse(BaseModel):
    id: int
    file_id: int
    ocr_text: str | None
    ocr_confidence: float | None
    ocr_word_count: int | None
    status: str
    processing_time: float | None
    warnings: list | None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class ImageAnalysisResponse(BaseModel):
    id: int
    file_id: int
    description: str | None
    ocr_text: str | None
    ocr_confidence: float | None
    ocr_word_count: int | None
    model_used: str | None
    status: str
    processing_time: float | None
    warnings: list | None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }