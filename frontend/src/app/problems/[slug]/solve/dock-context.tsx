"use client";

import { createContext, useContext } from "react";
import type {
  HintMetaOut,
  Language,
  ProblemDetail,
  ReviewOut,
  RunMode,
  RunResultOut,
  SubmissionHistoryItem,
  SubmissionResultOut,
  SubmissionStatus,
} from "@/lib/types";
import type { CoachMessage } from "./assistant-panel";
import type { EditableCase } from "./console-panel";

export interface DockValue {
  problem: ProblemDetail;
  slug: string;
  lang: Language;
  mode: RunMode;
  code: string;
  runCount: number;
  onCode: (v: string) => void;
  onModeChange: (m: RunMode) => void;
  onLangChange: (l: Language) => void;
  run: () => void;
  submit: () => void;
  running: boolean;
  submitting: boolean;
  submissions: SubmissionHistoryItem[];
  submissionsLoading: boolean;
  refreshSubmissions: () => void;
  hintMeta: HintMetaOut | null;
  revealedHints: Record<number, string>;
  armedHint: number | null;
  loadingHint: number | null;
  onHintClick: (level: number) => void;
  error: string | null;
  runResult: RunResultOut | null;
  submitResult: SubmissionResultOut | null;
  shown: RunResultOut | SubmissionResultOut | null;
  shownStatus: SubmissionStatus | undefined;
  consoleTab: string;
  setConsoleTab: (t: string) => void;
  editableCases: EditableCase[];
  onEditCase: (index: number, field: "input" | "expected_output", value: string) => void;
  onRunEditableCases: () => void;
  editableRunning: boolean;
  onResetEditableCases: () => void;
  review: ReviewOut | null;
  reviewLoading: boolean;
  fetchReview: () => void;
  focusConsole: () => void;
  coachMessages: CoachMessage[];
  coachLoading: boolean;
  coachProvider: string | null;
  includeCode: boolean;
  onToggleInclude: () => void;
  onSendCoach: (text: string) => void;
  onClearCoach: () => void;
  closeCoach: () => void;
  contextNote: string;
}

export const DockContext = createContext<DockValue | null>(null);

export function useDock(): DockValue {
  const ctx = useContext(DockContext);
  if (!ctx) throw new Error("dock panel must render inside DockContext");
  return ctx;
}
