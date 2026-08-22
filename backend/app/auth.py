import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.database import engine
from app.models import User

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_access_token(data: dict) -> str:
    """Creates a signed JWT token containing the given data, expiring in 1 hour."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """Decodes the JWT token from the request and returns the user's email.
    Raises 401 if the token is missing, invalid, or expired."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception


def get_current_admin_user(
    current_user_email: str = Depends(get_current_user_email),
) -> str:
    """Ensures the current user is an admin. Raises 403 if not."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == current_user_email)).first()
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires admin privileges",
            )
        return current_user_email