'use client';

import { Provider } from 'jotai';
import { RealmSelect } from '@/components/realm/realm-select';
import { PriceComparison } from '@/components/realm/price-comparison';
import { ItemSelect } from '@/components/item/item-select';

export default function Home() {
  return (
    <Provider>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="flex flex-col gap-4">
          <div className="rounded-lg border bg-card">
            <h2 className="p-4 font-semibold border-b">Realm Selection</h2>
            <RealmSelect />
          </div>
          <div className="rounded-lg border bg-card">
            <h2 className="p-4 font-semibold border-b">Item Selection</h2>
            <ItemSelect />
          </div>
        </div>
        <div className="rounded-lg border bg-card">
          <h2 className="p-4 font-semibold border-b">Market Analysis</h2>
          <PriceComparison />
        </div>
      </div>
    </Provider>
  );
}
