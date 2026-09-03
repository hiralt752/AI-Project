from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.base import SoftDeleteMixin


class File(Base, SoftDeleteMixin):

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    storage_reference: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    checksum: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    retention_status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    image_analysis = relationship(
        "ImageAnalysis",
        back_populates="file",
        uselist=False,
    )

    document_analysis = relationship(
        "DocumentAnalysis",
        back_populates="file",
        uselist=False,
    )