from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.admin_repository import (
    get_user_by_id_admin,
    update_user_admin,
    delete_user_admin,
    get_all_users_admin
)


def get_user_admin_service(
    db: Session,
    user_id: int,
):
    user = get_user_by_id_admin(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

def update_user_admin_service(
    db: Session,
    user_id: int,
    name: str | None = None,
    email: str | None = None,
):
    user = get_user_by_id_admin(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return update_user_admin(
        db=db,
        user=user,
        name=name,
        email=email,
    )

def delete_user_admin_service(
    db: Session,
    user_id: int,
):
    user = get_user_by_id_admin(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_user_admin(
        db=db,
        user=user,
    )

    return {
        "message": "User deleted successfully"
    }

def get_all_users_admin_service(db: Session):
    return get_all_users_admin(db)