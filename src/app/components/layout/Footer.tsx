"use client";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function Footer() {
  const { locale } = useLanguage();
  const t = getMessages(locale);

  return (
    <footer className="border-t border-white/10 py-10">
      <div className="container-custom text-center">
        <p className="text-white/70 text-sm">{t.footer.description}</p>
        <p className="text-white/40 text-sm mt-2">{t.footer.copyright}</p>
      </div>
    </footer>
  );
}
