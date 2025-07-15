from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_session
from app.dependencies.auth import get_current_user
from app.models.models import User
from app.schemas.user import UserCreateSchema
from app.core.jwt import create_access_token
from app.core.hashing import hash_password, verify_password

router = APIRouter()


@router.post("/register", status_code=201)
async def register_user(user_data: Annotated[UserCreateSchema, Depends()],
                        session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.username == user_data.username)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже занято"
        )

    hashed_password: str = hash_password(user_data.password)

    new_user = User(username=user_data.username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()

    return {"message": "Пользователь зарегистрирован"}


@router.post("/login")
async def login_user(user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.username == user_data.username)
    result = await session.execute(query)
    user: User | None = result.scalar_one_or_none()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"username": user.username, "id": user.id}
