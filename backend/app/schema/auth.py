from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    message: str
    user_id: int

class UpdateUserRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    status: str
    role_id: int

    model_config = {
        "from_attributes": True
    }

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

class TokenData(BaseModel):
    email: str | None = None
