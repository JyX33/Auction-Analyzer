"""
Database schema definitions for SQLite database.
"""

from sqlalchemy import MetaData, Table, Column, Integer, Text, ForeignKey, create_engine
from sqlalchemy.engine import Engine

metadata = MetaData()

items = Table(
    'items', metadata,
    Column('item_id', Integer, primary_key=True),
    Column('item_class_id', Integer),
    Column('item_class_name', Text),
    Column('item_subclass_id', Integer),
    Column('item_subclass_name', Text),
    Column('display_subclass_name', Text),
    Column('item_name', Text)
)

groups = Table(
    'groups', metadata,
    Column('group_id', Integer, primary_key=True, autoincrement=True),
    Column('group_name', Text, unique=True, nullable=False)
)

item_groups = Table(
    'item_groups', metadata,
    Column('item_id', Integer, ForeignKey('items.item_id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.group_id'), primary_key=True)
)

def init_db(engine: Engine) -> None:
    """Initialize database schema."""
    metadata.create_all(engine)
