import { PriceRankingCard } from "@/components/realm/price-ranking-card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  compareRealmsAtom,
  isLoadingAtom,
  selectedItemIdsAtom,
  selectedRealmsAtom
} from "@/lib/store";
import { useAtom } from "jotai";
import { useEffect } from "react";




export function PriceComparison() {  const [selectedRealms] = useAtom(selectedRealmsAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, compareRealms] = useAtom(compareRealmsAtom);
  const [selectedItems] = useAtom(selectedItemIdsAtom);
  const selectedItemIds = Array.from(selectedItems);
  
  useEffect(() => {
    if (selectedRealms.length > 0 && selectedItems.size > 0) {
      compareRealms();
    }
  }, [compareRealms, selectedRealms, selectedItems]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  if (selectedRealms.length === 0 || selectedItems.size === 0) {
    return (
      <div className="text-center p-4 text-muted-foreground">
        {selectedRealms.length === 0
          ? "Select realms to compare their prices"
          : "Select items to compare prices"
        }
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <h2 className="text-xl font-semibold">Price Rankings</h2>      

{/* New Section: Price Ranking Cards per selected item */}
{selectedItemIds.length > 0 && (
  <div className="mt-8">
    <h2 className="text-xl font-bold mb-4">Item Price Rankings</h2>
    <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {selectedItemIds.map((itemId) => (
        <PriceRankingCard key={itemId} itemId={itemId} />
      ))}
    </div>
  </div>
)}
</div>
);
}
