"""merge logs and population migrations

Revision ID: 94943c2ff48d
Revises: 37eec7227935, 615c8a4784e8
Create Date: 2025-02-04 19:52:24.700043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94943c2ff48d'
down_revision: Union[str, None] = ('37eec7227935', '615c8a4784e8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
