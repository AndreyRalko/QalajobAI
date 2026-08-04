"use client";

import Link from "next/link";
import { useTranslations } from "@/hooks/useTranslations";

export default function NotFound() {
  const { t } = useTranslations();

  return (
    <main className="min-h-screen bg-[#030712] text-white flex items-center justify-center p-4">
      <div className="text-center max-w-lg">
        <div className="text-9xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent mb-4">
          404
        </div>
        <h1 className="text-3xl font-bold mb-4">{t("errors.notFound")}</h1>
        <p className="text-white/50 mb-8 text-lg">{t("errors.notFoundDesc")}</p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/"
            className="px-8 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-bold transition-all"
          >
            {t("errors.goHome")}
          </Link>
          <button
            onClick={() => history.back()}
            className="px-8 py-3 rounded-2xl border border-white/20 hover:bg-white/5 font-bold transition-all"
          >
            {t("errors.goBack")}
          </button>
        </div>
      </div>
    </main>
  );
}
