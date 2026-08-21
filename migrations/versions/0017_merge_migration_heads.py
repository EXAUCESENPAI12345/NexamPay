"""Merge the historical PIN branch with the current schema branch.

Revision ID: 0017_merge_migration_heads
Revises: 0003_pin, 0016_user_network_and_settings
"""
from alembic import op

revision = "0017_merge_migration_heads"
down_revision = ("0003_pin", "0016_user_network_and_settings")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
