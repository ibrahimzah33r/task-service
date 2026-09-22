import asyncio
import logging

from app.workers.runner import worker_loop


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s - "
        "%(message)s"
    ),
)


if __name__ == "__main__":
    asyncio.run(worker_loop())