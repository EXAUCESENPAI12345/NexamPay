"""add user network and settings

Revision ID: 0016_user_network_and_settings
Revises: 0015_order_idempotency
"""
from alembic import op
import sqlalchemy as sa

revision = "0016_user_network_and_settings"
down_revision = "0015_order_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("network_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_network_id", "users", ["network_id"], unique=False)
    op.create_foreign_key(
        "fk_users_network_id_mobile_money_networks",
        "users",
        "mobile_money_networks",
        ["network_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False, server_default="fr"),
        sa.Column("currency_code", sa.String(length=10), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=False, server_default="nexam"),
        sa.Column("theme", sa.String(length=20), nullable=False, server_default="dark"),
        sa.Column("bot_notifications_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_settings_user_id", "user_settings", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_settings_user_id", table_name="user_settings")
    op.drop_table("user_settings")
    op.drop_constraint("fk_users_network_id_mobile_money_networks", "users", type_="foreignkey")
    op.drop_index("ix_users_network_id", table_name="users")
    op.drop_column("users", "network_id")
