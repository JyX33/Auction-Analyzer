'use client';

import {
  selectedItemIdsAtom,
  selectedRealmIdsAtom,
  selectedLanguagesAtom,
  timeRangeAtom,
} from '@/lib/store';
import { useAtom } from 'jotai';
import { useEffect, useRef } from 'react';

function useLocalStorage(isMounted: boolean) {
  const [selectedLanguages, setSelectedLanguages] = useAtom(selectedLanguagesAtom);
  const [selectedRealmIds, setSelectedRealmIds] = useAtom(selectedRealmIdsAtom);
  const [selectedItemIds, setSelectedItemIds] = useAtom(selectedItemIdsAtom);
  const [timeRange, setTimeRange] = useAtom(timeRangeAtom);
  const initialized = useRef(false);

  // Load from localStorage
  useEffect(() => {
    if (!isMounted || initialized.current || typeof window === 'undefined') return;

    try {
      const loadFromStorage = (key: string) => {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
      };

      const languages = loadFromStorage('selectedLanguages');
      if (Array.isArray(languages) && languages.every(lang => typeof lang === 'string')) {
        setSelectedLanguages(languages);
      }

      const realmIds = loadFromStorage('selectedRealmIds');
      if (Array.isArray(realmIds) && realmIds.every(id => typeof id === 'number')) {
        setSelectedRealmIds(realmIds);
      }

      const itemIds = loadFromStorage('selectedItemIds');
      if (Array.isArray(itemIds) && itemIds.every(id => typeof id === 'number')) {
        setSelectedItemIds(new Set(itemIds));
      }

      const time = loadFromStorage('timeRange');
      if (time && ['7d', '30d', 'all'].includes(time)) {
        setTimeRange(time as '7d' | '30d' | 'all');
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error);
    }

    initialized.current = true;
  }, [setSelectedLanguages, setSelectedRealmIds, setSelectedItemIds, setTimeRange, isMounted]);

  // Save to localStorage
  useEffect(() => {
    if (!isMounted || !initialized.current || typeof window === 'undefined') return;

    try {
      localStorage.setItem('selectedLanguages', JSON.stringify(selectedLanguages));
      localStorage.setItem('selectedRealmIds', JSON.stringify(selectedRealmIds));
      localStorage.setItem('selectedItemIds', JSON.stringify(Array.from(selectedItemIds)));
      localStorage.setItem('timeRange', JSON.stringify(timeRange));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }, [selectedLanguages, selectedRealmIds, selectedItemIds, timeRange, isMounted]);
}

interface StorageProviderProps {
  children: React.ReactNode;
  isMounted: boolean;
}

export function StorageProvider({ children, isMounted }: StorageProviderProps) {
  useLocalStorage(isMounted);
  return <>{children}</>;
}
