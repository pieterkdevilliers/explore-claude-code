from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import LocalSessionFactory, get_heroku_session_factory
from app.models.user import User
from app.services.auth_service import decode_token
from app.services.user_service import get_user_by_email

bearer_scheme = HTTPBearer()


async def get_local_db() -> AsyncGenerator[AsyncSession, None]:
    async with LocalSessionFactory() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_local_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_heroku_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_heroku_session_factory()
    if factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Heroku database not configured. Use POST /db-connection/save to set it up.",
        )
    async with factory() as session:
        yield session


async def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return current_user
