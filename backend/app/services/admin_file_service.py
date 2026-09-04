from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repository.admin_file_repository import (
    get_all_files,
    get_file_by_id_admin,
    get_user_files_admin,
    soft_delete_file_admin,
)

from app.utils.file_storage import UPLOAD_STORAGE


def get_all_files_admin_service(
    db: Session,
):
    return get_all_files(
        db=db,
    )


def get_file_admin_service(
    db: Session,
    file_id: int,
):
    file = get_file_by_id_admin(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return file

def get_user_files_admin_service(
    db: Session,
    user_id: int,
):
    return get_user_files_admin(
        db=db,
        user_id=user_id,
    )

def delete_file_admin_service(
    db: Session,
    file_id: int,
):
    # Find file
    file = get_file_by_id_admin(
        db=db,
        file_id=file_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    # Build physical file path
    relative_path = file.storage_reference.replace(
        "uploads/",
        "",
        1,
    )

    file_path = UPLOAD_STORAGE / relative_path

    # Soft delete database record
    soft_delete_file_admin(
        db=db,
        file=file,
    )

    # Delete physical file
    if file_path.exists():
        file_path.unlink()

    return {
        "message": "File deleted successfully",
        "file_id": file.id,
        "file_name": file.file_name,
    }