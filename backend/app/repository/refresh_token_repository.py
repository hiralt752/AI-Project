from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token_record(
    db: Session,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
):
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token_by_hash(
    db: Session,
    token_hash: str,
):
    return db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.is_deleted == False,
        )
    )


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
):
    refresh_token.revoked = True

    db.commit()
    db.refresh(refresh_token)

    return refresh_token