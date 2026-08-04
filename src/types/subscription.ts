// Subscription plans
export enum SubscriptionPlan {
  FREE = 'free',
  PREMIUM = 'premium',
  BUSINESS = 'business',
}

// Subscription model
export interface Subscription {
  id: string;
  userId: string;
  plan: SubscriptionPlan;
  startDate: Date;
  endDate?: Date;
  isActive: boolean;
  autoRenew: boolean;
  features: SubscriptionFeatures;
  createdAt: Date;
  updatedAt: Date;
}

// Subscription features
export interface SubscriptionFeatures {
  maxApplicationsPerMonth: number;
  maxSavedVacancies: number;
  aiMatchingEnabled: boolean;
  resumeAnalysisEnabled: boolean;
  interviewPrepEnabled: boolean;
  advancedFiltersEnabled: boolean;
  profileBadgeEnabled: boolean;
  prioritySupportEnabled: boolean;
}

// Plan details
export interface PlanDetails {
  name: SubscriptionPlan;
  price: number;
  currency: string;
  billingPeriod: 'monthly' | 'yearly';
  features: SubscriptionFeatures;
  description: string;
}

// Subscription history
export interface SubscriptionHistory {
  id: string;
  userId: string;
  plan: SubscriptionPlan;
  status: 'active' | 'expired' | 'cancelled';
  startDate: Date;
  endDate: Date;
  paymentId?: string;
  createdAt: Date;
}

// Upgrade/Downgrade payload
export interface SubscriptionChangePayload {
  newPlan: SubscriptionPlan;
  billingPeriod: 'monthly' | 'yearly';
}