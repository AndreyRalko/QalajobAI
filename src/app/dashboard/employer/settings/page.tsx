"use client";

import { useState, useEffect } from "react";

import { useTranslations } from "@/hooks/useTranslations";

import {
  getMe,
  setLanguageApi,
  changePassword,
  deleteAccount,
} from "@/lib/api";

export default function EmployerSettingsPage() {
const { t } = useTranslations();
const [language, setLanguage] =
useState("kz");



const [currentPassword, setCurrentPassword] =
  useState("");

const [newPassword, setNewPassword] =
  useState("");

const [confirmPassword, setConfirmPassword] =
  useState("");

const [notifications, setNotifications] =
  useState({
    applications: true,
    vacancyUpdates: true,
    analytics: true,
    aiCandidates: true,
  });


useEffect(() => {
  const loadSettings = async () => {
    try {
      const user = await getMe();

      setLanguage(
        user.language || "kz"
      );
    } catch (error) {
      console.error(error);
    }
  };

  loadSettings();
}, []);


const saveLanguage = async () => {
  try {
    await setLanguageApi(language);

    alert(t("employerSettings.languageSaved"));
  } catch (error) {
    console.error(error);
  }
};
const handleLogout = async () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");

  window.location.href = "/";
};
const handleChangePassword =
  async () => {
    try {

      if (
        newPassword !==
        confirmPassword
      ) {
        alert(
          t("employerSettings.passwordMismatch")
        );
        return;
      }

      await changePassword(
        currentPassword,
        newPassword
      );

      alert(
        t("employerSettings.passwordChanged")
      );

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

    } catch (error) {
      console.error(error);

      alert(
        t("employerSettings.passwordFailed")
      );
    }
  };

const handleDeleteAccount = async () => {
  try {
    const confirmDelete = confirm(
      t("employerSettings.deleteConfirm")
    );

    if (!confirmDelete) return;

    await deleteAccount();

    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    window.location.href = "/";
  } catch (error) {
    console.error(error);
    alert(t("employerSettings.accountDeleteFailed"));
  }
};

      

return ( <div className="p-8 text-white">

  <h1 className="text-4xl font-black">
    {t("employerSettings.title")}
  </h1>

  <div className="mt-10 space-y-6">

    <div className="rounded-3xl border border-white/10 p-6">

      <h3 className="font-bold text-xl">
        🌍 {t("employerSettings.language")}
      </h3>

      <p className="text-white/50 mt-1">
        {t("employerSettings.languageDescription")}
      </p>

      <select
        value={language}
        onChange={(e) =>
          setLanguage(
            e.target.value
          )
        }
        className="mt-5 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
      >
        <option value="kz">
          🇰🇿 Қазақша
        </option>

        <option value="ru">
          🇷🇺 Русский
        </option>

        <option value="en">
          🇺🇸 English
        </option>
      </select>

      <button
        onClick={
          saveLanguage
        }
        className="mt-4 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
      >
        {t("employerSettings.saveLanguage")}
      </button>

    </div>

    <div className="rounded-3xl border border-white/10 p-6">

      <h3 className="font-bold text-xl">
        🔔 {t("employerSettings.notifications")}
      </h3>

      <div className="mt-5 space-y-4">

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={
              notifications.applications
            }
            onChange={() =>
              setNotifications({
                ...notifications,
                applications:
                  !notifications.applications,
              })
            }
          />
          {t("employerSettings.newApplications")}
        </label>

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={
              notifications.vacancyUpdates
            }
            onChange={() =>
              setNotifications({
                ...notifications,
                vacancyUpdates:
                  !notifications.vacancyUpdates,
              })
            }
          />
          {t("employerSettings.vacancyUpdates")}
        </label>

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={
              notifications.analytics
            }
            onChange={() =>
              setNotifications({
                ...notifications,
                analytics:
                  !notifications.analytics,
              })
            }
          />
          {t("employerSettings.analyticsReports")}
        </label>

        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={
              notifications.aiCandidates
            }
            onChange={() =>
              setNotifications({
                ...notifications,
                aiCandidates:
                  !notifications.aiCandidates,
              })
            }
          />
          {t("employerSettings.aiCandidateRecommendations")}
        </label>

      </div>

      <button
       onClick={() => alert(t("employerSettings.notificationsSaved"))}
        className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
      >
        {t("employerSettings.saveNotifications")}
      </button>

    </div>

    <div className="rounded-3xl border border-white/10 p-6">

      <h3 className="font-bold text-xl">
        🔐 {t("employerSettings.security")}
      </h3>

      <p className="text-white/50 mt-1">
        {t("employerSettings.passwordSettings")}
      </p>

      <input
  type="password"
  placeholder={t("employerSettings.currentPassword")}
  value={currentPassword}
  onChange={(e) =>
    setCurrentPassword(
      e.target.value
    )
  }
  className="mt-5 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

      <input
  type="password"
  placeholder={t("employerSettings.newPassword")}
  value={newPassword}
  onChange={(e) =>
    setNewPassword(
      e.target.value
    )
  }
  className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

      <input
  type="password"
  placeholder={t("employerSettings.confirmPassword")}
  value={confirmPassword}
  onChange={(e) =>
    setConfirmPassword(
      e.target.value
    )
  }
  className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

      <button
  onClick={
    handleChangePassword
  }
  className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
>
  {t("employerSettings.changePassword")}
</button>

    </div>

    <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-6">

      <h3 className="font-bold text-xl text-red-400">
        🚨 {t("employerSettings.account")}
      </h3>

      <div className="mt-5 flex gap-4">

        <button
          onClick={
            handleLogout
          }
          className="px-6 py-3 rounded-2xl bg-white/10"
        >
          {t("employerSettings.logout")}
        </button>

        <button
  onClick={
    handleDeleteAccount
  }
  className="px-6 py-3 rounded-2xl bg-red-600 font-bold"
>
  {t("employerSettings.deleteAccount")}
</button>

      </div>

    </div>

  </div>

</div>

);
}
