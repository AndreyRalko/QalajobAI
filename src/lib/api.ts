/**
 * QalaJob AI Django Backend API Client
 * Full production-grade API client with auto-refresh, rate limiting, error handling.
 */

import {
  getAccessToken,
  getRefreshToken,
  setSession,
  clearSession,
  isTokenExpiringSoon,
} from "./session";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

type ApiOptions = RequestInit & {
  token?: string | null;
  lang?: string;
  auth?: boolean;
};

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function apiRequest<T>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const { token, lang, auth = false, headers, ...rest } = options;

  // Auto-refresh if token is expiring soon
  if (auth && !token && isTokenExpiringSoon()) {
    await ensureValidToken();
  }

  const accessToken = token ?? (auth ? getAccessToken() : null);

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(lang ? { "Accept-Language": lang === "kz" ? "kk" : lang } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(headers as Record<string, string>),
    },
  });

  let json: Record<string, unknown> = {};
  try {
    json = await res.json();
  } catch {
    json = {};
  }

  if (res.status === 401 && auth) {
    const refreshed = await ensureValidToken();
    if (refreshed) {
      return apiRequest<T>(path, { ...options, token: getAccessToken() });
    }
    clearSession();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  if (!res.ok) {
    const message =
      (json.message as string) ||
      (json.errors as { detail?: string })?.detail ||
      (json.error as string) ||
      "API request failed";
    throw new Error(message);
  }

  return (json.data ?? json) as T;
}

async function ensureValidToken(): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = tryRefreshToken().finally(() => {
    isRefreshing = false;
    refreshPromise = null;
  });

  return refreshPromise;
}

async function tryRefreshToken(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  try {
    const result = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!result.ok) return false;

    const json = await result.json();
    setSession({
      access: json.access,
      refresh: json.refresh || refresh,
    });
    return true;
  } catch {
    return false;
  }
}

// ── Auth ────────────────────────────────────────────────────────────

export async function registerApi(
  name: string,
  email: string,
  password: string,
  role: "student" | "employer"
) {
  return apiRequest<{
    user: ApiUser;
    access: string;
    refresh: string;
  }>("/auth/register/", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role }),
  });
}

export async function loginApi(email: string, password: string) {
  return apiRequest<{
    user: ApiUser;
    access: string;
    refresh: string;
  }>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logoutApi(refreshToken: string) {
  return apiRequest("/auth/logout/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ refresh: refreshToken }),
  });
}

export async function getMe(token?: string) {
  return apiRequest<ApiUser>("/auth/me/", {
    token,
    auth: !token,
  });
}

