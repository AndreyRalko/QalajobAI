'use client';

import React, { useState } from 'react';
import { ApplicationPayload } from '@/types/application';
import { Button } from '@/app/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/app/components/ui/dialog';
import { Label } from '@/app/components/ui/label';
import { Textarea } from '@/app/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { AlertCircle, FileUp } from 'lucide-react';

interface ApplicationFormProps {
  vacancyId: string;
  onSubmit?: (data: ApplicationPayload) => Promise<void>;
  onSuccess?: () => void;
  trigger?: React.ReactNode;
}

export const ApplicationForm: React.FC<ApplicationFormProps> = ({
  vacancyId,
  onSubmit,
  onSuccess,
  trigger,
}) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ApplicationPayload>({
    vacancyId,
  });
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.vacancyId) {
      toast({
        title: 'Ошибка',
        description: 'Выберите вакансию',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      if (onSubmit) {
        await onSubmit(formData);
      }

      toast({
        title: 'Успешно',
        description: 'Ваша заявка отправлена',
      });

      setFormData({ vacancyId });
      setOpen(false);
      onSuccess?.();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error instanceof Error ? error.message : 'Не удалось отправить заявку',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>Откликнуться</Button>}
      </DialogTrigger>

      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Подать заявку на вакансию</DialogTitle>
          <DialogDescription>
            Заполните форму для отправки вашей заявки работодателю
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-blue-50 p-3 rounded flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-800">
              Убедитесь, что ваш профиль заполнен полностью. Работодатели смогут видеть вашу информацию.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="coverLetter">Сопроводительное письмо</Label>
            <Textarea
              id="coverLetter"
              placeholder="Расскажите работодателю, почему вы подходите для этой позиции..."
              value={formData.coverLetter || ''}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setFormData((prev) => ({ ...prev, coverLetter: e.target.value }))
              }
              className="min-h-32"
            />
            <p className="text-xs text-gray-500">
              {(formData.coverLetter || '').length} / 2000 символов
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="resume" className="flex items-center gap-2">
              <FileUp className="w-4 h-4" />
              Прикрепить резюме
            </Label>
            <input
              type="file"
              id="resume"
              accept=".pdf,.doc,.docx"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  setFormData((prev) => ({
                    ...prev,
                    resume: file.name,
                  }));
                }
              }}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {formData.resume && (
              <p className="text-sm text-green-600">✓ Файл выбран: {formData.resume}</p>
            )}
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={loading}
            >
              Отмена
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Отправка...' : 'Отправить заявку'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};