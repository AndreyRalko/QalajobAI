"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "@/hooks/useTranslations";

import {
  getCompany,
  saveCompany,
} from "@/lib/api";

export default function CompanyProfilePage() {
  const { t } = useTranslations();
  const [companyName, setCompanyName] =
    useState("");

  const [industry, setIndustry] =
    useState("");

  const [location, setLocation] =
    useState("");

  const [website, setWebsite] =
    useState("");

  const [companySize, setCompanySize] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    const loadCompany = async () => {
      try {
        const company =
          await getCompany();

        if (!company) return;

        setCompanyName(
          company.company_name || ""
        );

        setIndustry(
          company.industry || ""
        );

        setLocation(
          company.location || ""
        );

        setWebsite(
          company.website || ""
        );

        setCompanySize(
          company.company_size || ""
        );

        setDescription(
          company.description || ""
        );
      } catch (error) {
        console.error(error);
      }
    };

    loadCompany();
  }, []);

  const handleSaveCompany =
    async () => {
      try {
        setLoading(true);

        await saveCompany({
          company_name:
            companyName,
          industry,
          location,
          website,
          company_size:
            companySize,
          description,
        });

        alert(
          t("employerCompany.success")
        );
      } catch (error) {
        console.error(error);

        alert(
          t("employerCompany.error")
        );
      } finally {
        setLoading(false);
      }
    };

  return (
    <div className="p-8 text-white">
      <h1 className="text-4xl font-black">
        {t("employerCompany.title")}
      </h1>

      <p className="text-white/50 mt-2">
        {t("employerCompany.subtitle")}
      </p>

      <div className="mt-10 space-y-5 max-w-4xl">

        <input
          type="text"
          placeholder={t("employerCompany.companyName")}
          value={companyName}
          onChange={(e) =>
            setCompanyName(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerCompany.industry")}
          value={industry}
          onChange={(e) =>
            setIndustry(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerCompany.location")}
          value={location}
          onChange={(e) =>
            setLocation(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerCompany.website")}
          value={website}
          onChange={(e) =>
            setWebsite(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerCompany.size")}
          value={companySize}
          onChange={(e) =>
            setCompanySize(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          placeholder={t("employerCompany.description")}
          value={description}
          onChange={(e) =>
            setDescription(
              e.target.value
            )
          }
          className="w-full h-40 p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <button
          onClick={handleSaveCompany}
          disabled={loading}
          className="px-8 py-4 rounded-2xl bg-cyan-500 text-black font-bold disabled:opacity-50"
        >
          {loading
            ? t("employerCompany.saving")
            : t("employerCompany.save")}
        </button>

      </div>
    </div>
  );
}
