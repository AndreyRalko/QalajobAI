import {
  getCurrentSubscription,
  subscribe,
} from "@/lib/api";

export async function getUserSubscription() {
  return getCurrentSubscription();
}

export async function getSubscription(): Promise<string> {
  const sub = (await getCurrentSubscription()) as {
    plan?: string;
  };

  return sub?.plan || "free";
}

export async function updateSubscription(
  plan: string,
  billing: string
) {
  return subscribe(
    plan,
    billing
  );
}

export async function changeSubscription(
  plan: string
) {
  return subscribe(
    plan,
    "monthly"
  );
}

export async function cancelSubscription() {
  const { API_BASE } =
    await import("@/lib/api");

  const { getAccessToken } =
    await import("@/lib/session");

  const token =
    getAccessToken();

  const res = await fetch(
    `${API_BASE}/subscriptions/cancel/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
        Authorization:
          `Bearer ${token}`,
      },
      body: JSON.stringify({
        reason:
          "user_cancelled",
      }),
    }
  );

  if (!res.ok) {
    throw new Error(
      "Cancel failed"
    );
  }

  return res.json();
}