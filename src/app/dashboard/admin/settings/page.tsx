"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { clearSession } from "@/lib/session";
import { saveAdminSettings } from "@/lib/admin";
import { useTranslations } from "@/hooks/useTranslations";

export default function AdminSettingsPage() {
  const { t } = useTranslations();
  const router = useRouter();

  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [registrationEnabled, setRegistrationEnabled] = useState(true);
  const [aiEnabled, setAiEnabled] = useState(true);
  const [language, setLanguage] = useState("en");
  const [saving, setSaving] = useState(false);

  const saveSettings = async () => {
    try {
      setSaving(true);

      await saveAdminSettings({
        maintenanceMode,
        registrationEnabled,
        aiEnabled,
        language,
      });

      alert(t("adminSettings.saved"));
    } catch (error) {
      console.error(error);
      alert(t("adminSettings.failed"));
    } finally {
      setSaving(false);
    }
  };

  const logout = () => {
    clearSession();
    router.replace("/login");
  };

  return (
    <div className="p-8 text-white">
      <h1 className="text-4xl font-black mb-8">
        {t("adminSettings.title")}
      </h1>

      <div className="space-y-6 max-w-2xl">

        <div className="p-6 rounded-3xl bg-white/5 border border-white/10">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="font-bold text-xl">
                {t("adminSettings.maintenanceMode")}
              </h2>

              <p className="text-white/50 mt-1">
                {t("adminSettings.maintenanceDesc")}
              </p>
            </div>

            <input
              type="checkbox"
              checked={maintenanceMode}
              onChange={() =>
                setMaintenanceMode(!maintenanceMode)
              }
              className="w-6 h-6"
            />
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-white/5 border border-white/10">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="font-bold text-xl">
                {t("adminSettings.registration")}
              </h2>

              <p className="text-white/50 mt-1">
                {t("adminSettings.registrationDesc")}
              </p>
            </div>

            <input
              type="checkbox"
              checked={registrationEnabled}
              onChange={() =>
                setRegistrationEnabled(
                  !registrationEnabled
                )
              }
              className="w-6 h-6"
            />
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-white/5 border border-white/10">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="font-bold text-xl">
                {t("adminSettings.aiAssistant")}
              </h2>

              <p className="text-white/50 mt-1">
                {t("adminSettings.aiDesc")}
              </p>
            </div>

            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={() =>
                setAiEnabled(!aiEnabled)
              }
              className="w-6 h-6"
            />
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-white/5 border border-white/10">
          <h2 className="font-bold text-xl">
            {t("adminSettings.language")}
          </h2>

          <p className="text-white/50 mt-1 mb-4">
            {t("adminSettings.languageDesc")}
          </p>

          <select
            value={language}
            onChange={(e) =>
              setLanguage(e.target.value)
            }
            className="
              w-full
              bg-[#030712]
              border
              border-white/10
              rounded-xl
              px-4
              py-3
              outline-none
            "
          >
            <option value="kk">
              🇰🇿 {t("adminSettings.languageKk")}
            </option>

            <option value="ru">
              🇷🇺 {t("adminSettings.languageRu")}
            </option>

            <option value="en">
              🇺🇸 {t("adminSettings.languageEn")}
            </option>
          </select>
        </div>

        <div className="flex gap-4">
          <button
            onClick={saveSettings}
            disabled={saving}
            className="
              px-8
              py-4
              rounded-2xl
              bg-cyan-500
              text-black
              font-bold
              hover:bg-cyan-400
              transition
              disabled:opacity-50
            "
          >
            {saving
              ? t("adminSettings.saving")
              : t("adminSettings.save")}
          </button>

          <button
            onClick={logout}
            className="
              px-8
              py-4
              rounded-2xl
              bg-red-500
              text-white
              font-bold
              hover:bg-red-600
              transition
            "
          >
            {t("adminSettings.logout")}
          </button>
        </div>

      </div>
    </div>
  );
}