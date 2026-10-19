"""add role to users

Revision ID: 0d130134a79d
Revises: 19813c0afa10
Create Date: 2026-10-01 11:51:15.226057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d130134a79d'
down_revision: Union[str, Sequence[str], None] = '19813c0afa10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('role', sa.String(), nullable=True)
    )

    op.execute(
        "UPDATE users SET role = 'user' WHERE role IS NULL"
    )

    op.alter_column(
        'users',
        'role',
        nullable=False
    )


def downgrade() -> None:
    op.drop_column('users', 'role')
