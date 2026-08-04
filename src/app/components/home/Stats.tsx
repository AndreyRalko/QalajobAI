"use client";

import { motion } from "motion/react";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function Stats() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  const stats = [
    {
      value: "5000+",
      label: t.stats.students,
      description: t.statsDescriptions.students,
      icon: "🎓",
    },
    {
      value: "1200+",
      label: t.stats.vacancies,
      description: t.statsDescriptions.vacancies,
      icon: "💼",
    },
    {
      value: "300+",
      label: t.stats.companies,
      description: t.statsDescriptions.companies,
      icon: "🚀",
    },
    {
      value: "92%",
      label: t.stats.ai,
      description: t.statsDescriptions.ai,
      icon: "🧠",
    },
  ];

  return (
    <section className="relative py-32 overflow-hidden">

      {/* BACKGROUND GLOW */}
      <div className="absolute inset-0 overflow-hidden">

        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[900px] bg-cyan-500/10 blur-[180px]" />

      </div>

      <div className="container-custom relative z-10">

        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >

          {/* BADGE */}
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-6 backdrop-blur-xl">

            {t.statsSection.badge}

          </div>

          {/* TITLE */}
          <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-tight">

            {t.statsSection.title1}

            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

              {t.statsSection.title2}

            </span>

          </h2>

          {/* DESCRIPTION */}
          <p className="mt-8 text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">

            {t.statsSection.description}

          </p>

        </motion.div>

        {/* STATS GRID */}
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-8">

          {stats.map((item, index) => (

            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 80 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.8,
                delay: index * 0.1,
              }}
              viewport={{ once: true }}
              whileHover={{
                y: -10,
                scale: 1.02,
              }}
              className="group relative overflow-hidden glass-card rounded-[36px] p-8"
            >

              {/* HOVER GLOW */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition duration-500 bg-cyan-400/5" />

              {/* ICON */}
              <div className="relative z-10 w-16 h-16 rounded-2xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-3xl mb-8">

                {item.icon}

              </div>

              {/* VALUE */}
              <h3 className="relative z-10 text-6xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

                {item.value}

              </h3>

              {/* LABEL */}
              <h4 className="relative z-10 mt-5 text-2xl font-bold">

                {item.label}

              </h4>

              {/* DESCRIPTION */}
              <p className="relative z-10 mt-5 text-white/60 leading-relaxed">

                {item.description}

              </p>

              {/* BOTTOM LINE */}
              <div className="relative z-10 mt-10 h-[2px] rounded-full bg-white/10 overflow-hidden">

                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: "100%" }}
                  transition={{
                    duration: 1,
                    delay: index * 0.2,
                  }}
                  viewport={{ once: true }}
                  className="h-full bg-cyan-400"
                />

              </div>

            </motion.div>

          ))}

        </div>

      </div>

    </section>
  );
}