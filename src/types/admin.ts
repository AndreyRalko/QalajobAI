// Admin roles
export enum AdminRole {
  SUPER_ADMIN = 'super_admin',
  MODERATOR = 'moderator',
  ANALYST = 'analyst',
}

// User status
export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  BANNED = 'banned',
}

// Admin action types
export enum AdminActionType {
  USER_BAN = 'user_ban',
  USER_UNBAN = 'user_unban',
  VACANCY_REMOVE = 'vacancy_remove',
  VACANCY_APPROVE = 'vacancy_approve',
  COMPANY_BAN = 'company_ban',
  COMPANY_UNBAN = 'company_unban',
  APPLICATION_REVIEW = 'application_review',
  PREMIUM_GRANT = 'premium_grant',
  PREMIUM_REVOKE = 'premium_revoke',
  SYSTEM_SETTING_CHANGE = 'system_setting_change',
}

// Dashboard analytics
export interface DashboardAnalytics {
  totalUsers: number;
  totalEmployers: number;
  totalCandidates: number;
  activeSubscriptions: number;
  totalVacancies: number;
  totalApplications: number;
  pendingApplications: number;
  totalRevenue: number;
  chartData: ChartData[];
}

// Chart data
export interface ChartData {
  label: string;
  value: number;
  date?: Date;
}

// Audit log entry
export interface AuditLogEntry {
  id: string;
  adminId: string;
  actionType: AdminActionType;
  targetUserId?: string;
  targetId?: string;
  details: Record<string, any>;
  timestamp: Date;
  ipAddress?: string;
  userAgent?: string;
}

// User management
export interface UserManagement {
  id: string;
  email: string;
  name: string;
  role: 'candidate' | 'employer' | 'admin';
  status: UserStatus;
  subscription?: {
    plan: string;
    expiresAt: Date;
  };
  createdAt: Date;
  lastLogin?: Date;
}

// Ban/Unban request
export interface BanRequest {
  userId: string;
  reason: string;
  duration?: number; // in days, null for permanent
}

// System settings
export interface SystemSettings {
  id: string;
  maintenanceMode: boolean;
  maxUploadSize: number;
  defaultCurrency: string;
  supportEmail: string;
  termsVersion: string;
  privacyVersion: string;
  updatedAt: Date;
  updatedBy: string;
}

// Moderation queue item
export interface ModerationQueueItem {
  id: string;
  type: 'vacancy' | 'company' | 'profile';
  targetId: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: Date;
  reviewedAt?: Date;
  reviewedBy?: string;
  notes?: string;
}

// Platform statistics
export interface PlatformStatistics {
  totalUsers: number;
  totalActiveUsers: number;
  totalVacancies: number;
  filledVacancies: number;
  averageApplicationsPerVacancy: number;
  successRate: number;
  averageTimeToHire: number;
  totalTransactions: number;
  totalRevenue: number;
  averageRevenuePerUser: number;
  retentionRate: number;
  churnRate: number;
}