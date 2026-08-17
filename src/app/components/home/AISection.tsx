"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/app/components/ui/button";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function AISection() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  const messages = [
    {
      role: "user",
      text: t.aiSection.msg1,
    },
    {
      role: "ai",
      text: t.aiSection.msg2,
    },
    {
      role: "user",
      text: t.aiSection.msg3,
    },
    {
      role: "ai",
      text: t.aiSection.msg4,
    },
  ];

  const features = [
    t.aiSection.feature1,
    t.aiSection.feature2,
    t.aiSection.feature3,
    t.aiSection.feature4,
    t.aiSection.feature5,
  ];

  return (
    <section className="relative py-40 overflow-hidden">

      <div className="absolute inset-0 overflow-hidden">

        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] bg-cyan-500/10 blur-[220px]" />

        <div className="absolute bottom-0 right-0 w-[700px] h-[700px] bg-purple-500/10 blur-[200px]" />

      </div>

      <div className="container-custom relative z-10">

        <div className="grid lg:grid-cols-2 gap-20 items-center">

          {/* LEFT */}
          <motion.div
            initial={{ opacity: 0, x: -80 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.9 }}
            viewport={{ once: true }}
          >

            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-8 backdrop-blur-xl">

              {t.aiSection.badge}

            </div>

            <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-tight">

              {t.aiSection.title1}

              <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

                {t.aiSection.title2}

              </span>

            </h2>

            <p className="mt-8 text-xl text-white/60 leading-relaxed max-w-2xl">

              {t.aiSection.description}

            </p>

            <div className="mt-12 space-y-5">

              {features.map((item) => (

                <div
                  key={item}
                  className="flex items-center gap-4"
                >

                  <div className="w-8 h-8 rounded-full bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400">

                    ✓

                  </div>

                  <span className="text-lg text-white/70">

                    {item}

                  </span>

                </div>

              ))}

            </div>

            <div className="mt-14 flex flex-wrap gap-5">

              <Link href="/login">
                <Button className="h-14 px-8 rounded-2xl bg-cyan-400 text-black hover:bg-cyan-300 text-lg font-semibold shadow-[0_0_50px_rgba(34,211,238,0.4)]">
                  {t.aiSection.button1}
                </Button>
              </Link>

              <Link href="/about">
                <Button
                  variant="outline"
                  className="h-14 px-8 rounded-2xl border-white/10 bg-white/5 backdrop-blur-xl hover:bg-white/10 text-lg"
                >
                  {t.aiSection.button2}
                </Button>
              </Link>

            </div>

          </motion.div>

          {/* RIGHT */}
          <motion.div
            initial={{ opacity: 0, x: 80 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.9 }}
            viewport={{ once: true }}
            className="relative"
          >

            <div className="glass-card rounded-[40px] p-8 overflow-hidden relative">

              <div className="flex items-center gap-3 pb-6 border-b border-white/10">

                <div className="flex gap-2">

                  <div className="w-3 h-3 rounded-full bg-red-400" />

                  <div className="w-3 h-3 rounded-full bg-yellow-400" />

                  <div className="w-3 h-3 rounded-full bg-green-400" />

                </div>

                <p className="text-white/40 text-sm ml-4">

                  {t.aiSection.chatTitle}

                </p>

              </div>

              <div className="mt-8 space-y-6">

                {messages.map((message, index) => (

                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{
                      duration: 0.6,
                      delay: index * 0.15,
                    }}
                    viewport={{ once: true }}
                    className={`flex ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >

                    <div
                      className={`max-w-[85%] rounded-3xl px-6 py-5 text-lg leading-relaxed ${
                        message.role === "user"
                          ? "bg-cyan-400 text-black font-medium"
                          : "bg-white/5 border border-white/10 text-white/80"
                      }`}
                    >

                      {message.text}

                    </div>

                  </motion.div>

                ))}

              </div>

              <div className="mt-8 flex items-center gap-4 rounded-3xl border border-white/10 bg-white/5 p-4">

                <input
                  type="text"
                  placeholder={t.aiSection.placeholder}
                  className="bg-transparent outline-none w-full text-white placeholder:text-white/30"
                />

                <button className="w-12 h-12 rounded-2xl bg-cyan-400 text-black text-xl font-bold shadow-[0_0_30px_rgba(34,211,238,0.4)]">

                  ↑

                </button>

              </div>

            </div>

            <div className="absolute -top-10 -right-10 w-40 h-40 bg-cyan-500/20 blur-[100px]" />

          </motion.div>

        </div>

      </div>

    </section>
  );
}