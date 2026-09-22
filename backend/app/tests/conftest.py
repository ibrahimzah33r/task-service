import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from jobs.models import Base


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


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