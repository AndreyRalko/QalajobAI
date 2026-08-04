"use client";

import { useCallback, useMemo } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { getMessages, type Locale } from "@/lib/i18n";

type MessageValue = string | MessageTree | MessageValue[];
type MessageTree = { [key: string]: MessageValue };

function getNestedValue(obj: MessageTree, path: string): string | undefined {
  const keys = path.split(".");
  let current: MessageValue = obj;

  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== "object" || Array.isArray(current)) {
      return undefined;
    }
    current = (current as MessageTree)[key];
  }

  return typeof current === "string" ? current : undefined;
}

function interpolate(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, key) => String(vars[key] ?? `{${key}}`));
}

export function useTranslations() {
  const { locale, setLocale } = useLanguage();
  const messages = useMemo(() => getMessages(locale) as MessageTree, [locale]);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>): string => {
      const value = getNestedValue(messages, key);
      if (value === undefined) {
        if (process.env.NODE_ENV === "development") {
          console.warn(`Missing translation: ${key} (${locale})`);
        }
        return key;
      }
      return interpolate(value, vars);
    },
    [messages, locale]
  );

  return { t, locale, setLocale, messages };
}

export type { Locale };
