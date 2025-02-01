"use client";

import { useAtom } from "jotai";
import { useEffect } from "react";
import {
  selectedRealmIdsAtom,
  realmsAtom,
  selectedRealmCategoryAtom,
  fetchRealmsAtom,
  isLoadingAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Check } from "lucide-react";

export function RealmSelect() {
  const [selectedRealmIds, setSelectedRealmIds] = useAtom(selectedRealmIdsAtom);
  const [realms] = useAtom(realmsAtom);
  const [selectedRealmCategory] = useAtom(selectedRealmCategoryAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, fetchRealms] = useAtom(fetchRealmsAtom);

  useEffect(() => {
    fetchRealms();
  }, [fetchRealms, selectedRealmCategory]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="grid gap-4 p-4">
      <div className="text-sm font-medium">Select Realms to Compare</div>
      <div className="grid gap-2">
        {realms.map((realm) => (
          <button
            key={realm.id}
            onClick={() => {
              if (selectedRealmIds.includes(realm.id)) {
                setSelectedRealmIds(selectedRealmIds.filter((id) => id !== realm.id));
              } else {
                setSelectedRealmIds([...selectedRealmIds, realm.id]);
              }
            }}
            className={`flex items-center justify-between p-2 text-left border rounded-lg transition-colors
              ${
                selectedRealmIds.includes(realm.id)
                  ? "border-primary bg-primary/10"
                  : "border-border hover:bg-accent"
              }`}
          >
            <span className="flex flex-col">
              <span className="font-medium">{realm.name}</span>
              <span className="text-xs text-muted-foreground">
                {realm.item_count.toLocaleString()} items
              </span>
            </span>
            {selectedRealmIds.includes(realm.id) && (
              <Check className="h-4 w-4 text-primary" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
