"""Add transfer idempotency key.

Revision ID: 0009_transfer_idempotency
Revises: 0008_transfers
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_transfer_idempotency"
down_revision = "0008_transfers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transfers",
        sa.Column(
            "idempotency_key",
            sa.String(100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_transfers_idempotency_key",
        "transfers",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transfers_idempotency_key",
        table_name="transfers",
    )

    op.drop_column(
        "transfers",
        "idempotency_key",
    )