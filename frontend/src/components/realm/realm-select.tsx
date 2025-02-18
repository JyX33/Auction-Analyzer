"use client";

import React from "react";
import { useAtom } from "jotai";
import { useEffect, useState } from "react";
import {
  selectedRealmIdsAtom,
  selectedLanguagesAtom,
  fetchRealmsAtom,
  isLoadingAtom,
  realmsByLanguageAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Check, ChevronDown } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface RealmSelectProps {
  compact?: boolean;
}

export function RealmSelect({ compact }: RealmSelectProps) {
  const [selectedRealmIds, setSelectedRealmIds] = useAtom(selectedRealmIdsAtom);
  const [selectedLanguages] = useAtom(selectedLanguagesAtom);
  const [realmsByLanguage] = useAtom(realmsByLanguageAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, fetchRealms] = useAtom(fetchRealmsAtom);
  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);


  const RealmsSelection = () => (
    <div className="max-h-[400px] overflow-y-auto">
      {Object.entries(filteredRealmsByLanguage).map(([language, realms]) => (
        <div key={language} className="mb-4">
          <div className="text-sm font-medium mb-2 sticky top-0 bg-white z-10 border-b pb-1">{language} Realms</div>
          <div className="grid grid-cols-2 gap-2">
            {realms.map((realm) => (
              <button
                key={realm.id}
                onClick={() => {
                  if (selectedRealmIds.includes(realm.id)) {
                    setSelectedRealmIds(selectedRealmIds.filter((id) => id !== realm.id));
                  } else {
                    setSelectedRealmIds([...selectedRealmIds, realm.id]);
                  }
                }}
                className={`flex items-center justify-between p-2 text-left border rounded-lg transition-colors
                  ${
                    selectedRealmIds.includes(realm.id)
                      ? "border-primary bg-primary/10"
                      : "border-border hover:bg-accent"
                  }`}
              >
                <span className="flex flex-col">
                  <span className="font-medium text-sm">{realm.name}</span>
                  <span className="flex items-center gap-2">
                    <span className={`text-xs font-semibold ${
                      realm.population_type === 'Full' ? 'text-red-600' :
                      realm.population_type === 'High' ? 'text-orange-600' :
                      realm.population_type === 'Medium' ? 'text-yellow-600' :
                      realm.population_type === 'Low' ? 'text-green-600' : 
                      'text-blue-600'
                    }`}>
                      {realm.population_type}
                    </span>
                    {realm.population && (
                      <span className="text-xs text-muted-foreground">
                        ({realm.population})
                      </span>
                    )}
                  </span>
                </span>
                {selectedRealmIds.includes(realm.id) && (
                  <Check className="h-4 w-4 text-primary" />
                )}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  useEffect(() => {
    fetchRealms();
  }, [fetchRealms, selectedLanguages]);

  const filteredRealmsByLanguage = Object.fromEntries(
    Object.entries(realmsByLanguage).map(([language, realms]) => [
      language,
      realms.filter(realm => 
        realm.name.toLowerCase().includes(search.toLowerCase())
      )
    ])
  );

  // Removed SelectionContent function

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  if (compact) {
    return (
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button 
            variant="outline"
            size="default"
            className="w-full justify-between"
            role="combobox"
          >
            <span>Select Realms</span>
            <ChevronDown className="w-4 h-4 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-4" align="start">
          <div className="space-y-4">
            <Input
              type="search"
              placeholder="Search realms..."
              className="w-full"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              autoComplete="off"
            />
            <RealmsSelection />
          </div>
        </PopoverContent>
      </Popover>
    );
  }

  return (
    <div className="grid gap-4 p-4">
      <RealmsSelection />
    </div>
  );
}
