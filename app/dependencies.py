from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models, security
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """Token'dan kullanıcıyı doğrular ve döndürür."""
    email = security.get_user_from_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Geçersiz token!")
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı!")
    return user
