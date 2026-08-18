"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/app/components/ui/button";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function CTA() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  return (
    <section className="relative py-40 overflow-hidden">

      <div className="absolute inset-0">

        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-cyan-500/15 blur-[220px]" />

      </div>

      <div className="container-custom relative z-10">

        <motion.div
          initial={{ opacity: 0, y: 80 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="rounded-[48px] border border-white/10 bg-white/[0.03] backdrop-blur-2xl p-12 md:p-20 text-center"
        >

          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-8">

            {t.ctaSection.badge}

          </div>

          <h2 className="text-5xl md:text-8xl font-black leading-none">

            {t.ctaSection.title1}

            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

              {t.ctaSection.title2}

            </span>

          </h2>

          <p className="mt-8 text-xl text-white/60 max-w-3xl mx-auto">

            {t.ctaSection.description}

          </p>

          <div className="mt-12 flex flex-wrap justify-center gap-5">

            <Link href="/login">

              <Button className="h-14 px-8 rounded-2xl bg-cyan-400 text-black hover:bg-cyan-300 text-lg font-semibold">

                {t.ctaSection.button1}

              </Button>

            </Link>

            <Link href="/about">

              <Button
                variant="outline"
                className="h-14 px-8 rounded-2xl border-white/10 bg-white/5"
              >

                {t.ctaSection.button2}

              </Button>

            </Link>

          </div>

        </motion.div>

      </div>

    </section>
  );
}