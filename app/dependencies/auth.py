from fastapi import Depends, HTTPException, status, Request
from jose import JWTError

from app.db.requests_db import get_user_by_id
from app.core.jwt import decode_access_token
from app.db.session import get_async_session, AsyncSession
from app.models.models import User


async def get_current_user(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (no token in cookies)",
        )

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials (invalid token)",
        )

    user = await get_user_by_id(session=session, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
