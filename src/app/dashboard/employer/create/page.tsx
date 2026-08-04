"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createVacancy } from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";

export default function CreateVacancyPage() {
  const router = useRouter();
  const { t } = useTranslations();
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

  const [loading, setLoading] =
    useState(false);

  const handleCreate = async () => {
    if (
      !title ||
      !company ||
      !location ||
      !salary ||
      !phone
    ) {
      alert(
        t("employerCreate.fillRequired")
      );
      return;
    }

    try {
      setLoading(true);

      

      
    await createVacancy({
  title,
  company_name: company,
  city: location,
  salary: Number(salary),
  job_type: type,
  phone,
  requirements,
  benefits,
  description,
});

      alert(
        t("employerCreate.success")
      );
      router.push("/dashboard/employer/vacancies");

      setTitle("");
      setCompany("");
      setLocation("");
      setSalary("");
      setType("");
      setPhone("");
      setRequirements("");
      setBenefits("");
      setDescription("");

    } catch (error) {
      console.error(error);

      alert(
        t("employerCreate.error")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 text-white">

      <h1 className="text-4xl font-black">
        {t("employerCreate.title")}
      </h1>

       <p className="text-white/50 mt-2">
         {t("employerCreate.subtitle")}
       </p>

      <div className="mt-10 space-y-5 max-w-4xl">

        <input
          type="text"
          placeholder={t("employerCreate.jobTitle")}
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
          placeholder={t("employerCreate.companyName")}
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
          placeholder={t("employerCreate.location")}
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
          placeholder={t("employerCreate.salary")}
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
             {t("employerCreate.selectType")}
           </option>

          <option value="Full Time">
            {t("employerCreate.fullTime")}
          </option>

          <option value="Part Time">
            {t("employerCreate.partTime")}
          </option>

          <option value="Internship">
            {t("employerCreate.internship")}
          </option>

          <option value="Remote">
            {t("employerCreate.remote")}
          </option>
        </select>

        <input
          type="text"
          placeholder={t("employerCreate.contactNumber")}
          value={phone}
          onChange={(e) =>
            setPhone(
              e.target.value
            )
          }
          className="w-full p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          placeholder={t("employerCreate.requirements")}
          value={requirements}
          onChange={(e) =>
            setRequirements(
              e.target.value
            )
          }
          className="w-full h-40 p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          placeholder={t("employerCreate.benefits")}
          value={benefits}
          onChange={(e) =>
            setBenefits(
              e.target.value
            )
          }
          className="w-full h-40 p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <textarea
          placeholder={t("employerCreate.description")}
          value={description}
          onChange={(e) =>
            setDescription(
              e.target.value
            )
          }
          className="w-full h-48 p-4 rounded-2xl bg-white/5 border border-white/10"
        />

        <button
          onClick={handleCreate}
          disabled={loading}
          className="px-8 py-4 rounded-2xl bg-cyan-500 text-black font-bold disabled:opacity-50"
        >
          {loading
            ? t("employerCreate.publishing")
            : t("employerCreate.publish")}
        </button>

      </div>

    </div>
  );
}