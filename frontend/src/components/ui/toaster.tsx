"use client";

import { useMemo } from "react";
import { useToast } from "@/context/toast-context";
import { Toast as ToastItem } from "@/components/ui/toast";

export function Toaster() {
  const { toasts, dismiss } = useToast();
  const visible = useMemo(() => toasts.slice().reverse(), [toasts]); // newest on top

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {visible.map((t) => (
        <div key={t.id} className="pointer-events-auto">
          <ToastItem toast={t} onDismiss={() => dismiss(t.id)} />
        </div>
      ))}
    </div>
  );
}
