"""Finalize user role migration.

Revision ID: 0004_user_role
Revises: 0003_user_role
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_user_role"
down_revision = "0003_user_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # La colonne role a déjà été créée
    # dans 0003_user_role.
    #
    # Cette migration est volontairement
    # sans modification supplémentaire.
    pass


def downgrade() -> None:
    # Aucun changement propre à annuler ici.
    pass