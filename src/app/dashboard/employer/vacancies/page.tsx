"use client";

import { useEffect, useState } from "react";

import Link from "next/link";
import { useTranslations } from "@/hooks/useTranslations";

import {
  fetchEmployerVacancies,
  deleteVacancyApi,
} from "@/lib/vacancies";

export default function MyVacanciesPage() {
  const { t } = useTranslations();

  const [vacancies, setVacancies] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  async function loadVacancies() {
    try {
      const data =
  await fetchEmployerVacancies();

      setVacancies(data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  }

  useEffect(() => {
    void loadVacancies();
  }, []);

  const handleDelete = async (
    vacancyId: string
  ) => {

    const confirmed =
      confirm(
        t("employerVacancies.deleteConfirm")
      );

    if (!confirmed) return;

    try {

      await deleteVacancyApi(
  vacancyId
);

      setVacancies((prev) =>
        prev.filter(
          (item) =>
            item.id !== vacancyId
        )
      );

      alert(
        t("employerVacancies.deleteSuccess")
      );

    } catch (error) {

      console.error(error);

      alert(
        t("employerVacancies.deleteError")
      );

    }

  };

  if (loading) {
    return (
      <div className="p-8 text-white">
        {t("employerVacancies.loading")}
      </div>
    );
  }

  return (
    <div className="p-8 text-white">

      <h1 className="text-4xl font-black">
        {t("employerVacancies.title")}
      </h1>

      <p className="text-white/50 mt-2">
        {t("employerVacancies.subtitle")}
      </p>

      <div className="grid gap-6 mt-10">

        {vacancies.map((vacancy) => (

          <div
            key={vacancy.id}
            className="rounded-3xl border border-white/10 bg-white/5 p-6"
          >

            <h2 className="text-2xl font-bold">
              {vacancy.title}
            </h2>

            <p className="text-cyan-400 mt-2">
              {vacancy.company_name}
            </p>

            <p className="text-white/60 mt-2">
              {vacancy.salary} ₸
            </p>

            <p className="text-white/60">
              {vacancy.location}
            </p>

            <p className="text-cyan-400 mt-2">
              {vacancy.type}
            </p>

            <div className="flex gap-4 mt-6">

              <Link
  href={`/dashboard/employer/vacancies/edit/${vacancy.id}`}
  className="px-5 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
>
  {t("employerVacancies.edit")}
</Link>

              <button
                onClick={() =>
                  handleDelete(
                    vacancy.id
                  )
                }
                className="px-5 py-3 rounded-2xl bg-red-500 text-white font-bold"
              >
                {t("employerVacancies.delete")}
              </button>

            </div>

          </div>

        ))}

        {vacancies.length === 0 && (

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6">

            <p className="text-white/40">
              {t("employerVacancies.noVacancies")}
            </p>

          </div>

        )}

      </div>

    </div>
  );
}