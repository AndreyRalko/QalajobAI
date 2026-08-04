"use client";

import { motion } from "motion/react";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

const companies = [
  {
    name: "Google",
    logo: "🌐",
  },
  {
    name: "Microsoft",
    logo: "💻",
  },
  {
    name: "Tesla",
    logo: "⚡",
  },
  {
    name: "Kaspi",
    logo: "🏦",
  },
  {
    name: "Kolesa",
    logo: "🚗",
  },
  {
    name: "Freedom",
    logo: "📈",
  },
];

export default function Companies() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  return (
    <section className="relative py-32 overflow-hidden">

      {/* BACKGROUND */}
      <div className="absolute inset-0 overflow-hidden">

        <div className="absolute bottom-[-200px] left-1/2 -translate-x-1/2 w-[1000px] h-[1000px] bg-cyan-500/10 blur-[220px]" />

      </div>

      <div className="container-custom relative z-10">

        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-24"
        >

          {/* BADGE */}
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-6 backdrop-blur-xl">

            {t.companiesSection.badge}

          </div>

          {/* TITLE */}
          <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-tight">

            {t.companiesSection.title1}

            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

              {t.companiesSection.title2}

            </span>

          </h2>

          {/* DESCRIPTION */}
          <p className="mt-8 text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">

            {t.companiesSection.description}

          </p>

        </motion.div>

        {/* COMPANIES GRID */}
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-6">

          {companies.map((company, index) => (

            <motion.div
              key={company.name}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7,
                delay: index * 0.1,
              }}
              viewport={{ once: true }}
              whileHover={{
                y: -8,
                scale: 1.03,
              }}
              className="group relative overflow-hidden rounded-[30px] border border-white/10 bg-white/[0.03] backdrop-blur-2xl p-8 flex flex-col items-center justify-center text-center"
            >

              {/* GLOW */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition duration-500 bg-cyan-400/5" />

              {/* LOGO */}
              <div className="relative z-10 w-20 h-20 rounded-3xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-4xl shadow-[0_0_50px_rgba(34,211,238,0.35)]">

                {company.logo}

              </div>

              {/* NAME */}
              <h3 className="relative z-10 mt-6 text-2xl font-black">

                {company.name}

              </h3>

              {/* STATUS */}
              <p className="relative z-10 mt-3 text-white/50 text-sm">

                {t.hiringNow}

              </p>

            </motion.div>

          ))}

        </div>

      </div>

    </section>
  );
}