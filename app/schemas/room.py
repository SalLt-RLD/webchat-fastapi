from datetime import datetime
from fastapi import Form
from pydantic import BaseModel


class RoomCreateSchema(BaseModel):
    name: str
    description: str | None = None


class RoomCreateForm:
    def __init__(self,
                 name: str = Form(...),
                 description: str | None = Form(None)):
        self.name = name
        self.description = description

    def to_schema(self) -> RoomCreateSchema:
        return RoomCreateSchema(name=self.name, description=self.description)


class RoomRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
