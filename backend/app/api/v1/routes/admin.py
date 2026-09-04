from fastapi import APIRouter, Depends,status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.authorization import require_role
from app.services.admin_service import (
    get_user_admin_service,
    update_user_admin_service,
    delete_user_admin_service,
    get_all_users_admin_service,
)
from app.schema.auth import UpdateUserRequest, UserResponse
from app.schema.file import AdminFileResponse
from app.services.admin_file_service import get_all_files_admin_service, get_file_admin_service, delete_file_admin_service, get_user_files_admin_service


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)

@router.get("/dashboard")
def admin_dashboard(
    current_user=Depends(
        require_role("Admin")
    ),
):
    return {
        "message": "Welcome to Admin Dashboard",
        "admin_id": current_user.id,
        "admin_email": current_user.email,
    }

@router.get("/users", response_model=list[UserResponse])
def get_all_users_admin(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    return get_all_users_admin_service(db)

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("Admin")
    ),
):
    return get_user_admin_service(
        db=db,
        user_id=user_id,
    )

@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user_admin(
    user_id: int,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("Admin")
    ),
):
    return update_user_admin_service(
        db=db,
        user_id=user_id,
        name=request.name,
        email=request.email,
    )

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("Admin")
    ),
):
    return delete_user_admin_service(
        db=db,
        user_id=user_id,
    )

@router.get(
    "/files",
    response_model=list[AdminFileResponse],
)
def get_all_admin_files(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    return get_all_files_admin_service(
        db=db,
    )


@router.get(
    "/files/{file_id}",
    response_model=AdminFileResponse,
)
def get_admin_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    return get_file_admin_service(
        db=db,
        file_id=file_id,
    )


@router.delete(
    "/files/{file_id}",
    status_code=status.HTTP_200_OK,
)
def delete_admin_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    return delete_file_admin_service(
        db=db,
        file_id=file_id,
    )

@router.get(
    "/users/{user_id}/files",
    response_model=list[AdminFileResponse],
)
def get_admin_user_files(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    return get_user_files_admin_service(
        db=db,
        user_id=user_id,
    )