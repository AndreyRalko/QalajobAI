"use client";

import { useEffect, useState } from "react";

import {
  useParams,
  useRouter,
} from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";
import {
  getVacancy,
  updateVacancy,
} from "@/lib/api";

export default function EditVacancyPage() {
  const { t } = useTranslations();
  const params = useParams();

  const router = useRouter();

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [title, setTitle] =
    useState("");

  const [company, setCompany] =
    useState("");

  const [location, setLocation] =
    useState("");

  const [salary, setSalary] =
    useState("");

  const [type, setType] =
    useState("");

  const [phone, setPhone] =
    useState("");

  const [requirements, setRequirements] =
    useState("");

  const [benefits, setBenefits] =
    useState("");

  const [description, setDescription] =
    useState("");

  useEffect(() => {
    const loadVacancy =
      async () => {
        try {
          const data = await getVacancy(
  params.id as string
);

            setTitle(
              data.title || ""
            );

            setCompany(
              data.company_name || ""
            );

            setLocation(
              data.city || ""
            );

            setSalary(
              String(
                data.salary || ""
              )
            );

            setType(
              data.job_type || ""
            );

            setPhone(
              data.phone || ""
            );

            setRequirements(
              data.requirements || ""
            );

            setBenefits(
              data.benefits || ""
            );

            setDescription(
              data.description || ""
            );
          }
        catch (error) {
          console.error(error);
        } finally {
          setLoading(false);
        }
      };

    loadVacancy();
  }, [params]);

  const handleSave =
    async () => {
      if (
        !title ||
        !company ||
        !location
      ) {
        alert(
          t("employerVacancyEdit.fillRequired")
        );

        return;
      }

      try {
        setSaving(true);

        await updateVacancy(
  params.id as string,
  {
    title,
    company_name: company,
    city: location,
    salary,
    job_type: type,
    phone,
    requirements,
    benefits,
    description,
  }
);

        alert(
          t("employerVacancyEdit.success")
        );

        router.push(
          "/dashboard/employer/vacancies"
        );
      } catch (error) {
        console.error(error);

        alert(
          t("employerVacancyEdit.updateError")
        );
      } finally {
        setSaving(false);
      }
    };

  if (loading) {
    return (
      <div className="p-8 text-white">
        {t("employerVacancyEdit.loading")}
      </div>
    );
  }

  return (
    <div className="p-8 text-white">

      <h1 className="text-4xl font-black">
        {t("employerVacancyEdit.title")}
      </h1>

      <p className="text-white/50 mt-2">
        {t("employerVacancyEdit.subtitle")}
      </p>

      <div className="mt-10 space-y-5 max-w-5xl">

        <input
          type="text"
          placeholder={t("employerVacancyEdit.placeholders.jobTitle")}
          value={title}
          onChange={(e) =>
            setTitle(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerVacancyEdit.placeholders.companyName")}
          value={company}
          onChange={(e) =>
            setCompany(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="text"
          placeholder={t("employerVacancyEdit.placeholders.location")}
          value={location}
          onChange={(e) =>
            setLocation(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <input
          type="number"
          placeholder={t("employerVacancyEdit.placeholders.salary")}
          value={salary}
          onChange={(e) =>
            setSalary(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <select
          value={type}
          onChange={(e) =>
            setType(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        >
          <option value="">
            {t("employerVacancyEdit.placeholders.selectType")}
          </option>

          <option value="Full Time">
            {t("employerVacancyEdit.placeholders.fullTime")}
          </option>

          <option value="Part Time">
            {t("employerVacancyEdit.placeholders.partTime")}
          </option>

          <option value="Internship">
            {t("employerVacancyEdit.placeholders.internship")}
          </option>

          <option value="Remote">
            {t("employerVacancyEdit.placeholders.remote")}
          </option>
        </select>

        <input
          type="text"
          placeholder={t("employerVacancyEdit.placeholders.whatsappNumber")}
          value={phone}
          onChange={(e) =>
            setPhone(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          rows={5}
          placeholder={t("employerVacancyEdit.placeholders.requirements")}
          value={requirements}
          onChange={(e) =>
            setRequirements(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          rows={5}
          placeholder={t("employerVacancyEdit.placeholders.benefits")}
          value={benefits}
          onChange={(e) =>
            setBenefits(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          rows={8}
          placeholder={t("employerVacancyEdit.placeholders.description")}
          value={description}
          onChange={(e) =>
            setDescription(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <button
          onClick={handleSave}
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
            ? t("employerVacancyEdit.saving")
            : t("employerVacancyEdit.save")}
        </button>

      </div>

    </div>
  );
}