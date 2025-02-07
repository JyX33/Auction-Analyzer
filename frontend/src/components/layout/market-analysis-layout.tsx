"use client";

import { RealmSelect } from "@/components/realm/realm-select";
import { LanguageSelect } from "@/components/realm/language-select";
import { ItemSelect } from "@/components/item/item-select";
import { SelectedRealmsBadges } from "@/components/realm/selected-realms-badges";
import { SelectedItemsBadges } from "@/components/item/selected-items-badges";
import { PriceComparison } from "@/components/realm/price-comparison";
import { useAtom } from "jotai";
import { itemsAtom, selectedItemIdsAtom } from "@/lib/store";
import { Button } from "@/components/ui/button";

export function MarketAnalysisLayout() {
  const [items] = useAtom(itemsAtom);
  const [, setSelectedItemIds] = useAtom(selectedItemIdsAtom);

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Control Bar - Sticky at top */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-lg border-b shadow-sm">
        <div className="container px-4 py-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-start">
            {/* Realm Selector Column */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Selected Realms</div>
              <LanguageSelect />
              <RealmSelect compact />
              <SelectedRealmsBadges />
            </div>

            {/* Item Selector Column */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Selected Items</div>
              <ItemSelect compact />
              <SelectedItemsBadges items={items} />
            </div>

            {/* Analysis Controls Column */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Analysis Tools</div>
              <Button 
                variant="default" 
                className="w-full shadow hover:shadow-md"
              >
                Compare Markets
              </Button>
              <Button 
                variant="ghost" 
                className="w-full"
                onClick={() => setSelectedItemIds(new Set())}
              >
                Clear Selections
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Analysis Content - Scrollable area */}
      <div className="flex-1 overflow-auto">
        <div className="container px-4 py-6">
          <PriceComparison />
        </div>
      </div>
    </div>
  );
}
