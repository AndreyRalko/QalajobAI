"use client";

import { useEffect, useState } from "react";
import {
  getVacancies,
  deleteVacancy,
} from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";

export interface ApiVacancy {
  id: number;
  employer_id: number;
  title: string;
  company_name: string;
  salary: string;
  city: string;
  location: string;
  phone: string;
  job_type: string;
}

export default function AdminVacanciesPage() {
  const { t } = useTranslations();
const [vacancies, setVacancies] =
  useState<ApiVacancy[]>([]);

  const [loading, setLoading] =
    useState(true);

const loadVacancies = async () => {
  try {
    const data =
      await getVacancies();

    setVacancies(data);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    void loadVacancies();
  }, []);

const handleDelete = async (
  id: number
) => {
      const confirmDelete =
        confirm(
          t("adminVacancies.deleteConfirm")
        );

      if (!confirmDelete)
        return;

      try {
        await deleteVacancy(id);

        setVacancies((prev) =>
          prev.filter(
            (item) =>
              item.id !== id
          )
        );

        alert(
          t("adminVacancies.deleteSuccess")
        );
      } catch (error) {
        console.error(error);

        alert(
          t("adminVacancies.deleteError")
        );
      }
    };

  if (loading) {
    return (
      <div className="p-8 text-white">
        {t("adminVacancies.loading")}
      </div>
    );
  }

  return (
    <div className="p-8 text-white">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-4xl font-black">
          {t("adminVacancies.title")}
        </h1>

        <div className="px-4 py-2 rounded-xl bg-cyan-500/20 text-cyan-400">
          {t("adminVacancies.total")}: {vacancies.length}
        </div>
      </div>

      {vacancies.length === 0 ? (
        <div className="text-center py-20 text-white/50">
          {t("adminVacancies.noVacancies")}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-3xl border border-white/10">
          <table className="w-full">
            <thead>
              <tr className="bg-white/5">
                <th className="p-4 text-left">
                  Title
                </th>

                <th className="p-4 text-left">
                  Company
                </th>

                <th className="p-4 text-left">
                  Location
                </th>

                <th className="p-4 text-left">
                  Salary
                </th>

                <th className="p-4 text-left">
                  Type
                </th>

                <th className="p-4 text-left">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody>
              {vacancies.map(
                (vacancy) => (
                  <tr
                    key={
                      vacancy.id
                    }
                    className="border-t border-white/10"
                  >
                    <td className="p-4">
                      {
                        vacancy.title
                      }
                    </td>

                    <td className="p-4">
                      {
                        vacancy.company_name
                      }
                    </td>

                    <td className="p-4">
                      {
                        vacancy.location
                      }
                    </td>

                    <td className="p-4 text-cyan-400 font-bold">
                      {vacancy.salary?.toLocaleString()} ₸
                    </td>

                    <td className="p-4">
                      {
                        vacancy.job_type
                      }
                    </td>

                    <td className="p-4">
                      <button
                        onClick={() =>
                          handleDelete(
                            vacancy.id
                          )
                        }
                        className="px-4 py-2 rounded-xl bg-red-500 hover:bg-red-600 transition"
                      >
                        {t("adminVacancies.delete")}
                      </button>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}