import kk from "@/messages/kk.json";
import ru from "@/messages/ru.json";
import en from "@/messages/en.json";

export const messages = {
  kk,
  ru,
  en,
} as const;

export type Locale = keyof typeof messages;

export function getMessages(locale: Locale) {
  return messages[locale] ?? messages.kk;
}

export function normalizeLocale(value: string | undefined | null): Locale {
  if (value === "ru" || value === "en") return value;
  if (value === "kz" || value === "kk") return "kk";
  return "kk";
}

export const LOCALE_LABELS: Record<Locale, string> = {
  kk: "Қазақша",
  ru: "Русский",
  en: "English",
};
