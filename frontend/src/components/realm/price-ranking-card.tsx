import { useAtom } from "jotai";
import { ArrowUp, ArrowDown } from "lucide-react";
import { realmComparisonAtom, itemsAtom } from "@/lib/store";

interface PriceRankingCardProps {
  itemId: number;
}

export function PriceRankingCard({ itemId }: PriceRankingCardProps) {
  const [realmComparison] = useAtom(realmComparisonAtom);
  const [items] = useAtom(itemsAtom);
  const item = items.find((it) => it.item_id === itemId);

  // Build an array of { realm, itemDetail } for realms that contain data for this item.
  const realmsForItem = realmComparison
    .map((realm) => {
      const itemDetail = realm.items.find((i) => i.item_id === itemId);
      return itemDetail ? { realm, itemDetail } : null;
    })
    .filter(Boolean) as { realm: typeof realmComparison[0]; itemDetail: { average_lowest_five: number } }[];

  // Sort descending by average_lowest_five (highest first) and take the top 10
  const sortedRealms = realmsForItem
    .sort((a, b) => b.itemDetail.average_lowest_five - a.itemDetail.average_lowest_five)
    .slice(0, 10);

  return (
    <div className="border rounded-lg p-4 shadow-sm bg-white">
      <h3 className="text-lg font-bold mb-2">{item ? item.item_name : `Item ${itemId}`}</h3>
      {sortedRealms.length === 0 ? (
        <div className="text-sm text-muted-foreground">No price data available for this item</div>
      ) : (
        <div className="space-y-2">
          {sortedRealms.map((entry, index) => (
            <div key={entry.realm.id} className="flex justify-between items-center">
              <span className="font-medium">{entry.realm.name}</span>
              <span className="flex items-center gap-1 text-sm">
                {index === 0 && <ArrowUp className="text-green-500 w-4 h-4" />}
                {index === sortedRealms.length - 1 && <ArrowDown className="text-red-500 w-4 h-4" />}
                <span>{entry.itemDetail.average_lowest_five.toFixed(2)}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
