"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import LanguageSwitcher from "@/app/components/layout/LanguageSwitcher";
import { useTranslations } from "@/hooks/useTranslations";
import { getUserRole, logoutUser } from "@/lib/auth";

export default function DashboardHeader() {
  const { t } = useTranslations();
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    void getUserRole().then((user) => {
      if (user?.role) setRole(user.role);
    });
  }, []);

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error(error);
    } finally {
      router.push("/login");
    }
  };

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#030712]/85 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-6 md:px-10 py-4">
        <div className="min-w-0">
          <p className="text-sm text-white/40 truncate">
            {t("common.platformTagline")}
          </p>
          <p className="text-base font-semibold text-white truncate">
            {t("common.platformName")}
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {role === "admin" && (
            <>
              <Link
                href="/dashboard/admin"
                className="hidden md:inline-flex px-4 py-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 text-sm text-cyan-300 hover:text-cyan-200 transition"
              >
                {t("admin.menu.dashboard")}
              </Link>
              <Link
                href="/dashboard/admin/lms-sync"
                className="hidden lg:inline-flex px-4 py-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 text-sm text-cyan-300 hover:text-cyan-200 transition"
              >
                {t("admin.menu.lmsSync")}
              </Link>
            </>
          )}
          <LanguageSwitcher variant="compact" />
          {role !== "admin" && (
            <Link
              href="/dashboard/student/settings"
              className="hidden sm:inline-flex px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 hover:text-white transition"
            >
              {t("student.menu.settings")}
            </Link>
          )}
          <button
            type="button"
            onClick={() => void handleLogout()}
            className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 hover:text-white transition"
          >
            {t("navbar.logout")}
          </button>
        </div>
      </div>
    </header>
  );
}
