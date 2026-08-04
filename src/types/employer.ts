export type EmployerSubscription =
  | "free"
  | "pro"
  | "business"
  | "Free"
  | "Pro"
  | "Business";

export interface EmployerUser {
  uid: string;
  name: string;
  email: string;
  role: "employer";
  phone?: string;
  position?: string;
  photoURL?: string;
  subscription?: EmployerSubscription;
}

export interface CompanyProfile {
  ownerId: string;
  companyName: string;
  industry: string;
  location: string;
  website: string;
  companySize: string;
  description: string;
  logo?: string;
}

export interface EmployerVacancy {
  id?: string;
  employerId: string;
  title: string;
  salary: string;
  city: string;
  company?: string;
  location?: string;
  phone?: string;
  type: string;
  description: string;
  createdAt?: Date | null;
}

export type ApplicationStatus =
  | "pending"
  | "accepted"
  | "rejected";

export interface EmployerApplication {
  id?: string;
  vacancyId: string;
  studentId: string;
  employerId: string;
  status: ApplicationStatus;
  createdAt?: Date | null;
  studentName?: string;
  studentEmail?: string | null;
  university?: string;
  resume?: string;
  vacancyTitle?: string;
}