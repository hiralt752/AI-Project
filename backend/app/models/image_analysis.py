"""Provide image analysis components for the application."""

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.base import SoftDeleteMixin


class ImageAnalysis(Base, SoftDeleteMixin):

    """Represent the ImageAnalysis database model."""

    __tablename__ = "image_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id"),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ocr_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ocr_word_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    detected_objects: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    model_used: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    processing_time: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    warnings: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    file = relationship(
        "File",
        back_populates="image_analysis",
    )
