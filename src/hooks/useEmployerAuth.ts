"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getEmployerUser } from "@/lib/employer";
import { getAccessToken } from "@/lib/session";

import type { EmployerUser } from "@/types/employer";

export const useEmployerAuth = () => {
  const router = useRouter();

  const [user, setUser] = useState<EmployerUser | null>(null);
  const [employer, setEmployer] = useState<EmployerUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkEmployer = async () => {
      try {
        const token = getAccessToken();

        if (!token) {
          router.replace("/login");
          return;
        }

        const data = await getEmployerUser();

        if (!data) {
          router.replace("/login");
          return;
        }

        if (data.role !== "employer") {
          router.replace("/dashboard");
          return;
        }

        setUser(data as any);
        setEmployer(data as any);
      } catch (error) {
        console.error("Employer auth error:", error);
        router.replace("/dashboard");
      } finally {
        setLoading(false);
      }
    };

    checkEmployer();
  }, [router]);

  return {
    user,
    employer,
    setEmployer,
    loading,
  };
};