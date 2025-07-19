from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Iterable, AsyncGenerator

from app.models.models import Message, User, Room


async def get_user_by_name(session: AsyncSession, username: str) -> User | None:
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def add_user(session: AsyncSession, username: str, hashed_password: str) -> None:
    new_user = User(username=username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()


async def get_messages_stream(session: AsyncSession, room_id: int) -> AsyncGenerator[Message]:
    query = select(Message).where(Message.room_id == room_id).order_by(Message.timestamp)
    stream = await session.stream(query)
    async for row in stream:
        yield row.Message


async def add_message(session: AsyncSession, content: str, user_id: int,
                      room_id: int) -> Message:
    new_message = Message(content=content,
                          user_id=user_id,
                          room_id=room_id)
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)
    return new_message


async def get_rooms(session: AsyncSession) -> Iterable[Room]:
    query = select(Room)
    result = await session.execute(query)
    return result.scalars().all()


async def add_room(session: AsyncSession, name: str, description: str) -> Room:
    new_room = Room(name=name, description=description)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)

    return new_room
