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

export interface LmsSyncLog {
  id: number;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  status: "running" | "success" | "failed";
  students_created: number;
  students_updated: number;
  students_skipped: number;
  error_message: string;
}

export interface LmsSyncSchedule {
  enabled: boolean;
  hour: number;
  minute: number;
  time: string;
  timezone: string;
  last_scheduled_run: string | null;
  next_run_at: string | null;
  updated_at: string;
}

export async function getLmsSyncSchedule(): Promise<LmsSyncSchedule> {
  return adminRequest<LmsSyncSchedule>("lms-sync-schedule/");
}

export async function saveLmsSyncSchedule(payload: {
  enabled: boolean;
  hour: number;
  minute: number;
}): Promise<LmsSyncSchedule> {
  return adminRequest<LmsSyncSchedule>("lms-sync-schedule/", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export interface AiActionLog {
  id: number;
  created_at: string;
  user_name: string;
  user_login: string;
  student_id: string | null;
  feature: string;
  feature_label: string;
  endpoint: string;
  status: "success" | "failed" | "demo";
  model_name: string;
  provider: string;
  duration_ms: number;
  request_payload: Record<string, unknown>;
  ai_input: Record<string, unknown>;
  ai_output: string;
  error_message: string;
}

export async function getAiActionLogs(params?: {
  feature?: string;
  status?: string;
  student_id?: string;
  login?: string;
  days?: number;
  limit?: number;
}): Promise<AiActionLog[]> {
  const query = new URLSearchParams();
  if (params?.feature) query.set("feature", params.feature);
  if (params?.status) query.set("status", params.status);
  if (params?.student_id) query.set("student_id", params.student_id);
  if (params?.login) query.set("login", params.login);
  if (params?.days) query.set("days", String(params.days));
  if (params?.limit) query.set("limit", String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return adminRequest<AiActionLog[]>(`ai-action-logs/${suffix}`);
}

export async function getLmsSyncLogs(params?: {
  status?: string;
  limit?: number;
}): Promise<LmsSyncLog[]> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.limit) query.set("limit", String(params.limit));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return adminRequest<LmsSyncLog[]>(`lms-sync-logs/${suffix}`);
}

export async function runLmsSync(full = false): Promise<LmsSyncLog> {
  return adminRequest<LmsSyncLog>("lms-sync-run/", {
    method: "POST",
    body: JSON.stringify({ full }),
  });
}
