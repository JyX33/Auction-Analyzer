"""Add raw_craft_cost column to items table

Revision ID: 7f8e9d2a1b3c
Revises: 0d7be1e52518
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '7f8e9d2a1b3c'
down_revision = '0d7be1e52518'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('items', sa.Column('raw_craft_cost', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('items', 'raw_craft_cost')