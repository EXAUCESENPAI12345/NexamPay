"""Add virtual card applications and virtual cards.

Revision ID: 0002_virtual_cards
Revises: 0001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_virtual_cards"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "virtual_card_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("cardholder_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=30), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("admin_note", sa.String(length=1000), nullable=True),
        sa.Column("rejection_reason", sa.String(length=1000), nullable=True),
        sa.Column("reviewed_by_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["country_id"], ["countries.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_virtual_card_applications_application_id",
        "virtual_card_applications",
        ["application_id"],
        unique=True,
    )
    op.create_index(
        "ix_virtual_card_applications_user_id",
        "virtual_card_applications",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_virtual_card_applications_status",
        "virtual_card_applications",
        ["status"],
        unique=False,
    )

    op.create_table(
        "virtual_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.String(length=50), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("currency_code", sa.String(length=10), nullable=False),
        sa.Column("brand", sa.String(length=30), nullable=True),
        sa.Column("masked_number", sa.String(length=32), nullable=True),
        sa.Column("last4", sa.String(length=4), nullable=True),
        sa.Column("expiry_month", sa.Integer(), nullable=True),
        sa.Column("expiry_year", sa.Integer(), nullable=True),
        sa.Column("provider_card_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["virtual_card_applications.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id"),
        sa.UniqueConstraint(
            "user_id",
            "status",
            name="uq_virtual_cards_user_status",
        ),
    )
    op.create_index(
        "ix_virtual_cards_card_id",
        "virtual_cards",
        ["card_id"],
        unique=True,
    )
    op.create_index(
        "ix_virtual_cards_user_id",
        "virtual_cards",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_virtual_cards_provider_card_id",
        "virtual_cards",
        ["provider_card_id"],
        unique=False,
    )
    op.create_index(
        "ix_virtual_cards_status",
        "virtual_cards",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_virtual_cards_status", table_name="virtual_cards")
    op.drop_index(
        "ix_virtual_cards_provider_card_id",
        table_name="virtual_cards",
    )
    op.drop_index("ix_virtual_cards_user_id", table_name="virtual_cards")
    op.drop_index("ix_virtual_cards_card_id", table_name="virtual_cards")
    op.drop_table("virtual_cards")

    op.drop_index(
        "ix_virtual_card_applications_status",
        table_name="virtual_card_applications",
    )
    op.drop_index(
        "ix_virtual_card_applications_user_id",
        table_name="virtual_card_applications",
    )
    op.drop_index(
        "ix_virtual_card_applications_application_id",
        table_name="virtual_card_applications",
    )
    op.drop_table("virtual_card_applications")
