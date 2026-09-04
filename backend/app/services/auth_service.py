from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
    create_password_reset_token,
    decode_password_reset_token,
)

from app.repository.auth_repository import (
    get_user_by_email,
    get_role_by_name,
    create_user,
    update_last_login,
    get_user_by_id,
    update_user_password,
)

from app.repository.refresh_token_repository import(
    create_refresh_token_record,
    get_refresh_token_by_hash,
    revoke_refresh_token,
)


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
):

    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_role = get_role_by_name(
        db,
        "User",
    )

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default User role not configured",
        )

    password_hash = hash_password(password)

    user = create_user(
        db=db,
        name=name,
        email=email,
        password_hash=password_hash,
        role_id=user_role.id,
    )

    return user

def login_user(
    db: Session,
    email: str,
    password: str,
):

    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    user = update_last_login(
        db,
        user,
    )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role_id=user.role_id,
    )

    

   

    expires_at = get_refresh_token_expiry()

    refresh_token = create_refresh_token(
            user_id=user.id,
            expires_at=expires_at,
        )

    token_hash = hash_refresh_token(
        refresh_token)

    create_refresh_token_record(
    db=db,
    user_id=user.id,
    token_hash=token_hash,
    expires_at=expires_at,)


    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



def refresh_access_token(
    db: Session,
    refresh_token: str
):
    # 1. Decode refresh token
    try:
        payload = decode_refresh_token(
            refresh_token
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # 2. Get user ID from JWT
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # 3. Hash the refresh token
    token_hash = hash_refresh_token(
        refresh_token
    )

    # 4. Check refresh token in database
    stored_token = get_refresh_token_by_hash(
        db=db,
        token_hash=token_hash,
    )

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or revoked",
        )

    # 5. Check database expiry
    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # 6. Get user
    user = get_user_by_id(
        db,
        int(user_id),
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # 7. Check user status
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # 8. Create new access token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role_id=user.role_id,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

def logout_user(
    db: Session,
    refresh_token: str,
):
    # 1. Validate refresh token
    try:
        decode_refresh_token(
            refresh_token
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # 2. Hash refresh token
    token_hash = hash_refresh_token(
        refresh_token
    )

    # 3. Find token in database
    stored_token = get_refresh_token_by_hash(
        db=db,
        token_hash=token_hash,
    )

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or already revoked",
        )

    # 4. Revoke token
    revoke_refresh_token(
        db=db,
        refresh_token=stored_token,
    )

    return {
        "message": "Logout successful",
    }



def forgot_password(
    db: Session,
    email: str,
):
    user = get_user_by_email(
        db,
        email,
    )

    # Do not reveal whether email exists
    if not user:
        return {
            "message": (
                "If the email exists, "
                "a password reset link "
                "has been generated."
            )
        }

    reset_token = create_password_reset_token(
        user_id=user.id,
    )

    # Development/testing only
    return {
        "message": (
            "If the email exists, "
            "a password reset link "
            "has been generated."
        ),
        "reset_token": reset_token,
    }


def reset_password(
    db: Session,
    token: str,
    new_password: str,
):
    # 1. Validate reset token
    try:
        payload = decode_password_reset_token(
            token
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid or expired "
                "password reset token"
            ),
        )

    # 2. Get user ID
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password reset token",
        )

    # 3. Find user
    user = get_user_by_id(
        db,
        int(user_id),
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 4. Check account status
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # 5. Hash new password
    password_hash = hash_password(
        new_password
    )

    # 6. Update password
    update_user_password(
        db=db,
        user=user,
        password_hash=password_hash,
    )

    return {
        "message": "Password reset successful",
    }