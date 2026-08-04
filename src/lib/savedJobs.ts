import {
  getSavedJobs as getSavedJobsApi,
  saveJob as saveJobApi,
  unsaveJob,
} from "@/lib/api";

export async function fetchSavedJobs() {
  return getSavedJobsApi();
}

export async function getSavedJobs() {
  return getSavedJobsApi();
}

export async function saveJob(
  vacancyId: string | number
) {
  return saveJobApi(vacancyId);
}

export async function addSavedJob(
  vacancyId: string | number
) {
  return saveJobApi(vacancyId);
}

export async function removeSavedJob(
  savedJobId: number
) {
  return unsaveJob(savedJobId);
}