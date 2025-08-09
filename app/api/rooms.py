from typing import Annotated, Iterable
from fastapi import APIRouter, Depends

from app.db.requests_db import get_rooms, add_room
from app.db.session import get_async_session, AsyncSession
from app.dependencies.auth import get_current_user
from app.models.models import Room, User
from app.schemas.room import RoomRead, RoomCreateForm

router = APIRouter()


@router.get("/")
async def get_rooms_handler(session: AsyncSession = Depends(get_async_session)) -> list[RoomRead]:
    rooms: Iterable[Room] = await get_rooms(session=session)
    return [RoomRead.model_validate(room, from_attributes=True) for room in rooms]


@router.post("/", status_code=201)
async def create_room(room_data: Annotated[RoomCreateForm, Depends()],
                      current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session)) -> RoomRead:
    new_room: Room = await add_room(
        session=session,
        name=room_data.name,
        description=room_data.description
    )
    return RoomRead.model_validate(new_room, from_attributes=True)
