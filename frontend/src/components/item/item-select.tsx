"use client";

import { useAtom } from "jotai";
import { useEffect, useState } from "react";
import {
  selectedItemIdsAtom,
  itemsAtom,
  fetchItemsAtom,
  isLoadingAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Check, ChevronDown } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ItemBase } from "@/lib/api";

interface ItemSelectProps {
  compact?: boolean;
}

export function ItemSelect({ compact }: ItemSelectProps) {
  const [selectedItemIds, setSelectedItemIds] = useAtom(selectedItemIdsAtom);
  const [items] = useAtom(itemsAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, fetchItems] = useAtom(fetchItemsAtom);
  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const filteredItems = items.filter((item: ItemBase) =>
    item.item_name.toLowerCase().includes(search.toLowerCase()) ||
    item.item_class_name.toLowerCase().includes(search.toLowerCase())
  );

  const itemsByClass = filteredItems.reduce((acc: Record<string, ItemBase[]>, item: ItemBase) => {
    if (!acc[item.item_class_name]) {
      acc[item.item_class_name] = [];
    }
    acc[item.item_class_name].push(item);
    return acc;
  }, {});

  const SelectionContent = () => (
    <div className="space-y-4">
      {Object.entries(itemsByClass).map(([className, items]) => (
        <div key={className}>
          <div className="text-sm font-medium mb-2">{className}</div>
          <div className="grid gap-2">
            {items.map((item) => (
              <button
                key={item.item_id}
                onClick={() => {
                  const newSelected = new Set(selectedItemIds);
                  if (newSelected.has(item.item_id)) {
                    newSelected.delete(item.item_id);
                  } else {
                    newSelected.add(item.item_id);
                  }
                  setSelectedItemIds(newSelected);
                }}
                className={`flex items-center justify-between p-3 text-left rounded-xl border-2 transition-all
                  ${selectedItemIds.has(item.item_id)
                    ? "border-blue-300 bg-blue-50/50 shadow-inner"
                    : "border-gray-200 hover:border-blue-200 hover:bg-white hover:shadow-sm"}`}
              >
                <span className="flex flex-col">
                  <span className="font-medium">{item.item_name}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.item_subclass_name}
                  </span>
                </span>
                {selectedItemIds.has(item.item_id) && (
                  <Check className="h-4 w-4 text-primary" />
                )}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  if (compact) {
    return (
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button 
            variant="outline"
            size="default"
            className="w-full justify-between hover:border-blue-300 hover:bg-white/50"
            role="combobox"
          >
            <span className="text-gray-700">Select Items</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-4" align="start">
          <div className="space-y-4">
            <Input
              type="search"
              placeholder="Search items..."
              className="w-full"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              autoComplete="off"
            />
            <SelectionContent />
          </div>
        </PopoverContent>
      </Popover>
    );
  }

  return (
    <div className="grid gap-4 p-4">
      <Input
        type="search"
        placeholder="Search items..."
        className="w-full"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <SelectionContent />
    </div>
  );
}
