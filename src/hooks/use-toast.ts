'use client';

import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';

export interface Toast {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export const useToast = () => {
  return {
    toast: (props: Toast) => {
      if (props.variant === 'destructive') {
        toast.error(props.description || props.title || 'An error occurred');
      } else {
        toast.success(props.description || props.title || 'Success');
      }
    },
  };
};