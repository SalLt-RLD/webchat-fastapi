import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'chat.db')}"

engine = create_async_engine(
    DATABASE_URL,
    future=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_temp_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
