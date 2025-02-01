import { useAtom } from "jotai";
import { useEffect } from "react";
import {
  sortedRealmComparisonAtom,
  compareRealmsAtom,
  isLoadingAtom,
  selectedRealmsAtom,
  selectedItemIdsAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { WowMoneyIcon } from "@/components/ui/wow-money-icon";
import { ArrowUp, ArrowDown } from "lucide-react";

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

export function PriceComparison() {
  const [realmComparison] = useAtom(sortedRealmComparisonAtom);
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
        {realmComparison.map((comparison, index) => {
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
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{realm.name}</span>
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
                    Rank #{index + 1}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Average Item Value</div>
                  <FormattedMoney copper={comparison.value_per_item} />
                </div>
                <div>
                  <div className="text-muted-foreground">Total Market Value</div>
                  <FormattedMoney copper={comparison.total_value} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}