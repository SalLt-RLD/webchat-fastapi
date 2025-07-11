from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.models.models import Room
from app.schemas.room import RoomRead, RoomCreate

router = APIRouter()


@router.get("/")
async def get_rooms(session: AsyncSession = Depends(get_async_session)) -> list[RoomRead]:
    query = select(Room)
    result = await session.execute(query)
    return [RoomRead.model_validate(room, from_attributes=True) for room in result.scalars().all()]


@router.post("/", status_code=201)
async def create_room(room_data: Annotated[RoomCreate, Depends()],
                      session: AsyncSession = Depends(get_async_session)) -> RoomRead:
    new_room = Room(name=room_data.name, description=room_data.description)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)

    return RoomRead.model_validate(new_room, from_attributes=True)
