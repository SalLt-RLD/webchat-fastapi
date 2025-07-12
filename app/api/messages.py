from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.dependencies.auth import get_current_user
from app.models.models import Message, User
from app.schemas.message import MessageRead, MessageCreate

router = APIRouter()


@router.get("/{room_id}/messages")
async def get_messages(room_id: int, session: AsyncSession = Depends(get_async_session)) -> list[MessageRead]:
    query = select(Message).where(Message.room_id == room_id)
    result = await session.execute(query)
    messages = result.scalars().all()

    return [MessageRead.model_validate(message, from_attributes=True) for message in messages]


@router.post("/{room_id}/messages", status_code=201)
async def create_message(room_id: int,
                         message_data: Annotated[MessageCreate, Depends()],
                         current_user: Annotated[User, Depends(get_current_user)],
                         session: AsyncSession = Depends(get_async_session)
                         ) -> MessageRead:
    new_message = Message(content=message_data.content,
                          user_id=current_user.id,
                          room_id=room_id)
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)

    return MessageRead.model_validate(new_message, from_attributes=True)
