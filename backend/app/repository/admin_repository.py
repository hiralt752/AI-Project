"""Provide admin repository components for the application."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id_admin(
    db: Session,
    user_id: int,
):
    """Get user by id admin."""

    return db.scalar(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False,
        )
    )


def update_user_admin(
    db: Session,
    user: User,
    name: str | None = None,
    email: str | None = None,
):
    """Update user admin."""

    if name is not None:
        user.name = name

    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)

    return user


def delete_user_admin(
    db: Session,
    user: User,
):
    """Delete user admin."""

    user.is_deleted = True

    db.commit()
    db.refresh(user)

    return user

def get_all_users_admin(db: Session):
    """Get all users admin."""

    return db.scalars(
        select(User).where(
            User.is_deleted == False
        )
    ).all()