export async function forgotPasswordApi(email: string) {
  return apiRequest<{ message: string }>("/auth/forgot-password/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPasswordApi(token: string, newPassword: string) {
  return apiRequest<{ message: string }>("/auth/reset-password/", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

export async function verifyEmailApi(token: string) {
  return apiRequest<{ message: string }>("/auth/verify-email/", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function resendVerificationApi() {
  return apiRequest<{ message: string }>("/auth/resend-verification/", {
    method: "POST",
    auth: true,
  });
}

export async function setLanguageApi(language: string) {
  return apiRequest<ApiUser>("/i18n/set-language/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ language }),
  });
}

// ── Vacancies ───────────────────────────────────────────────────────

export async function getVacancies(
  params?: Record<string, string>
): Promise<ApiVacancy[]> {
  const qs = params ? `?${new URLSearchParams(params)}` : "";
  const response = await apiRequest<
    { results?: ApiVacancy[] } | ApiVacancy[]
  >(`/vacancies/${qs}`);
  return Array.isArray(response) ? response : response.results ?? [];
}

export async function getEmployerVacanciesApi() {
  return apiRequest<{ results?: ApiVacancy[] } | ApiVacancy[]>(
    "/vacancies/?mine=true",
    { auth: true }
  );
}

export async function getVacancy(id: number | string, token?: string) {
  return apiRequest<ApiVacancy>(`/vacancies/${id}/`, {
    token,
    auth: !token,
  });
}

export async function createVacancy(data: Record<string, unknown>) {
  return apiRequest<ApiVacancy>("/vacancies/", {
    method: "POST",
    auth: true,
    body: JSON.stringify(data),
  });
}

export async function updateVacancy(
  id: number | string,
  data: Record<string, unknown>
) {
  return apiRequest<ApiVacancy>(`/vacancies/${id}/`, {
    method: "PATCH",
    auth: true,
    body: JSON.stringify(data),
  });
}

export async function deleteVacancy(id: number | string) {
  return apiRequest<void>(`/vacancies/${id}/`, {
    method: "DELETE",
    auth: true,
  });
}

export async function pauseVacancy(id: number | string) {
  return apiRequest<ApiVacancy>(`/vacancies/${id}/pause/`, {
    method: "POST",
    auth: true,
  });
}

export async function archiveVacancy(id: number | string) {
  return apiRequest<ApiVacancy>(`/vacancies/${id}/archive/`, {
    method: "POST",
    auth: true,
  });
}

// ── Applications ────────────────────────────────────────────────────

export async function applyToVacancy(
  vacancyId: number | string,
  coverLetter?: string
) {
  return apiRequest("/applications/apply/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ vacancyId, coverLetter }),
  });
}

export async function getStudentApplications() {
  return apiRequest<ApiApplication[]>("/applications/student/", {
    auth: true,
  });
}

export async function getEmployerApplicationsApi() {
  return apiRequest<ApiApplication[]>("/applications/employer/", {
    auth: true,
  });
}

export async function updateApplicationStatus(id: number, status: string) {
  return apiRequest(`/applications/${id}/update_status/`, {
    method: "POST",
    auth: true,
    body: JSON.stringify({ status }),
  });
}

// ── Profile & Resume ────────────────────────────────────────────────

export async function getProfile() {
  return apiRequest<ApiProfile>("/profiles/me/", { auth: true });
}

export async function saveProfile(data: Record<string, unknown>) {
  return apiRequest<ApiProfile>("/profiles/me/", {
    method: "PUT",
    auth: true,
    body: JSON.stringify(data),
  });
}

export async function getResume() {
  return apiRequest<ApiResume>("/resumes/me/", { auth: true });
}

export async function saveResume(data: Record<string, unknown>) {
  return apiRequest<ApiResume>("/resumes/me/", {
    method: "PUT",
    auth: true,
    body: JSON.stringify(data),
  });
}

/** Convenience helpers for the resume workspace */
export async function getMyResume() {
  return getResume();
}

export async function saveMyResume(content: string) {
  return saveResume({ content });
}

// ── Company ─────────────────────────────────────────────────────────

export async function getCompany() {
  return apiRequest<ApiCompany | null>("/companies/me/", { auth: true });
}

export async function saveCompany(data: Record<string, unknown>) {
  return apiRequest<ApiCompany>("/companies/me/", {
    method: "PUT",
    auth: true,
    body: JSON.stringify(data),
  });
}

// ── Saved Jobs ──────────────────────────────────────────────────────

export async function getSavedJobs() {
  return apiRequest<ApiSavedJob[]>("/saved-jobs/", { auth: true });
}

export async function saveJob(vacancyId: number | string) {
  return apiRequest("/saved-jobs/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ vacancy_id: vacancyId }),
  });
}

export async function unsaveJob(id: number) {
  return apiRequest(`/saved-jobs/${id}/`, { method: "DELETE", auth: true });
}

// ── Users (Admin) ───────────────────────────────────────────────────

export async function getUsers() {
  return apiRequest<ApiUser[]>("/users/", { auth: true });
}

export async function deleteUser(userId: string) {
  return apiRequest(`/users/${userId}/`, {
    method: "DELETE",
    auth: true,
  });
}

export async function banUser(userId: string) {
  return apiRequest(`/users/${userId}/ban/`, {
    method: "POST",
    auth: true,
  });
}

export async function unbanUser(userId: string) {
  return apiRequest(`/users/${userId}/unban/`, {
    method: "POST",
    auth: true,
  });
}

// ── Notifications ───────────────────────────────────────────────────

export async function getNotifications() {
  return apiRequest<ApiNotification[]>("/notifications/", { auth: true });
}

export async function markNotificationRead(id: number) {
  return apiRequest(`/notifications/${id}/read/`, {
    method: "POST",
    auth: true,
  });
}

export async function markAllNotificationsRead() {
  return apiRequest("/notifications/read-all/", {
    method: "POST",
    auth: true,
  });
}

export async function getUnreadNotificationCount() {
  return apiRequest<{ count: number }>("/notifications/unread-count/", {
    auth: true,
  });
}

// ── AI ──────────────────────────────────────────────────────────────

export type AiChatMessage = { role: "user" | "assistant"; content: string };

export type WorkspaceMode =
  | "resume"
  | "cover_letter"
  | "interview"
  | "mock_interview";

export type AiResumeChatResponse = {
  chat_id: number;
  mode?: WorkspaceMode;
  reply: string;
  resume_draft?: string | null;
  document_draft?: string | null;
  messages?: AiChatMessage[];
};

export type AiResumeChatState = {
  chat_id: number | null;
  mode?: WorkspaceMode;
  messages: AiChatMessage[];
  topic?: string;
  updated_at?: string;
};

export async function getResumeAssistantChat(mode: WorkspaceMode = "resume") {
  return apiRequest<AiResumeChatState>(
    `/ai/career-coach/?mode=${encodeURIComponent(mode)}`,
    { auth: true }
  );
}

export async function aiCareerCoach(
  message: string,
  history?: { role: string; content: string }[],
  language?: string,
  resumeDraft?: string,
  chatId?: number | null,
  mode: WorkspaceMode = "resume",
  resumeContext?: string,
  jobContext?: {
    jobTitle?: string;
    company?: string;
    jobDescription?: string;
    newSession?: boolean;
  }
) {
  return apiRequest<AiResumeChatResponse>("/ai/career-coach/", {
    method: "POST",
    auth: true,
    lang: language,
    body: JSON.stringify({
      message,
      history,
      language,
      mode,
      resume_draft: resumeDraft || "",
      document_draft: resumeDraft || "",
      resume_context: resumeContext || "",
      job_title: jobContext?.jobTitle || "",
      company: jobContext?.company || "",
      job_description: jobContext?.jobDescription || "",
      new_session: Boolean(jobContext?.newSession),
      ...(chatId && !jobContext?.newSession ? { chat_id: chatId } : {}),
    }),
  });
}

export async function aiResumeAssistant(
  message: string,
  history?: { role: string; content: string }[],
  language?: string,
  resumeDraft?: string,
  chatId?: number | null,
  mode: WorkspaceMode = "resume",
  resumeContext?: string,
  jobContext?: {
    jobTitle?: string;
    company?: string;
    jobDescription?: string;
    newSession?: boolean;
  }
) {
  return aiCareerCoach(
    message,
    history,
    language,
    resumeDraft,
    chatId,
    mode,
    resumeContext,
    jobContext
  );
}

export async function aiGenerateCoverLetter(params: {
  jobTitle: string;
  company?: string;
  jobDescription?: string;
  tone?: string;
  resume?: string;
  language?: string;
}) {
  return apiRequest<{
    id: number;
    cover_letter: string;
    document_draft: string;
    key_points: string[];
  }>("/ai/cover-letter/", {
    method: "POST",
    auth: true,
    lang: params.language,
    body: JSON.stringify({
      job_title: params.jobTitle,
      company: params.company || "",
      job_description: params.jobDescription || "",
      tone: params.tone || "professional",
      resume: params.resume || "",
      language: params.language,
    }),
  });
}

export async function aiInterviewPrep(params: {
  jobTitle: string;
  company?: string;
  requirements?: string;
  difficulty?: string;
  language?: string;
}) {
  return apiRequest<{
    id: number;
    questions: unknown[];
    tips: string[];
    estimated_duration: number;
    document_draft: string;
  }>("/ai/interview-prep/", {
    method: "POST",
    auth: true,
    lang: params.language,
    body: JSON.stringify({
      job_title: params.jobTitle,
      company: params.company || "",
      requirements: params.requirements || "",
      difficulty: params.difficulty || "medium",
      language: params.language,
    }),
  });
}

export async function aiImportResumeText(params: {
  text: string;
  source?: "paste" | "linkedin" | "pdf";
  language?: string;
  save?: boolean;
}) {
  return apiRequest<{
    resume: string;
    document_draft: string;
    notes: string;
    source: string;
    saved: boolean;
  }>("/ai/import-resume/", {
    method: "POST",
    auth: true,
    lang: params.language,
    body: JSON.stringify({
      text: params.text,
      source: params.source || "paste",
      language: params.language,
      save: params.save !== false,
    }),
  });
}

export async function aiImportResumePdf(
  file: File,
  language?: string,
  save = true
) {
  const accessToken = getAccessToken();
  const form = new FormData();
  form.append("file", file);
  form.append("source", "pdf");
  form.append("save", save ? "true" : "false");
  if (language) form.append("language", language);

  const res = await fetch(`${API_BASE}/ai/import-resume/`, {
    method: "POST",
    headers: {
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(language ? { "Accept-Language": language } : {}),
    },
    body: form,
  });

  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(
      (json.message as string) || "Failed to import PDF"
    );
  }
  return (json.data ?? json) as {
    resume: string;
    document_draft: string;
    notes: string;
    source: string;
    saved: boolean;
  };
}

export type HhVacancyListItem = {
  id: string;
  name: string;
  company: string;
  area: string;
  salary: string;
  requirement: string;
  responsibility: string;
  url: string;
  published_at: string;
  source: string;
};

export type HhVacancyDetail = HhVacancyListItem & {
  description: string;
  skills: string[];
  experience: string;
  employment: string;
  demo?: boolean;
};

export async function hhSearchVacancies(params: {
  text: string;
  area?: string;
  page?: number;
  perPage?: number;
}) {
  const q = new URLSearchParams();
  q.set("text", params.text || "");
  if (params.area) q.set("area", params.area);
  q.set("page", String(params.page ?? 0));
  q.set("per_page", String(params.perPage ?? 20));
  return apiRequest<{
    items: HhVacancyListItem[];
    found: number;
    page: number;
    pages: number;
    per_page: number;
    demo?: boolean;
    warning?: string;
  }>(`/ai/hh/vacancies/?${q.toString()}`, { auth: true });
}

export async function hhGetVacancy(vacancyId: string) {
  return apiRequest<HhVacancyDetail>(
    `/ai/hh/vacancies/${encodeURIComponent(vacancyId)}/`,
    { auth: true }
  );
}

export async function hhAdaptResume(params: {
  vacancyId?: string;
  vacancyText?: string;
  vacancyTitle?: string;
  resume?: string;
  language?: string;
  save?: boolean;
}) {
  return apiRequest<{
    vacancy: HhVacancyDetail;
    adapted_resume: string;
    document_draft: string;
    match_notes: string;
    missing_skills: string[];
    saved: boolean;
  }>("/ai/hh/adapt-resume/", {
    method: "POST",
    auth: true,
    lang: params.language,
    body: JSON.stringify({
      vacancy_id: params.vacancyId || "",
      vacancy_text: params.vacancyText || "",
      vacancy_title: params.vacancyTitle || "",
      resume: params.resume || "",
      language: params.language,
      save: params.save !== false,
    }),
  });
}

export async function aiAssistant(
  message: string,
  history?: { role: string; content: string }[],
  language?: string
) {
  return apiRequest<{ reply: string }>("/ai/assistant/", {
    method: "POST",
    auth: true,
    lang: language,
    body: JSON.stringify({ message, history, language }),
  });
}

export async function aiResumeEnhance(resume: string, language?: string) {
  return apiRequest<{ enhancedResume: string }>("/ai/resume-enhance/", {
    method: "POST",
    auth: true,
    lang: language,
    body: JSON.stringify({ resume, language }),
  });
}

export async function aiAnalyzeResume(resumeUrl: string) {
  return apiRequest<ApiResumeAnalysis>("/ai/analyze-resume/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ resume_url: resumeUrl }),
  });
}

