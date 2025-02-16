import { WowMoneyIcon } from "@/components/ui/wow-money-icon";
import { itemsAtom, realmComparisonAtom, selectedRealmsAtom } from "@/lib/store";
import { cn } from "@/lib/utils";
import { useAtom } from "jotai";
import { ArrowDown, ArrowUp, Trophy, Users } from "lucide-react";

interface PriceRankingCardProps {
  itemId: number;
}

const languageToFlag: Record<string, string> = {
  'English': '🇬🇧',
  'German': '🇩🇪',
  'French': '🇫🇷',
  'Spanish': '🇪🇸',
  'Russian': '🇷🇺',
  'Portuguese': '🇵🇹',
  'Italian': '🇮🇹'
};

function FormattedMoney({ copper, className }: { copper: number; className?: string }) {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const remainingCopper = copper % 100;

  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      {gold > 0 && (
        <>
          <WowMoneyIcon type="gold" className="w-4 h-4" />
          <span className="font-medium">{gold}</span>
        </>
      )}
      {(gold > 0 || silver > 0) && (
        <>
          <WowMoneyIcon type="silver" className="w-4 h-4" />
          <span className="font-medium">{silver}</span>
        </>
      )}
      <WowMoneyIcon type="copper" className="w-4 h-4" />
      <span className="font-medium">{remainingCopper}</span>
    </div>
  );
}

function PopulationBadge({ type, population }: { type: string; population?: string }) {
  const colorMap: Record<string, { bg: string; text: string }> = {
    'Full': { bg: 'bg-green-100', text: 'text-green-700' },
    'High': { bg: 'bg-blue-100', text: 'text-blue-700' },
    'Medium': { bg: 'bg-yellow-100', text: 'text-yellow-700' },
    'Low': { bg: 'bg-red-100', text: 'text-red-700' }
  };

  const { bg, text } = colorMap[type] || { bg: 'bg-gray-100', text: 'text-gray-700' };

  return (
    <div className="flex items-center gap-1.5">
      <span className={cn("inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium", bg, text)}>
        <Users className="w-3 h-3" />
        {type}
        {population && <span className="ml-1">({population})</span>}
      </span>
    </div>
  );
}

function RealmInfo({ realmName, language, populationType, population }: { 
  realmName: string; 
  language: string;
  populationType: string;
  population?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        <span className="font-medium text-gray-900 text-sm">{realmName}</span>
        <span className="text-base" role="img" aria-label={`${language} flag`}>
          {languageToFlag[language] || '🌍'}
        </span>
      </div>
      <PopulationBadge type={populationType} population={population} />
    </div>
  );
}

export function PriceRankingCard({ itemId }: PriceRankingCardProps) {
  const [realmComparison] = useAtom(realmComparisonAtom);
  const [items] = useAtom(itemsAtom);
  const [selectedRealms] = useAtom(selectedRealmsAtom);
  const item = items.find((it) => it.item_id === itemId);

  // Build an array of { realm, itemDetail } for realms that contain data for this item.
  const realmsForItem = realmComparison
    .map((realm) => {
      const itemDetail = realm.items.find((i) => i.item_id === itemId);
      const selectedRealm = selectedRealms.find((r) => r.id === realm.realm_id);
      return itemDetail && selectedRealm ? {
        realm,
        itemDetail,
        realmName: selectedRealm.name,
        language: selectedRealm.language,
        populationType: selectedRealm.population_type,
        population: selectedRealm.population
      } : null;
    })
    .filter(Boolean) as {
      realm: typeof realmComparison[0];
      itemDetail: { average_lowest_five: number };
      realmName: string;
      language: string;
      populationType: string;
      population?: string;
    }[];

  // Filter realms where price > raw_craft_cost and sort by price
  const sortedRealms = realmsForItem
    .filter(entry => item?.raw_craft_cost ? entry.itemDetail.average_lowest_five > item.raw_craft_cost : true)
    .sort((a, b) => b.itemDetail.average_lowest_five - a.itemDetail.average_lowest_five)
    .slice(0, 10);

  return (
    <div className="relative rounded-lg p-4 shadow-md bg-gradient-to-br from-white to-gray-50 border transition-all duration-300 hover:shadow-xl hover:scale-[1.02]">
      <div className="flex flex-col gap-2 mb-4">
        <div className="flex items-center gap-1.5">
          <h3 className="text-lg font-bold text-gray-900 truncate">{item ? item.item_name : `Item ${itemId}`}</h3>
          {sortedRealms.length > 0 && (
            <Trophy className="w-5 h-5 text-amber-500" aria-label="Price Rankings" />
          )}
        </div>
        {item?.raw_craft_cost && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Craft Cost:</span>
            <FormattedMoney copper={item.raw_craft_cost} />
          </div>
        )}
      </div>
      
      {sortedRealms.length === 0 ? (
        <div className="text-sm text-muted-foreground">No price data available for this item</div>
      ) : (
        <div className="space-y-2">
          {sortedRealms.map((entry, index) => {
            const isTop = index === 0;
            const isBottom = index === sortedRealms.length - 1;
            
            return (
              <div 
                key={entry.realm.realm_id} 
                className={cn(
                  "flex justify-between items-start p-2 rounded-lg transition-colors",
                  isTop && "bg-amber-50 border border-amber-200",
                  isBottom && "bg-red-50 border border-red-200",
                  !isTop && !isBottom && "hover:bg-gray-50"
                )}
              >
                <RealmInfo 
                  realmName={entry.realmName}
                  language={entry.language}
                  populationType={entry.populationType}
                  population={entry.population}
                />
                <span className="flex items-center gap-2 text-sm">
                  {isTop && (
                    <ArrowUp className="text-green-500 w-5 h-5 animate-bounce" />
                  )}
                  {isBottom && (
                    <ArrowDown className="text-red-500 w-5 h-5 animate-bounce" />
                  )}
                  <FormattedMoney 
                    copper={entry.itemDetail.average_lowest_five} 
                    className={cn(
                      isTop && "text-amber-700",
                      isBottom && "text-red-700"
                    )}
                  />
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
