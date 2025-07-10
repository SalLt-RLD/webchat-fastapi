from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt

from app.db.session import get_async_session
from app.models.models import User
from app.schemas.user import UserCreateSchema

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

    hashed_password = bcrypt.hash(user_data.password)

    # Создаём нового пользователя
    new_user = User(username=user_data.username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()

    return {"message": "Пользователь зарегистрирован"}
