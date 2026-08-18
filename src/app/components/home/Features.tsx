"use client";

import { motion } from "motion/react";

import { useLanguage } from "@/context/LanguageContext";
import { getMessages } from "@/lib/i18n";

const features = [
  {
    icon: "📄",
    color: "from-cyan-400 to-blue-500",
  },
  {
    icon: "✉️",
    color: "from-purple-400 to-pink-500",
  },
  {
    icon: "🎙️",
    color: "from-cyan-400 to-teal-500",
  },
  {
    icon: "🎯",
    color: "from-green-400 to-emerald-500",
  },
];

export default function Features() {

  const { locale } = useLanguage();

  const t = getMessages(locale);

  const featureData = [
    {
      title: t.featuresSection.feature1Title,
      description: t.featuresSection.feature1Desc,
      icon: features[0].icon,
      color: features[0].color,
    },
    {
      title: t.featuresSection.feature2Title,
      description: t.featuresSection.feature2Desc,
      icon: features[1].icon,
      color: features[1].color,
    },
    {
      title: t.featuresSection.feature3Title,
      description: t.featuresSection.feature3Desc,
      icon: features[2].icon,
      color: features[2].color,
    },
    {
      title: t.featuresSection.feature4Title,
      description: t.featuresSection.feature4Desc,
      icon: features[3].icon,
      color: features[3].color,
    },
  ];

  return (
    <section className="relative py-32 overflow-hidden">

      {/* BACKGROUND */}
      <div className="absolute inset-0">

        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.08),transparent_40%)]" />

      </div>

      <div className="container-custom relative z-10">

        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >

          {/* BADGE */}
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-5 py-2 text-sm text-cyan-300 mb-6 backdrop-blur-xl">

            {t.featuresSection.badge}

          </div>

          {/* TITLE */}
          <h2 className="text-5xl md:text-7xl font-black leading-[0.95] tracking-tight">

            {t.featuresSection.title1}

            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

              {t.featuresSection.title2}

            </span>

          </h2>

          {/* DESCRIPTION */}
          <p className="mt-8 text-xl text-white/60 max-w-3xl mx-auto leading-relaxed">

            {t.featuresSection.description}

          </p>

        </motion.div>

        {/* FEATURES GRID */}
        <div className="grid md:grid-cols-2 gap-8">

          {featureData.map((feature, index) => (

            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 60 }}
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
              className="group relative overflow-hidden rounded-[36px] border border-white/10 bg-white/[0.03] backdrop-blur-2xl p-8"
            >

              {/* HOVER GLOW */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition duration-500 bg-cyan-400/5" />

              {/* ICON */}
              <div className={`relative z-10 w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-3xl shadow-[0_0_40px_rgba(34,211,238,0.25)]`}>

                {feature.icon}

              </div>

              {/* TITLE */}
              <h3 className="relative z-10 mt-8 text-2xl font-black">

                {feature.title}

              </h3>

              {/* DESCRIPTION */}
              <p className="relative z-10 mt-5 text-white/60 leading-relaxed text-lg">

                {feature.description}

              </p>

              {/* BOTTOM LINE */}
              <div className="relative z-10 mt-10 h-[2px] rounded-full bg-white/10 overflow-hidden">

                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: "100%" }}
                  transition={{
                    duration: 1,
                    delay: index * 0.15,
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