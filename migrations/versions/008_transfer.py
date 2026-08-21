"""Add NexamPay transfers.

Revision ID: 0008_transfers
Revises: 0007_wallet_reserved_balance
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_transfers"
down_revision = "0007_wallet_reserved_balance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transfers",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "transfer_id",
            sa.String(50),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "transaction_id",
            sa.Integer(),
            sa.ForeignKey(
                "transactions.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "sender_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),

        sa.Column(
            "receiver_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),

        sa.Column(
            "sender_currency",
            sa.String(10),
            nullable=False,
        ),

        sa.Column(
            "receiver_currency",
            sa.String(10),
            nullable=False,
        ),

        sa.Column(
            "amount_sent",
            sa.Numeric(20, 2),
            nullable=False,
        ),

        sa.Column(
            "fee",
            sa.Numeric(20, 2),
            nullable=False,
        ),

        sa.Column(
            "total_debited",
            sa.Numeric(20, 2),
            nullable=False,
        ),

        sa.Column(
            "exchange_rate",
            sa.Numeric(30, 12),
            nullable=False,
        ),

        sa.Column(
            "amount_received",
            sa.Numeric(20, 2),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
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
        "ix_transfers_transfer_id",
        "transfers",
        ["transfer_id"],
        unique=True,
    )

    op.create_index(
        "ix_transfers_sender_id",
        "transfers",
        ["sender_id"],
    )

    op.create_index(
        "ix_transfers_receiver_id",
        "transfers",
        ["receiver_id"],
    )

    op.create_index(
        "ix_transfers_status",
        "transfers",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transfers_status",
        table_name="transfers",
    )

    op.drop_index(
        "ix_transfers_receiver_id",
        table_name="transfers",
    )

    op.drop_index(
        "ix_transfers_sender_id",
        table_name="transfers",
    )

    op.drop_index(
        "ix_transfers_transfer_id",
        table_name="transfers",
    )

    op.drop_table("transfers")