export async function aiMatchVacancy(vacancyId: string) {
  return apiRequest<ApiVacancyMatch>("/ai/match-vacancies/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ vacancy_id: vacancyId }),
  });
}

export async function aiSkillGap(targetRole: string) {
  return apiRequest<ApiSkillGap>("/ai/analyze-skill-gap/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ target_role: targetRole }),
  });
}

// ── Subscriptions ───────────────────────────────────────────────────

export async function subscribe(plan: string, billing: string) {
  return apiRequest("/subscriptions/subscribe/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ plan, billing }),
  });
}

export interface CurrentSubscription {
  plan: string;
}

export async function getCurrentSubscription() {
  return apiRequest<CurrentSubscription>("/subscriptions/current/", {
    auth: true,
  });
}

export async function cancelSubscription() {
  return apiRequest("/subscriptions/cancel/", {
    method: "POST",
    auth: true,
  });
}

export async function getSubscriptions() {
  return apiRequest("/subscriptions/", { auth: true });
}

export async function updateSubscriptionStatus(id: string, status: string) {
  return apiRequest(`/subscriptions/${id}/`, {
    method: "PATCH",
    auth: true,
    body: JSON.stringify({ status }),
  });
}

// ── Password ────────────────────────────────────────────────────────

export async function changePassword(
  currentPassword: string,
  newPassword: string
) {
  return apiRequest("/auth/change-password/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
}

export async function deleteAccount() {
  return apiRequest("/auth/delete-account/", {
    method: "DELETE",
    auth: true,
  });
}

// ── Messaging ───────────────────────────────────────────────────────

export async function getConversations() {
  return apiRequest<ApiConversation[]>("/messaging/conversations/", {
    auth: true,
  });
}

export async function getMessages(conversationId: number) {
  return apiRequest<ApiMessage[]>(
    `/messaging/conversations/${conversationId}/messages/`,
    { auth: true }
  );
}

export async function sendMessage(conversationId: number, content: string) {
  return apiRequest<ApiMessage>(
    `/messaging/conversations/${conversationId}/messages/`,
    {
      method: "POST",
      auth: true,
      body: JSON.stringify({ content }),
    }
  );
}

export async function startConversation(recipientId: number, message: string) {
  return apiRequest<ApiConversation>("/messaging/conversations/", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ recipient_id: recipientId, message }),
  });
}

