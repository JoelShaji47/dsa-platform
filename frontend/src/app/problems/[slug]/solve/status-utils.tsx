"use client";

import { CheckCircle2, XCircle } from "lucide-react";
import type { Difficulty } from "@/lib/types";

export const STATUS_STYLES: Record<
  string,
  { chip: string; icon: React.ReactNode; label: string }
> = {
  ACCEPTED: {
    chip: "border-emerald-500/50 bg-emerald-500/15 text-emerald-400",
    icon: <CheckCircle2 size={16} />,
    label: "Accepted",
  },
  WRONG_ANSWER: {
    chip: "border-red-500/50 bg-red-500/15 text-red-400",
    icon: <XCircle size={16} />,
    label: "Wrong Answer",
  },
  TLE: {
    chip: "border-yellow-500/50 bg-yellow-500/15 text-yellow-300",
    icon: <XCircle size={16} />,
    label: "Time Limit Exceeded",
  },
  RUNTIME_ERROR: {
    chip: "border-orange-500/50 bg-orange-500/15 text-orange-300",
    icon: <XCircle size={16} />,
    label: "Runtime Error",
  },
  COMPILATION_ERROR: {
    chip: "border-purple-500/50 bg-purple-500/15 text-purple-300",
    icon: <XCircle size={16} />,
    label: "Compilation Error",
  },
};

export const DIFFICULTY_STYLE: Record<Difficulty, string> = {
  EASY: "text-emerald-400",
  MEDIUM: "text-yellow-300",
  HARD: "text-red-400",
};

const STATUS_KEY_LABELS: Record<string, string> = {
  ACCEPTED: "Accepted",
  WRONG_ANSWER: "Wrong Answer",
  TIME_LIMIT_EXCEEDED: "Time Limit Exceeded",
  COMPILATION_ERROR: "Compilation Error",
  RUNTIME_ERROR_SIGSEGV: "Runtime Error",
  RUNTIME_ERROR_SIGXFSZ: "Runtime Error",
  RUNTIME_ERROR_SIGFPE: "Runtime Error",
  RUNTIME_ERROR_SIGABRT: "Runtime Error",
  RUNTIME_ERROR_UNKNOWN: "Runtime Error",
  INTERNAL_ERROR: "Judge Error",
  EXEC_FORMAT_ERROR: "Runtime Error",
};

export function statusKeyLabel(key: string): string {
  if (STATUS_KEY_LABELS[key]) return STATUS_KEY_LABELS[key];
  return key
    .toLowerCase()
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function errDetail(err: unknown): string {
  const detail = (
    err as { response?: { data?: { detail?: string } } }
  )?.response?.data?.detail;
  return detail || "Could not reach the judge. Try again.";
}
