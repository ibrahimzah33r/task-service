"""make timestamps timezone aware

Revision ID: 5046c9b1fcd1
Revises: a34eadbe9246
Create Date: 2026-09-23 10:01:31.130288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5046c9b1fcd1'
down_revision: Union[str, Sequence[str], None] = 'a34eadbe9246'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "workers",
        "last_heartbeat",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="last_heartbeat AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "jobs",
        "lease_expires_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="lease_expires_at AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )

    op.alter_column(
        "jobs",
        "retry_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="retry_at AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )

    op.alter_column(
        "jobs",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "jobs",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "jobs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "jobs",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "jobs",
        "retry_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="retry_at AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )

    op.alter_column(
        "jobs",
        "lease_expires_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="lease_expires_at AT TIME ZONE 'UTC'",
        existing_nullable=True,
    )

    op.alter_column(
        "workers",
        "last_heartbeat",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="last_heartbeat AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )