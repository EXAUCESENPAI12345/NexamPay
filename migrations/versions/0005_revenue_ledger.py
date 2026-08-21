"""Add NexamPay revenue ledger.

Revision ID: 0005_revenue_ledger
Revises: 0004_user_role
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_revenue_ledger"
down_revision = "0004_user_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "revenue_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "revenue_id",
            sa.String(50),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "revenue_type",
            sa.String(40),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
        ),

        sa.Column(
            "amount",
            sa.Numeric(20, 2),
            nullable=False,
        ),

        sa.Column(
            "currency_code",
            sa.String(10),
            nullable=False,
        ),

        sa.Column(
            "source_transaction_id",
            sa.Integer(),
            sa.ForeignKey(
                "transactions.id",
            ),
            nullable=True,
        ),

        sa.Column(
            "source_order_id",
            sa.Integer(),
            sa.ForeignKey(
                "orders.id",
            ),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.String(500),
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
        "ix_revenue_ledger_revenue_id",
        "revenue_ledger",
        ["revenue_id"],
        unique=True,
    )

    op.create_index(
        "ix_revenue_ledger_revenue_type",
        "revenue_ledger",
        ["revenue_type"],
    )

    op.create_index(
        "ix_revenue_ledger_status",
        "revenue_ledger",
        ["status"],
    )

    op.create_index(
        "ix_revenue_ledger_currency_code",
        "revenue_ledger",
        ["currency_code"],
    )

    op.create_index(
        "ix_revenue_ledger_source_transaction_id",
        "revenue_ledger",
        ["source_transaction_id"],
    )

    op.create_index(
        "ix_revenue_ledger_source_order_id",
        "revenue_ledger",
        ["source_order_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_revenue_ledger_source_order_id",
        table_name="revenue_ledger",
    )

    op.drop_index(
        "ix_revenue_ledger_source_transaction_id",
        table_name="revenue_ledger",
    )

    op.drop_index(
        "ix_revenue_ledger_currency_code",
        table_name="revenue_ledger",
    )

    op.drop_index(
        "ix_revenue_ledger_status",
        table_name="revenue_ledger",
    )

    op.drop_index(
        "ix_revenue_ledger_revenue_type",
        table_name="revenue_ledger",
    )

    op.drop_index(
        "ix_revenue_ledger_revenue_id",
        table_name="revenue_ledger",
    )

    op.drop_table("revenue_ledger")