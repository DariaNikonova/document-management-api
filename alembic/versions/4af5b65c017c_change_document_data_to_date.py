"""change document data to date

Revision ID: 4af5b65c017c
Revises: 0d130134a79d
Create Date: 2026-10-02 10:18:18.893679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af5b65c017c'
down_revision: Union[str, Sequence[str], None] = '0d130134a79d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "documents",
        "data",
        existing_type=sa.INTEGER(),
        type_=sa.Date(),
        postgresql_using="make_date(data, 1, 1)",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "documents",
        "data",
        existing_type=sa.Date(),
        type_=sa.INTEGER(),
        postgresql_using="EXTRACT(YEAR FROM data)::integer",
        existing_nullable=False,
    )
