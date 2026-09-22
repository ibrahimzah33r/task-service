import asyncio
import socket
import uuid
from time import monotonic

from jobs.db_jobs import (
    claim_job,
    complete_job,
    get_dispatchable_job_ids,
    get_job_by_id,
    reset_expired_jobs,
    schedule_retry,
)
from jobs.models import JobType
from jobs.queue import push_job
from jobs.queue import pop_job
from workers.db_workers import (
    mark_worker_stopped,
    register_worker,
    update_worker_heartbeat,
)


HEARTBEAT_INTERVAL_SECONDS = 10
IDLE_SLEEP_SECONDS = 0.5


def generate_worker_name():
    hostname = socket.gethostname()
    unique = uuid.uuid4().hex[:6]

    return f"{hostname}-{unique}"


async def process_job(job):
    if job.type == JobType.UPPERCASE:
        await asyncio.sleep(1)

        return job.payload.upper()

    raise ValueError(
        f"Unknown job type: {job.type}"
    )


async def dispatch_pending_jobs():
    job_ids = await get_dispatchable_job_ids()

    for job_id in job_ids:
        await push_job(job_id)


async def recover_expired_jobs():
    job_ids = await reset_expired_jobs()

    for job_id in job_ids:
        await push_job(job_id)


async def worker_loop():
    worker_name = generate_worker_name()
    worker_id = await register_worker(worker_name)

    print(
        f"Worker started: {worker_name} "
        f"(ID {worker_id})"
    )

    last_heartbeat = monotonic()

    try:
        while True:
            now = monotonic()

            if (
                now - last_heartbeat
                >= HEARTBEAT_INTERVAL_SECONDS
            ):
                await update_worker_heartbeat(
                    worker_id
                )

                last_heartbeat = now

            await recover_expired_jobs()
            await dispatch_pending_jobs()

            job_id = await pop_job()

            if job_id is None:
                await asyncio.sleep(
                    IDLE_SLEEP_SECONDS
                )
                continue

            claimed = await claim_job(
                job_id,
                worker_id,
            )

            if not claimed:
                continue

            job = await get_job_by_id(job_id)

            if job is None:
                continue

            print(
                f"Job started: {job.id}"
            )

            try:
                result = await process_job(job)

                await complete_job(
                    job.id,
                    result,
                )

                print(
                    f"Job completed: {job.id}"
                )

            except Exception as exc:
                print(
                    f"Job {job.id} failed: {exc}"
                )

                retrying, attempt = (
                    await schedule_retry(job.id)
                )

                if retrying:
                    print(
                        f"Job {job.id} scheduled "
                        f"for retry {attempt}"
                    )

                else:
                    print(
                        f"Job {job.id} permanently "
                        f"failed after {attempt - 1} retries"
                    )

    finally:
        await mark_worker_stopped(
            worker_id
        )


if __name__ == "__main__":
    asyncio.run(worker_loop())