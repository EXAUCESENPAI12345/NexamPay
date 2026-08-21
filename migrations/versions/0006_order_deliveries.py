"""Add order deliveries.

Revision ID: 0006_order_deliveries
Revises: 0005_revenue_ledger
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_order_deliveries"
down_revision = "0005_revenue_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "order_deliveries",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey(
                "orders.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "telegram_user_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "delivery_type",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_order_deliveries_order_id",
        "order_deliveries",
        ["order_id"],
        unique=True,
    )

    op.create_index(
        "ix_order_deliveries_telegram_user_id",
        "order_deliveries",
        ["telegram_user_id"],
    )

    op.create_index(
        "ix_order_deliveries_status",
        "order_deliveries",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_deliveries_status",
        table_name="order_deliveries",
    )

    op.drop_index(
        "ix_order_deliveries_telegram_user_id",
        table_name="order_deliveries",
    )

    op.drop_index(
        "ix_order_deliveries_order_id",
        table_name="order_deliveries",
    )

    op.drop_table("order_deliveries")