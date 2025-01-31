'use client';

import { WowMoneyIcon } from './wow-money-icon';

interface WowMoneyProps {
  copper: number;
  showIcons?: boolean;
  className?: string;
  iconSize?: number;
}

export function WowMoney({ copper, showIcons = true, className = '', iconSize = 14 }: WowMoneyProps) {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const remainingCopper = copper % 100;

  const iconStyles = { width: `${iconSize}px`, height: `${iconSize}px` };

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {gold > 0 && (
        <span className="flex items-center gap-0.5">
          <span className="font-medium">{gold.toLocaleString()}</span>
          {showIcons ? (
            <span style={iconStyles}>
              <WowMoneyIcon type="gold" className="flex-shrink-0" />
            </span>
          ) : (
            <span className="text-yellow-500">g</span>
          )}
        </span>
      )}
      {(silver > 0 || gold > 0) && (
        <span className="flex items-center gap-0.5">
          <span className="font-medium">{silver}</span>
          {showIcons ? (
            <span style={iconStyles}>
              <WowMoneyIcon type="silver" className="flex-shrink-0" />
            </span>
          ) : (
            <span className="text-gray-400">s</span>
          )}
        </span>
      )}
      <span className="flex items-center gap-0.5">
        <span className="font-medium">{remainingCopper}</span>
        {showIcons ? (
          <span style={iconStyles}>
            <WowMoneyIcon type="copper" className="flex-shrink-0" />
          </span>
        ) : (
          <span className="text-orange-400">c</span>
        )}
      </span>
    </div>
  );
}