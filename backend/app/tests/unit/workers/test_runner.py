from types import SimpleNamespace

import pytest

from jobs.models import JobType
from workers.runner import generate_worker_name, process_job


def test_generate_worker_name_contains_separator():
    worker_name = generate_worker_name()

    assert "-" in worker_name


@pytest.mark.asyncio
async def test_process_uppercase_job():
    job = SimpleNamespace(
        type=JobType.UPPERCASE,
        payload="hello world",
    )

    result = await process_job(job)

    assert result == "HELLO WORLD"


@pytest.mark.asyncio
async def test_unknown_job_type_raises_error():
    job = SimpleNamespace(
        type="unknown",
        payload="hello",
    )

    with pytest.raises(
        ValueError,
        match="Unknown job type",
    ):
        await process_job(job)