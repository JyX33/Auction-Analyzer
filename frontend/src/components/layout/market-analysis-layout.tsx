"use client";

import { RealmSelect } from "@/components/realm/realm-select";
import { LanguageSelect } from "@/components/realm/language-select";
import { ItemSelect } from "@/components/item/item-select";
import { SelectedRealmsBadges } from "@/components/realm/selected-realms-badges";
import { SelectedItemsBadges } from "@/components/item/selected-items-badges";
import { PriceComparison } from "@/components/realm/price-comparison";
import { useAtom } from "jotai";
import { useEffect } from "react";
import { itemsAtom, selectedItemIdsAtom, selectedLanguagesAtom, selectedRealmsAtom } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { getRealmsForLanguage } from "@/lib/utils";

export function MarketAnalysisLayout() {
  const [items] = useAtom(itemsAtom);
  const [, setSelectedItemIds] = useAtom(selectedItemIdsAtom);
  const [selectedLanguages] = useAtom(selectedLanguagesAtom);
  const [, setSelectedRealms] = useAtom(selectedRealmsAtom);

  useEffect(() => {
    if (selectedLanguages && selectedLanguages.length > 0) {
      let realms: number[] = [];
      selectedLanguages.forEach(language => {
        realms.push(...getRealmsForLanguage(language));
      });
      setSelectedRealms(new Set(realms));
    } else {
      setSelectedRealms(new Set());
    }
  }, [selectedLanguages, setSelectedRealms]);

  return (
    <div className="flex min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Control Bar - Sidebar on left side */}
      <div className="w-64 sticky left-0 top-0 h-screen bg-white/80 backdrop-blur-lg border-r shadow-sm">
        <div className="p-4">
          <div className="grid grid-rows-3 gap-6 items-start">
            {/* Language Selector */}
            <div className="bg-indigo-50 p-4 border rounded-lg shadow-sm flex flex-col space-y-3">
              <div className="text-lg font-semibold">Languages</div>
              <LanguageSelect />
            </div>

            {/* Item Selector */}
            <div className="bg-gray-50 p-4 border rounded-lg shadow-sm flex flex-col space-y-3">
              <div className="text-lg font-semibold">Items</div>
              <ItemSelect compact />
              <SelectedItemsBadges items={items} />
            </div>

            {/* Analysis Controls */}
            <div className="bg-gray-50 p-4 border rounded-lg shadow-sm flex flex-col space-y-3">
              <div className="text-lg font-semibold">Analysis Tools</div>
              <Button variant="default" className="w-full shadow hover:shadow-md">
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
