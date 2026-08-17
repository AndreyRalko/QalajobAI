"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/app/components/ui/button";
import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { locale, setLocale } = useLanguage();
  const t = getMessages(locale);

  return (
    <>
      <header className="fixed top-0 left-0 w-full z-50">
        <div className="container-custom">
          <div className="mt-4 flex items-center justify-between rounded-[28px] border border-white/10 bg-[#050816]/80 backdrop-blur-2xl px-6 lg:px-8 py-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-black font-black text-lg shadow-[0_0_40px_rgba(34,211,238,0.45)]">
                Q
              </div>
              <div>
                <h1 className="text-xl font-black tracking-tight">QalaJob AI</h1>
                <p className="text-xs text-white/40">AI Resume Assistant</p>
              </div>
            </Link>

            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 border border-white/10 bg-white/5 rounded-full px-2 py-1 backdrop-blur-xl">
                <button
                  type="button"
                  onClick={() => setLocale("kk")}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                    locale === "kk"
                      ? "bg-cyan-400 text-black"
                      : "text-white/60 hover:text-white"
                  }`}
                >
                  KK
                </button>
                <button
                  type="button"
                  onClick={() => setLocale("ru")}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                    locale === "ru"
                      ? "bg-cyan-400 text-black"
                      : "text-white/60 hover:text-white"
                  }`}
                >
                  RU
                </button>
                <button
                  type="button"
                  onClick={() => setLocale("en")}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                    locale === "en"
                      ? "bg-cyan-400 text-black"
                      : "text-white/60 hover:text-white"
                  }`}
                >
                  EN
                </button>
              </div>

              <Link href="/login">
                <Button className="hidden md:flex rounded-xl bg-cyan-400 text-black hover:bg-cyan-300">
                  {t.navbar.login}
                </Button>
              </Link>

              <button
                type="button"
                onClick={() => setMobileMenuOpen(true)}
                className="md:hidden text-white text-3xl"
                aria-label="Menu"
              >
                ☰
              </button>
            </div>
          </div>
        </div>
      </header>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-[100] bg-[#030712]/90 backdrop-blur-md md:hidden">
          <div className="max-w-sm mx-auto mt-10 px-4">
            <div className="rounded-[32px] border border-white/10 bg-[#050816] p-5 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-black font-black">
                    Q
                  </div>
                  <div>
                    <h2 className="font-black text-lg">QalaJob AI</h2>
                    <p className="text-xs text-white/40">AI Resume Assistant</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xl hover:bg-white/10 transition"
                >
                  ✕
                </button>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setLocale("en")}
                  className={`h-12 rounded-xl font-medium transition ${
                    locale === "en"
                      ? "bg-cyan-400 text-black"
                      : "bg-white/5 border border-white/10 text-white/70"
                  }`}
                >
                  EN
                </button>
                <button
                  type="button"
                  onClick={() => setLocale("ru")}
                  className={`h-12 rounded-xl font-medium transition ${
                    locale === "ru"
                      ? "bg-cyan-400 text-black"
                      : "bg-white/5 border border-white/10 text-white/70"
                  }`}
                >
                  RU
                </button>
                <button
                  type="button"
                  onClick={() => setLocale("kk")}
                  className={`h-12 rounded-xl font-medium transition ${
                    locale === "kk"
                      ? "bg-cyan-400 text-black"
                      : "bg-white/5 border border-white/10 text-white/70"
                  }`}
                >
                  KK
                </button>
              </div>

              <div className="mt-6 flex flex-col gap-3">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button className="w-full h-12 rounded-xl bg-cyan-400 text-black hover:bg-cyan-300">
                    {t.navbar.login}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
