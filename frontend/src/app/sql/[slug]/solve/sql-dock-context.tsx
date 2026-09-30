"use client";

import { createContext, useContext } from "react";
import type {
  HintMetaOut,
  ProblemDetail,
  ReviewOut,
  RunResultOut,
  SubmissionHistoryItem,
  SubmissionResultOut,
  SubmissionStatus,
} from "@/lib/types";
import type { CoachMessage } from "../../../problems/[slug]/solve/assistant-panel";
import type { EditableCase } from "../../../problems/[slug]/solve/console-panel";

export interface SqlDockValue {
  problem: ProblemDetail;
  slug: string;
  code: string;
  runCount: number;
  onCode: (v: string) => void;
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

export const SqlDockContext = createContext<SqlDockValue | null>(null);

export function useSqlDock(): SqlDockValue {
  const ctx = useContext(SqlDockContext);
  if (!ctx) throw new Error("dock panel must render inside SqlDockContext");
  return ctx;
}
