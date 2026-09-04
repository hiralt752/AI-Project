from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.repository.file_repository import create_file , get_user_files , soft_delete_file , get_user_file_by_id

from app.utils.file_validation import (
    sanitize_filename,
    validate_extension,
    validate_mime_type,
    validate_file_size,
)

from app.utils.checksum import calculate_sha256

from app.utils.file_storage import (
    create_storage_directories,
    generate_storage_filename,
    get_upload_path,
    save_upload_file,
    UPLOAD_STORAGE
)

from fastapi import HTTPException
from pathlib import Path


async def upload_file_service(
    db: Session,
    file: UploadFile,
    owner_id: int,
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    # 1. Sanitize filename
    file_name = sanitize_filename(
        file.filename
    )

    # 2. Extension validation
    extension = validate_extension(
        file_name
    )

    # 3. MIME validation
    validate_mime_type(
        file.content_type
    )

    # 4. File-size validation
    file_size = await validate_file_size(
        file
    )

    # 5. Checksum
    checksum = await calculate_sha256(
        file
    )

    # 6. Create directories
    create_storage_directories()

    # 7. Generate safe storage filename
    stored_filename = generate_storage_filename(
        extension
    )

    # 8. Storage path
    storage_path = get_upload_path(
        stored_filename
    )

    # 9. Save file
    save_upload_file(
        file,
        storage_path,
    )

    # 10. Storage reference
    storage_reference = (
        f"uploads/{stored_filename}"
    )

    # 11. Save database record
    file_record = create_file(
        db=db,
        owner_id=owner_id,
        file_name=file_name,
        file_type=file.content_type,
        size=file_size,
        storage_reference=storage_reference,
        checksum=checksum,
    )

    return file_record


def get_user_files_service(
    db: Session,
    owner_id: int,
):
    return get_user_files(
        db=db,
        owner_id=owner_id,
    )

def delete_file_service(
    db: Session,
    file_id: int,
    owner_id: int,
):
    # 1. Find file belonging to current user
    file = get_user_file_by_id(
        db=db,
        file_id=file_id,
        owner_id=owner_id,
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    # 2. Build physical storage path
    relative_path = file.storage_reference.replace(
        "uploads/",
        "",
        1,
    )

    file_path = UPLOAD_STORAGE / relative_path

    # 3. Soft delete database record
    soft_delete_file(
        db=db,
        file=file,
    )

    # 4. Delete physical file
    if file_path.exists():
        file_path.unlink()

    return {
        "message": "File deleted successfully",
        "file_id": file.id,
        "file_name": file.file_name,
    }