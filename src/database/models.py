"""
SQLAlchemy models for database entities.
"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, ForeignKey, String, DateTime, Boolean, UniqueConstraint
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
    extension = Column(Text, nullable=True)
    
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
    population = Column(Integer)  # Stores the population value as integer
    logs = Column(Integer)  # Stores logs value as integer
    realm_category = Column(String)
    status = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    auctions = relationship('Auction', back_populates='connected_realm')

class Auction(Base):
    """Model representing an auction from the WoW API."""
    __tablename__ = 'auctions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auction_id = Column(Integer, nullable=False)
    connected_realm_id = Column(Integer, ForeignKey('connected_realms.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('auction_id', 'connected_realm_id', name='idx_auction_id_realm_id'),
    )
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    buyout_price = Column(Integer)
    quantity = Column(Integer, nullable=False)
    time_left = Column(String)
    last_modified = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True, nullable=False, index=True)

    connected_realm = relationship('ConnectedRealm', back_populates='auctions')
    item = relationship('Item', backref='auctions')
