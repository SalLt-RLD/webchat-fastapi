import asyncio
from app.db.session import engine
from app.models.models import Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы успешно созданы!")


if __name__ == "__main__":
    asyncio.run(init_models())
