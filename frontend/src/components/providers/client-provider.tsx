"use client";

"use client";

import { useEffect, useState } from "react";
import { Provider } from "jotai";
import { StorageProvider } from "./storage-provider";
import store from "@/lib/store";

export function ClientProvider({ children }: { children: React.ReactNode }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  return (
    <Provider store={store}>
      <StorageProvider isMounted={isMounted}>
        {children}
      </StorageProvider>
    </Provider>
  );
}
