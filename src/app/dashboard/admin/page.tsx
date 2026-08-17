"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "@/hooks/useTranslations";
import { useAuthGuard } from "@/hooks/useAuthGuard";
import { getUsers, getVacancies } from "@/lib/api";

export default function AdminDashboard() {
  const { t } = useTranslations();
  const { loading: authLoading } = useAuthGuard("admin");
  const [users, setUsers] = useState(0);
  const [students, setStudents] = useState(0);
  const [employers, setEmployers] = useState(0);
  const [vacanciesCount, setVacanciesCount] = useState(0);
  const [bannedUsers, setBannedUsers] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    const loadStats = async () => {
      try {
        const [usersData, vacanciesData] = await Promise.all([
          getUsers(),
          getVacancies(),
        ]);

        setUsers(usersData.length);
        setVacanciesCount(vacanciesData.length);
        setStudents(usersData.filter((u) => u.role === "student").length);
        setEmployers(usersData.filter((u) => u.role === "employer").length);
        setBannedUsers(usersData.filter((u) => u.is_banned).length);
      } catch (error) {
        console.error("Admin Dashboard Error:", error);
      } finally {
        setLoading(false);
      }
    };
    void loadStats();
  }, [authLoading]);

  if (authLoading || loading) {
    return (
      <div className="text-white p-10 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white/50">{t("common.loading")}</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      label: t("admin.dashboard.totalUsers"),
      value: users,
      color: "cyan",
      icon: "👥",
    },
    {
      label: t("admin.dashboard.students"),
      value: students,
      color: "green",
      icon: "🎓",
    },
    {
      label: t("admin.dashboard.employers"),
      value: employers,
      color: "purple",
      icon: "🏢",
    },
    {
      label: t("admin.dashboard.vacancies"),
      value: vacanciesCount,
      color: "orange",
      icon: "💼",
    },
  ];

  const colorMap: Record<string, { border: string; bg: string; text: string }> = {
    cyan: {
      border: "border-cyan-500/20",
      bg: "bg-cyan-500/10",
      text: "text-cyan-400",
    },
    green: {
      border: "border-green-500/20",
      bg: "bg-green-500/10",
      text: "text-green-400",
    },
    purple: {
      border: "border-purple-500/20",
      bg: "bg-purple-500/10",
      text: "text-purple-400",
    },
    orange: {
      border: "border-orange-500/20",
      bg: "bg-orange-500/10",
      text: "text-orange-400",
    },
  };

  const quickLinks = [
    { label: t("admin.menu.users"), href: "/dashboard/admin/users", icon: "👥" },
    { label: t("admin.menu.vacancies"), href: "/dashboard/admin/vacancies", icon: "💼" },
    { label: t("admin.menu.applications"), href: "/dashboard/admin/applications", icon: "📋" },
    { label: t("admin.menu.lmsSync"), href: "/dashboard/admin/lms-sync", icon: "🔄" },
    { label: t("admin.menu.settings"), href: "/dashboard/admin/settings", icon: "⚙️" },
  ];

  return (
    <div className="text-white p-6 md:p-10 overflow-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl md:text-5xl font-black">
            {t("admin.dashboard.title")} ⚙️
          </h1>
          <p className="text-white/50 mt-2">{t("admin.dashboard.overview")}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-medium">
            🟢 {t("admin.dashboard.operational")}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mt-8">
        {statCards.map(({ label, value, color, icon }) => {
          const c = colorMap[color];
          return (
            <div
              key={label}
              className={`rounded-3xl border ${c.border} ${c.bg} p-6 hover:scale-[1.02] transition-transform`}
            >
              <div className="flex justify-between items-start">
                <h3 className="text-white/50 text-sm">{label}</h3>
                <span className="text-2xl">{icon}</span>
              </div>
              <p className={`text-4xl md:text-5xl font-black ${c.text} mt-3`}>
                {value}
              </p>
            </div>
          );
        })}
      </div>

      {/* Extra Stats */}
      <div className="grid md:grid-cols-3 gap-4 mt-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <p className="text-white/50 text-sm">{t("admin.dashboard.bannedUsers")}</p>
          <p className="text-3xl font-bold text-red-400 mt-2">{bannedUsers}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <p className="text-white/50 text-sm">{t("admin.dashboard.platformStatus")}</p>
          <p className="text-lg font-bold text-green-400 mt-2">
            {t("admin.dashboard.operational")}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <p className="text-white/50 text-sm">{t("admin.dashboard.todayRevenue")}</p>
          <p className="text-3xl font-bold text-emerald-400 mt-2">0 ₸</p>
        </div>
      </div>

      {/* Quick Links */}
      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">{t("common.actions")}</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {quickLinks.map(({ label, href, icon }) => (
            <Link
              key={href}
              href={href}
              className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center hover:border-indigo-500/30 hover:bg-indigo-500/5 transition-colors"
            >
              <div className="text-2xl mb-2">{icon}</div>
              <p className="text-sm font-medium">{label}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}