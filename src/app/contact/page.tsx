"use client";

import { useTranslations } from "@/hooks/useTranslations";

export default function ContactPage() {
  const { t } = useTranslations();

  return (
    <main className="min-h-screen bg-[#030712] text-white">
      <section className="max-w-7xl mx-auto px-6 py-20">

        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-black">
            {t("contactPage.title")}
          </h1>
          <p className="mt-6 text-white/60 text-lg max-w-2xl mx-auto">
            {t("contactPage.subtitle")}
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-10 mt-20">

          <div className="space-y-6">

            <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
              <h2 className="text-2xl font-bold mb-6">{t("contactPage.contactInfo")}</h2>
              <div className="space-y-5">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 flex items-center justify-center">📧</div>
                  <div>
                    <p className="text-white/50 text-sm">{t("contactPage.email")}</p>
                    <p>support@qalajob.ai</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center">📞</div>
                  <div>
                    <p className="text-white/50 text-sm">{t("contactPage.phone")}</p>
                    <p>+7 777 123 45 67</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-green-500/20 flex items-center justify-center">📍</div>
                  <div>
                    <p className="text-white/50 text-sm">{t("contactPage.location")}</p>
                    <p>{t("contactPage.address")}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
              <h2 className="text-2xl font-bold mb-6">{t("contactPage.socialMedia")}</h2>
              <div className="flex gap-4">
                <a href="https://github.com" target="_blank" className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center hover:bg-white/20 transition">🐙</a>
                <a href="https://linkedin.com" target="_blank" className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center hover:bg-white/20 transition">💼</a>
              </div>
            </div>

          </div>

          <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
            <h2 className="text-3xl font-bold mb-8">{t("contactPage.sendMessage")}</h2>
            <form className="space-y-5">
              <input type="text" placeholder={t("contactPage.yourName")} className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none" />
              <input type="email" placeholder={t("contactPage.emailAddress")} className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none" />
              <input type="text" placeholder={t("contactPage.subject")} className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none" />
              <textarea rows={6} placeholder={t("contactPage.yourMessage")} className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none resize-none" />
              <button type="submit" className="w-full py-4 rounded-2xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition">
                {t("contactPage.sendMessage")}
              </button>
            </form>
          </div>

        </div>

      </section>
    </main>
  );
}