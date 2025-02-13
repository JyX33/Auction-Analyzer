import { useAtom } from "jotai";
import { useEffect } from "react";
import {  
  realmComparisonAtom,
  compareRealmsAtom,
  isLoadingAtom,
  selectedRealmsAtom,
  selectedItemIdsAtom,
  itemsAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { WowMoneyIcon } from "@/components/ui/wow-money-icon";
import { ArrowUp, ArrowDown, Users } from "lucide-react";
import type { RealmComparison } from "@/lib/api";
import { PriceRankingCard } from "@/components/realm/price-ranking-card";

function FormattedMoney({ copper }: { copper: number }) {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const remainingCopper = copper % 100;

  return (
    <div className="flex items-center gap-1">
      {gold > 0 && (
        <>
          <WowMoneyIcon type="gold" className="w-4 h-4" />
          <span>{gold}</span>
        </>
      )}
      {(gold > 0 || silver > 0) && (
        <>
          <WowMoneyIcon type="silver" className="w-4 h-4" />
          <span>{silver}</span>
        </>
      )}
      <WowMoneyIcon type="copper" className="w-4 h-4" />
      <span>{remainingCopper}</span>
    </div>
  );
}

function PopulationBadge({ type }: { type: string }) {
  const colors = {
    Full: "bg-red-100 text-red-800",
    High: "bg-orange-100 text-orange-800",
    Medium: "bg-yellow-100 text-yellow-800",
    Low: "bg-green-100 text-green-800",
    'New Players': "bg-blue-100 text-blue-800",
  }[type] || "bg-gray-100 text-gray-800";

  return (
    <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${colors}`}>
      <Users className="w-3 h-3" />
      <span>{type}</span>
    </div>
  );
}

export function PriceComparison() {
  const [realmComparison] = useAtom(realmComparisonAtom);
  const [selectedRealms] = useAtom(selectedRealmsAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, compareRealms] = useAtom(compareRealmsAtom);
  const [selectedItems] = useAtom(selectedItemIdsAtom);
  
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
      <div className="grid gap-4">
        {realmComparison.map((comparison: RealmComparison, index: number) => {
          const realm = selectedRealms.find((r) => r.id === comparison.realm_id);
          if (!realm) return null;

          const isHighest = index === 0;
          const isLowest = index === realmComparison.length - 1;

          return (
            <div
              key={realm.id}
              className={`p-4 border rounded-lg ${
                isHighest ? "border-green-500 bg-green-50/10" :
                isLowest ? "border-red-500 bg-red-50/10" :
                "border-border"
              }`}
            >
              <div className="flex items-center justify-between mb-4">
               <div className="flex items-center gap-2">
                 <span className="font-medium">{realm.name}</span>
                 <PopulationBadge type={realm.population_type} />
                 {realm.population && (
                   <span className="text-sm text-muted-foreground">
                     ({realm.population})
                   </span>
                 )}
               </div>
               <div className="flex items-center gap-2">
                 <div className="flex items-center gap-2">
                   {isHighest ? (
                     <ArrowUp className="text-green-500" />
                   ) : isLowest ? (
                     <ArrowDown className="text-red-500" />
                   ) : null}
                   <span className={`text-sm font-medium ${
                     isHighest ? "text-green-500" :
                     isLowest ? "text-red-500" :
                     "text-muted-foreground"
                   }`}>
                     Market Rank #{index + 1}
                   </span>
                   <span className="text-sm text-muted-foreground">
                     (Rating: {comparison.rating.toFixed(2)})
                   </span>
                 </div>
               </div>
             </div>

             <div className="grid grid-cols-3 gap-4 text-sm mb-4">
               <div>
                 <div className="text-muted-foreground">Average Item Value</div>
                 <FormattedMoney copper={comparison.value_per_item} />
               </div>
               <div>
                 <div className="text-muted-foreground">Total Market Value</div>
                 <FormattedMoney copper={comparison.total_value} />
               </div>
               <div>
                 <div className="text-muted-foreground">Market Rating</div>
                 <span className={`font-medium ${
                   isHighest ? "text-green-500" :
                   isLowest ? "text-red-500" :
                   "text-muted-foreground"
                 }`}>
                   {comparison.rating.toFixed(0)}
                 </span>
               </div>
             </div>

              {comparison.items && (
                <div className="space-y-4">
                  <div className="text-sm font-medium">Item Details</div>
                  <div className="divide-y">
                    {comparison.items.map((item) => (
                      <div key={item.item_id} className="py-2">
                        <div className="font-medium mb-2">{item.item_name}</div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="text-muted-foreground">Lowest Price</div>
                            <FormattedMoney copper={item.lowest_price} />
                          </div>
                          <div>
                            <div className="text-muted-foreground">Highest Price</div>
                            <FormattedMoney copper={item.highest_price} />
                          </div>
                          <div>
                            <div className="text-muted-foreground">Quantity Available</div>
                            <span>{item.quantity}</span>
                          </div>
                          <div>
                            <div className="text-muted-foreground">Avg. of Lowest 5</div>
                            <FormattedMoney copper={item.average_lowest_five} />
                          </div>
                          <div>
                            <div className="text-muted-foreground">Item Rating</div>
                            <span className="font-medium">
                              {item.rating.toFixed(0)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
