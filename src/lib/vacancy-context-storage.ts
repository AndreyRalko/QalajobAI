export type StoredVacancyContext = {
  jobTitle: string;
  company: string;
  jobDescription: string;
  url?: string;
};

const STORAGE_KEY = "qalajob:vacancy-context";

export function saveVacancyContext(context: StoredVacancyContext) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(context));
}

export function loadVacancyContext(): StoredVacancyContext | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredVacancyContext;
    if (!parsed?.jobTitle?.trim()) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function buildVacancyDescription(vacancy: {
  name?: string;
  company?: string;
  area?: string;
  salary?: string;
  requirement?: string;
  responsibility?: string;
  url?: string;
}) {
  const parts = [
    vacancy.area ? `Город: ${vacancy.area}` : "",
    vacancy.salary ? `Зарплата: ${vacancy.salary}` : "",
    vacancy.requirement ? `Требования: ${vacancy.requirement}` : "",
    vacancy.responsibility ? `Обязанности: ${vacancy.responsibility}` : "",
    vacancy.url ? `Ссылка: ${vacancy.url}` : "",
  ].filter(Boolean);
  return parts.join("\n\n");
}
