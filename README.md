# Distributed Task Service

A distributed background job-processing service built with **FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, Docker, and Python asyncio**.

The project demonstrates how an API can accept jobs, persist them reliably, distribute them through a queue, and process them across independent workers with retry, leasing, recovery, and atomic job claiming.

## Architecture

```text
Client
  │
  ▼
FastAPI API
  │
  ├── Store job ──────────────► PostgreSQL
  │
  └── Queue job ID ───────────► Redis
                                  │
                                  ▼
                               Worker
                                  │
                     Atomic claim in PostgreSQL
                                  │
                                  ▼
                            Process job
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
                 SUCCESS                     FAILURE
                    │                           │
                    ▼                           ▼
             Store result              Schedule retry
             in PostgreSQL              with backoff
```

### Component responsibilities

- **FastAPI** — exposes HTTP endpoints for creating and retrieving jobs.
- **PostgreSQL** — source of truth for job state, results, workers, retries, and leases.
- **Redis** — fast queue used to distribute job IDs to workers.
- **Worker** — claims and processes jobs independently from the API.
- **SQLAlchemy** — async database access and ORM mapping.
- **Alembic** — database schema migrations.
- **Docker Compose** — runs PostgreSQL, Redis, migrations, API, and worker services.
- **GitHub Actions** — automatically runs the test suite on pushes and pull requests.

## Job lifecycle

A job normally moves through:

```text
PENDING
   │
   ▼
IN_PROGRESS
   │
   ├── success ──► SUCCESS
   │
   └── failure ──► PENDING / retry
                       │
                       └── retries exhausted ──► FAILED
```

When a client creates a job:

1. FastAPI writes the full job to PostgreSQL.
2. The job ID is pushed into Redis.
3. A worker pops the ID from Redis.
4. The worker atomically claims the job in PostgreSQL.
5. The worker processes the job.
6. The result and final status are stored in PostgreSQL.

Redis is therefore used for **distribution**, while PostgreSQL remains the authoritative record.

## Reliability features

### Atomic job claiming

Workers claim jobs using a conditional database update.

Only a job that is still `PENDING` can be changed to `IN_PROGRESS`.

This prevents two workers from successfully processing the same job simultaneously.

### Job leases

When a worker claims a job, it receives a temporary lease.

If the worker dies while processing the job, the lease eventually expires and the job can be recovered.

### Worker heartbeats

Workers periodically update their heartbeat timestamp so the system can track whether they are still active.

### Retry scheduling

Failed jobs are returned to `PENDING` with:

- incremented retry count
- future retry timestamp
- cleared worker assignment
- cleared lease

Retries use exponential backoff.

### Expired-job recovery

Jobs left `IN_PROGRESS` after their worker disappears can be detected through expired leases and returned to the queue.

### Queue deduplication

Redis uses:

```text
jobs_queue
```

as the FIFO job queue and:

```text
queued_jobs
```

as a set of IDs already queued.

This reduces accidental duplicate queue entries.

## Technology stack

- Python 3.14
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- asyncpg
- Redis
- asyncio
- Alembic
- Pydantic
- Pytest
- pytest-asyncio
- Docker
- Docker Compose
- GitHub Actions

## Project structure

```text
task-service/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   │   ├── integration/
│   │   └── unit/
│   │
│   ├── app/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── main.py
│   │   │
│   │   ├── jobs/
│   │   │   ├── db_jobs.py
│   │   │   ├── models.py
│   │   │   ├── queue.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   │
│   │   └── workers/
│   │       ├── db_workers.py
│   │       ├── runner.py
│   │       └── __main__.py
│   │
│   ├── Dockerfile
│   ├── alembic.ini
│   └── pyproject.toml
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Local setup

Create and activate a virtual environment from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a root `.env` file containing the required database and Redis configuration.

Example structure:

```text
DATABASE_URL=postgresql+asyncpg://taskuser:<password>@localhost:5432/taskdb
TEST_DATABASE_URL=postgresql+asyncpg://taskuser:<password>@localhost:5432/taskdb_test
REDIS_URL=redis://localhost:6379
POSTGRES_PASSWORD=<password>
```

Do not commit `.env`.

## Run infrastructure locally

Start only PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Run the API from `backend/`:

```bash
./scripts/run-api.sh
```

Run a worker in another terminal:

```bash
./scripts/run-worker.sh
```

The API runs at:

```text
http://localhost:8000
```

## Run the full system with Docker

From the repository root:

```bash
docker compose up --build
```

Compose starts:

```text
PostgreSQL
Redis
Migration service
FastAPI API
Worker
```

The migration service executes:

```bash
alembic upgrade head
```

before the API and worker begin normal operation.

Stop everything with:

```bash
docker compose down
```

## Example API usage

Create an uppercase job:

```bash
curl \
  -X POST \
  http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"uppercase","payload":"hello world"}'
```

Example response:

```json
{
  "job_id": 1,
  "status": "PENDING"
}
```

Retrieve it:

```bash
curl http://localhost:8000/jobs/1
```

Once processed:

```json
{
  "job_id": 1,
  "type": "uppercase",
  "status": "SUCCESS",
  "payload": "hello world",
  "result": "HELLO WORLD",
  "worker_id": 1,
  "retry_count": 0,
  "max_retries": 3
}
```

## Testing

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

From `backend/` run the complete suite:

```bash
./scripts/test.sh
```

Run only unit tests:

```bash
./scripts/test-unit.sh
```

Run only integration tests:

```bash
./scripts/test-integration.sh
```

The test suite covers:

- worker job processing
- unsupported job types
- atomic job claiming
- retry scheduling
- expired lease recovery
- worker failure handling

## Continuous integration

GitHub Actions runs the test suite automatically on:

- pushes to `main`
- pull requests targeting `main`

The CI environment creates temporary PostgreSQL and Redis services so integration tests run against real infrastructure.

## Database migrations

Schema changes are managed with Alembic.

Create a migration:

```bash
alembic revision --autogenerate -m "describe change"
```

Review the generated migration before applying it.

Apply migrations:

```bash
alembic upgrade head
```

## Key design decisions

### PostgreSQL instead of Redis as the source of truth

Redis is intentionally used only for fast job distribution.

If Redis state is lost, PostgreSQL still contains the authoritative job state.

### Independent workers

Workers are separate processes from the API and can be scaled independently.

### Database-level claiming

Correctness does not depend on two workers checking state at exactly the right time.

The database decides which worker successfully claims each job.

### Leases instead of permanent ownership

A crashed worker cannot hold a job forever. Expired leases allow abandoned work to be recovered.

## Future extensions

Possible additions include:

- multiple job types
- worker concurrency limits
- dead-letter queues
- job cancellation
- priority queues
- metrics and dashboards
- OpenTelemetry tracing
- distributed scheduler service
- Redis transactions or Lua-based queue operations
- horizontal worker autoscaling
