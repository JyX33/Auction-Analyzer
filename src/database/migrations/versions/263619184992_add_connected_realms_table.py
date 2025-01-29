"""add connected_realms table

Revision ID: 263619184992
Revises: 
Create Date: 2025-01-29 16:43:52.035980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '263619184992'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'connected_realms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connected_realm_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('population_type', sa.String()),
        sa.Column('realm_category', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('last_updated', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('connected_realm_id')
    )

def downgrade() -> None:
    op.drop_table('connected_realms')
