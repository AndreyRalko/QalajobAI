"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { registerUser, googleLogin } from "@/lib/auth";
import { useTranslations } from "@/hooks/useTranslations";

export default function RegisterForm() {
  const router = useRouter();
  const { t } = useTranslations();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!name || !email || !password) {
      alert(t("register.alertRequired"));
      return;
    }
    try {
      setLoading(true);
      await registerUser(name, email, password, "student");
      alert(t("register.alertEmailSent"));
      router.push("/dashboard/student/ai");
    } catch (error: any) {
      console.error(error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await googleLogin();
      router.push("/dashboard/student/ai");
    } catch (error: any) {
      console.error(error);
      if (error.message === "GOOGLE_LOGIN_DISABLED") {
        alert(t("register.googleDisabled"));
        return;
      }
      alert(error.message);
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
        <h1 className="text-5xl font-black tracking-tight text-white">{t("register.title")}</h1>
        <p className="mt-4 text-lg text-white/40">{t("register.subtitle")}</p>

        <div className="mt-12">
          <button
            onClick={handleGoogleLogin}
            className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 hover:bg-white/10 transition text-lg font-semibold flex items-center justify-center gap-3 backdrop-blur-xl"
          >
            <span>◎</span> {t("register.googleLogin")}
          </button>

          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-white/30 text-sm">{t("register.orEmail")}</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <div className="space-y-5">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("register.fullNamePlaceholder")}
              className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 px-6 text-lg text-white outline-none focus:border-cyan-400 transition backdrop-blur-xl"
            />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("register.emailPlaceholder")}
              className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 px-6 text-lg text-white outline-none focus:border-cyan-400 transition backdrop-blur-xl"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("register.passwordPlaceholder")}
              className="w-full h-16 rounded-[24px] border border-white/10 bg-white/5 px-6 text-lg text-white outline-none focus:border-cyan-400 transition backdrop-blur-xl"
            />
          </div>

          <button
            onClick={handleRegister}
            disabled={loading}
            className="mt-8 w-full h-16 rounded-[24px] bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] transition-all duration-300 text-xl font-bold shadow-[0_0_60px_rgba(99,102,241,0.4)] disabled:opacity-50"
          >
            {loading ? t("register.loading") : t("register.button")}
          </button>

          <p className="mt-8 text-center text-white/40">
            {t("register.hasAccount")}{" "}
            <Link href="/login" className="text-cyan-400 hover:text-cyan-300 transition font-semibold">
              {t("register.login")}
            </Link>
          </p>
        </div>
      </motion.div>

    </section>
  );
}
