"""Provide auth components for the application."""

import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


def validate_password_strength(password: str) -> str:
    """Validate password strength."""

    if not re.search(r"[A-Za-z]", password):
        raise ValueError(
            "Password must contain at least one alphabetic character"
        )

    if not re.search(r"\d", password):
        raise ValueError(
            "Password must contain at least one numeric character"
        )

    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError(
            "Password must contain at least one special character"
        )

    return password


class RegisterRequest(BaseModel):
    """Define the RegisterRequest API schema."""

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr = Field(
        max_length=254,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        password: str,
    ) -> str:
        """Validate registration password."""

        return validate_password_strength(password)


class LoginRequest(BaseModel):
    """Define the LoginRequest API schema."""

    email: EmailStr = Field(
        max_length=254,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    """Define the TokenResponse API schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Define the RegisterResponse API schema."""

    message: str
    user_id: int


class UpdateUserRequest(BaseModel):
    """Define the UpdateUserRequest API schema."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = Field(
        default=None,
        max_length=254,
    )


class UserResponse(BaseModel):
    """Define the UserResponse API schema."""

    id: int
    name: str
    email: str
    status: str
    role_id: int

    model_config = {
        "from_attributes": True,
    }


class RefreshTokenRequest(BaseModel):
    """Define the RefreshTokenRequest API schema."""

    refresh_token: str = Field(
        min_length=1,
    )


class ForgotPasswordRequest(BaseModel):
    """Define the ForgotPasswordRequest API schema."""

    email: EmailStr = Field(
        max_length=254,
    )


class ResetPasswordRequest(BaseModel):
    """Define the ResetPasswordRequest API schema."""

    token: str = Field(
        min_length=1,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        password: str,
    ) -> str:
        """Validate reset password."""

        return validate_password_strength(password)


class TokenData(BaseModel):
    """Define the TokenData API schema."""

    email: str | None = None