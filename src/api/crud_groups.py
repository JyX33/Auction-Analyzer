from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from .models import ItemGroup, ItemGroupAssociation
from .schemas import ItemGroupCreate, ItemGroupUpdate

class GroupCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_group(self, group: ItemGroupCreate) -> ItemGroup:
        db_group = ItemGroup(**group.dict())
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def get_group(self, group_id: int) -> Optional[ItemGroup]:
        return self.db.get(ItemGroup, group_id)

    def list_groups(self, skip: int = 0, limit: int = 100) -> List[ItemGroup]:
        return self.db.execute(
            select(ItemGroup)
            .offset(skip)
            .limit(limit)
        ).scalars().all()

    def update_group(self, group_id: int, group_data: ItemGroupUpdate) -> Optional[ItemGroup]:
        group = self.get_group(group_id)
        if group:
            for key, value in group_data.dict(exclude_unset=True).items():
                setattr(group, key, value)
            self.db.commit()
            self.db.refresh(group)
        return group

    def delete_group(self, group_id: int) -> bool:
        group = self.get_group(group_id)
        if group:
            self.db.delete(group)
            self.db.commit()
            return True
        return False

    def add_items_to_group(self, group_id: int, item_ids: List[int]) -> int:
        existing = set(
            self.db.execute(
                select(ItemGroupAssociation.item_id)
                .where(ItemGroupAssociation.group_id == group_id)
            ).scalars().all()
        )
        
        new_items = [
            ItemGroupAssociation(group_id=group_id, item_id=item_id)
            for item_id in item_ids
            if item_id not in existing
        ]
        
        self.db.add_all(new_items)
        self.db.commit()
        return len(new_items)

    def remove_items_from_group(self, group_id: int, item_ids: List[int]) -> int:
        result = self.db.execute(
            delete(ItemGroupAssociation)
            .where(ItemGroupAssociation.group_id == group_id)
            .where(ItemGroupAssociation.item_id.in_(item_ids))
        )
        self.db.commit()
        return result.rowcount

    def list_group_items(self, group_id: int) -> List[int]:
        return self.db.execute(
            select(ItemGroupAssociation.item_id)
            .where(ItemGroupAssociation.group_id == group_id)
        ).scalars().all()
