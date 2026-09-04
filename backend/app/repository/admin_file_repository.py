from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file import File

def get_all_files(
    db: Session,
):
    return db.scalars(
        select(File)
        .where(
            File.is_deleted == False,
        )
        .order_by(File.id.desc())
    ).all()




def get_file_by_id_admin(
    db: Session,
    file_id: int,
):
    return db.scalar(
        select(File).where(
            File.id == file_id,
            File.is_deleted == False,
        )
    )

def get_user_files_admin(
    db: Session,
    user_id: int,
):
    return db.scalars(
        select(File)
        .where(
            File.owner_id == user_id,
            File.is_deleted == False,
        )
        .order_by(File.id.desc())
    ).all()


def soft_delete_file_admin(
    db: Session,
    file: File,
):
    file.is_deleted = True
    file.retention_status = "deleted"

    db.commit()
    db.refresh(file)

    return file