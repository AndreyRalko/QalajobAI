"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";

export default function AdminSidebar() {
  const pathname = usePathname();
  const { t } = useTranslations();

  const menu = [
    { title: t("admin.menu.dashboard"), href: "/dashboard/admin", icon: "🏠" },
    { title: t("admin.menu.users"), href: "/dashboard/admin/users", icon: "👥" },
    { title: t("admin.menu.vacancies"), href: "/dashboard/admin/vacancies", icon: "💼" },
    { title: t("admin.menu.applications"), href: "/dashboard/admin/applications", icon: "📨" },
    { title: t("admin.menu.settings"), href: "/dashboard/admin/settings", icon: "⚙️" },
  ];

  return (
    <aside aria-label={t("admin.panel")} className="w-72 min-h-screen bg-[#07101f] border-r border-white/10 p-6 flex flex-col">
      <div>
        <h2 className="text-3xl font-black text-white">{t("admin.panel")}</h2>
        <p className="text-white/40 mt-2">{t("common.platformName")}</p>
      </div>

      <nav className="mt-10 space-y-3 flex-1" aria-label={t("common.mainNavigation")}>
        {menu.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`flex items-center gap-3 p-4 rounded-2xl transition-all duration-300 ${
                active
                  ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                  : "text-white hover:bg-white/5"
              }`}
            >
              <span aria-hidden="true" className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.title}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 pt-5">
        <div className="rounded-2xl bg-cyan-500/10 border border-cyan-500/20 p-4">
          <p className="text-cyan-400 font-bold">{t("common.platformName")}</p>
          <p className="text-white/50 text-sm mt-1">{t("admin.systemAdmin")}</p>
        </div>
      </div>
    </aside>
  );
}
