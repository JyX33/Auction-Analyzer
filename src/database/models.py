"""
SQLAlchemy models for database entities.
"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()

class Item(Base):
    """Model representing a game item."""
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True)
    item_class_id = Column(Integer)
    item_class_name = Column(Text)
    item_subclass_id = Column(Integer)
    item_subclass_name = Column(Text)
    display_subclass_name = Column(Text)
    item_name = Column(Text)
    
    groups = relationship('Group', secondary='item_groups', back_populates='items')

class Group(Base):
    """Model representing a user-defined item group."""
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(Text, unique=True, nullable=False)
    
    items = relationship('Item', secondary='item_groups', back_populates='groups')

class ItemGroup(Base):
    """Junction model for many-to-many relationship between items and groups."""
    __tablename__ = 'item_groups'

    item_id = Column(Integer, ForeignKey('items.item_id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), primary_key=True)

class ConnectedRealm(Base):
    """Model representing a connected realm in World of Warcraft."""
    __tablename__ = 'connected_realms'

    id = Column(Integer, primary_key=True)
    connected_realm_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    population_type = Column(String)
    realm_category = Column(String)
    status = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
