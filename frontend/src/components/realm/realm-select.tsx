"use client";

import { useAtom } from "jotai";
import { useEffect } from "react";
import {
  selectedRealmIdsAtom,
  selectedLanguagesAtom,
  fetchRealmsAtom,
  isLoadingAtom,
  realmsByLanguageAtom,
} from "@/lib/store";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Check } from "lucide-react";

const ALL_LANGUAGES = ['English', 'French', 'German', 'Spanish', 'Portuguese', 'Italian', 'Russian'];

export function RealmSelect() {
  const [selectedRealmIds, setSelectedRealmIds] = useAtom(selectedRealmIdsAtom);
  const [selectedLanguages, setSelectedLanguages] = useAtom(selectedLanguagesAtom);
  const [realmsByLanguage] = useAtom(realmsByLanguageAtom);
  const [isLoading] = useAtom(isLoadingAtom);
  const [, fetchRealms] = useAtom(fetchRealmsAtom);

  useEffect(() => {
    fetchRealms();
  }, [fetchRealms, selectedLanguages]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="grid gap-4 p-4">
      <div>
        <div className="text-sm font-medium mb-2">Select Languages</div>
        <div className="grid gap-2">
          {ALL_LANGUAGES.map((language) => (
            <button
              key={language}
              onClick={() => {
                if (selectedLanguages.includes(language)) {
                  setSelectedLanguages(selectedLanguages.filter((l) => l !== language));
                } else {
                  setSelectedLanguages([...selectedLanguages, language]);
                }
              }}
              className={`flex items-center justify-between p-2 text-left border rounded-lg transition-colors
                ${
                  selectedLanguages.includes(language)
                    ? "border-primary bg-primary/10"
                    : "border-border hover:bg-accent"
                }`}
            >
              <span className="font-medium">{language}</span>
              {selectedLanguages.includes(language) && (
                <Check className="h-4 w-4 text-primary" />
              )}
            </button>
          ))}
        </div>
      </div>

      {Object.entries(realmsByLanguage).map(([language, realms]) => (
        <div key={language}>
          <div className="text-sm font-medium mb-2">{language} Realms</div>
          <div className="grid gap-2">
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
                  <span className="font-medium">{realm.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {realm.item_count.toLocaleString()} items
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
}
