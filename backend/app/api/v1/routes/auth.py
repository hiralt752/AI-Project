from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.connection import get_db

from app.schema.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse,
    UpdateUserRequest
)

from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
     forgot_password,
    reset_password,
    

)

from app.services.user_service import (
    update_user_service,
    delete_user_service,
    check_user_access
)

from app.schema.auth import RegisterRequest
from app.core.oauth2 import get_current_user


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    user = register_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
    )

    return {
        "message": "User registered successfully",
        "user_id": user.id,
    }

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    return login_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )


@router.post(
    "/refresh",
)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):

    return refresh_access_token(
        db=db,
        refresh_token=request.refresh_token,
    )


@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: RegisterRequest = Depends(get_current_user)
):
    return logout_user(
        db=db,
        refresh_token=request.refresh_token,
    )



@router.post("/forgot-password")
def forgot_password_route(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    current_user: RegisterRequest = Depends(get_current_user)
):
    return forgot_password(
        db=db,
        email=request.email,
    )


@router.post("/reset-password")
def reset_password_route(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return reset_password(
        db=db,
        token=request.token,
        new_password=request.new_password,
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_user_access(
    current_user,
    user_id,
)
    return update_user_service(
        db=db,
        user_id=user_id,
        name=request.name,
        email=request.email,
    )

@router.delete(
    "/{user_id}",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_user_access(
        current_user,
        user_id,
    )
    return delete_user_service(
        db=db,
        user_id=user_id,
    )
