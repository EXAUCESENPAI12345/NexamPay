"""Add notifications.

Revision ID: 0010_notifications
Revises: 0009_transfer_idempotency
"""

from alembic import op
import sqlalchemy as sa


revision = "0010_notifications"
down_revision = "0009_transfer_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "type",
            sa.String(30),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "reference_id",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
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
        "ix_notifications_user_id",
        "notifications",
        ["user_id"],
    )

    op.create_index(
        "ix_notifications_type",
        "notifications",
        ["type"],
    )

    op.create_index(
        "ix_notifications_reference_id",
        "notifications",
        ["reference_id"],
    )

    op.create_index(
        "ix_notifications_is_read",
        "notifications",
        ["is_read"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notifications_is_read",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_reference_id",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_type",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_user_id",
        table_name="notifications",
    )

    op.drop_table("notifications")