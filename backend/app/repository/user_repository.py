"""Provide user repository components for the application."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(
    db: Session,
    user_id: int,
):
    """Get user by id."""

    return db.scalar(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False,
        )
    )

def update_user(
    db: Session,
    user: User,
    name: str | None = None,
    email: str | None = None,
):
    """Update user."""

    if name is not None:
        user.name = name

    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)

    return user


def soft_delete_user(
    db: Session,
    user: User,
):
    """Soft delete user."""

    user.is_deleted = True

    db.commit()
    db.refresh(user)

    return user
