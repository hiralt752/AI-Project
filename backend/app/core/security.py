from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

import os
from dotenv import load_dotenv
import hashlib
import secrets
from sqlalchemy.orm import Session
from app.schema import auth
from app.models.user import User

load_dotenv()


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: int,
    email: str,
    role_id: int,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
   
    payload = {
        "sub": str(user_id),
        "email": email,
        "role_id": role_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM"),
    )


def get_refresh_token_expiry():
    expire_days = int(
        os.getenv(
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
            "7",
        )
    )

    return datetime.now(timezone.utc) + timedelta(
        days=expire_days
    )

def create_refresh_token(user_id: int,  expires_at: datetime) -> str:

    # expire = get_refresh_token_expiry()

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires_at,
        "jti": secrets.token_urlsafe(32),
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv(
            "JWT_ALGORITHM",
            "HS256",
        ),
    )



def decode_refresh_token(
    refresh_token: str,
) -> dict:

    try:
        payload = jwt.decode(
            refresh_token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[
                os.getenv("JWT_ALGORITHM")
            ],
        )

        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return payload

    except JWTError:
        raise ValueError("Invalid or expired refresh token")


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()



def create_password_reset_token(
    user_id: int,
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=int(
            os.getenv(
                "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
                "15",
            )
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "password_reset",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv(
            "JWT_ALGORITHM",
            "HS256",
        ),
    )


def decode_password_reset_token(
    token: str,
) -> dict:

    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[
                os.getenv(
                    "JWT_ALGORITHM",
                    "HS256",
                )
            ],
        )

        if payload.get("type") != "password_reset":
            raise JWTError(
                "Invalid token type"
            )

        return payload

    except JWTError:
        raise ValueError(
            "Invalid or expired password reset token"
        )

def verify_token(token: str, credentials_exception, db: Session):
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        current_user = db.get(User, int(user_id))
        if not current_user:
            raise credentials_exception

        return current_user

    except (JWTError, TypeError, ValueError):
        raise credentials_exception


