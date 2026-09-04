from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from  app.core.security import verify_token
from sqlalchemy.orm import Session
from app.database.connection import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception, db)