"""
FastAPI main application module implementing the REST API endpoints.
"""

import math
import re
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.database.models import Auction, ConnectedRealm, Group, Item
from src.database.operations import get_db

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
# Error response models
class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    errors: List[ErrorDetail]


# Request validation model
class PriceRequestParams(BaseModel):
    items: str
    time_range: str = "7d"

    @field_validator("items")
    def validate_items(cls, v):
        try:
            item_ids = [int(id.strip()) for id in v.split(",")]
            if not item_ids:
                raise ValueError("At least one item ID is required")
            return v
        except ValueError:
            raise ValueError(
                "Invalid item ID format. Use comma-separated integers (e.g., '123' or '123,456')"
            )

    @field_validator("time_range")
    def validate_time_range(cls, v):
        if not re.match(r"^\d+d$", v):
            raise ValueError(
                "Time range must be in format 'Nd' where N is number of days (e.g., '7d')"
            )
        days = int(v[:-1])
        if days < 1:
            raise ValueError("Time range must be at least 1 day")
        return v


class ItemBase(BaseModel):
    item_id: int
    item_name: str    
    raw_craft_cost: Optional[float] = None
    item_class_name: str
    item_subclass_name: str
    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class GroupDetail(GroupBase):
    items: List[ItemBase]


class RealmData(BaseModel):
    id: int
    name: str
    language: str
    population_type: str
    population: Optional[int] = None
    item_count: int
    last_updated: str


class PriceMetrics(BaseModel):
    average_price: float
    price_trend: float
    item_details: List[dict] = []


class ItemPriceDetails(BaseModel):
    item_id: int
    item_name: str
    lowest_price: float
    highest_price: float
    quantity: int
    average_lowest_five: float
    rating: float = 0.0


class RealmComparison(BaseModel):
    realm_id: int
    total_value: float
    value_per_item: float
    rating: float
    items: List[ItemPriceDetails]


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
    db: Session = Depends(get_db),
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
        items=items,
    )


@app.get("/api/v1/item-classes", response_model=List[ItemClass])
async def list_item_classes(db: Session = Depends(get_db)):
    """List all unique item classes."""
    classes = db.query(Item.item_class_id, Item.item_class_name).distinct().all()

    return [
        ItemClass(item_class_id=c.item_class_id, item_class_name=c.item_class_name)
        for c in classes
    ]


