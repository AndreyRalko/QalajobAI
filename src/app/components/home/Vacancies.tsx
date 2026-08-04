"use client";

import Link from "next/link";
import { motion } from "motion/react";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function Vacancies() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  return (
    <section className="relative py-32 overflow-hidden">

      <div className="container-custom">

        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20 flex flex-col lg:flex-row lg:items-end lg:justify-between gap-8"
        >

          <div>

            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-6">

              {t.vacanciesSection.badge}

            </div>

            <h2 className="text-5xl md:text-7xl font-black leading-none">

              {t.vacanciesSection.title1}

              <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

                {t.vacanciesSection.title2}

              </span>

            </h2>

            <p className="mt-6 text-white/60 text-xl max-w-2xl">

              {t.vacanciesSection.description}

            </p>

          </div>

          <Link href="/vacancies">
            <button className="text-cyan-400 hover:text-cyan-300 font-semibold">
              {t.vacanciesSection.viewAll} →
            </button>
          </Link>

        </motion.div>

        {/* CARDS */}
        <div className="grid lg:grid-cols-3 gap-8">

          {(t as { homeVacancies: Array<{ title: string; company: string; salary: string; match: string }> }).homeVacancies.map((job, index) => (

            <motion.div
              key={job.title}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{
                delay: index * 0.15,
              }}
              viewport={{ once: true }}
              whileHover={{
                y: -10,
              }}
              className="rounded-[32px] border border-white/10 bg-white/[0.03] backdrop-blur-xl p-8"
            >

              {/* MATCH */}
              <div className="flex justify-between items-center">

                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center font-black">

                  {job.company[0]}
                </div>

                <div className="rounded-full bg-green-500/10 border border-green-500/20 px-4 py-2 text-green-400 text-sm font-bold">

                  {job.match}

                </div>

              </div>

              {/* TITLE */}
              <h3 className="mt-6 text-2xl font-black">

                {job.title}

              </h3>

              {/* COMPANY */}
              <p className="mt-2 text-white/50">

                {job.company}

              </p>

              {/* SKILLS */}
              <div className="flex flex-wrap gap-2 mt-6">

                <span className="px-3 py-1 rounded-full bg-white/5 text-white/60 text-sm">
                  React
                </span>

                <span className="px-3 py-1 rounded-full bg-white/5 text-white/60 text-sm">
                  TypeScript
                </span>

                <span className="px-3 py-1 rounded-full bg-white/5 text-white/60 text-sm">
                  Tailwind
                </span>

              </div>

              {/* SALARY */}
              <div className="mt-8 flex items-center justify-between">

                <span className="text-cyan-400 font-bold text-lg">

                  {job.salary}

                </span>

                <span className="rounded-full bg-green-500/10 border border-green-500/20 px-3 py-1 text-green-400 text-sm">

                  {t.remote}

                </span>

              </div>

            </motion.div>

          ))}

        </div>

      </div>

    </section>
  );
}