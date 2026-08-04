// Application statuses
export enum ApplicationStatus {
  PENDING = 'pending',
  REVIEWING = 'reviewing',
  INTERVIEW = 'interview',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  WITHDRAWN = 'withdrawn',
}

// Application model
export interface Application {
  id: string;
  vacancyId: string;
  candidateId: string;
  employerId: string;
  status: ApplicationStatus;
  appliedAt: Date;
  updatedAt: Date;
  resume?: string;
  coverLetter?: string;
  notes?: string;
  interviewDate?: Date;
  rejectionReason?: string;
}

// Application form payload
export interface ApplicationPayload {
  vacancyId: string;
  resume?: string;
  coverLetter?: string;
}

// Application history entry
export interface ApplicationHistoryEntry {
  applicationId: string;
  status: ApplicationStatus;
  changedAt: Date;
  changedBy: string;
  notes?: string;
}

// Application statistics
export interface ApplicationStats {
  totalApplications: number;
  pendingCount: number;
  reviewingCount: number;
  interviewCount: number;
  acceptedCount: number;
  rejectedCount: number;
  withdrawnCount: number;
}