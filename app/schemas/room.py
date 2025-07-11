from datetime import datetime
from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    description: str | None = None


class RoomRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
