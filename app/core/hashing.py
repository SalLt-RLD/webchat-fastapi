from typing import Union
from passlib.context import CryptContext
from sqlalchemy.orm import Mapped

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
StrType = Union[str, Mapped[str]]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: StrType, hashed_password: StrType) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
