"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type VacancyContextValue = {
  jobTitle: string;
  setJobTitle: (value: string) => void;
  company: string;
  setCompany: (value: string) => void;
  jobDescription: string;
  setJobDescription: (value: string) => void;
};

const VacancyContext = createContext<VacancyContextValue | null>(null);

export function VacancyProvider({ children }: { children: ReactNode }) {
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const value = useMemo(
    () => ({
      jobTitle,
      setJobTitle,
      company,
      setCompany,
      jobDescription,
      setJobDescription,
    }),
    [jobTitle, company, jobDescription]
  );

  return (
    <VacancyContext.Provider value={value}>{children}</VacancyContext.Provider>
  );
}

export function useVacancyContext() {
  const ctx = useContext(VacancyContext);
  if (!ctx) {
    throw new Error("useVacancyContext must be used within VacancyProvider");
  }
  return ctx;
}