// ── Types ───────────────────────────────────────────────────────────

export interface ApiUser {
  id: number;
  email: string;
  name: string;
  role: "student" | "employer" | "admin";
  language: string;
  subscription?: string;
  is_banned?: boolean;
  email_verified?: boolean;
}

export interface ApiVacancy {
  id: number;
  employer_id: number;
  title: string;
  company_name: string;
  salary: string;
  city: string;
  location: string;
  phone: string;
  job_type: string;
  description: string;
  requirements?: string;
  benefits?: string;
  status: string;
  created_at: string;
}

export interface ApiApplication {
  id: number;
  vacancy_id: string;
  employer_id: string;
  status: string;
  cover_letter?: string;
  applied_at: string;
  candidate_email?: string;
}

export interface ApiProfile {
  name: string;
  university: string;
  major: string;
  course: string;
  city: string;
  phone: string;
  github: string;
  linkedin: string;
  skills: string[];
  about: string;
  resume_text: string;
  ai_score: number;
  completion: number;
}

export interface ApiResume {
  content: string;
  file_url: string;
  ai_analysis: Record<string, unknown>;
  ai_score: number;
}

export interface ApiCompany {
  id: number;
  company_name: string;
  industry: string;
  location: string;
  website: string;
  company_size: string;
  description: string;
  logo: string;
  is_verified: boolean;
  completion: number;
}

export interface ApiSavedJob {
  id: number;
  vacancy: ApiVacancy;
  saved_at: string;
}

export interface ApiNotification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface ApiResumeAnalysis {
  id: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  overall_score: number;
  key_skills: string[];
}

export interface ApiVacancyMatch {
  id: number;
  match_score: number;
  skill_match: number;
  experience_match: number;
  missing_skills: string[];
  matching_skills: string[];
  explanation: string;
}

export interface ApiSkillGap {
  id: number;
  target_role: string;
  current_skills: string[];
  required_skills: string[];
  gap_skills: string[];
  recommendations: string[];
  estimated_learning_time: number;
}

export interface ApiConversation {
  id: number;
  participant: {
    id: number;
    name: string;
    role: string;
  };
  last_message?: string;
  unread_count: number;
  updated_at: string;
}

export interface ApiMessage {
  id: number;
  sender_id: number;
  content: string;
  is_read: boolean;
  created_at: string;
}

export function unwrapList<T>(data: { results?: T[] } | T[]): T[] {
  return Array.isArray(data) ? data : data.results ?? [];
}

export { API_BASE };