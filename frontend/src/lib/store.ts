import { atom, createStore } from 'jotai';
import { apiClient, type RealmData, type PriceMetrics, type RealmComparison } from './api';

const store = createStore();

// Atoms with default values for SSR
export const selectedRegionAtom = atom<string>('French');
export const selectedRealmIdsAtom = atom<number[]>([]);
export const selectedItemIdsAtom = atom<Set<number>>(new Set<number>());
export const isItemSelectedAtom = atom(
  (get) => (id: number) => get(selectedItemIdsAtom).has(id)
);
export const selectedItemsCountAtom = atom(
  (get) => get(selectedItemIdsAtom).size
);

// Actions
export const toggleItemSelectionAtom = atom(
  null,
  (get, set, id: number) => {
    const selected = get(selectedItemIdsAtom);
    const newSelected = new Set(selected);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    set(selectedItemIdsAtom, newSelected);
  }
);

export const bulkSelectItemsAtom = atom(
  null,
  (get, set, ids: number[]) => {
    const selected = get(selectedItemIdsAtom);
    const newSelected = new Set(selected);
    ids.forEach(id => newSelected.add(id));
    set(selectedItemIdsAtom, newSelected);
  }
);

export const clearSelectionAtom = atom(
  null,
  (get, set) => {
    set(selectedItemIdsAtom, new Set());
  }
);
export const timeRangeAtom = atom<'7d' | '30d' | 'all'>('7d');

// UI state atoms
export const isLoadingAtom = atom<boolean>(false);
export const errorAtom = atom<string | null>(null);

// Data atoms
export const realmsAtom = atom<RealmData[]>([]);
export const priceMetricsAtom = atom<Record<number, PriceMetrics>>({});
export const realmComparisonAtom = atom<RealmComparison[]>([]);

// Derived atoms
export const selectedRealmsAtom = atom(
  (get) => {
    const realms = get(realmsAtom);
    const selectedIds = get(selectedRealmIdsAtom);
    return realms.filter(realm => selectedIds.includes(realm.id));
  }
);

export const sortedRealmComparisonAtom = atom(
  (get) => {
    const comparison = get(realmComparisonAtom);
    return [...comparison].sort((a, b) => b.value_per_item - a.value_per_item);
  }
);

// Action atoms
export const fetchRealmsAtom = atom(
  null,
  async (get, set) => {
    const region = get(selectedRegionAtom);
    set(isLoadingAtom, true);
    set(errorAtom, null);

    try {
      const realms = await apiClient.getRealms(region);
      set(realmsAtom, realms);
    } catch (error) {
      set(errorAtom, error instanceof Error ? error.message : 'Failed to fetch realms');
    } finally {
      set(isLoadingAtom, false);
    }
  }
);

export const fetchPriceMetricsAtom = atom(
  null,
  async (get, set, realmId: number) => {
    const itemIds = Array.from(get(selectedItemIdsAtom));
    const timeRange = get(timeRangeAtom);
    set(isLoadingAtom, true);
    set(errorAtom, null);

    try {
      const metrics = await apiClient.getRealmPrices(realmId, itemIds, timeRange);
      set(priceMetricsAtom, prev => ({ ...prev, [realmId]: metrics }));
    } catch (error) {
      set(errorAtom, error instanceof Error ? error.message : 'Failed to fetch price metrics');
    } finally {
      set(isLoadingAtom, false);
    }
  }
);

export const compareRealmsAtom = atom(
  null,
  async (get, set) => {
    const realmIds = get(selectedRealmIdsAtom);
    const itemIds = Array.from(get(selectedItemIdsAtom));
    set(isLoadingAtom, true);
    set(errorAtom, null);

    try {
      const comparison = await apiClient.compareRealms(realmIds, itemIds);
      set(realmComparisonAtom, comparison);
    } catch (error) {
      set(errorAtom, error instanceof Error ? error.message : 'Failed to compare realms');
    } finally {
      set(isLoadingAtom, false);
    }
  }
);

export default store;
