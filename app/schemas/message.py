from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    content: str
    timestamp: datetime
    user_id: int
    room_id: int
