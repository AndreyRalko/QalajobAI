"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";

export default function AboutPage() {
  const router = useRouter();
  const { t } = useTranslations();

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      <section className="max-w-7xl mx-auto px-6 py-20">

        <button
          onClick={() => router.back()}
          className="mb-10 px-5 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition"
        >
          ← {t("errors.goBack")}
        </button>

        <div className="text-center">
          <h1 className="text-6xl font-black">
            {t("aboutPage.title")}
          </h1>
          <p className="mt-6 text-xl text-white/60 max-w-3xl mx-auto">
            {t("aboutPage.subtitle")}
          </p>
        </div>

        <div className="mt-24 rounded-3xl bg-white/5 border border-white/10 p-10">
          <h2 className="text-3xl font-bold">{t("aboutPage.mission")}</h2>
          <p className="mt-5 text-white/70 leading-8">{t("aboutPage.missionDesc")}</p>
        </div>

        <div className="mt-12 rounded-3xl bg-white/5 border border-white/10 p-10">
          <h2 className="text-3xl font-bold">{t("aboutPage.whyTitle")}</h2>
          <p className="mt-4 text-white/70 leading-7 max-w-3xl">{t("aboutPage.whyDesc")}</p>
          <div className="grid md:grid-cols-3 gap-6 mt-6">
            <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
              <h4 className="font-bold text-xl">{t("aboutPage.reason1Title")}</h4>
              <p className="mt-2 text-white/60">{t("aboutPage.reason1Desc")}</p>
            </div>
            <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
              <h4 className="font-bold text-xl">{t("aboutPage.reason2Title")}</h4>
              <p className="mt-2 text-white/60">{t("aboutPage.reason2Desc")}</p>
            </div>
            <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
              <h4 className="font-bold text-xl">{t("aboutPage.reason3Title")}</h4>
              <p className="mt-2 text-white/60">{t("aboutPage.reason3Desc")}</p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="rounded-3xl bg-white/5 border border-white/10 p-8">
            <h3 className="text-2xl font-bold">{t("aboutPage.feature1Title")}</h3>
            <p className="mt-3 text-white/60">{t("aboutPage.feature1Desc")}</p>
          </div>
          <div className="rounded-3xl bg-white/5 border border-white/10 p-8">
            <h3 className="text-2xl font-bold">{t("aboutPage.feature2Title")}</h3>
            <p className="mt-3 text-white/60">{t("aboutPage.feature2Desc")}</p>
          </div>
          <div className="rounded-3xl bg-white/5 border border-white/10 p-8">
            <h3 className="text-2xl font-bold">{t("aboutPage.feature3Title")}</h3>
            <p className="mt-3 text-white/60">{t("aboutPage.feature3Desc")}</p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6 mt-20">
          {[
            { value: "100+", key: "statStudents" },
            { value: "50+", key: "statVacancies" },
            { value: "20+", key: "statCompanies" },
            { value: "AI", key: "statPowered" },
          ].map((stat) => (
            <div key={stat.key} className="rounded-3xl bg-cyan-500/10 border border-cyan-500/20 p-8 text-center">
              <h3 className="text-4xl font-black text-cyan-400">{stat.value}</h3>
              <p className="mt-2 text-white/60">{t(`aboutPage.${stat.key}`)}</p>
            </div>
          ))}
        </div>

        <div className="mt-24">
          <h2 className="text-4xl font-bold text-center">{t("aboutPage.howTitle")}</h2>
          <div className="grid md:grid-cols-3 gap-6 mt-10">
            {[1, 2, 3].map((step) => (
              <div key={step} className="rounded-3xl bg-white/5 border border-white/10 p-8">
                <h3 className="font-bold text-xl">{t(`aboutPage.step${step}Title`)}</h3>
                <p className="mt-3 text-white/60">{t(`aboutPage.step${step}Desc`)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-24 rounded-3xl bg-white/5 border border-white/10 p-10">
          <h2 className="text-3xl font-bold text-center">{t("aboutPage.teamTitle")}</h2>
          <div className="mt-8 grid md:grid-cols-3 gap-6 items-center">
            <div className="md:col-span-1 text-center">
              <img src="/file.svg" alt="Founder" className="mx-auto w-28 h-28 rounded-full bg-white/5 p-3" />
              <h3 className="mt-4 font-bold">{t("aboutPage.founderName")}</h3>
              <p className="text-white/60 mt-1">{t("aboutPage.founderRole")}</p>
            </div>
            <div className="md:col-span-2">
              <p className="text-white/70 leading-7">{t("aboutPage.founderDesc")}</p>
              <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="rounded-2xl bg-white/5 border border-white/10 p-4 text-center">
                    <p className="font-bold">{t(`aboutPage.teamRole${i}`)}</p>
                    <p className="text-white/60 text-sm mt-1">{t(`aboutPage.teamRole${i}Desc`)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-24 text-center rounded-3xl bg-cyan-500/10 border border-cyan-500/20 p-14">
          <h2 className="text-4xl font-black">{t("aboutPage.ctaTitle")}</h2>
          <p className="mt-4 text-white/60">{t("aboutPage.ctaDesc")}</p>
          <div className="mt-8 flex justify-center gap-4">
            <button
              onClick={() => router.push("/login")}
              className="px-8 py-4 rounded-2xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition"
            >
              {t("aboutPage.ctaButton")}
            </button>
            <button
              onClick={() => router.push("/contact")}
              className="px-8 py-4 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition"
            >
              {t("aboutPage.ctaContact")}
            </button>
          </div>
        </div>

      </section>
    </main>
  );
}