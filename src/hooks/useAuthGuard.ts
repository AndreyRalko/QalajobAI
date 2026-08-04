"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getUserRole } from "@/lib/auth";
import { getAccessToken } from "@/lib/session";

type Role = "student" | "employer" | "admin";

export function useAuthGuard(requiredRole?: Role) {
  const router = useRouter();

  const [user, setUser] = useState<any>(null);
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getAccessToken();

        if (!token) {
          router.replace("/login");
          return;
        }

        const userData = await getUserRole();

        if (!userData) {
          router.replace("/login");
          return;
        }

        if (userData.isBanned) {
          router.replace("/login");
          return;
        }

        if (
          requiredRole &&
          userData.role !== requiredRole
        ) {
          router.replace("/dashboard");
          return;
        }

        setUser(userData);
        setRole(userData.role);
      } catch (error) {
        console.error(error);
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router, requiredRole]);

  return {
    user,
    role,
    loading,
  };
}