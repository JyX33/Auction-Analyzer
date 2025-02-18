'use client';

import { cn } from '@/lib/utils';
import { WowMoneyIcon } from './wow-money-icon';

interface WowMoneyProps {
  copper: number;
  showIcons?: boolean;
  className?: string;
  iconSize?: number;
}

export function WowMoney({ copper, showIcons = true, className = ''}: WowMoneyProps) {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const remainingCopper = copper % 100;

  return (
    <div className={cn("inline-flex items-center gap-1.5 font-semibold", className)}>
      {gold > 0 && (
        <span className="flex items-center gap-1 text-yellow-600">
          <span>{gold.toLocaleString()}</span>
          {showIcons ? (
            <WowMoneyIcon type="gold" className="w-4 h-4" />
          ) : (
            <span>g</span>
          )}
        </span>
      )}
      {(silver > 0 || gold > 0) && (
        <span className="flex items-center gap-1 text-gray-500">
          <span>{silver}</span>
          {showIcons ? (
            <WowMoneyIcon type="silver" className="w-4 h-4" />
          ) : (
            <span>s</span>
          )}
        </span>
      )}
      <span className="flex items-center gap-1 text-orange-600">
        <span>{remainingCopper}</span>
        {showIcons ? (
          <WowMoneyIcon type="copper" className="w-4 h-4" />
        ) : (
          <span>c</span>
        )}
      </span>
    </div>
  );
}
