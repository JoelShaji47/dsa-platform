"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type ToastVariant = "default" | "destructive";

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: ToastVariant;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  toast: (props: Omit<Toast, "id">) => string;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

/**
 * Module-level hook so the API client (which can't use React hooks) can
 * surface errors as toasts once the provider has mounted.
 */
export let onError: ((message: string) => void) | null = null;
export function setErrorHandler(fn: (message: string) => void) {
  onError = fn;
}

let nextId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((t) => t.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (props: Omit<Toast, "id">) => {
      const id = (++nextId).toString();
      const entry: Toast = { id, duration: 4000, ...props };
      setToasts((t) => [...t, entry]);
      return id;
    },
    []
  );

  const value = useMemo(
    () => ({ toasts, toast, dismiss }),
    [toasts, toast, dismiss]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
