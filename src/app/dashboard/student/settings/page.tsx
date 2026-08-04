"use client";

import { useState, useEffect } from "react";

import { useTranslations } from "@/hooks/useTranslations";

import {
  getMe,
  setLanguageApi,
  changePassword,
  deleteAccount,
} from "@/lib/api";

import { logoutUser } from "@/lib/auth";

export default function StudentSettingsPage() {
  const { t } = useTranslations();
  const [language, setLanguage] =
  useState("kk");

  const [notifications, setNotifications] =
    useState({
      vacancies: true,
      interviews: true,
      applications: true,
      ai: true,
    });

    const [currentPassword, setCurrentPassword] =
  useState("");

const [newPassword, setNewPassword] =
  useState("");

const [confirmPassword, setConfirmPassword] =
  useState("");

useEffect(() => {
  const loadProfile = async () => {
    try {
      const user = await getMe();

      if (user.language) {
        setLanguage(user.language);
      }
    } catch (error) {
      console.error(error);
    }
  };

  loadProfile();
}, []);

const saveLanguage = async () => {
  try {
    await setLanguageApi(language);

    alert(t("studentSettings.languageSaved"));
  } catch (error) {
    console.error(error);

    alert(t("studentSettings.languageFailed"));
  }
};

  

const saveNotifications = async () => {
  try {
    localStorage.setItem(
      "qalajob-notifications",
      JSON.stringify(notifications)
    );

    alert(t("studentSettings.notificationsSaved"));
  } catch (error) {
    console.error(error);

    alert(t("studentSettings.notificationsFailed"));
  }
};

const handleLogout = async () => {
  await logoutUser();

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
          t("studentSettings.passwordMismatch")
        );

        return;
      }

      if (
        newPassword.length < 6
      ) {

        alert(
          t("studentSettings.passwordTooShort")
        );

        return;
      }

      await changePassword(
  currentPassword,
  newPassword
);

alert(
  t("studentSettings.passwordChanged")
);

setCurrentPassword("");
setNewPassword("");
setConfirmPassword("");

    } catch (error) {

      console.error(error);

      alert(
        t("studentSettings.passwordFailed")
      );

    }

  };

const handleDeleteAccount = async () => {
  const confirmDelete = confirm(
    t("studentSettings.deleteConfirm")
  );

  if (!confirmDelete) {
    return;
  }

  try {
    await deleteAccount();

    await logoutUser();

    alert(
      t("studentSettings.accountDeleted")
    );

    window.location.href = "/";
  } catch (error) {
    console.error(error);

    alert(
      t("studentSettings.accountDeleteFailed")
    );
  }
};
  return (
    <div className="p-6 md:p-10">
        <h1 className="text-5xl font-black">
          {t("studentSettings.title")}
        </h1>

        <div className="mt-10 space-y-6">

          {/* LANGUAGE */}

          <div className="rounded-3xl border border-white/10 p-6">

            <h3 className="font-bold text-xl">
              {t("studentSettings.language")}
            </h3>

            <p className="text-white/50 mt-1">
              {t("studentSettings.languageDescription")}
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
              <option value="kk">
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
              {t("studentSettings.saveLanguage")}
            </button>

          </div>

          {/* NOTIFICATIONS */}

          <div className="rounded-3xl border border-white/10 p-6">

            <h3 className="font-bold text-xl">
              {t("studentSettings.notifications")}
            </h3>

            <div className="mt-5 space-y-4">

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={
                    notifications.vacancies
                  }
                  onChange={() =>
                    setNotifications({
                      ...notifications,
                      vacancies:
                        !notifications.vacancies,
                    })
                  }
                />
                {t("studentSettings.vacancies")}
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={
                    notifications.interviews
                  }
                  onChange={() =>
                    setNotifications({
                      ...notifications,
                      interviews:
                        !notifications.interviews,
                    })
                  }
                />
                {t("studentSettings.interviews")}
              </label>

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
                {t("studentSettings.applicationUpdates")}
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={
                    notifications.ai
                  }
                  onChange={() =>
                    setNotifications({
                      ...notifications,
                      ai:
                        !notifications.ai,
                    })
                  }
                />
                {t("studentSettings.aiRecommendations")}
              </label>

            </div>

            <button
              onClick={
                saveNotifications
              }
              className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
            >
              {t("studentSettings.saveNotifications")}
            </button>

          </div>


          {/* SECURITY */}

          <div className="rounded-3xl border border-white/10 p-6">

            <h3 className="font-bold text-xl">
              {t("studentSettings.security")}
            </h3>

            <p className="text-white/50 mt-1">
              {t("studentSettings.passwordSettings")}
            </p>

            <input
  type="password"
  value={currentPassword}
  onChange={(e) =>
    setCurrentPassword(
      e.target.value
    )
  }
  placeholder={t("studentSettings.currentPassword")}
  className="mt-5 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

            <input
  type="password"
  value={newPassword}
  onChange={(e) =>
    setNewPassword(
      e.target.value
    )
  }
  placeholder={t("studentSettings.newPassword")}
  className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

            <input
  type="password"
  value={confirmPassword}
  onChange={(e) =>
    setConfirmPassword(
      e.target.value
    )
  }
  placeholder={t("studentSettings.confirmPassword")}
  className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10"
/>

            <button
  onClick={
    handleChangePassword
  }
  className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
>
  {t("studentSettings.changePassword")}
</button>

          </div>

          {/* ACCOUNT */}

          <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-6">

            <h3 className="font-bold text-xl text-red-400">
              {t("studentSettings.account")}
            </h3>

            <div className="mt-5 flex gap-4">

              <button
                onClick={
                  handleLogout
                }
                className="px-6 py-3 rounded-2xl bg-white/10"
              >
                {t("studentSettings.logout")}
              </button>

              <button
  onClick={
    handleDeleteAccount
  }
  className="px-6 py-3 rounded-2xl bg-red-600 font-bold"
>
  {t("studentSettings.deleteAccount")}
</button>

            </div>

          </div>

        </div>
    </div>
  );
}