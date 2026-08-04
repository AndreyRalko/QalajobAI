import {
  fetchEmployerApplications,
  fetchEmployerVacancies,
  changeApplicationStatus,
  createVacancyApi,
  updateVacancyApi,
  deleteVacancyApi,
} from "@/lib/vacancies";

import {
  getCompany,
  saveCompany,
  getMe,
  subscribe,
} from "@/lib/api";

export async function getEmployerVacancies() {
  const vacancies =
    await fetchEmployerVacancies();

  return vacancies.map((item: any) => ({
    id: String(item.id),
    employerId: String(item.employer_id),
    title: item.title,
    company: item.company_name,
    salary: item.salary,
    city: item.city,
    location: item.location,
    phone: item.phone,
    type: item.job_type,
    description: item.description,
    createdAt: item.created_at,
  }));
}

export async function getEmployerApplications() {
  const applications =
    await fetchEmployerApplications();

  return applications.map(
    (item: any) => ({
      id: String(item.id),
      vacancyId: item.vacancy_id,
      employerId: item.employer_id,
      studentEmail:
        item.candidate_email,
      studentName:
        item.candidate_email,
      vacancyTitle:
        `Vacancy #${item.vacancy_id}`,
      status: item.status,
    })
  );
}

export async function updateEmployerApplicationStatus(
  applicationId: string,
  status: string
) {
  return changeApplicationStatus(
    Number(applicationId),
    status
  );
}

export async function createEmployerVacancy(
  vacancy: any
) {
  return createVacancyApi({
    title: vacancy.title,
    company_name:
      vacancy.company,
    salary: vacancy.salary,
    city: vacancy.city,
    location:
      vacancy.location,
    phone: vacancy.phone,
    job_type: vacancy.type,
    description:
      vacancy.description,
  });
}

export async function updateEmployerVacancy(
  vacancyId: string,
  vacancy: any
) {
  return updateVacancyApi(
    vacancyId,
    {
      title: vacancy.title,
      company_name:
        vacancy.company,
      salary: vacancy.salary,
      city: vacancy.city,
      location:
        vacancy.location,
      phone: vacancy.phone,
      job_type: vacancy.type,
      description:
        vacancy.description,
    }
  );
}

export async function deleteEmployerVacancy(
  vacancyId: string
) {
  return deleteVacancyApi(
    vacancyId
  );
}

export async function getCompanyForEmployer() {
  return getCompany();
}

export async function saveCompanyForEmployer(
  data: any
) {
  return saveCompany(data);
}

export async function getEmployerUser() {
  return getMe();
}

export async function changeEmployerSubscription(
  plan: string
) {
  return subscribe(
    plan,
    "monthly"
  );
}