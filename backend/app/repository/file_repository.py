from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file import File


def create_file(
    db: Session,
    owner_id: int,
    file_name: str,
    file_type: str,
    size: int,
    storage_reference: str,
    checksum: str,
):

    file_record = File(
        owner_id=owner_id,
        file_name=file_name,
        file_type=file_type,
        size=size,
        storage_reference=storage_reference,
        checksum=checksum,
        retention_status="active",
    )

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return file_record


def get_user_file_by_id(
    db: Session,
    file_id: int,
    owner_id: int,
):
    return db.scalar(
        select(File).where(
            File.id == file_id,
            File.owner_id == owner_id,
            File.is_deleted == False,
        )
    )


def get_user_files(
    db: Session,
    owner_id: int,
):
    return db.scalars(
        select(File)
        .where(
            File.owner_id == owner_id,
            File.is_deleted == False,
        )
        .order_by(File.id.desc())
    ).all()


def soft_delete_file(
    db: Session,
    file: File,
):

    file.is_deleted = True
    file.retention_status = "deleted"

    db.commit()
    db.refresh(file)

    return file