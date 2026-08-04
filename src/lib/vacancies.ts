import {
  applyToVacancy as applyApi,
  createVacancy,
  deleteVacancy,
  getEmployerApplicationsApi,
  getEmployerVacanciesApi,
  getStudentApplications,
  getVacancies as getVacanciesApi,
  getVacancy,
  pauseVacancy,
  archiveVacancy,
  updateApplicationStatus,
  updateVacancy,
  unwrapList,
  
  type ApiVacancy,
} from "@/lib/api";

export type Vacancy = ApiVacancy & {
  id: string | number;
  employerId?: string | number;
  company?: string;
  type?: string;
  skills?: string[];
  resume?: string;
};

function mapVacancy(v: ApiVacancy): Vacancy {
  return {
    ...v,
    id: v.id,
    employerId: v.employer_id,
    company: v.company_name,
    type: v.job_type,
    skills: [],
  };
}

export const fetchVacancies = async (params?: Record<string, string>) => {
  const data = await getVacanciesApi(params);
  return unwrapList(data).map(mapVacancy);
};

export const getVacancies = fetchVacancies;

export const fetchVacancyById = async (id: string | number) => mapVacancy(await getVacancy(id));
export const getVacancyById = fetchVacancyById;

export async function createVacancyApi(data: Record<string, unknown>) {
  return createVacancy(data);
}

export async function updateVacancyApi(id: string | number, data: Record<string, unknown>) {
  return updateVacancy(id, data);
}

export async function deleteVacancyApi(id: string | number) {
  return deleteVacancy(id);
}

export async function pauseVacancyApi(id: string | number) {
  return pauseVacancy(id);
}

export async function archiveVacancyApi(id: string | number) {
  return archiveVacancy(id);
}

export async function fetchEmployerVacancies() {
  const data = await getEmployerVacanciesApi();
  return unwrapList(data).map(mapVacancy);
}

export async function applyToVacancy(vacancyId: string | number, coverLetter?: string) {
  return applyApi(vacancyId, coverLetter);
}

export async function submitApplication(vacancyId: string | number, coverLetter?: string) {
  return applyApi(vacancyId, coverLetter);
}

export async function fetchStudentApplications() {
  return getStudentApplications();
}

export async function fetchEmployerApplications() {
  return getEmployerApplicationsApi();
}

export async function changeApplicationStatus(applicationId: number, status: string) {
  return updateApplicationStatus(applicationId, status);
}

export type { ApiVacancy };
