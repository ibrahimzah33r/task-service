from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import engine
from jobs.queue import close_redis
from jobs.routes import router 


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )