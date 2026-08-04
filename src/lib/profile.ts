import { getProfile as getProfileApi, saveProfile as saveProfileApi, type ApiProfile } from "@/lib/api";

export type ProfileData = Omit<ApiProfile, "skills"> & { resume?: string; skills: string };

export async function getProfile(_uid?: string): Promise<ProfileData> {
  const data = await getProfileApi();
  return {
    ...data,
    resume: data.resume_text,
    skills: Array.isArray(data.skills) ? data.skills.join(", ") : data.skills || "",
  };
}

export async function saveProfile(uidOrData: string | Record<string, unknown>, data?: Record<string, unknown>) {
  const payload = typeof uidOrData === "string" ? (data || {}) : uidOrData;
  if (typeof payload.skills === "string") {
    payload.skills = (payload.skills as string)
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return saveProfileApi(payload);
}

export async function getUserProfile() {
  return getProfile();
}

export async function updateUserProfile(data: Record<string, unknown>) {
  return saveProfile(data);
}

export function calculateProfileCompletion(profile: ProfileData | Record<string, unknown> | null): number {
  if (!profile) return 0;
  const p = profile as ProfileData;
  if (typeof p.completion === "number") return p.completion;
  const fields = [p.name, p.university, p.major, p.city, p.skills, p.about];
  const filled = fields.filter((f) => (Array.isArray(f) ? f.length : f)).length;
  return Math.round((filled / fields.length) * 100);
}

export function calculateAIScore(
  profile: ProfileData | Record<string, unknown> | null,
  resumeText = ""
): number {
  if (!profile) return 0;
  const p = profile as ProfileData;
  if (p.ai_score) return p.ai_score;
  const completion = calculateProfileCompletion(profile);
  const skillsArr = Array.isArray(p.skills) ? p.skills : String(p.skills || "").split(",").filter(Boolean);
  const skillsBonus = Math.min(skillsArr.length * 5, 30);
  const resumeBonus = (resumeText || p.resume_text || p.resume || "").length > 100 ? 10 : 0;
  return Math.min(completion + skillsBonus + resumeBonus, 100);
}

export function analyzeResume(
  textOrProfile: string | ProfileData | Record<string, unknown>
): { strengths: string[]; gaps: string[]; score: number } {
  const text =
    typeof textOrProfile === "string"
      ? textOrProfile
      : String(
          (textOrProfile as ProfileData).resume_text ||
            (textOrProfile as ProfileData).resume ||
            ""
        );
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  const score = Math.min(Math.round(words / 5), 100);
  return {
    strengths: words > 50 ? ["Detailed experience", "Good length"] : ["Concise format"],
    gaps: words < 100 ? ["Add more project details", "Include measurable achievements"] : [],
    score,
  };
}

export function calculateJobMatch(
  profile: ProfileData | Record<string, unknown> | null,
  vacancy: { title?: string; description?: string }
): number {
  if (!profile) return 50;
  const p = profile as ProfileData;
  const skills = Array.isArray(p.skills)
    ? p.skills
    : String(p.skills || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
  const text = `${vacancy.title || ""} ${vacancy.description || ""}`.toLowerCase();
  const matches = skills.filter((s) => text.includes(String(s).toLowerCase())).length;
  return Math.min(50 + matches * 10, 99);
}
