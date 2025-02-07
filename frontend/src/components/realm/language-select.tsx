"use client";

import { useAtom } from "jotai";
import { Check } from "lucide-react";
import { selectedLanguagesAtom } from "@/lib/store";

const ALL_LANGUAGES = [
  "English",
  "French",
  "German",
  "Spanish",
  "Portuguese",
  "Italian",
  "Russian",
];

export function LanguageSelect() {
  const [selectedLanguages, setSelectedLanguages] = useAtom(selectedLanguagesAtom);

  return (
    <div>
      <div className="text-sm font-medium mb-2">Select Languages</div>
      <div className="grid grid-cols-2 gap-2">
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
            className={`flex items-center justify-between p-2 text-left rounded-lg border transition-all text-sm
              ${selectedLanguages.includes(language)
                ? "border-primary bg-primary/10"
                : "border-gray-200 hover:bg-accent"}`}
          >
            <span className="font-medium">{language}</span>
            {selectedLanguages.includes(language) && (
              <Check className="h-4 w-4 text-primary" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
