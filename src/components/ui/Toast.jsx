import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import useUiStore from '@/store/uiStore';

const icons = { success: CheckCircle, error: AlertCircle, warning: AlertTriangle, info: Info };

function ToastItem({ toast }) {
  const { removeToast } = useUiStore();
  const Icon = icons[toast.type] || Info;

  useEffect(() => {
    const timer = setTimeout(() => removeToast(toast.id), toast.duration || 4000);
    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, removeToast]);

  return (
    <div className={`toast toast-${toast.type || 'info'}`}>
      <Icon className="toast-icon" size={20} />
      <span className="toast-message">{toast.message}</span>
      <button className="toast-close" onClick={() => removeToast(toast.id)}><X size={16} /></button>
    </div>
  );
}

export default function Toast() {
  const { toasts } = useUiStore();
  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((t) => <ToastItem key={t.id} toast={t} />)}
    </div>
  );
}
