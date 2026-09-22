import os
from pathlib import Path

from dotenv import load_dotenv
from redis.asyncio import Redis


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


REDIS_URL = os.environ["REDIS_URL"]

QUEUE_KEY = "jobs_queue"
QUEUED_JOBS_KEY = "queued_jobs"


redis = Redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def push_job(job_id: int):
    job_id_str = str(job_id)

    added = await redis.sadd(
        QUEUED_JOBS_KEY,
        job_id_str,
    )

    if added:
        await redis.lpush(
            QUEUE_KEY,
            job_id_str,
        )


async def pop_job():
    job_id = await redis.rpop(QUEUE_KEY)

    if job_id is None:
        return None

    await redis.srem(
        QUEUED_JOBS_KEY,
        job_id,
    )

    return int(job_id)


async def close_redis():
    await redis.aclose()