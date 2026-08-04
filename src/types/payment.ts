// Payment providers
export enum PaymentProvider {
  STRIPE = 'stripe',
  KASPI = 'kaspi',
  HALYK = 'halyk',
}

// Payment status
export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
  CANCELLED = 'cancelled',
}

// Payment method type
export enum PaymentMethodType {
  CARD = 'card',
  BANK_TRANSFER = 'bank_transfer',
  MOBILE_WALLET = 'mobile_wallet',
}

// Payment record
export interface Payment {
  id: string;
  userId: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  provider: PaymentProvider;
  methodType: PaymentMethodType;
  transactionId: string;
  subscriptionId?: string;
  invoiceId?: string;
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

// Payment intent
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  provider: PaymentProvider;
  clientSecret?: string;
  status: PaymentStatus;
  expiresAt: Date;
}

// Invoice
export interface Invoice {
  id: string;
  userId: string;
  paymentId: string;
  amount: number;
  currency: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  issuedAt: Date;
  dueDate: Date;
  paidAt?: Date;
  items: InvoiceItem[];
  notes?: string;
}

// Invoice item
export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
}

// Payment history
export interface PaymentHistory {
  id: string;
  userId: string;
  payments: Payment[];
  totalAmount: number;
  currency: string;
  period: {
    startDate: Date;
    endDate: Date;
  };
}

// Payment webhook payload
export interface PaymentWebhookPayload {
  provider: PaymentProvider;
  eventType: string;
  data: Record<string, any>;
  timestamp: Date;
}

// Refund request
export interface RefundRequest {
  paymentId: string;
  reason: string;
  amount?: number;
}