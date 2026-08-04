"use client";

import { useEffect, useState } from "react";

import { useTranslations } from "@/hooks/useTranslations";

import {
  getEmployerApplications,
  updateApplicationStatus,
} from "@/lib/applications";

export default function ApplicationsPage() {
  const { t } = useTranslations();
  const [applications, setApplications] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  async function loadApplications() {
    try {
     const data =
  await getEmployerApplications();
      setApplications(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadApplications();
  }, []);

  const handleAccept = async (
  id: string | number
) => {
    try {
      await updateApplicationStatus(
        id,
        "accepted"
      );

      await loadApplications();
    } catch (error) {
      console.error(error);
      alert("Accept error");
    }
  };

const handleReject = async (
  id: string | number
) => {
    try {
      await updateApplicationStatus(
        id,
        "rejected"
      );

      await loadApplications();
    } catch (error) {
      console.error(error);
      alert("Reject error");
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-white">
        {t("employerApplications.loading")}
      </div>
    );
  }

  return (
    <div className="p-8 text-white">

      <h1 className="text-4xl font-black">
        {t("employerApplications.title")}
      </h1>

      <p className="text-white/50 mt-2">
        Manage job applications
      </p>

      <div className="grid gap-6 mt-10">

        {applications.length === 0 && (
          <div
            className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            p-8
            "
          >
            {t("employerApplications.noApplications")}
          </div>
        )}

        {applications.map((app) => (

          <div
            key={app.id}
            className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            p-8
            "
          >

            <div className="flex justify-between items-start">

              <div>

                <h2 className="text-3xl font-black">
                  {app.studentName ||
                    "Unknown Student"}
                </h2>

                <p className="text-white/60 mt-2">
                  {app.studentEmail}
                </p>

                <p className="text-cyan-400 mt-2">
                  {app.university ||
                    "University not specified"}
                </p>

              </div>

              <div>

                <span
                  className={`
                  px-4
                  py-2
                  rounded-xl
                  text-sm
                  font-bold
                  ${
                    app.status ===
                    "accepted"
                      ? "bg-green-500/20 text-green-400"
                      : app.status ===
                        "rejected"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-yellow-500/20 text-yellow-400"
                  }
                `}
                >
                  {app.status}
                </span>

              </div>

            </div>

            <div
              className="
              mt-6
              border-t
              border-white/10
              pt-6
              "
            >

              <p className="text-white/50">
                Vacancy
              </p>

              <h3 className="text-2xl font-bold mt-2">
                {app.vacancyTitle}
              </h3>

              <p className="text-cyan-400 mt-2">
                {app.company}
              </p>

            </div>

            <div
              className="
              mt-6
              grid
              md:grid-cols-2
              gap-4
              "
            >

              <div
                className="
                rounded-2xl
                bg-white/5
                p-4
                "
              >
                <p className="text-white/50">
                  Course
                </p>

                <p className="mt-2">
                  {app.course ||
                    t("common.notSpecified")}
                </p>
              </div>

              <div
                className="
                rounded-2xl
                bg-white/5
                p-4
                "
              >
                <p className="text-white/50">
                  Major
                </p>

                <p className="mt-2">
                  {app.major ||
                    t("common.notSpecified")}
                </p>
              </div>

              <div
                className="
                rounded-2xl
                bg-white/5
                p-4
                "
              >
                <p className="text-white/50">
                  {t("common.phone")}
                </p>

                <p className="mt-2">
                  {app.phone ||
                    t("common.notSpecified")}
                </p>
              </div>

              <div
                className="
                rounded-2xl
                bg-white/5
                p-4
                "
              >
                <p className="text-white/50">
                  Skills
                </p>

                <p className="mt-2 break-words">
                  {app.skills ||
                    t("common.notSpecified")}
                </p>
              </div>

            </div>

            <div className="flex flex-wrap gap-4 mt-8">

              {app.resume && (

                <a
                  href={app.resume}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="
                  px-5
                  py-3
                  rounded-2xl
                  bg-blue-500
                  text-white
                  font-bold
                  hover:bg-blue-400
                  transition
                  "
                >
                  {t("employerApplications.viewResume")}
                </a>

              )}

              <button
                onClick={() =>
                  handleAccept(app.id)
                }
                className="
                px-5
                py-3
                rounded-2xl
                bg-green-500
                text-black
                font-bold
                hover:bg-green-400
                transition
                "
              >
                {t("employerApplications.accept")}
              </button>

              <button
                onClick={() =>
                  handleReject(app.id)
                }
                className="
                px-5
                py-3
                rounded-2xl
                bg-red-500
                text-white
                font-bold
                hover:bg-red-400
                transition
                "
              >
                {t("employerApplications.reject")}
              </button>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}