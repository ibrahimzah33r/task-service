import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.config import TEST_DATABASE_URL
from app.jobs.models import Base


@pytest.fixture
async def test_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield session_factory

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )

    await engine.dispose()