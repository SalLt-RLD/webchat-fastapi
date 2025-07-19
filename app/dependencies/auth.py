from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.db.requests_db import get_user_by_id
from app.core.jwt import decode_access_token
from app.db.session import get_async_session, AsyncSession
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (invalid token)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict | None = decode_access_token(token)
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user: User | None = await get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise credentials_exception

    return user
