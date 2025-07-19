from typing import Annotated
from fastapi import APIRouter, Depends

from app.db.requests_db import get_messages_stream, add_message
from app.db.session import get_async_session, AsyncSession
from app.dependencies.auth import get_current_user
from app.models.models import User, Message
from app.schemas.message import MessageRead, MessageCreate

router = APIRouter()


@router.get("/{room_id}/messages")
async def get_messages_handler(room_id: int, session: AsyncSession = Depends(get_async_session)) -> list[MessageRead]:
    messages: list[MessageRead] = []
    async for message in get_messages_stream(session, room_id):
        messages += [MessageRead.model_validate(message, from_attributes=True)]
    return messages


@router.post("/{room_id}/messages", status_code=201)
async def create_message(room_id: int,
                         message_data: Annotated[MessageCreate, Depends()],
                         current_user: Annotated[User, Depends(get_current_user)],
                         session: AsyncSession = Depends(get_async_session)
                         ) -> MessageRead:
    new_message: Message = await add_message(session=session, content=message_data.content,
                                             user_id=current_user.id, room_id=room_id)
    return MessageRead.model_validate(new_message, from_attributes=True)
