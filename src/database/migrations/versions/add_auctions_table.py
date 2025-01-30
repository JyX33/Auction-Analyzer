"""add auctions table

Revision ID: 5053fc297bd4
Revises: 263619184992
Create Date: 2024-01-29 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5053fc297bd4'
down_revision = '263619184992'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'auctions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('auction_id', sa.Integer(), nullable=False),
        sa.Column('connected_realm_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('buyout_price', sa.Integer()),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('time_left', sa.String()),
        sa.Column('last_modified', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['connected_realm_id'], ['connected_realms.id']),
        sa.ForeignKeyConstraint(['item_id'], ['items.item_id'])
    )
    
    op.create_index(
        'idx_auction_id_realm_id',
        'auctions',
        ['auction_id', 'connected_realm_id'],
        unique=True
    )

def downgrade() -> None:
    op.drop_index('idx_auction_id_realm_id')
    op.drop_table('auctions')
