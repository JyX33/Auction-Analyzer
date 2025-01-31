"""
FastAPI main application module implementing the REST API endpoints.
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database.models import Item, Group
from src.database.operations import get_db
from pydantic import BaseModel

app = FastAPI(title="Game Item API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class RealmData(BaseModel):
    id: int
    name: str
    language: str
    item_count: int
    last_updated: str

class PriceMetrics(BaseModel):
    average_price: float
    price_trend: float
    item_details: List[dict] = []

class RealmComparison(BaseModel):
    realm_id: int
    total_value: float
    value_per_item: float

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

@app.get("/api/v1/realms", response_model=List[RealmData])
async def get_realms(language: Optional[str] = 'French', db: Session = Depends(get_db)):
    """Get list of realms, optionally filtered by language category."""
    from src.database.models import ConnectedRealm, Auction
    from sqlalchemy import func
    
    # Start with base query
    query = db.query(
        ConnectedRealm.id,
        ConnectedRealm.name,
        ConnectedRealm.realm_category.label('language'),
        func.count(Auction.id).label('item_count'),
        func.max(ConnectedRealm.last_updated).label('last_updated')
    ).outerjoin(Auction)
    
    # Apply language filter if provided
    if language:
        query = query.filter(ConnectedRealm.realm_category == language)
    
    # Group by realm and execute query
    realms_data = query.group_by(
        ConnectedRealm.id,
        ConnectedRealm.name,
        ConnectedRealm.realm_category
    ).all()
    
    # Convert to RealmData objects
    return [
        RealmData(
            id=r.id,
            name=r.name,
            language=r.language,
            item_count=r.item_count,
            last_updated=r.last_updated.isoformat() if r.last_updated else None
        )
        for r in realms_data
    ]

@app.get("/api/v1/prices/{realm_id}", response_model=PriceMetrics)
async def get_realm_prices(
    realm_id: int,
    item_ids: str = Query(..., description="Comma-separated list of item IDs"),
    time_range: str = Query("7d", description="Time range for price data"),
    db: Session = Depends(get_db)
):
    """Get price metrics for items in a specific realm."""
    # TODO: Implement actual price data fetching from database
    # This is a placeholder implementation
    return PriceMetrics(
        average_price=100.0,
        price_trend=1.5,
        item_details=[
            {
                "item_id": int(id),
                "current_price": 100.0,
                "historical_low": 90.0,
                "historical_high": 110.0
            }
            for id in item_ids.split(",")
        ]
    )

@app.post("/api/v1/comparison", response_model=List[RealmComparison])
async def compare_realms(
    request: dict,
    db: Session = Depends(get_db)
):
    """Compare realms based on item prices."""
    realm_ids = request.get("realms", [])
    item_ids = request.get("items", [])
    
    # TODO: Implement actual comparison logic using both realm_ids and item_ids
    # This is a placeholder implementation
    return [
        RealmComparison(
            realm_id=realm_id,
            total_value=1000.0 * len(item_ids),  # Scale by number of items
            value_per_item=1000.0
        )
        for realm_id in realm_ids
    ]
