"""Add account PIN hash.

Revision ID: 0003_pin
Revises: 0002_virtual_cards
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_pin"
down_revision = "0002_virtual_cards"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "pin_hash" not in columns:
        op.add_column(
            "users",
            sa.Column("pin_hash", sa.String(length=256), nullable=True),
        )

def downgrade() -> None:
    op.drop_column("users", "pin_hash")
