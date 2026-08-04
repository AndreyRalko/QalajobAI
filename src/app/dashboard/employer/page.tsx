"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";
import { useAuth } from "@/context/AuthContext";
import {
  getEmployerVacanciesApi,
  getEmployerApplicationsApi,
  unwrapList,
} from "@/lib/api";

export default function EmployerDashboard() {
  const { t } = useTranslations();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [vacancies, setVacancies] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user || user.role !== "employer") {
      router.replace("/dashboard");
      return;
    }
    const loadData = async () => {
      try {
        const [vacRes, appRes] = await Promise.all([
          getEmployerVacanciesApi(),
          getEmployerApplicationsApi(),
        ]);
        setVacancies(unwrapList(vacRes as any));
        setApplications(appRes || []);
      } catch (error) {
        console.error("Dashboard Error:", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [authLoading, user, router]);

  if (loading) {
    return (
      <div className="flex-1 p-8 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white/50">{t("common.loading")}</p>
        </div>
      </div>
    );
  }

  const activeVacancies = vacancies.filter((v: any) => v.status !== "archived");
  const newApps = applications.filter((a: any) => a.status === "pending");
  const interviewApps = applications.filter((a: any) => a.status === "interview" || a.status === "accepted");

  const statusColor = (s: string) => {
    const map: Record<string, string> = {
      pending: "text-yellow-400 bg-yellow-500/10",
      reviewing: "text-blue-400 bg-blue-500/10",
      interview: "text-purple-400 bg-purple-500/10",
      accepted: "text-green-400 bg-green-500/10",
      rejected: "text-red-400 bg-red-500/10",
    };
    return map[s] || "text-white/50 bg-white/5";
  };

  const vacancyStatusColor = (s: string) => {
    const map: Record<string, string> = {
      active: "bg-green-500/10 text-green-400",
      paused: "bg-yellow-500/10 text-yellow-400",
      archived: "bg-gray-500/10 text-gray-400",
    };
    return map[s] || "bg-green-500/10 text-green-400";
  };

  return (
    <div className="flex-1 p-6 md:p-8 text-white overflow-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl md:text-5xl font-black">
            {t("employer.dashboard")} 🏢
          </h1>
          <p className="text-white/50 mt-2">
            {t("dashboard.welcome")}, {user?.name || t("common.employer")}
          </p>
        </div>
        <Link
          href="/dashboard/employer/create"
          className="px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-bold text-sm transition-all"
        >
          + {t("employer.create.title")}
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mt-8">
        <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 hover:border-indigo-500/30 transition-colors">
          <p className="text-white/50 text-sm">{t("employer.stats.activeVacancies")}</p>
          <h2 className="text-4xl font-black mt-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            {activeVacancies.length}
          </h2>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 hover:border-green-500/30 transition-colors">
          <p className="text-white/50 text-sm">{t("employer.stats.totalApplications")}</p>
          <h2 className="text-4xl font-black mt-2 text-green-400">
            {applications.length}
          </h2>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 hover:border-orange-500/30 transition-colors">
          <p className="text-white/50 text-sm">{t("employer.stats.newApplications")}</p>
          <h2 className="text-4xl font-black mt-2 text-orange-400">
            {newApps.length}
          </h2>
        </div>

        <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/5 backdrop-blur-sm p-6 hover:border-cyan-500/40 transition-colors">
          <p className="text-white/50 text-sm">{t("employer.stats.interviewsScheduled")}</p>
          <h2 className="text-4xl font-black mt-2 text-cyan-400">
            {interviewApps.length}
          </h2>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8 mt-10">
        {/* Recent Vacancies */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">{t("employer.vacancies.title")}</h2>
            <Link
              href="/dashboard/employer/vacancies"
              className="text-indigo-400 hover:text-indigo-300 text-sm"
            >
              {t("common.view")} →
            </Link>
          </div>

          <div className="space-y-3">
            {vacancies.slice(0, 5).map((vacancy: any) => (
              <div
                key={vacancy.id}
                className="rounded-2xl border border-white/10 bg-white/5 p-5 hover:border-indigo-500/30 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold">{vacancy.title}</h3>
                    <p className="text-cyan-400 text-sm mt-1">
                      {vacancy.company_name || vacancy.company}
                    </p>
                    <p className="text-white/40 text-sm mt-1">
                      📍 {vacancy.city || vacancy.location || t("common.notSpecified")}
                    </p>
                  </div>
                  <span className={`text-xs px-3 py-1 rounded-full ${vacancyStatusColor(vacancy.status)}`}>
                    {vacancy.status || t("employer.vacancies.active")}
                  </span>
                </div>
              </div>
            ))}

            {vacancies.length === 0 && (
              <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center">
                <p className="text-white/30 text-lg mb-2">💼</p>
                <p className="text-white/40">{t("employer.vacancies.empty")}</p>
                <p className="text-white/30 text-sm mt-1">{t("employer.vacancies.emptyDesc")}</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Applications */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">{t("employer.applications.title")}</h2>
            <Link
              href="/dashboard/employer/applications"
              className="text-indigo-400 hover:text-indigo-300 text-sm"
            >
              {t("common.view")} →
            </Link>
          </div>

          <div className="space-y-3">
            {applications.slice(0, 5).map((app: any) => (
              <div
                key={app.id}
                className="rounded-2xl border border-white/10 bg-white/5 p-5 hover:border-indigo-500/30 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold">
                      {app.candidate_email || app.student_email || t("common.noName")}
                    </h3>
                    <p className="text-cyan-400 text-sm mt-1">
                      {app.vacancy_title || `${t("vacancies.title")} #${app.vacancy_id}`}
                    </p>
                  </div>
                  <span className={`text-xs px-3 py-1 rounded-full ${statusColor(app.status)}`}>
                    {t(`applications.status.${app.status}`) || app.status}
                  </span>
                </div>
              </div>
            ))}

            {applications.length === 0 && (
              <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center">
                <p className="text-white/30 text-lg mb-2">📋</p>
                <p className="text-white/40">{t("employer.applications.empty")}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}