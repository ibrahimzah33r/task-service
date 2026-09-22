from jobs.db_jobs import claim_job
from jobs.models import Job, JobStatus, JobType


async def test_job_can_only_be_claimed_once(
    test_db,
    monkeypatch,
):
    monkeypatch.setattr(
        "jobs.db_jobs.async_session",
        test_db,
    )

    async with test_db() as session:
        job = Job(
            type=JobType.UPPERCASE,
            payload="hello",
            status=JobStatus.PENDING,
        )

        session.add(job)
        await session.commit()
        await session.refresh(job)

        job_id = job.id

    first_claim = await claim_job(
        job_id,
        worker_id=10,
    )

    second_claim = await claim_job(
        job_id,
        worker_id=20,
    )

    assert first_claim is True
    assert second_claim is False

    async with test_db() as session:
        job = await session.get(
            Job,
            job_id,
        )

        assert job.status == JobStatus.IN_PROGRESS
        assert job.worker_id == 10
        assert job.lease_expires_at is not None