"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/app/components/ui/button";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function Hero() {
  const { locale } = useLanguage();
  const t = getMessages(locale);

  const stats = [
    ["AI", t.stats.ai],
    ["hh.kz", t.stats.hh],
    ["PDF", t.stats.pdf],
  ];

  return (
    <section className="relative overflow-hidden min-h-[85vh] flex items-center grid-bg pt-20">

      {/* BACKGROUND */}
      <div className="absolute inset-0 overflow-hidden">

        <div className="absolute top-[-250px] left-1/2 -translate-x-1/2 w-[900px] h-[900px] bg-cyan-500/20 blur-[180px]" />

        <div className="absolute bottom-[-200px] right-[-100px] w-[500px] h-[500px] bg-purple-500/20 blur-[160px]" />

      </div>

      <div className="container-custom relative z-10">

        <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-8 xl:gap-12 items-center">

          {/* LEFT */}
          <motion.div
            initial={{ opacity: 0, y: 80 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
          >

            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-8 backdrop-blur-xl">

              {t.hero.badge}

            </div>

            <h1
              className="
              text-4xl
              sm:text-5xl
              md:text-6xl
              lg:text-7xl
              xl:text-[5rem]
              2xl:text-[5.5rem]
              font-black
              leading-[0.9]
              tracking-[-0.03em]
              max-w-[700px]
              "
            >

              {t.hero.title1}

              <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

                {t.hero.title2}

              </span>

              {t.hero.title3}

            </h1>

            <p className="mt-8 text-lg md:text-xl text-white/60 leading-relaxed max-w-xl">

              {t.hero.description}

            </p>

            <div className="mt-10 flex flex-wrap gap-4">

              <Link href="/login">
                <Button className="h-14 px-8 rounded-2xl bg-cyan-400 text-black hover:bg-cyan-300 text-lg font-semibold">
                  {t.hero.start}
                </Button>
              </Link>

              <Link href="#how-it-works">
                <Button
                  variant="outline"
                  className="h-14 px-8 rounded-2xl border-white/10 bg-white/5 backdrop-blur-xl hover:bg-white/10"
                >
                  {t.hero.explore}
                </Button>
              </Link>

            </div>

            {/* STATS */}
            <div className="mt-12 flex flex-wrap gap-4">

              {stats.map((item) => (

                <div
                  key={item[1]}
                  className="glass-card rounded-3xl px-6 py-5 min-w-[140px]"
                >

                  <h3 className="text-3xl font-black text-cyan-400">

                    {item[0]}

                  </h3>

                  <p className="text-white/50 text-sm mt-1">

                    {item[1]}

                  </p>

                </div>

              ))}

            </div>

          </motion.div>

          {/* RIGHT */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1 }}
            className="hidden lg:flex justify-center"
          >

            <div className="relative w-[450px] h-[450px]">

              {/* CENTER ORB */}
              <div className="absolute inset-0 flex items-center justify-center">

                <div className="relative">

                  <div className="absolute inset-0 bg-cyan-500/30 blur-[100px] rounded-full" />

                  <div className="w-28 h-28 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-4xl">

                    🧠

                  </div>

                </div>

              </div>

              {/* CARD 1 */}
              <motion.div
                animate={{ y: [0, -15, 0] }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                }}
                className="absolute top-10 left-0 w-[260px] glass-card rounded-[28px] p-6"
              >

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-white/40 text-sm">
                      {t.hero.card1Label}
                    </p>

                    <h3 className="mt-2 text-2xl font-black leading-tight">
                      {t.hero.card1Value}
                    </h3>

                  </div>

                  <div className="w-12 h-12 rounded-xl bg-cyan-400/20 flex items-center justify-center text-xl">

                    📄

                  </div>

                </div>

                <div className="mt-5 h-2 rounded-full bg-white/10 overflow-hidden">

                  <div className="h-full w-[88%] bg-cyan-400 rounded-full" />

                </div>

              </motion.div>

              {/* CARD 2 */}
              <motion.div
                animate={{ y: [0, 15, 0] }}
                transition={{
                  duration: 5,
                  repeat: Infinity,
                }}
                className="absolute bottom-10 right-0 w-[260px] glass-card rounded-[28px] p-6"
              >

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-white/40 text-sm">
                      {t.hero.card2Label}
                    </p>

                    <h3 className="mt-2 text-2xl font-black leading-tight">
                      {t.hero.card2Value}
                    </h3>

                  </div>

                  <div className="w-12 h-12 rounded-xl bg-pink-400/20 flex items-center justify-center text-xl">

                    🎯

                  </div>

                </div>

                <div className="mt-5 h-2 rounded-full bg-white/10 overflow-hidden">

                  <div className="h-full w-[80%] bg-cyan-400 rounded-full" />

                </div>

              </motion.div>

            </div>

          </motion.div>

        </div>

      </div>

    </section>
  );
}