"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { X, CheckCircle2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Toast } from "@/context/toast-context";

interface ToastProps {
  toast: Toast;
  onDismiss: () => void;
}

const ICONS: Record<
  NonNullable<Toast["variant"]>,
  React.ComponentType<{ className?: string; size?: number }>
> = {
  default: CheckCircle2,
  destructive: AlertTriangle,
};

export function Toast({ toast, onDismiss }: ToastProps) {
  const [dismissing, setDismissing] = useState(false);
  const [paused, setPaused] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dismiss = useCallback(() => {
    setDismissing(true);
    timer.current && clearTimeout(timer.current);
    setTimeout(() => onDismiss(), 120); // match exit transition
  }, [onDismiss]);

  const restart = useCallback(() => {
    timer.current && clearTimeout(timer.current);
    if (paused || dismissing) return;
    timer.current = setTimeout(() => onDismiss(), toast.duration ?? 4000);
  }, [paused, dismissing, toast.duration, onDismiss]);

  useEffect(() => {
    restart();
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [restart]);

  const variant = toast.variant ?? "default";
  const Icon = ICONS[variant];
  const accent = variant === "destructive" ? "text-rust border-rust/30" : "text-quest border-quest/30";

  return (
    <div
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onClick={dismiss}
      className={cn(
        "group flex items-center gap-3 rounded-lg border bg-paper p-3 text-ink shadow-card transition-all duration-120",
        accent,
        dismissing && "opacity-0 translate-x-4 pointer-events-none",
      )}
      role="alert"
      aria-live="polite"
    >
      <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-paper-deep">
        <Icon size={14} className={cn("text-current", variant === "destructive" ? "text-rust" : "text-quest")} />
      </div>
      <div className="min-w-0 flex-1">
        {toast.title && (
          <p className="text-sm font-semibold text-ink">{toast.title}</p>
        )}
        {toast.description && (
          <p className={cn("text-xs text-ink-soft", toast.title && "mt-1")}>
            {toast.description}
          </p>
        )}
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          dismiss();
        }}
        className="shrink-0 p-1 text-ink-soft hover:text-rust transition-colors"
        aria-label="Dismiss"
      >
        <X size={13} />
      </button>
    </div>
  );
}
