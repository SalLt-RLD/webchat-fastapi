from fastapi import Form
from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    password: str


class UserCreateForm:
    def __init__(
            self,
            username: str = Form(...),
            password: str = Form(...)
    ):
        self.username = username
        self.password = password

    def to_schema(self) -> UserCreateSchema:
        return UserCreateSchema(username=self.username, password=self.password)
