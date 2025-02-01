"use client";

import { useAtom } from "jotai";
import { selectedItemIdsAtom } from "@/lib/store";
import { X } from "lucide-react";
import { ItemBase } from "@/lib/api";

interface SelectedItemsBadgesProps {
  items: ItemBase[];
}

export function SelectedItemsBadges({ items }: SelectedItemsBadgesProps) {
  const [selectedItemIds, setSelectedItemIds] = useAtom(selectedItemIdsAtom);
  
  if (selectedItemIds.size === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No items selected
      </div>
    );
  }
  
  const selectedItems = items.filter(item => selectedItemIds.has(item.item_id));
  
  return (
    <div className="flex flex-wrap gap-2">
      {selectedItems.map((item) => (
        <div 
          key={item.item_id}
          className="flex items-center gap-1 px-2 py-1 text-sm rounded-md bg-secondary"
        >
          <span>{item.item_name}</span>
          <button
            onClick={() => {
              const newSelected = new Set(selectedItemIds);
              newSelected.delete(item.item_id);
              setSelectedItemIds(newSelected);
            }}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ))}
    </div>
  );
}