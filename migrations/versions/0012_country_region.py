"""Add region to countries.

Revision ID: 0012_country_region
Revises: 0011_countries_and_mobile_money
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_country_region"
down_revision = "0011_countries_and_mobile_money"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "countries",
        sa.Column(
            "region",
            sa.String(30),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_countries_region",
        "countries",
        ["region"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_countries_region",
        table_name="countries",
    )

    op.drop_column(
        "countries",
        "region",
    )