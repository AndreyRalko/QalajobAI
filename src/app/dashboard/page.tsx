"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getMe } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await getMe();
        if (!user) {
          router.push("/login");
          return;
        }
      router.replace("/dashboard/student/ai/resume");
      } catch {
        router.push("/login");
      }
    };

    void checkAuth();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center text-white">
      Loading...
    </div>
  );
}
