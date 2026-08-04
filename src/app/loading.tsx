"use client";

import { useTranslations } from "@/hooks/useTranslations";

export default function Loading() {
  const { t } = useTranslations();
  return (
    <main className="min-h-screen bg-[#030712] flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-white/50">{t("loading.text")}</p>
      </div>
    </main>
  );
}
