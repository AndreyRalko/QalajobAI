"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import { changePassword } from "@/lib/api";

export default function StudentSettingsPage() {
  const { t } = useTranslations();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      alert(t("studentSettings.passwordMismatch"));
      return;
    }

    if (newPassword.length < 6) {
      alert(t("studentSettings.passwordTooShort"));
      return;
    }

    setSaving(true);
    try {
      await changePassword(currentPassword, newPassword);
      alert(t("studentSettings.passwordChanged"));
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      console.error(error);
      alert(t("studentSettings.passwordFailed"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 md:p-10">
      <h1 className="text-5xl font-black">{t("studentSettings.title")}</h1>

      <div className="mt-10 max-w-xl rounded-3xl border border-white/10 p-6">
        <h3 className="font-bold text-xl">{t("studentSettings.security")}</h3>
        <p className="text-white/50 mt-1">{t("studentSettings.passwordSettings")}</p>

        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          placeholder={t("studentSettings.currentPassword")}
          className="mt-5 w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder={t("studentSettings.newPassword")}
          className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder={t("studentSettings.confirmPassword")}
          className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <button
          type="button"
          onClick={() => void handleChangePassword()}
          disabled={
            saving ||
            !currentPassword ||
            !newPassword ||
            !confirmPassword
          }
          className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold disabled:opacity-50"
        >
          {t("studentSettings.changePassword")}
        </button>
      </div>
    </div>
  );
}
