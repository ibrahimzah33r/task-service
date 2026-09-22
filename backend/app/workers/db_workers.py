from datetime import datetime

from sqlalchemy import insert, select, update

from db import async_session
from jobs.models import Job, Worker


async def register_worker(name: str) -> int:
    async with async_session() as session:
        result = await session.execute(
            insert(Worker)
            .values(
                name=name,
                status="RUNNING",
                last_heartbeat=datetime.utcnow(),
            )
            .returning(Worker.id)
        )

        worker_id = result.scalar_one()

        await session.commit()

        return worker_id


async def update_worker_heartbeat(
    worker_id: int,
):
    async with async_session() as session:
        await session.execute(
            update(Worker)
            .where(Worker.id == worker_id)
            .values(
                status="RUNNING",
                last_heartbeat=datetime.utcnow(),
            )
        )

        await session.commit()


async def mark_worker_stopped(
    worker_id: int,
):
    async with async_session() as session:
        await session.execute(
            update(Worker)
            .where(Worker.id == worker_id)
            .values(
                status="STOPPED",
                last_heartbeat=datetime.utcnow(),
            )
        )

        await session.commit()


async def get_jobs_for_worker(
    worker_id: int,
):
    async with async_session() as session:
        result = await session.execute(
            select(Job).where(
                Job.worker_id == worker_id
            )
        )

        return result.scalars().all()