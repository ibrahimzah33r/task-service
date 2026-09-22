from datetime import datetime, timedelta

from sqlalchemy import select, update

from db import async_session
from jobs.models import Job, JobStatus


LEASE_SECONDS = 30


async def get_job_by_id(job_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Job).where(Job.id == job_id)
        )

        return result.scalar_one_or_none()


async def claim_job(
    job_id: int,
    worker_id: int,
) -> bool:
    lease_expires_at = datetime.utcnow() + timedelta(
        seconds=LEASE_SECONDS
    )

    async with async_session() as session:
        result = await session.execute(
            update(Job)
            .where(
                Job.id == job_id,
                Job.status == JobStatus.PENDING,
                (
                    (Job.retry_at == None)
                    | (Job.retry_at <= datetime.utcnow())
                ),
            )
            .values(
                status=JobStatus.IN_PROGRESS,
                worker_id=worker_id,
                lease_expires_at=lease_expires_at,
                retry_at=None,
                updated_at=datetime.utcnow(),
            )
        )

        await session.commit()

        return result.rowcount == 1


async def complete_job(
    job_id: int,
    result: str,
):
    async with async_session() as session:
        await session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                result=result,
                status=JobStatus.SUCCESS,
                lease_expires_at=None,
                retry_at=None,
                updated_at=datetime.utcnow(),
            )
        )

        await session.commit()


async def schedule_retry(job_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Job)
            .where(Job.id == job_id)
            .with_for_update()
        )

        job = result.scalar_one_or_none()

        if job is None:
            return False, 0

        next_retry_count = job.retry_count + 1

        if next_retry_count > job.max_retries:
            job.status = JobStatus.FAILED
            job.lease_expires_at = None
            job.retry_at = None
            job.updated_at = datetime.utcnow()

            await session.commit()

            return False, next_retry_count

        delay_seconds = 2 ** next_retry_count

        job.retry_count = next_retry_count
        job.retry_at = datetime.utcnow() + timedelta(
            seconds=delay_seconds
        )

        job.status = JobStatus.PENDING
        job.worker_id = None
        job.lease_expires_at = None
        job.updated_at = datetime.utcnow()

        await session.commit()

        return True, next_retry_count


async def reset_expired_jobs():
    now = datetime.utcnow()

    async with async_session() as session:
        result = await session.execute(
            select(Job.id).where(
                Job.status == JobStatus.IN_PROGRESS,
                Job.lease_expires_at != None,
                Job.lease_expires_at < now,
            )
        )

        job_ids = list(result.scalars().all())

        if not job_ids:
            return []

        await session.execute(
            update(Job)
            .where(Job.id.in_(job_ids))
            .values(
                status=JobStatus.PENDING,
                worker_id=None,
                lease_expires_at=None,
                updated_at=now,
            )
        )

        await session.commit()

        return job_ids


async def get_dispatchable_job_ids(
    limit: int = 100,
):
    now = datetime.utcnow()

    async with async_session() as session:
        result = await session.execute(
            select(Job.id)
            .where(
                Job.status == JobStatus.PENDING,
                (
                    (Job.retry_at == None)
                    | (Job.retry_at <= now)
                ),
            )
            .limit(limit)
        )

        return list(result.scalars().all())