@app.get(
    "/api/v1/item-classes/{class_id}/subclasses", response_model=List[ItemSubclass]
)
async def list_subclasses_for_class(class_id: int, db: Session = Depends(get_db)):
    """List all subclasses for a specific item class."""
    # First check if the class exists
    class_exists = db.query(Item).filter(Item.item_class_id == class_id).first()
    if not class_exists:
        raise HTTPException(status_code=404, detail="Item class not found")

    subclasses = (
        db.query(Item.item_subclass_id, Item.item_subclass_name)
        .filter(Item.item_class_id == class_id)
        .distinct()
        .all()
    )

    return [
        ItemSubclass(
            item_subclass_id=s.item_subclass_id, item_subclass_name=s.item_subclass_name
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
async def get_realms(
    realm_category: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    Get list of realms, optionally filtered by realm category.

    Parameters:
    - realm_category: Optional filter for realm category (e.g., 'French', 'German', etc.)
    """
    # Start with base query
    query = db.query(
        ConnectedRealm.id,
        ConnectedRealm.name,
        ConnectedRealm.realm_category.label("language"),
        ConnectedRealm.population_type,
        ConnectedRealm.population,
        func.count(Auction.id).label("item_count"),
        func.max(ConnectedRealm.last_updated).label("last_updated"),
    ).outerjoin(Auction)

    # Apply realm category filter if provided
    if realm_category:
        query = query.filter(ConnectedRealm.realm_category == realm_category)

    # Group by realm and execute query
    realms_data = query.group_by(
        ConnectedRealm.id,
        ConnectedRealm.name,
        ConnectedRealm.realm_category,
        ConnectedRealm.population_type,
        ConnectedRealm.population,
    ).all()

    # Convert to RealmData objects
    result = [
        RealmData(
            id=r.id,
            name=r.name,
            language=r.language,
            population_type=r.population_type or "Medium",
            population=r.population,
            item_count=r.item_count,
            last_updated=r.last_updated.isoformat() if r.last_updated else None,
        )
        for r in realms_data
    ]
    return result


# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [
                {"field": error["loc"][-1], "message": error["msg"]}
                for error in exc.errors()
            ],
        },
    )


@app.get("/api/v1/prices/{realm_id}", response_model=PriceMetrics)
async def get_realm_prices(
    realm_id: int, params: PriceRequestParams = Depends(), db: Session = Depends(get_db)
):
    """
    Get price metrics for items in a specific realm.

    Parameters:
    - realm_id: ID of the realm to query
    - items: Comma-separated list of item IDs (e.g., "123" or "123,456,789")
    - time_range: Time range for price data in format "Nd" where N is number of days (e.g., "7d")

    Returns:
    - PriceMetrics object containing average price, price trend, and item details
    """
    """Get price metrics for items in a specific realm."""
    from datetime import datetime, timedelta

    # Check if realm exists in connected_realms table
    realm_query = db.query(ConnectedRealm).filter(
        (ConnectedRealm.id == realm_id)
        | (ConnectedRealm.connected_realm_id == realm_id)
    )
    realm = realm_query.first()

    if not realm:
        # Show available realms for better error context
        all_realms = db.query(
            ConnectedRealm.id, ConnectedRealm.connected_realm_id, ConnectedRealm.name
        ).all()
        available_realms = [
            f"ID: {r.id} (Connected Realm ID: {r.connected_realm_id}) - {r.name}"
            for r in all_realms
        ]
        raise HTTPException(
            status_code=404,
            detail=(
                f"Realm with ID {realm_id} not found. "
                f"Available realms:\n{chr(10).join(available_realms)}"
            ),
        )

    # Parse item IDs (validation already done by Pydantic model)
    item_id_list = [int(id.strip()) for id in params.items.split(",")]

    # Validate items exist
    items_query = db.query(Item.item_id, Item.item_name).filter(
        Item.item_id.in_(item_id_list)
    )

    existing_items = items_query.all()
    existing_item_ids = {item.item_id for item in existing_items}

    # Find which items don't exist
    missing_items = set(item_id_list) - existing_item_ids
    if missing_items:
        # Get names of existing items for better error context
        existing_item_names = {
            f"{item.item_id} ({item.item_name})" for item in existing_items
        }
        raise HTTPException(
            status_code=404,
            detail=(
                f"Items not found: {', '.join(str(id) for id in missing_items)}. "
                f"Found items: {', '.join(existing_item_names)}"
            ),
        )

    # Parse time range (validation already done by Pydantic model)
    days = int(params.time_range[:-1])
    start_date = datetime.utcnow() - timedelta(days=days)

    # Query base for auctions within time range and realm
    base_query = db.query(Auction).filter(
        and_(
            Auction.connected_realm_id
            == realm.connected_realm_id,  # Use connected_realm_id instead of id
            Auction.item_id.in_(existing_item_ids),
            Auction.last_modified >= start_date,
            Auction.buyout_price > 0,  # Exclude invalid prices
            Auction.active,  # Only get active auctions
        )
    )

    # Calculate current prices (average of most recent day)
    recent_date = datetime.utcnow() - timedelta(days=1)
    current_prices = {}
    historical_stats = {}

    for item_id in existing_item_ids:
        # Get recent auctions for price per unit calculation
        recent_auctions = base_query.filter(
            and_(Auction.item_id == item_id, Auction.last_modified >= recent_date)
        ).all()

        if recent_auctions:
            # Calculate price per unit for each auction
            prices_per_unit = [
                auction.buyout_price / auction.quantity for auction in recent_auctions
            ]
            current_price = sum(prices_per_unit) / len(prices_per_unit)
            current_prices[item_id] = current_price

            # Calculate historical stats
            historical_auctions = base_query.filter(Auction.item_id == item_id).all()
            historical_prices = [
                auction.buyout_price / auction.quantity
                for auction in historical_auctions
            ]

            if historical_prices:
                historical_stats[item_id] = {
                    "low": min(historical_prices),
                    "high": max(historical_prices),
                }

    if not current_prices:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No recent auction data found for items {', '.join(str(id) for id in item_id_list)} "
                f"in realm {realm.name} (ID: {realm_id}, Connected Realm ID: {realm.connected_realm_id})"
            ),
        )

    # Calculate average price across all items
    average_price = sum(current_prices.values()) / len(current_prices)

    # Calculate price trend (comparing current to historical average)
    # Calculate historical average price per item
    historical_avg = 0
    if current_prices:
        item_averages = []
        for item_id in current_prices.keys():
            item_auctions = base_query.filter(Auction.item_id == item_id).all()
            if item_auctions:
                total_price = sum(
                    auction.buyout_price / auction.quantity for auction in item_auctions
                )
                avg_price = total_price / len(item_auctions)
                item_averages.append(avg_price)

        if item_averages:
            historical_avg = sum(item_averages) / len(item_averages)

    price_trend = (average_price / historical_avg) - 1 if historical_avg > 0 else 0

    # Prepare item details
    item_details = [
        {
            "item_id": item_id,
            "current_price": current_prices.get(item_id, 0),
            "historical_low": historical_stats.get(item_id, {}).get("low", 0),
            "historical_high": historical_stats.get(item_id, {}).get("high", 0),
        }
        for item_id in existing_item_ids
    ]
    return PriceMetrics(
        average_price=average_price, price_trend=price_trend, item_details=item_details
    )


class ComparisonRequest(BaseModel):
    realms: List[int]
    items: List[int]


@app.post("/api/v1/comparison", response_model=List[RealmComparison])
async def compare_realms(request: ComparisonRequest, db: Session = Depends(get_db)):
    """Compare realms based on item prices and calculate realm ratings."""
    recent_date = datetime.utcnow() - timedelta(days=1)
    EPSILON = 1  # Small constant to avoid division by zero

    # Validate realms exist
    realms = (
        db.query(ConnectedRealm).filter(ConnectedRealm.id.in_(request.realms)).all()
    )
    if not realms:
        raise HTTPException(status_code=404, detail="No valid realms found")

    # Get all items at once and create a map for quick lookup
    items = db.query(Item).filter(Item.item_id.in_(request.items)).all()
    item_map = {item.item_id: item for item in items}
    if not items:
        raise HTTPException(status_code=404, detail="No valid items found")

    comparisons = []
    for realm in realms:
        # Base query for this realm's auctions
        base_query = db.query(Auction).filter(
            and_(
                Auction.connected_realm_id == realm.connected_realm_id,
                Auction.item_id.in_(request.items),
                Auction.last_modified >= recent_date,
                Auction.buyout_price > 0,
                # Auction.active  # Only get active auctions
            )
        )

        total_value = 0
        total_quantity = 0
        item_details = []
        realm_rating = 0

        for item_id in request.items:
            item = item_map[item_id]
            item_auctions = base_query.filter(Auction.item_id == item_id).all()

            if item_auctions:
                # Calculate weighted prices based on quantity
                # Calculate prices per unit for all auctions
                prices_per_unit = []
                quantities = []
                for auction in item_auctions:
                    price_per_unit = auction.buyout_price / auction.quantity
                    prices_per_unit.append(price_per_unit)
                    quantities.append(auction.quantity)

                # Sort prices for median calculation
                sorted_prices = sorted(prices_per_unit)
                n = len(sorted_prices)

                # Calculate median price (robust central tendency)
                if n % 2 == 0:
                    median_price = (
                        sorted_prices[n // 2 - 1] + sorted_prices[n // 2]
                    ) / 2
                else:
                    median_price = sorted_prices[n // 2]

                # Calculate trimmed mean (excluding top and bottom 10%)
                trim_size = int(n * 0.1)  # 10% trim
                if n > 10:  # Only apply trimming if we have enough data points
                    trimmed_prices = sorted_prices[trim_size:-trim_size]
                    trimmed_mean = sum(trimmed_prices) / len(trimmed_prices)
                else:
                    trimmed_mean = median_price  # Fall back to median for small samples

                # Use the more conservative of median and trimmed mean
                robust_price = min(median_price, trimmed_mean)

                # Calculate effective supply (auctions within ±20% of robust price)
                price_threshold = robust_price * 0.2  # 20% threshold
                effective_quantity = sum(
                    quantity
                    for price, quantity in zip(prices_per_unit, quantities)
                    if abs(price - robust_price) <= price_threshold
                )

                # Fall back to total quantity if effective quantity is too small
                total_quantity = sum(quantities)
                if (
                    effective_quantity < total_quantity * 0.2
                ):  # If less than 20% of total
                    effective_quantity = total_quantity

                # Calculate market quality factor using population and logs data
                # Use geometric mean approach for balanced consideration of both factors
                # Add 1 to logs to avoid zero in case logs data is missing
                market_quality = (realm.population or 0) * (
                    realm.logs + 1 if realm.logs else 1
                )

                # Calculate item rating using robust price, effective supply, and market quality
                item_rating = (
                    (robust_price / (effective_quantity + EPSILON))
                    * math.sqrt(market_quality)
                    / 10000000
                )

                # Calculate stats for item details
                lowest_price = min(prices_per_unit) if prices_per_unit else 0
                highest_price = max(prices_per_unit) if prices_per_unit else 0
                # Calculate average of lowest 5 prices (or all if less than 5)
                sorted_prices = sorted(prices_per_unit)
                lowest_five_avg = (
                    sum(sorted_prices[:5]) / min(5, len(sorted_prices))
                    if sorted_prices
                    else 0
                )

                item_details.append(
                    ItemPriceDetails(
                        item_id=item_id,
                        item_name=item.item_name,
                        lowest_price=lowest_price,
                        highest_price=highest_price,
                        quantity=total_quantity,
                        average_lowest_five=lowest_five_avg,
                        rating=item_rating,
                    )
                )

                total_value += sum(
                    p * q for p, q in zip(prices_per_unit, [1] * len(prices_per_unit))
                )
                total_quantity += effective_quantity
                realm_rating += item_rating

        value_per_item = total_value / total_quantity if total_quantity > 0 else 0
        avg_realm_rating = realm_rating / len(request.items) if request.items else 0

        comparisons.append(
            RealmComparison(
                realm_id=realm.id,
                total_value=total_value,
                value_per_item=value_per_item,
                rating=avg_realm_rating,
                items=item_details,
            )
        )

    # Sort by rating in descending order
    comparisons.sort(key=lambda x: x.rating, reverse=True)
    return comparisons
