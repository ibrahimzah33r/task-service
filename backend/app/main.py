from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import engine
from app.jobs.queue import close_redis
from app.jobs.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="Distributed Job System",
    lifespan=lifespan,
)

app.include_router(router)