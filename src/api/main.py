"""
FastAPI main application module implementing the REST API endpoints.
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from src.database.models import Item, Group
from src.database.operations import get_db
from pydantic import BaseModel

app = FastAPI(title="Game Item API")

# Pydantic models for API responses
class ItemBase(BaseModel):
    item_id: int
    item_name: str
    item_class_name: str
    item_subclass_name: str
    model_config = {
        'from_attributes': True
    }

class ItemDetail(ItemBase):
    item_class_id: int
    item_subclass_id: int
    display_subclass_name: Optional[str] = None
    groups: List[str] = []

class ItemListResponse(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: List[ItemBase]

class ItemClass(BaseModel):
    item_class_id: int
    item_class_name: str

class ItemSubclass(BaseModel):
    item_subclass_id: int
    item_subclass_name: str

class GroupBase(BaseModel):
    group_id: int
    group_name: str

    model_config = {
        'from_attributes': True
    }

class GroupDetail(GroupBase):
    items: List[ItemBase]

@app.get("/api/v1/items/{item_id}", response_model=ItemDetail)
async def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific item."""
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Convert item groups to list of group names
    group_names = [group.group_name for group in item.groups]
    
    # Create response with groups
    response = ItemDetail.model_validate(item)
    response.groups = group_names
    return response

@app.get("/api/v1/items", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    item_class_name: Optional[str] = None,
    item_subclass_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List items with optional filtering and pagination."""
    query = db.query(Item)
    
    # Apply filters if provided
    if item_class_name:
        query = query.filter(Item.item_class_name == item_class_name)
    if item_subclass_name:
        query = query.filter(Item.item_subclass_name == item_subclass_name)
    
    # Get total count for pagination
    total_items = query.count()
    total_pages = (total_items + page_size - 1) // page_size
    
    # Apply pagination
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ItemListResponse(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        items=items
    )

@app.get("/api/v1/item-classes", response_model=List[ItemClass])
async def list_item_classes(db: Session = Depends(get_db)):
    """List all unique item classes."""
    classes = db.query(
        Item.item_class_id,
        Item.item_class_name
    ).distinct().all()
    
    return [
        ItemClass(item_class_id=c.item_class_id, item_class_name=c.item_class_name)
        for c in classes
    ]

@app.get("/api/v1/item-classes/{class_id}/subclasses", response_model=List[ItemSubclass])
async def list_subclasses_for_class(class_id: int, db: Session = Depends(get_db)):
    """List all subclasses for a specific item class."""
    # First check if the class exists
    class_exists = db.query(Item).filter(Item.item_class_id == class_id).first()
    if not class_exists:
        raise HTTPException(status_code=404, detail="Item class not found")
    
    subclasses = db.query(
        Item.item_subclass_id,
        Item.item_subclass_name
    ).filter(
        Item.item_class_id == class_id
    ).distinct().all()
    
    return [
        ItemSubclass(
            item_subclass_id=s.item_subclass_id,
            item_subclass_name=s.item_subclass_name
        )
        for s in subclasses
    ]

@app.get("/api/v1/groups", response_model=List[GroupBase])
async def list_groups(db: Session = Depends(get_db)):
    """List all user-defined item groups."""
    groups = db.query(Group).all()
    return groups

@app.get("/api/v1/groups/{group_id}", response_model=GroupDetail)
async def get_group_by_id(group_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific group."""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@app.get("/api/v1/groups/{group_id}/items", response_model=List[ItemBase])
async def list_items_in_group(group_id: int, db: Session = Depends(get_db)):
    """List all items in a specific group."""
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return group.items