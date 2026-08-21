"""Add currencies.

Revision ID: 0013_currencies
Revises: 0012_country_region
"""

from alembic import op
import sqlalchemy as sa


revision = "0013_currencies"
down_revision = "0012_country_region"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "currencies",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "code",
            sa.String(10),
            nullable=False,
            unique=True,
        ),

        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),

        sa.Column(
            "symbol",
            sa.String(10),
            nullable=False,
        ),

        sa.Column(
            "decimals",
            sa.Integer(),
            nullable=False,
            server_default="2",
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
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
        "ix_currencies_code",
        "currencies",
        ["code"],
        unique=True,
    )

    op.create_index(
        "ix_currencies_is_active",
        "currencies",
        ["is_active"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_currencies_is_active",
        table_name="currencies",
    )

    op.drop_index(
        "ix_currencies_code",
        table_name="currencies",
    )

    op.drop_table("currencies")