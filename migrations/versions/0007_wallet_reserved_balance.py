"""Add reserved balance to wallets.

Revision ID: 0007_wallet_reserved_balance
Revises: 0006_order_deliveries
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_wallet_reserved_balance"
down_revision = "0006_order_deliveries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "wallets",
        sa.Column(
            "reserved_balance",
            sa.Numeric(20, 2),
            nullable=False,
            server_default="0.00",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "wallets",
        "reserved_balance",
    )