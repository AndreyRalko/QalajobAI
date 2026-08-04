"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "@/hooks/useTranslations";

import {
  getProfile,
  saveProfile,
} from "@/lib/api";

export default function EmployerProfilePage() {
  const { t } = useTranslations();

  const [fullName, setFullName] =
    useState("");

  const [position, setPosition] =
    useState("");

  const [phone, setPhone] =
    useState("");

  const [bio, setBio] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {

 const loadProfile = async () => {
  try {
    const profile =
      await getProfile();

    setFullName(
      profile.name || ""
    );

    setPosition(
      profile.major || ""
    );

    setPhone(
      profile.phone || ""
    );

    setBio(
      profile.about || ""
    );
  } catch (error) {
    console.error(error);
  }
};

loadProfile();

  }, []);

const handleSaveProfile =
  async () => {

      try {

        setLoading(true);


 await saveProfile({
  name: fullName,
  major: position,
  phone,
  about: bio,
});

        alert(
          t("employerProfile.success")
        );

      } catch (error) {

        console.error(
          error
        );

        alert(
          t("employerProfile.error")
        );

      } finally {

        setLoading(false);

      }

    };

  return (
    <div className="p-8 text-white">

      <h1 className="text-4xl font-black">
        {t("employerProfile.title")}
      </h1>

      <p className="text-white/50 mt-2">
        {t("employerProfile.subtitle")}
      </p>

      <div className="mt-10 space-y-5 max-w-3xl">

        <input
          type="text"
          placeholder={t("employerProfile.fullName")}
          value={fullName}
          onChange={(e) =>
            setFullName(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <input
          type="text"
          placeholder={t("employerProfile.position")}
          value={position}
          onChange={(e) =>
            setPosition(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <input
          type="text"
          placeholder={t("employerProfile.phone")}
          value={phone}
          onChange={(e) =>
            setPhone(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <textarea
          placeholder="About yourself"
          value={bio}
          onChange={(e) =>
            setBio(
              e.target.value
            )
          }
          className="w-full h-40 p-4 rounded-2xl bg-white/5 border border-white/10 outline-none"
        />

        <button
          onClick={handleSaveProfile}
          disabled={loading}
          className="px-8 py-4 rounded-2xl bg-cyan-500 text-black font-bold hover:opacity-90 transition"
        >
          {loading
            ? t("employerProfile.saving")
            : t("employerProfile.saveProfile")}
        </button>

      </div>

    </div>
  );
}
