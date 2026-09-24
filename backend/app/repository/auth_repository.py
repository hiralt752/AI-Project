"""Provide auth repository components for the application."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    """Get user by email."""

    return db.scalar(
        select(User).where(
            User.email == email,
            User.is_deleted == False,
        )
    )


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:

    """Get user by id."""

    return db.scalar(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False,
        )
    )


def get_role_by_name(
    db: Session,
    role_name: str,
) -> Role | None:

    """Get role by name."""

    return db.scalar(
        select(Role).where(
            Role.name == role_name,
            Role.is_deleted == False,
        )
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
    role_id: int,
) -> User:

    """Create user."""

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        status="active",
        role_id=role_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def update_last_login(
    db: Session,
    user: User,
) -> User:

    """Update last login."""

    from datetime import datetime, timezone

    user.last_login_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return user


def update_user_password(
    db: Session,
    user: User,
    password_hash: str,
) -> User:

    """Update user password."""

    user.password_hash = password_hash

    db.commit()
    db.refresh(user)

    return user
