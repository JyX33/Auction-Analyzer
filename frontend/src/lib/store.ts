"use client";

import { atom, createStore } from 'jotai';
import { apiClient, type RealmData, type PriceMetrics, type RealmComparison, type ItemBase } from './api';

const store = createStore();

// Atoms with default values for SSR
export const selectedLanguagesAtom = atom<string[]>(['English', 'French', 'German', 'Spanish', 'Portuguese', 'Italian']); // All except Russian
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
export const itemsAtom = atom<ItemBase[]>([]);
export const priceMetricsAtom = atom<Record<number, PriceMetrics>>({});
export const realmComparisonAtom = atom<RealmComparison[]>([]);

// Fetching actions
export const fetchItemsAtom = atom(
  null,
  async (get, set) => {
    set(isLoadingAtom, true);
    try {
      const response = await apiClient.listItems({ page_size: 100 });
      set(itemsAtom, response.items);
    } catch (error) {
      set(errorAtom, error instanceof Error ? error.message : 'Failed to fetch items');
    } finally {
      set(isLoadingAtom, false);
    }
  }
);

// Derived atoms
export const selectedRealmsAtom = atom(
  (get) => {
    const realms = get(realmsAtom);
    const selectedIds = get(selectedRealmIdsAtom);
    console.log("selectedIds", selectedIds);
    return realms.filter(realm => selectedIds.includes(realm.id));
  }
);

export const realmsByLanguageAtom = atom(
  (get) => {
    const realms = get(realmsAtom);
    const selectedLanguages = get(selectedLanguagesAtom);
    return realms
      .filter(realm => selectedLanguages.includes(realm.language))
      .reduce((acc, realm) => {
        if (!acc[realm.language]) {
          acc[realm.language] = [];
        }
        acc[realm.language].push(realm);
        return acc;
      }, {} as Record<string, RealmData[]>);
  }
);

// Action atoms
export const fetchRealmsAtom = atom(
  null,
  async (get, set) => {
    set(isLoadingAtom, true);
    set(errorAtom, null);

    try {
      const realms = await apiClient.getRealms();
      set(realmsAtom, realms);
      // Select all realms by default
      set(selectedRealmIdsAtom, realms
        .filter(realm => get(selectedLanguagesAtom).includes(realm.language))
        .map(realm => realm.id)
      );
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
