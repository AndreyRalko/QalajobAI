"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";

import { setLanguageApi, getMe } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { type Locale, normalizeLocale } from "@/lib/i18n";

const STORAGE_KEY = "qalajob-locale";

type LanguageContextType = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  ready: boolean;
};

const LanguageContext = createContext<LanguageContextType>({
  locale: "kk",
  setLocale: () => {},
  ready: false,
});

export function LanguageProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [locale, setLocaleState] = useState<Locale>("kk");
  const [ready, setReady] = useState(false);

  const persistLocale = useCallback(
    async (next: Locale) => {
      localStorage.setItem(STORAGE_KEY, next);
      document.cookie = `qalajob-locale=${next}; path=/; max-age=31536000; SameSite=Lax`;

      const token = getAccessToken();
      if (!token) return;

      try {
        await setLanguageApi(next);
      } catch (error) {
        console.error(error);
      }
    },
    []
  );

  const setLocale = useCallback(
    (next: Locale) => {
      setLocaleState(next);
      void persistLocale(next);
    },
    [persistLocale]
  );

  useEffect(() => {
    const loadLanguage = async () => {
      // Read from localStorage on mount (client-side only)
      const localLocale = localStorage.getItem(STORAGE_KEY);
      if (localLocale) {
        setLocaleState(normalizeLocale(localLocale));
        document.cookie = `qalajob-locale=${normalizeLocale(localLocale)}; path=/; max-age=31536000; SameSite=Lax`;
      }

      const token = getAccessToken();

      if (!token) {
        setReady(true);
        return;
      }

      try {
        const profile = await getMe(token);

        if (profile.language) {
          const normalized = normalizeLocale(
            profile.language
          );

          setLocaleState(normalized);

          localStorage.setItem(
            STORAGE_KEY,
            normalized
          );
        }
      } catch (error) {
        console.error(error);
      } finally {
        setReady(true);
      }
    };

    loadLanguage();
  }, []);

  return (
    <LanguageContext.Provider
      value={{
        locale,
        setLocale,
        ready,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}