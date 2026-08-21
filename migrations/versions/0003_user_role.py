"""Add user role.

Revision ID: 0003_user_role
Revises: 0002_user_sessions
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_user_role"
down_revision = "0002_user_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(30),
            nullable=False,
            server_default="user",
        ),
    )

    op.create_index(
        "ix_users_role",
        "users",
        ["role"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_role",
        table_name="users",
    )

    op.drop_column(
        "users",
        "role",
    )