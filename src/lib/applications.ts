import {
  applyToVacancy as applyApi,
  fetchEmployerApplications,
  fetchStudentApplications,
  changeApplicationStatus as changeStatusApi,
} from "@/lib/vacancies";

export type ApplyPayload = {
  vacancyId?: string | number;
  coverLetter?: string;
  [key: string]: unknown;
};

export async function applyToVacancy(
  vacancyOrPayload: string | number | ApplyPayload,
  coverLetter?: string
) {
  if (typeof vacancyOrPayload === "object") {
    return applyApi(
      vacancyOrPayload.vacancyId!,
      vacancyOrPayload.coverLetter
    );
  }

  return applyApi(
    vacancyOrPayload,
    coverLetter
  );
}

export const createApplication =
  applyToVacancy;

export async function getStudentApplications() {
  return fetchStudentApplications();
}

export async function getEmployerApplications() {
  return fetchEmployerApplications();
}

export async function updateApplicationStatus(
  id: string | number,
  status: string
) {
  return changeStatusApi(
    Number(id),
    status
  );
}