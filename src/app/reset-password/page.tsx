"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { resetPassword } from "@/lib/auth";
import { useTranslations } from "@/hooks/useTranslations";

function ResetPasswordForm() {
  const { t } = useTranslations();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError(t("auth.passwordMismatch"));
      return;
    }

    if (password.length < 8) {
      setError(t("auth.passwordTooShort"));
      return;
    }

    setLoading(true);

    try {
      await resetPassword(token, password);
      setSuccess(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">{t("auth.invalidResetLink")}</h2>
        <Link href="/forgot-password" className="text-indigo-400 hover:text-indigo-300">
          {t("auth.requestNewLink")}
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="text-center mb-8">
        <h1 className="text-4xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          QalaJob AI
        </h1>
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-8">
        {success ? (
          <div className="text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold mb-3">{t("auth.passwordResetSuccess")}</h2>
            <p className="text-white/60 mb-6">{t("auth.passwordResetSuccessDesc")}</p>
            <Link
              href="/login"
              className="inline-block px-8 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 font-bold"
            >
              {t("auth.loginTitle")} →
            </Link>
          </div>
        ) : (
          <>
            <h2 className="text-2xl font-bold mb-2">{t("auth.resetPasswordTitle")}</h2>
            <p className="text-white/60 mb-6">{t("auth.resetPasswordDesc")}</p>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-white/70 mb-2">
                  {t("auth.newPassword")}
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:outline-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm text-white/70 mb-2">
                  {t("auth.confirmPassword")}
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:outline-none transition-colors"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full p-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-bold transition-all disabled:opacity-50"
              >
                {loading ? t("common.loading") : t("auth.resetPasswordButton")}
              </button>
            </form>
          </>
        )}
      </div>
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <main className="min-h-screen bg-[#030712] text-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Suspense fallback={<div className="text-center p-10">Loading...</div>}>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </main>
  );
}
