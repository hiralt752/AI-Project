from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
       ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    role = relationship(
        "Role",
        back_populates="users",
    )

    refresh_tokens = relationship(
    "RefreshToken",
    back_populates="user",
)