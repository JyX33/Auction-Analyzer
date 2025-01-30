"""add_extension_to_items

Revision ID: 99d0a9539c1e
Revises: 5053fc297bd4
Create Date: 2025-01-30 14:54:44.525790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99d0a9539c1e'
down_revision: Union[str, None] = '5053fc297bd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('extension', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('items', 'extension')
