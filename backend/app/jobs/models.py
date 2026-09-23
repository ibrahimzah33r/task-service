import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text

from app.db import engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class JobType(str, enum.Enum):
    UPPERCASE = "uppercase"


class Worker(Base):
    __tablename__ = "workers"

    id = Column(
        Integer,
        primary_key=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="RUNNING",
    )

    last_heartbeat = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    
class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
    )

    type = Column(
        Enum(JobType),
        nullable=False,
    )

    payload = Column(
        Text,
        nullable=True,
    )

    status = Column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
    )

    result = Column(
        Text,
        nullable=True,
    )

    worker_id = Column(
        Integer,
        nullable=True,
    )

    lease_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    retry_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    max_retries = Column(
        Integer,
        default=3,
        nullable=False,
    )

    retry_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )