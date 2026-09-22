from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from jobs.models import Job, JobStatus
from jobs.queue import push_job
from jobs.schemas import JobCreateSchema


router = APIRouter()


@router.post("/jobs")
async def create_job(
    job_in: JobCreateSchema,
    session: AsyncSession = Depends(
        get_session
    ),
):
    job = Job(
        type=job_in.type,
        payload=job_in.payload,
        status=JobStatus.PENDING,
    )

    session.add(job)

    await session.commit()
    await session.refresh(job)

    await push_job(job.id)

    return {
        "job_id": job.id,
        "status": job.status,
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: int,
    session: AsyncSession = Depends(
        get_session
    ),
):
    result = await session.execute(
        select(Job).where(
            Job.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job.id,
        "type": job.type,
        "status": job.status,
        "payload": job.payload,
        "result": job.result,
        "worker_id": job.worker_id,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
    }