"""merge_spell_id_migrations

Revision ID: 4f8e8f83d0c8
Revises: 8d4e2f1a9c3b, c47d93f5e28a
Create Date: 2025-02-15 09:54:10.863336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f8e8f83d0c8'
down_revision: Union[str, None] = ('8d4e2f1a9c3b', 'c47d93f5e28a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('spell_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    pass
