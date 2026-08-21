"""Add countries and mobile money networks.

Revision ID: 0011_countries_and_mobile_money
Revises: 0010_notifications
"""

from alembic import op
import sqlalchemy as sa


revision = "0011_countries_and_mobile_money"
down_revision = "0010_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "code",
            sa.String(3),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "currency_code",
            sa.String(10),
            nullable=False,
        ),
        sa.Column(
            "flag_code",
            sa.String(10),
            nullable=False,
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
        "ix_countries_code",
        "countries",
        ["code"],
        unique=True,
    )

    op.create_index(
        "ix_countries_is_active",
        "countries",
        ["is_active"],
    )

    op.create_table(
        "mobile_money_networks",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "country_id",
            sa.Integer(),
            sa.ForeignKey(
                "countries.id",
                ondelete="RESTRICT",
            ),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "logo_url",
            sa.String(1000),
            nullable=True,
        ),
        sa.Column(
            "currency_code",
            sa.String(10),
            nullable=False,
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
        sa.UniqueConstraint(
            "country_id",
            "code",
            name="uq_mobile_money_country_code",
        ),
    )

    op.create_index(
        "ix_mobile_money_networks_country_id",
        "mobile_money_networks",
        ["country_id"],
    )

    op.create_index(
        "ix_mobile_money_networks_is_active",
        "mobile_money_networks",
        ["is_active"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mobile_money_networks_is_active",
        table_name="mobile_money_networks",
    )

    op.drop_index(
        "ix_mobile_money_networks_country_id",
        table_name="mobile_money_networks",
    )

    op.drop_table(
        "mobile_money_networks"
    )

    op.drop_index(
        "ix_countries_is_active",
        table_name="countries",
    )

    op.drop_index(
        "ix_countries_code",
        table_name="countries",
    )

    op.drop_table("countries")