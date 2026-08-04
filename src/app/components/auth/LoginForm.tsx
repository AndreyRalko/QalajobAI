"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { loginUser, googleLogin, forgotPassword } from "@/lib/auth";
import { useTranslations } from "@/hooks/useTranslations";

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t } = useTranslations();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      alert(t("auth.emailPasswordRequired"));
      return;
    }

    try {
      setLoading(true);
      const userData = await loginUser(email, password);

      if (userData?.is_banned) {
        alert(t("auth.accountBanned"));
        setLoading(false); // Қатып қалмас үшін loading-ті өшіреміз
        return;
      }

      alert(t("auth.loginSuccess"));

      // URL-дегі ?redirect=%2Fdashboard параметрін оқимыз, жоқ болса /dashboard дефолтты қолданамыз
      const redirectTo = searchParams.get("redirect") || "/dashboard/student/ai";

      // Полная перезагрузка, чтобы сессия из localStorage/cookies подхватилась сервером
      window.location.href = redirectTo;
    } catch (error: unknown) {
      console.error(error);
      const message = error instanceof Error ? error.message : "";
      if (message === "EMAIL_NOT_VERIFIED") {
        alert(t("auth.emailNotVerified"));
        return;
      }
      if (message === "ACCOUNT_BANNED") {
        alert(t("auth.accountBanned"));
        return;
      }
      alert(t("auth.loginFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      // Пытаемся авторизоваться через Google
      await googleLogin();
      
      const redirectTo = searchParams.get("redirect") || "/dashboard/student/ai";
      router.push(redirectTo);
      router.refresh();
    } catch (error: unknown) {
      console.error(error);
      const message = error instanceof Error ? error.message : "";
      
      if (message === "GOOGLE_LOGIN_DISABLED") {
        alert(t("auth.googleDisabled") || "Google арқылы кіру уақытша қолжетімсіз. Электрондық пошта арқылы кіріңіз.");
        return;
      }
      if (message === "EMAIL_NOT_VERIFIED") {
        alert(t("auth.emailNotVerified"));
        return;
      }
      alert(t("auth.loginFailed"));
    }
  };

  const handleForgotPassword = async () => {
    if (!email) {
      alert(t("auth.emailPasswordRequired"));
      return;
    }
    try {
      await forgotPassword(email);
      alert(t("auth.passwordResetSent"));
    } catch {
      alert(t("errors.generic"));
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
          <button
            onClick={handleGoogleLogin}
            className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 hover:bg-white/10 transition text-lg font-semibold flex items-center justify-center gap-3 backdrop-blur-xl text-white"
          >
            {t("auth.googleLogin")}
          </button>

          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-white/30 text-sm">{t("auth.orEmail")}</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <div className="space-y-5">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("auth.email")}
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
            onClick={handleForgotPassword}
            className="mt-3 text-sm text-cyan-400 hover:text-cyan-300"
          >
            {t("auth.forgotPassword")}
          </button>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="mt-8 w-full h-16 rounded-[24px] bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] transition-all duration-300 text-xl font-bold text-white shadow-[0_0_60px_rgba(99,102,241,0.4)] disabled:opacity-50"
          >
            {loading ? t("common.loading") : (t("auth.loginButton") || "Kiry →")}
          </button>

          <p className="mt-8 text-center text-white/40">
            {t("auth.noAccount")}{" "}
            <Link
              href="/register"
              className="text-cyan-400 hover:text-cyan-300 transition font-semibold"
            >
              {t("navbar.register")}
            </Link>
          </p>
        </div>
      </motion.div>
    </section>
  );
}