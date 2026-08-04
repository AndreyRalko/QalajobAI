"use client";

import { useEffect, useState } from "react";

import { getAdminApplications, getModerationQueue } from "@/lib/admin";
import {
  updateApplicationStatus,
} from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";

interface Application {
  id: number;
  vacancy_id: string;
  employer_id: string;
  status: string;
  candidate_email?: string;
  applied_at: string;
}

export default function AdminApplicationsPage() {
  const { t } = useTranslations();
  const [applications, setApplications] =
    useState<Application[]>([]);

  const [loading, setLoading] =
    useState(true);

  const loadApplications =
    async () => {
      try {
        const data =
          await getAdminApplications();

        setApplications(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    void loadApplications();
  }, []);

  const handleStatusUpdate =
    async (
      id: number,
      status: string
    ) => {
      try {
        await updateApplicationStatus(
          id,
          status
        );

        setApplications(
          (prev) =>
            prev.map((app) =>
              app.id === id
                ? {
                    ...app,
                    status,
                  }
                : app
            )
        );

        alert(
          t("adminApplications.statusUpdated")
        );
      } catch (error) {
        console.error(error);

        alert(
          t("adminApplications.updateFailed")
        );
      }
    };

  if (loading) {
    return (
      <div className="p-8 text-white">
        {t("adminApplications.loading")}
      </div>
    );
  }

  return (
    <div className="p-8 text-white">

      <div className="flex justify-between items-center mb-8">

        <h1 className="text-4xl font-black">
          {t("adminApplications.title")}
        </h1>

        <div className="px-4 py-2 rounded-xl bg-cyan-500/20 text-cyan-400">
          Total: {applications.length}
        </div>

      </div>

      {applications.length === 0 ? (

        <div className="text-center py-20 text-white/50">
          {t("adminApplications.noApplications")}
        </div>

      ) : (

        <div className="overflow-x-auto rounded-3xl border border-white/10">

          <table className="w-full">

            <thead>
              <tr className="bg-white/5">

                <th className="p-4 text-left">
                  {t("adminApplications.candidate")}
                </th>

                <th className="p-4 text-left">
                  {t("adminApplications.vacancyId")}
                </th>

                <th className="p-4 text-left">
                  {t("adminApplications.status")}
                </th>

                <th className="p-4 text-left">
                  {t("adminApplications.actions")}
                </th>

              </tr>
            </thead>

            <tbody>

              {applications.map(
                (app) => (
                  <tr
                    key={app.id}
                    className="border-t border-white/10"
                  >

                    <td className="p-4">
                      {app.candidate_email ||
                        "Unknown"}
                    </td>

                    <td className="p-4">
                      {app.vacancy_id}
                    </td>

                    <td className="p-4">

                      <span className="px-3 py-1 rounded-xl bg-cyan-500/20 text-cyan-400">
                        {app.status}
                      </span>

                    </td>

                    <td className="p-4 flex gap-2">

                      <button
                        onClick={() =>
                          handleStatusUpdate(
                            app.id,
                            "accepted"
                          )
                        }
                        className="px-4 py-2 rounded-xl bg-green-600 hover:bg-green-700"
                      >
                        {t("adminApplications.approve")}
                      </button>

                      <button
                        onClick={() =>
                          handleStatusUpdate(
                            app.id,
                            "rejected"
                          )
                        }
                        className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700"
                      >
                        {t("adminApplications.reject")}
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