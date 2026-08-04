"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";

export default function EmployerSidebar() {
  const pathname = usePathname();
  const { t } = useTranslations();

  const menu = [
    { name: t("employer.menu.dashboard"), href: "/dashboard/employer", icon: "🏠" },
    { name: t("employer.menu.profile"), href: "/dashboard/employer/profile", icon: "👤" },
    { name: t("employer.menu.company"), href: "/dashboard/employer/company", icon: "🏢" },
    { name: t("employer.menu.createVacancy"), href: "/dashboard/employer/create", icon: "➕" },
    { name: t("employer.menu.vacancies"), href: "/dashboard/employer/vacancies", icon: "📋" },
    { name: t("employer.menu.aiAssistant"), href: "/dashboard/employer/ai-assistant", icon: "🤖" },
    { name: t("employer.menu.applications"), href: "/dashboard/employer/applications", icon: "📨" },
    { name: t("employer.menu.settings"), href: "/dashboard/employer/settings", icon: "⚙️" },
  ];

  return (
    <aside aria-label={t("employer.dashboard")} className="w-72 min-h-screen bg-[#020817] border-r border-white/10 p-6">
      <h1 className="text-3xl font-black text-white">{t("common.platformName")}</h1>
      <p className="text-white/40 text-sm mt-1">{t("employer.dashboard")}</p>

      <nav className="mt-10 flex flex-col gap-3" aria-label={t("common.mainNavigation")}>
        {menu.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            aria-current={pathname === item.href ? "page" : undefined}
            className={`flex items-center gap-3 px-4 py-4 rounded-2xl transition ${
              pathname === item.href
                ? "bg-cyan-500/20 border border-cyan-500 text-cyan-400"
                : "text-white/70 hover:bg-white/5"
            }`}
          >
            <span aria-hidden="true">{item.icon}</span>
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
