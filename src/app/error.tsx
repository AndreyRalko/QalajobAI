"use client";

import { useTranslations } from "@/hooks/useTranslations";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { t } = useTranslations();

  return (
    <main className="min-h-screen bg-[#030712] text-white flex items-center justify-center p-4">
      <div className="text-center max-w-lg">
        <div className="text-9xl font-black text-red-500/50 mb-4">500</div>
        <h1 className="text-3xl font-bold mb-4">{t("errors.serverError")}</h1>
        <p className="text-white/50 mb-8 text-lg">{t("errors.serverErrorDesc")}</p>
        <button
          onClick={() => reset()}
          className="px-8 py-3 rounded-2xl bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 font-bold transition-all"
        >
          {t("common.tryAgain")}
        </button>
      </div>
    </main>
  );
}
