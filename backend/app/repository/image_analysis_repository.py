from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.image_analysis import ImageAnalysis


def create_image_analysis(
    db: Session,
    file_id: int,
    description: str | None = None,
    ocr_text: str | None = None,
    ocr_confidence: float | None = None,
    ocr_word_count: int | None = None,
    model_used: str | None = None,
    status: str = "pending",
    processing_time: float | None = None,
    warnings: list | None = None,
):
    image_analysis = ImageAnalysis(
        file_id=file_id,
        description=description,
        ocr_text=ocr_text,
        ocr_confidence=ocr_confidence,
        ocr_word_count=ocr_word_count,
        model_used=model_used,
        status=status,
        processing_time=processing_time,
        warnings=warnings,
    )

    db.add(image_analysis)
    db.commit()
    db.refresh(image_analysis)

    return image_analysis


def get_image_analysis_by_file_id(
    db: Session,
    file_id: int,
):
    return db.scalar(
        select(ImageAnalysis).where(
            ImageAnalysis.file_id == file_id,
            ImageAnalysis.is_deleted == False,
        )
    )


def update_image_analysis(
    db: Session,
    image_analysis: ImageAnalysis,
    description: str | None = None,
    ocr_text: str | None = None,
    ocr_confidence: float | None = None,
    ocr_word_count: int | None = None,
    model_used: str | None = None,
    status: str | None = None,
    processing_time: float | None = None,
    warnings: list | None = None,
):
    if description is not None:
        image_analysis.description = description

    if ocr_text is not None:
        image_analysis.ocr_text = ocr_text

    if ocr_confidence is not None:
        image_analysis.ocr_confidence = ocr_confidence

    if ocr_word_count is not None:
        image_analysis.ocr_word_count = ocr_word_count

    if model_used is not None:
        image_analysis.model_used = model_used

    if status is not None:
        image_analysis.status = status

    if processing_time is not None:
        image_analysis.processing_time = processing_time

    if warnings is not None:
        image_analysis.warnings = warnings

    db.commit()
    db.refresh(image_analysis)

    return image_analysis