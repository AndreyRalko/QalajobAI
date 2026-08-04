'use client';

import React from 'react';
import { Application, ApplicationStatus } from '@/types/application';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/app/components/ui/card';
import { CheckCircle2, Clock, MessageCircle, XCircle } from 'lucide-react';

interface ApplicationCardProps {
  application: Application;
  onViewDetails?: (id: string) => void;
  onWithdraw?: (id: string) => void;
  isEmployerView?: boolean;
  onReview?: (id: string) => void;
}

const statusConfig: Record<ApplicationStatus, { icon: React.ReactNode; color: string; label: string }> = {
  [ApplicationStatus.PENDING]: {
    icon: <Clock className="w-4 h-4" />,
    color: 'bg-yellow-100 text-yellow-800',
    label: 'На рассмотрении',
  },
  [ApplicationStatus.REVIEWING]: {
    icon: <MessageCircle className="w-4 h-4" />,
    color: 'bg-blue-100 text-blue-800',
    label: 'Проверяется',
  },
  [ApplicationStatus.INTERVIEW]: {
    icon: <Clock className="w-4 h-4" />,
    color: 'bg-purple-100 text-purple-800',
    label: 'Собеседование',
  },
  [ApplicationStatus.ACCEPTED]: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    color: 'bg-green-100 text-green-800',
    label: 'Принято',
  },
  [ApplicationStatus.REJECTED]: {
    icon: <XCircle className="w-4 h-4" />,
    color: 'bg-red-100 text-red-800',
    label: 'Отклонено',
  },
  [ApplicationStatus.WITHDRAWN]: {
    icon: <XCircle className="w-4 h-4" />,
    color: 'bg-gray-100 text-gray-800',
    label: 'Отозвано',
  },
};

export const ApplicationCard: React.FC<ApplicationCardProps> = ({
  application,
  onViewDetails,
  onWithdraw,
  isEmployerView = false,
  onReview,
}) => {
  const statusInfo = statusConfig[application.status];

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">Заявка #{application.id.slice(-6)}</CardTitle>
            <CardDescription>
              Отправлено {new Date(application.appliedAt).toLocaleDateString('ru-RU')}
            </CardDescription>
          </div>
          <Badge className={statusInfo.color}>
            <span className="flex items-center gap-1">
              {statusInfo.icon}
              {statusInfo.label}
            </span>
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {application.notes && (
          <div className="text-sm text-gray-600">
            <p className="font-medium text-gray-700">Примечания:</p>
            <p>{application.notes}</p>
          </div>
        )}

        {application.interviewDate && (
          <div className="text-sm bg-blue-50 p-2 rounded">
            <p className="font-medium text-blue-900">
              Собеседование запланировано на:{' '}
              {new Date(application.interviewDate).toLocaleString('ru-RU')}
            </p>
          </div>
        )}

        {application.rejectionReason && application.status === ApplicationStatus.REJECTED && (
          <div className="text-sm bg-red-50 p-2 rounded">
            <p className="font-medium text-red-900">Причина отклонения:</p>
            <p className="text-red-800">{application.rejectionReason}</p>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          {onViewDetails && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onViewDetails(application.id)}
            >
              Просмотр
            </Button>
          )}

          {!isEmployerView && application.status === ApplicationStatus.PENDING && onWithdraw && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => onWithdraw(application.id)}
            >
              Отозвать
            </Button>
          )}

          {isEmployerView && onReview && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onReview(application.id)}
            >
              Рассмотреть
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};