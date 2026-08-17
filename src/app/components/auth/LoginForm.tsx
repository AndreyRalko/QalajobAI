"use client";

import { motion } from "motion/react";
import { useState } from "react";
import { useSearchParams } from "next/navigation";

import { loginUser } from "@/lib/auth";
import { useTranslations } from "@/hooks/useTranslations";

export default function LoginForm() {
  const searchParams = useSearchParams();
  const { t } = useTranslations();

  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!login || !password) {
      alert(t("auth.emailPasswordRequired"));
      return;
    }

    try {
      setLoading(true);
      const userData = await loginUser(login, password);

      if (userData?.is_banned) {
        alert(t("auth.accountBanned"));
        setLoading(false);
        return;
      }

      alert(t("auth.loginSuccess"));

      const defaultRedirect =
        userData?.role === "admin"
          ? "/dashboard/admin"
          : userData?.role === "employer"
            ? "/dashboard/employer"
            : "/dashboard/student/ai";

      const redirectTo = searchParams.get("redirect") || defaultRedirect;
      window.location.href = redirectTo;
    } catch (error: unknown) {
      console.error(error);
      const message = error instanceof Error ? error.message : "";
      if (message === "ACCOUNT_BANNED") {
        alert(t("auth.accountBanned"));
        return;
      }
      alert(t("auth.loginFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-[#030712] overflow-hidden px-6">
      <div className="absolute top-[-200px] left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-blue-500/10 blur-[160px]" />

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-xl"
      >
        <h1 className="text-5xl font-black tracking-tight text-white">
          {t("auth.loginTitle") || "Kipy"}
        </h1>

        <p className="mt-4 text-lg text-white/40">
          {t("auth.loginSubtitle")}
        </p>

        <div className="mt-12">
          <div className="space-y-5">
            <input
              type="text"
              autoComplete="username"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder={t("auth.login")}
              className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 px-6 text-lg text-white outline-none focus:border-cyan-400 transition backdrop-blur-xl"
            />

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("auth.password")}
              className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 px-6 text-lg text-white outline-none focus:border-cyan-400 transition backdrop-blur-xl"
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="mt-8 w-full h-16 rounded-[24px] bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] transition-all duration-300 text-xl font-bold text-white shadow-[0_0_60px_rgba(99,102,241,0.4)] disabled:opacity-50"
          >
            {loading ? t("common.loading") : (t("auth.loginButton") || "Kiry →")}
          </button>
        </div>
      </motion.div>
    </section>
  );
}
