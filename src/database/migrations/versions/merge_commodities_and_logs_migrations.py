"""merge commodities and logs migrations

Revision ID: c47d93f5e28a
Revises: 0d7be1e52518, f57e2cf8de73
Create Date: 2024-02-14 11:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c47d93f5e28a'
down_revision = ('0d7be1e52518', 'f57e2cf8de73')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass