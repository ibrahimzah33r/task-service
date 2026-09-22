from sqlalchemy import select

from app.jobs.db_jobs import (
    schedule_retry as real_schedule_retry,
)
from app.jobs.models import (
    Job,
    JobStatus,
    JobType,
)
from app.workers.runner import handle_job


async def test_worker_failure_schedules_retry(
    test_db,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.jobs.db_jobs.async_session",
        test_db,
    )

    monkeypatch.setattr(
        "app.workers.runner.schedule_retry",
        real_schedule_retry,
    )

    async with test_db() as session:
        job = Job(
            type=JobType.UPPERCASE,
            payload="hello",
            status=JobStatus.IN_PROGRESS,
            worker_id=10,
            retry_count=0,
            max_retries=3,
        )

        session.add(job)

        await session.commit()
        await session.refresh(job)

        job_id = job.id

    async def failing_process_job(job):
        raise RuntimeError(
            "simulated worker failure"
        )

    monkeypatch.setattr(
        "app.workers.runner.process_job",
        failing_process_job,
    )

    async with test_db() as session:
        result = await session.execute(
            select(Job).where(
                Job.id == job_id
            )
        )

        job = result.scalar_one()

    await handle_job(
        job,
        worker_id=10,
    )

    async with test_db() as session:
        result = await session.execute(
            select(Job).where(
                Job.id == job_id
            )
        )

        updated_job = result.scalar_one()

        assert updated_job.status == JobStatus.PENDING
        assert updated_job.retry_count == 1
        assert updated_job.retry_at is not None
        assert updated_job.worker_id is None
        assert updated_job.lease_expires_at is None