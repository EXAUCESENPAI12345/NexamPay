"""Add order idempotency key.

Revision ID: 0015_order_idempotency
Revises: 0014_merge_and_pin
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_order_idempotency"
down_revision = "0014_merge_and_pin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
    )
    op.execute(
        "UPDATE orders SET idempotency_key = 'legacy:' || order_number WHERE idempotency_key IS NULL"
    )
    op.alter_column(
        "orders",
        "idempotency_key",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.create_index(
        "ix_orders_idempotency_key",
        "orders",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_orders_idempotency_key", table_name="orders")
    op.drop_column("orders", "idempotency_key")
