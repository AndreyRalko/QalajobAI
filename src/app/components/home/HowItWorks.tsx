"use client";

import { motion } from "motion/react";
import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

export default function HowItWorks() {
  const { locale } = useLanguage();
  const t = getMessages(locale);

  const steps = [
    {
      number: "01",
      title: t.howSection.step1Title,
      description: t.howSection.step1Desc,
      icon: "🔑",
    },
    {
      number: "02",
      title: t.howSection.step2Title,
      description: t.howSection.step2Desc,
      icon: "📄",
    },
    {
      number: "03",
      title: t.howSection.step3Title,
      description: t.howSection.step3Desc,
      icon: "🎯",
    },
    {
      number: "04",
      title: t.howSection.step4Title,
      description: t.howSection.step4Desc,
      icon: "🎙️",
    },
  ];

  return (
    <section id="how-it-works" className="relative py-32 overflow-hidden scroll-mt-24">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[1000px] bg-cyan-500/10 blur-[200px]" />
      </div>

      <div className="container-custom relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-24"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-6 backdrop-blur-xl">
            {t.howSection.badge}
          </div>

          <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-tight">
            {t.howSection.title}
          </h2>

          <p className="mt-6 text-xl text-white/50 max-w-2xl mx-auto">
            {t.howSection.description}
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="rounded-[32px] border border-white/10 bg-white/[0.03] p-8"
            >
              <div className="text-4xl mb-4">{step.icon}</div>
              <p className="text-cyan-400 font-bold mb-2">{step.number}</p>
              <h3 className="text-2xl font-black">{step.title}</h3>
              <p className="mt-3 text-white/50">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
