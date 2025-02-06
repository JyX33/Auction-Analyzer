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
          className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-full bg-white border-2 border-blue-100 shadow-sm hover:shadow"
        >
          <span className="text-blue-800">{item.item_name}</span>
          <button
            onClick={() => {
              const newSelected = new Set(selectedItemIds);
              newSelected.delete(item.item_id);
              setSelectedItemIds(newSelected);
            }}
          >
            <X className="h-4 w-4 text-blue-400 hover:text-blue-600 transition-colors" />
          </button>
        </div>
      ))}
    </div>
  );
}
