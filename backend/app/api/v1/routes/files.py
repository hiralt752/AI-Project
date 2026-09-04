from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.oauth2 import get_current_user

from app.schema.file import FileUploadResponse
from fastapi.responses import FileResponse

from app.services.file_service import (
    upload_file_service,
    get_user_files_service,
    delete_file_service,
)


router = APIRouter(
    prefix="/api/v1/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await upload_file_service(
        db=db,
        file=file,
        owner_id=current_user.id,
    )


@router.get(
    "/",
    response_model=list[FileUploadResponse],
)
def get_my_files(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_user_files_service(
        db=db,
        owner_id=current_user.id,
    )

@router.delete(
    "/{file_id}",
)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_file_service(
        db=db,
        file_id=file_id,
        owner_id=current_user.id,
    )