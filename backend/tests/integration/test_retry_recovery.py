from datetime import datetime, timedelta

from app.jobs.db_jobs import (
    reset_expired_jobs,
    schedule_retry,
)
from app.jobs.models import (
    Job,
    JobStatus,
    JobType,
)


async def test_schedule_retry_updates_job(
    test_db,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.jobs.db_jobs.async_session",
        test_db,
    )

    async with test_db() as session:
        job = Job(
            type=JobType.UPPERCASE,
            payload="hello",
            status=JobStatus.IN_PROGRESS,
            retry_count=0,
            max_retries=3,
        )

        session.add(job)
        await session.commit()
        await session.refresh(job)

        job_id = job.id

    retrying, attempt = await schedule_retry(
        job_id
    )

    assert retrying is True
    assert attempt == 1

    async with test_db() as session:
        job = await session.get(
            Job,
            job_id,
        )

        assert job.status == JobStatus.PENDING
        assert job.retry_count == 1
        assert job.retry_at is not None
        assert job.worker_id is None
        assert job.lease_expires_at is None


async def test_reset_expired_job(
    test_db,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.jobs.db_jobs.async_session",
        test_db,
    )

    expired_time = (
        datetime.utcnow()
        - timedelta(seconds=10)
    )

    async with test_db() as session:
        job = Job(
            type=JobType.UPPERCASE,
            payload="hello",
            status=JobStatus.IN_PROGRESS,
            worker_id=25,
            lease_expires_at=expired_time,
        )

        session.add(job)
        await session.commit()
        await session.refresh(job)

        job_id = job.id

    recovered_ids = await reset_expired_jobs()

    assert job_id in recovered_ids

    async with test_db() as session:
        job = await session.get(
            Job,
            job_id,
        )

        assert job.status == JobStatus.PENDING
        assert job.worker_id is None
        assert job.lease_expires_at is None