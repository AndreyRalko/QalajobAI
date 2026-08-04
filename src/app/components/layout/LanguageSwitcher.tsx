"use client";

import { useLanguage } from "@/context/LanguageContext";
import { LOCALE_LABELS, type Locale } from "@/lib/i18n";

const LOCALES: Locale[] = ["kk", "ru", "en"];

type LanguageSwitcherProps = {
  variant?: "compact" | "full";
  className?: string;
};

export default function LanguageSwitcher({
  variant = "compact",
  className = "",
}: LanguageSwitcherProps) {
  const { locale, setLocale } = useLanguage();

  if (variant === "full") {
    return (
      <div className={`flex gap-2 ${className}`}>
        {LOCALES.map((loc) => (
          <button
            key={loc}
            type="button"
            onClick={() => setLocale(loc)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition ${
              locale === loc
                ? "bg-cyan-500 text-black"
                : "bg-white/5 border border-white/10 text-white/70 hover:text-white"
            }`}
          >
            {LOCALE_LABELS[loc]}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-1 border border-white/10 bg-white/5 rounded-full px-2 py-1 ${className}`}>
      {LOCALES.map((loc) => (
        <button
          key={loc}
          type="button"
          onClick={() => setLocale(loc)}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
            locale === loc
              ? "bg-cyan-400 text-black"
              : "text-white/60 hover:text-white"
          }`}
        >
          {loc.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
