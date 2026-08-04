import { API_BASE } from "./api";
import { getAccessToken } from "./session";

async function adminRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${API_BASE}/admin-api/${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || json.message || "Admin API error");
  return json.data ?? json;
}

export async function getAdminDashboard() {
  return adminRequest("dashboard/");
}

export async function banUser(userId: number, reason: string, isPermanent = false) {
  return adminRequest("ban-user/", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, reason, is_permanent: isPermanent }),
  });
}

export async function unbanUser(userId: number, reason: string) {
  return adminRequest("unban-user/", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, reason }),
  });
}

export async function getModerationQueue(status = "pending") {
  return adminRequest(`moderation-queue/?status=${status}`);
}

export async function getAuditLogs(days = 30) {
  return adminRequest(`audit-logs/?days=${days}`);
}

export async function getVacanciesAdmin() {
  const token = getAccessToken();
  const res = await fetch(`${API_BASE}/vacancies/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const json = await res.json();
  return json.results ?? json.data ?? json;
}

export async function approveVacancy(id: number) {
  return adminRequest(`${id}/approve/`, { method: "POST" });
}

export async function rejectVacancy(id: number) {
  return adminRequest(`${id}/reject/`, { method: "POST" });
}

export async function getAdminApplications(): Promise<any[]> {
  return adminRequest<any[]>("applications/");
}

export async function saveAdminSettings(settings: {
  maintenanceMode: boolean;
  registrationEnabled: boolean;
  aiEnabled: boolean;
  language: string;
}) {
  return adminRequest("settings/", {
    method: "PUT",
    body: JSON.stringify(settings),
  });
}
