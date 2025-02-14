"""Add recipe_id column to items table

Revision ID: 8d4e2f1a9c3b
Revises: 7f8e9d2a1b3c
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '8d4e2f1a9c3b'
down_revision = '7f8e9d2a1b3c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('items', sa.Column('recipe_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('items', 'recipe_id')