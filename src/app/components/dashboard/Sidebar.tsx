"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "@/hooks/useTranslations";
import { WORKSPACE_MODES, workspaceHref } from "@/lib/workspace-routes";

export default function Sidebar() {
  const pathname = usePathname();
  const { t } = useTranslations();

  const workspaceItems = WORKSPACE_MODES.map((mode) => ({
    mode,
    href: workspaceHref(mode),
    icon:
      mode === "resume"
        ? "📄"
        : mode === "cover_letter"
          ? "✉️"
          : mode === "interview"
            ? "💼"
            : "🎙️",
    title:
      mode === "resume"
        ? t("student.menu.resume")
        : mode === "cover_letter"
          ? t("student.menu.coverLetter")
          : mode === "interview"
            ? t("student.menu.interview")
            : t("student.menu.mockInterview"),
  }));

  const bottomItems = [
    {
      title: t("student.menu.settings"),
      href: "/dashboard/student/settings",
      icon: "⚙️",
    },
  ];

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(`${href}/`);

  return (
    <aside
      aria-label={t("common.sidebarLabel")}
      className="w-72 min-h-screen bg-[#07101f] border-r border-white/10 p-6 flex flex-col"
    >
      <div>
        <h2 className="text-3xl font-black text-white">
          {t("common.platformName")}
        </h2>
        <p className="text-white/40 text-sm mt-1">
          {t("common.platformTagline")}
        </p>
      </div>

      <nav
        className="mt-10 space-y-1 flex-1"
        aria-label={t("common.mainNavigation")}
      >
        <p className="px-4 pb-2 text-[11px] font-semibold uppercase tracking-wider text-white/30">
          {t("student.menu.workspace")}
        </p>
        {workspaceItems.map((item) => {
          const active = isActive(item.href);
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
              <span aria-hidden="true" className="text-lg">
                {item.icon}
              </span>
              <span className="font-medium">{item.title}</span>
            </Link>
          );
        })}

        <p className="px-4 pt-6 pb-2 text-[11px] font-semibold uppercase tracking-wider text-white/30">
          {t("student.menu.account")}
        </p>
        {bottomItems.map((item) => {
          const active = isActive(item.href);
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
              <span aria-hidden="true" className="text-lg">
                {item.icon}
              </span>
              <span className="font-medium">{item.title}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 pt-5">
        <div className="rounded-2xl bg-cyan-500/10 border border-cyan-500/20 p-4">
          <p className="text-cyan-400 font-bold">{t("common.platformName")}</p>
          <p className="text-white/50 text-sm mt-1">
            {t("common.aiPoweredPlatform")}
          </p>
        </div>
      </div>
    </aside>
  );
}
