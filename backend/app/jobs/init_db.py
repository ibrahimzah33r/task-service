import asyncio

from app.db import engine
from app.jobs.models import Base


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )


if __name__ == "__main__":
    asyncio.run(init_db())