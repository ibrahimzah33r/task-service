"""baseline existing schema

Revision ID: a34eadbe9246
Revises: 
Create Date: 2026-09-22 12:06:46.844097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a34eadbe9246"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


job_status_enum = postgresql.ENUM(
    "PENDING",
    "IN_PROGRESS",
    "SUCCESS",
    "FAILED",
    name="jobstatus",
    create_type=False,
)

job_type_enum = postgresql.ENUM(
    "UPPERCASE",
    name="jobtype",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    job_status_enum.create(
        bind,
        checkfirst=True,
    )

    job_type_enum.create(
        bind,
        checkfirst=True,
    )

    op.create_table(
        "workers",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "last_heartbeat",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jobs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "type",
            job_type_enum,
            nullable=False,
        ),
        sa.Column(
            "payload",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            job_status_enum,
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "worker_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "lease_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "max_retries",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "retry_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("workers")

    bind = op.get_bind()

    job_type_enum.drop(
        bind,
        checkfirst=True,
    )

    job_status_enum.drop(
        bind,
        checkfirst=True,
    )