"""add commodities table

Revision ID: f57e2cf8de73
Revises: f56e1cf7de72
Create Date: 2024-02-14 11:24:14.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f57e2cf8de73'
down_revision = 'f56e1cf7de72'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'commodities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Integer(), nullable=False),
        sa.Column('last_modified', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'unit_price', name='idx_item_unit_price')
    )

def downgrade():
    op.drop_table('commodities')