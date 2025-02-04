"""convert_population_and_logs_to_integer

Revision ID: 0d7be1e52518
Revises: 94943c2ff48d
Create Date: 2025-02-04 21:15:24.527649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


def convert_population_to_int(value: str) -> int:
    """Convert population string value to integer."""
    if not value:
        return 0
    value = value.lower().strip()
    if value.endswith('k+'):
        return int(float(value[:-2]) * 1000)
    elif value.endswith('k'):
        return int(float(value[:-1]) * 1000)
    try:
        return int(value)
    except ValueError:
        return 0


def convert_logs_to_int(value: str) -> int:
    """Convert logs string value to integer."""
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


# revision identifiers, used by Alembic.
revision: str = '0d7be1e52518'
down_revision: Union[str, None] = '94943c2ff48d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert existing data before changing column types
    conn = op.get_bind()
    
    # Get all existing records
    results = conn.execute(
        text('SELECT id, population, logs FROM connected_realms')
    ).fetchall()
    
    # Update each record with converted integer values
    for id_, pop, logs in results:
        pop_int = convert_population_to_int(pop) if pop else 0
        logs_int = convert_logs_to_int(logs) if logs else 0
        conn.execute(
            text('UPDATE connected_realms SET population = :pop, logs = :logs WHERE id = :id'),
            {'pop': pop_int, 'logs': logs_int, 'id': id_}
        )

    # Change column types after data conversion
    with op.batch_alter_table('connected_realms', schema=None) as batch_op:
        batch_op.alter_column(
            'population',
            existing_type=sa.VARCHAR(),
            type_=sa.Integer(),
            existing_nullable=True
        )
        batch_op.alter_column(
            'logs',
            existing_type=sa.VARCHAR(),
            type_=sa.Integer(),
            existing_nullable=True
        )

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('connected_realms', schema=None) as batch_op:
        batch_op.alter_column(
            'logs',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(),
            existing_nullable=True
        )
        batch_op.alter_column(
            'population',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(),
            existing_nullable=True
        )

    # ### end Alembic commands ###
