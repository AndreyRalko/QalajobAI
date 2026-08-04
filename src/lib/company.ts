import { saveCompany, getCompany } from "@/lib/api";

export async function saveCompanyProfile(data: Record<string, unknown>) {
  return saveCompany(data);
}

export async function getCompanyProfile() {
  return getCompany();
}
