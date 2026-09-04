from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.user_repository import (
    get_user_by_id,
    update_user,
    soft_delete_user,
)


def update_user_service(
    db: Session,
    user_id: int,
    name: str | None = None,
    email: str | None = None,
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated_user = update_user(
        db=db,
        user=user,
        name=name,
        email=email,
    )

    return updated_user

def delete_user_service(
    db: Session,
    user_id: int,
):
    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    soft_delete_user(
        db=db,
        user=user,
    )

    return {
        "message": "User deleted successfully"
    }

def check_user_access(
    current_user,
    target_user_id: int,
):
    if (
        current_user.id != target_user_id
        and current_user.role.name != "Admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to modify this user",
        )