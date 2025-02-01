from fastapi import APIRouter, Depends, HTTPException
from typing import List

from .crud_groups import GroupCRUD
from .schemas import (
    ItemGroupResponse,
    ItemGroupUpdate,
    PaginationParams,
    ItemGroupItemOperation
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[ItemGroupResponse])
def list_groups(
    pagination: PaginationParams = Depends(),
    crud: GroupCRUD = Depends(GroupCRUD)
):
    return crud.list_groups(
        skip=pagination.skip,
        limit=pagination.limit
    )

@router.get("/{group_id}", response_model=ItemGroupResponse)
def get_group(
    group_id: int,
    crud: GroupCRUD = Depends(GroupCRUD)
):
    group = crud.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{group_id}", response_model=ItemGroupResponse)
def update_group(
    group_id: int,
    group_data: ItemGroupUpdate,
    crud: GroupCRUD = Depends(GroupCRUD)
):
    updated = crud.update_group(group_id, group_data.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated

@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    crud: GroupCRUD = Depends(GroupCRUD)
):
    deleted = crud.delete_group(group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"deleted": deleted}

@router.get("/{group_id}/items")
def list_group_items(
    group_id: int,
    crud: GroupCRUD = Depends(GroupCRUD)
):
    items = crud.list_group_items(group_id)
    return {"items": items}

@router.delete("/{group_id}/items")
def remove_group_items(
    group_id: int,
    items: ItemGroupItemOperation,
    crud: GroupCRUD = Depends(GroupCRUD)
):
    removed = crud.remove_items_from_group(group_id, items.item_ids)
    return {"removed": removed}
