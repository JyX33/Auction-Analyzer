"use client";

import { useAtom } from "jotai";
import { selectedRealmsAtom, selectedRealmIdsAtom } from "@/lib/store";
import { X } from "lucide-react";

export function SelectedRealmsBadges() {
  const [selectedRealms] = useAtom(selectedRealmsAtom);
  const [selectedRealmIds, setSelectedRealmIds] = useAtom(selectedRealmIdsAtom);
  
  if (selectedRealms.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No realms selected
      </div>
    );
  }
  
  return (
    <div className="flex flex-wrap gap-2">
      {selectedRealms.map((realm) => (
        <div 
          key={realm.id}
          className="flex items-center gap-1 px-2 py-1 text-sm rounded-md bg-secondary"
        >
          <span>{realm.name}</span>
          <button
            onClick={() => setSelectedRealmIds(selectedRealmIds.filter(id => id !== realm.id))}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ))}
    </div>
  );
}