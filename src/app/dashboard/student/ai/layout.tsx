"use client";

import { VacancyProvider } from "@/app/dashboard/student/ai/vacancy-context";

export default function AiWorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <VacancyProvider>{children}</VacancyProvider>;
}
