"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Award,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Check,
  Clock,
  EyeOff,
  FileCode2,
  History,
  Lightbulb,
  Loader2,
  Play,
  Send,
  Sparkles,
  SquareTerminal,
  XCircle,
  Zap,
} from "lucide-react";
import CodeMirror from "@uiw/react-codemirror";
import { ArrowLeft, Brain, Loader2, Play, Send } from "lucide-react";
import { DockviewReact } from "dockview-react";
import type { DockviewApi, DockviewReadyEvent } from "dockview-core";
import "./dockview-base.css";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import client from "@/lib/api";
import { CodeEditor } from "@/components/arena/code-editor";
import { ProblemStatement } from "@/components/arena/problem-statement";
import { ThemeToggle, useTheme } from "@/context/theme-context";
import type {
  CustomRunOut,
  Difficulty,
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
import { type CoachMessage } from "./assistant-panel";
import { DockContext, type DockValue } from "./dock-context";
import {
  CoachTabPanel,
  CodeTabPanel,
  ConsoleTabPanel,
  DescriptionTabPanel,
  SubmissionsTabPanel,
} from "./dock-panels";
import { DIFFICULTY_STYLE, errDetail } from "./status-utils";

const LANGS: { key: Language; label: string; ext: () => unknown }[] = [
  { key: "python", label: "Python", ext: python },
  { key: "cpp", label: "C++", ext: cpp },
  { key: "java", label: "Java", ext: java },
];

const DOCK_COMPONENTS = {
  description: DescriptionTabPanel,
  submissions: SubmissionsTabPanel,
  code: CodeTabPanel,
  console: ConsoleTabPanel,
  coach: CoachTabPanel,
};
const STATUS_STYLES: Record<string, { chip: string; icon: React.ReactNode; label: string }> = {
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

const DIFFICULTY_STYLE: Record<Difficulty, string> = {
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

function statusKeyLabel(key: string): string {
  if (STATUS_KEY_LABELS[key]) return STATUS_KEY_LABELS[key];
  return key
    .toLowerCase()
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function errDetail(err: unknown): string {
  const detail = (
    err as { response?: { data?: { detail?: string } } }
  )?.response?.data?.detail;
  return detail || "Could not reach the judge. Try again.";
}

function TestChip({ passed, index }: { passed: boolean; index: number }) {
  return (
    <span
      title={`Test ${index + 1}: ${passed ? "passed" : "failed"}`}
      className={`flex h-7 w-7 items-center justify-center rounded-md border font-mono text-xs font-bold ${
        passed
          ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
          : "border-red-500/50 bg-red-500/15 text-red-400"
      }`}
    >
      {index + 1}
    </span>
  );
}

function DescriptionTab({ problem }: { problem: ProblemDetail }) {
  return <ProblemStatement text={problem.description} />;
}

function SubmissionsTab({
  submissions,
  loading,
}: {
  submissions: SubmissionHistoryItem[];
  loading: boolean;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-gray-500">
        <Loader2 size={16} className="mr-2 animate-spin" />
        Loading submissions...
      </div>
    );
  }
  if (!submissions.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <History size={32} className="mb-3 text-gray-600" />
        <p className="text-sm text-gray-500">No submissions yet</p>
        <p className="mt-1 text-xs text-gray-600">Submit your code to see results here</p>
      </div>
    );
  }

  const langMap: Record<string, () => unknown> = { python, cpp, java };

  return (
    <div className="space-y-1.5">
      {submissions.map((s) => {
        const style = STATUS_STYLES[s.status] || {
          chip: "text-gray-400",
          icon: null,
          label: s.status,
        };
        const passed = s.status === "ACCEPTED";
        const totalPassed = s.judge_summary
          ? s.judge_summary.filter((t) => t.passed).length
          : null;
        const totalTests = s.judge_summary ? s.judge_summary.length : null;
        const isExpanded = expanded === s.submission_id;
        return (
          <div
            key={s.submission_id}
            className={`overflow-hidden rounded-lg border transition-colors ${
              passed
                ? "border-emerald-500/30 bg-emerald-500/5"
                : "border-white/10 bg-white/[0.02]"
            }`}
          >
            <button
              onClick={() => setExpanded(isExpanded ? null : s.submission_id)}
              className="flex w-full items-center gap-3 px-3 py-2.5 text-left transition-colors hover:bg-white/[0.03]"
            >
              <ChevronRight
                size={14}
                className={`shrink-0 text-gray-500 transition-transform ${isExpanded ? "rotate-90" : ""}`}
              />
              <span className={`flex items-center gap-1.5 text-xs font-medium ${style.chip}`}>
                {style.icon}
                {style.label}
              </span>
              <span className="rounded-md bg-white/5 px-2 py-0.5 font-mono text-[11px] text-gray-400">
                {s.language}
              </span>
              {totalPassed !== null && (
                <span className="text-[11px] text-gray-500">
                  {totalPassed}/{totalTests}
                </span>
              )}
              <span className="ml-auto flex items-center gap-3">
                <span className="flex items-center gap-1 text-[11px] text-gray-500">
                  <Clock size={11} />
                  {s.runtime_ms != null ? `${s.runtime_ms.toFixed(0)} ms` : "—"}
                </span>
                <span className="text-[11px] text-gray-500">
                  {s.memory_kb != null ? `${(s.memory_kb / 1024).toFixed(2)} MB` : "—"}
                </span>
                <span className="text-[11px] text-gray-600">
                  {new Date(s.submitted_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </span>
            </button>
            {isExpanded && (
              <div className="border-t border-white/10 bg-[#16162a]">
                <div className="p-3">
                  <CodeMirror
                    value={s.code}
                    height="auto"
                    style={{ fontSize: "13px", maxHeight: "350px", overflow: "auto" }}
                    theme={oneDark}
                    extensions={[(langMap[s.language] ?? python)() as never]}
                    readOnly
                    basicSetup={{ highlightActiveLine: false, highlightActiveLineGutter: false }}
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function HintsSection({
  hintMeta,
  revealedHints,
  armedHint,
  loadingHint,
  onHintClick,
}: {
  hintMeta: HintMetaOut | null;
  revealedHints: Record<number, string>;
  armedHint: number | null;
  loadingHint: number | null;
  onHintClick: (level: number) => void;
}) {
  if (!hintMeta) return null;
  return (
    <div className="mt-4 rounded-xl border border-white/10 bg-[#1e1e30] p-4">
      <p className="flex items-center gap-2 text-sm font-semibold text-gray-200">
        <Lightbulb size={15} className="text-yellow-400" />
        Hints
        <span className="text-xs font-normal text-gray-500">
          Viewing any hint forfeits first-solve XP
        </span>
      </p>
      <div className="mt-3 space-y-1.5">
        {hintMeta.levels.map((entry: HintLevelInfo) => (
          <div key={entry.level} className="overflow-hidden rounded-lg border border-white/10">
            <button
              onClick={() => onHintClick(entry.level)}
              disabled={loadingHint !== null}
              className={`flex w-full items-center gap-2 px-3 py-2.5 text-left text-sm transition-colors ${
                entry.revealed || armedHint === entry.level
                  ? "bg-yellow-500/10 text-yellow-300"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              } disabled:opacity-50`}
            >
              {loadingHint === entry.level ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Lightbulb
                  size={14}
                  className={entry.revealed || armedHint === entry.level ? "text-yellow-400" : ""}
                />
              )}
              Level {entry.level}: {entry.label}
              {!entry.revealed && (
                <span className="ml-auto text-xs text-gray-500">
                  {hintMeta.xp_forfeit_applies
                    ? armedHint === entry.level
                      ? "Click again — XP will be forfeited"
                      : "Reveal · costs XP"
                    : "Reveal"}
                </span>
              )}
            </button>
            {revealedHints[entry.level] && (
              <div className="border-t border-white/10 bg-white/[0.02] px-3 py-2.5">
                <article className="prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                  <Markdown remarkPlugins={[remarkGfm]}>
                    {revealedHints[entry.level]}
                  </Markdown>
                </article>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SolveClient() {
  const params = useParams();
  const slug = Array.isArray(params.slug) ? params.slug[0] : (params.slug as string);
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [pageStatus, setPageStatus] = useState("loading");
  const [unavailable, setUnavailable] = useState(false);
  const [lang, setLang] = useState<Language>("python");
  const [mode, setMode] = useState<RunMode>("main");
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<RunResultOut | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmissionResultOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hintMeta, setHintMeta] = useState<HintMetaOut | null>(null);
  const [revealedHints, setRevealedHints] = useState<Record<number, string>>({});
  const [armedHint, setArmedHint] = useState<number | null>(null);
  const [loadingHint, setLoadingHint] = useState<number | null>(null);
  const [review, setReview] = useState<ReviewOut | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [consoleTab, setConsoleTab] = useState("testcase");
  const [caseIdx, setCaseIdx] = useState(0);
  const [customInput, setCustomInput] = useState("");
  const [customResult, setCustomResult] = useState<CustomRunOut | null>(null);
  const [customRunning, setCustomRunning] = useState(false);
  const [runCount, setRunCount] = useState(0);

  const [submissions, setSubmissions] = useState<SubmissionHistoryItem[]>([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);

  const [assistantOpen, setAssistantOpen] = useState(false);
  const [coachMessages, setCoachMessages] = useState<CoachMessage[]>([]);
  const [coachLoading, setCoachLoading] = useState(false);
  const [coachProvider, setCoachProvider] = useState<string | null>(null);
  const [includeCode, setIncludeCode] = useState(true);

  const [dockApi, setDockApi] = useState<DockviewApi | null>(null);
  const dark = useTheme() === "dark";
  const th = (d: string, l: string) => (dark ? d : l);

  useEffect(() => {
    let cancelled = false;
    client
      .get<ProblemDetail>(`/problems/${slug}`)
      .then((res) => {
        if (cancelled) return;
        setProblem(res.data);
        setUnavailable(!res.data.solvable);
        setCode(res.data.starter_code.python);
        setPageStatus("ok");
        return client.get<HintMetaOut>(`/problems/${slug}/hints`);
      })
      .then((res) => {
        if (cancelled || !res) return;
        setHintMeta(res.data);
      })
      .catch(() => {
        if (!cancelled) setPageStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  const starterFor = useCallback(
    (p: ProblemDetail | null, l: Language, m: RunMode) => {
      if (!p) return "";
      if (m === "function" && p.function_starter?.[l]) {
        return p.function_starter[l] as string;
      }
      return p.starter_code[l];
    },
    []
  );

  const handleLangChange = useCallback(
    (next: Language) => {
      setLang(next);
      const starter = starterFor(problem, next, mode);
      if (starter) setCode(starter);
    },
    [problem, mode, starterFor]
  );

  const handleModeChange = useCallback(
    (next: RunMode) => {
      setMode(next);
      const starter = starterFor(problem, lang, next);
      if (starter) setCode(starter);
      setRunResult(null);
      setSubmitResult(null);
    },
    [problem, lang, starterFor]
  );

  const fetchSubmissions = useCallback(async () => {
    setSubmissionsLoading(true);
    try {
      const res = await client.get<SubmissionHistoryItem[]>(
        `/problems/${slug}/submissions`
      );
      setSubmissions(res.data);
    } catch {
    } finally {
      setSubmissionsLoading(false);
    }
  }, [slug]);

  const focusConsole = useCallback(() => {
    try {
      dockApi?.getPanel("console")?.focus();
    } catch {
    }
  }, [dockApi]);
  const handleLeftTab = useCallback(
    (tab: string) => {
      setLeftTab(tab);
      if (tab === "submissions") fetchSubmissions();
    },
    [fetchSubmissions]
  );

  const run = useCallback(async () => {
    setRunning(true);
    setError(null);
    setSubmitResult(null);
    try {
      const res = await client.post<RunResultOut>(
        `/problems/${slug}/run`,
        { language: lang, source_code: code, mode },
        { timeout: 120000 }
      );
      setRunResult(res.data);
      setRunCount((n) => n + 1);
      setConsoleTab("result");
      focusConsole();
    } catch (err) {
      setError(errDetail(err));
      setConsoleTab("output");
      focusConsole();
    } finally {
      setRunning(false);
    }
  }, [slug, lang, code, mode, focusConsole]);

  const runCustom = useCallback(async () => {
    setCustomRunning(true);
    setCustomResult(null);
    try {
      const res = await client.post<CustomRunOut>(
        "/custom-run",
        { language: lang, source_code: code, stdin: customInput },
        { timeout: 120000 }
      );
      setCustomResult(res.data);
      setConsoleOpen(true);
      setConsoleTab("custom");
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Could not run with custom input. Try again.";
      setCustomResult(null);
      setError(message);
      setConsoleOpen(true);
      setConsoleTab("custom");
    } finally {
      setCustomRunning(false);
    }
  }, [lang, code, customInput]);

  const submit = useCallback(async () => {
    setSubmitting(true);
    setError(null);
    setRunResult(null);
    setReview(null);
    try {
      const res = await client.post<SubmissionResultOut>(
        `/problems/${slug}/submit`,
        { language: lang, source_code: code, mode },
        { timeout: 120000 }
      );
      setSubmitResult(res.data);
      setRunCount((n) => n + 1);
      setConsoleTab("result");
      focusConsole();
      fetchSubmissions();
    } catch (err) {
      setError(errDetail(err));
      setConsoleTab("output");
      focusConsole();
    } finally {
      setSubmitting(false);
    }
  }, [slug, lang, code, mode, focusConsole, fetchSubmissions]);

  const revealHint = useCallback(
    async (level: number) => {
      setLoadingHint(level);
      setError(null);
      try {
        const res = await client.post<{ content: string }>(
          `/problems/${slug}/hints/${level}`
        );
        setRevealedHints((prev) => ({ ...prev, [level]: res.data.content }));
        setHintMeta((prev) =>
          prev
            ? {
                ...prev,
                levels: prev.levels.map((l) =>
                  l.level === level ? { ...l, revealed: true } : l
                ),
              }
            : prev
        );
        setArmedHint(null);
      } catch (err) {
        setError(
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Could not load the hint. Try again."
        );
      } finally {
        setLoadingHint(null);
      }
    },
    [slug]
  );

  const onHintClick = useCallback(
    (level: number) => {
      if (revealedHints[level]) return;
      if (hintMeta?.xp_forfeit_applies && armedHint !== level) {
        setArmedHint(level);
        return;
      }
      revealHint(level);
    },
    [revealedHints, hintMeta, armedHint, revealHint]
  );

  const fetchReview = useCallback(async () => {
    if (!submitResult) return;
    setReviewLoading(true);
    setError(null);
    try {
      const res = await client.post<ReviewOut>(
        `/submissions/${submitResult.submission_id}/review`
      );
      setReview(res.data);
    } catch (err) {
      setError(
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Could not get an AI review. Try again."
      );
    } finally {
      setReviewLoading(false);
    }
  }, [submitResult]);

  const sendCoach = useCallback(
    async (text: string) => {
      const history = coachMessages.slice(-8).map((m) => ({
        role: m.role,
        content: m.content.slice(0, 2000),
      }));
      const shown = submitResult || runResult;
      const failing =
        shown && shown.status !== "ACCEPTED"
          ? shown.test_results
              .filter((t) => !t.passed)
              .slice(0, 2)
              .map(
                (t) =>
                  `case ${t.index + 1} (${t.status_key}): expected ${String(
                    (t as { expected_output?: unknown }).expected_output ?? ""
                  ).slice(0, 300)} got ${String(
                    t.actual_output ?? ""
                  ).slice(0, 300)}`
              )
              .join("\n")
          : "";
      const next: CoachMessage[] = [...coachMessages, { role: "user", content: text }];
      setCoachMessages(next);
      setCoachLoading(true);
      try {
        const res = await client.post<{ reply: string; provider: string }>(
          `/problems/${slug}/assistant`,
          {
            message: text,
            language: lang,
            code: includeCode ? code.slice(0, 8000) : "",
            include_code: includeCode,
            history,
            last_result: shown
              ? {
                  status: shown.status,
                  passed: shown.test_results.filter((t) => t.passed).length,
                  total: shown.test_results.length,
                  failing,
                }
              : null,
          },
          { timeout: 60000 }
        );
        setCoachProvider(res.data.provider === "groq" ? "Groq" : "Gemini");
        setCoachMessages([...next, { role: "assistant", content: res.data.reply }]);
      } catch (err) {
        const detail =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Coach is unavailable right now. Try again.";
        setCoachMessages([...next, { role: "assistant", content: `_${detail}_` }]);
      } finally {
        setCoachLoading(false);
      }
    },
    [coachMessages, submitResult, runResult, slug, lang, code, includeCode]
  );

  const closeCoach = useCallback(() => {
    setAssistantOpen(false);
    try {
      dockApi?.getPanel("coach")?.api.close();
    } catch {
    }
  }, [dockApi]);

  const onDockReady = useCallback((event: DockviewReadyEvent) => {
    const api = event.api;
    if (api.panels.length > 0) {
      setDockApi(api);
      return;
    }
    api.addPanel({ id: "description", title: "Description", component: "description" });
    api.addPanel({ id: "submissions", title: "Submissions", component: "submissions" });
    api.addPanel({
      id: "code",
      title: "Code",
      component: "code",
      position: { referencePanel: "description", direction: "right" },
    });
    api.addPanel({
      id: "console",
      title: "Console",
      component: "console",
      position: { referencePanel: "code", direction: "below" },
    });
    try {
      api.getPanel("description")?.focus();
    } catch {
    }
    setDockApi(api);
  }, []);

  // Keep the dock coach tab in sync with the toggle.
  useEffect(() => {
    if (!dockApi) return;
    const existing = (() => {
      try {
        return dockApi.getPanel("coach");
      } catch {
        return undefined;
      }
    })();
    if (assistantOpen && !existing) {
      try {
        dockApi.addPanel({
          id: "coach",
          title: "Coach",
          component: "coach",
          position: { referencePanel: "code", direction: "right" },
        });
      } catch {
      }
    } else if (!assistantOpen && existing) {
      try {
        existing.api.close();
      } catch {
      }
    }
  }, [dockApi, assistantOpen]);

  const contextNote = useMemo(() => {
    const s = submitResult || runResult;
    const score = s
      ? submitResult
        ? `submit ${s.test_results.filter((t) => t.passed).length}/${s.test_results.length}`
        : `run ${s.test_results.filter((t) => t.passed).length}/${s.test_results.length}`
      : "no run yet";
    return `${lang} · ${mode} · ${score} · code ${includeCode ? "attached" : "off"}`;
  }, [lang, mode, submitResult, runResult, includeCode]);

  const dockValue: DockValue = {
    problem: problem as ProblemDetail,
    slug,
    lang,
    mode,
    code,
    runCount,
    onCode: setCode,
    onModeChange: handleModeChange,
    onLangChange: handleLangChange,
    run,
    submit,
    running,
    submitting,
    submissions,
    submissionsLoading,
    refreshSubmissions: fetchSubmissions,
    hintMeta,
    revealedHints,
    armedHint,
    loadingHint,
    onHintClick,
    error,
    runResult,
    submitResult,
    shown: (submitResult || runResult) as DockValue["shown"],
    shownStatus: (submitResult || runResult)?.status,
    consoleTab,
    setConsoleTab,
    review,
    reviewLoading,
    fetchReview,
    focusConsole,
    coachMessages,
    coachLoading,
    coachProvider,
    includeCode,
    onToggleInclude: () => setIncludeCode((v) => !v),
    onSendCoach: sendCoach,
    onClearCoach: () => {
      setCoachMessages([]);
      setCoachProvider(null);
    },
    closeCoach,
    contextNote,
  };

  useEffect(() => {
    if (!runResult?.test_results.length) return;
    const firstFailed = runResult.test_results.findIndex((t) => !t.passed);
    setCaseIdx(firstFailed === -1 ? 0 : firstFailed);
  }, [runResult]);

  if (pageStatus === "loading") {
    return (
      <div className="atlas-bg flex h-screen items-center justify-center gap-2 text-ink-soft">
        <Loader2 size={20} className="animate-spin" />
        Loading...
      </div>
    );
  }

  if (pageStatus === "error" || !problem) {
    return (
      <div className="atlas-bg flex h-screen flex-col items-center justify-center gap-4">
        <p className="text-lg text-ink-soft">This problem does not exist.</p>
        <Link href="/problems" className="font-semibold text-quest hover:underline">
          Back to the library
        </Link>
      </div>
    );
  }

  if (unavailable) {
    return (
      <div className="atlas-bg flex h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="font-display text-2xl font-bold text-ink">Coming soon</p>
        <p className="max-w-md text-ink-soft">
          &quot;{problem.title}&quot; is in the roadmap catalog but hasn&apos;t
          been fully authored yet (no starter code or test cases). It will be
          solvable once it&apos;s added to the library.
        </p>
        <Link href="/problems" className="font-semibold text-quest hover:underline">
          Back to library
        </Link>
      </div>
    );
  }

  const shown = submitResult || runResult;
  const shownStatus: SubmissionStatus | undefined = shown?.status;
  const compileError =
    shown &&
    (shownStatus === "COMPILATION_ERROR" || shownStatus === "RUNTIME_ERROR")
      ? (
          shown as { test_results?: { stderr?: string | null }[] }
        ).test_results?.find((t) => t && t.stderr)?.stderr ?? null
      : null;
  const hasOutputTab = error || compileError;
  const runSel = runResult?.test_results
    ? runResult.test_results[Math.min(caseIdx, runResult.test_results.length - 1)]
    : null;

  return (
    <div className={th("flex h-screen flex-col bg-[#0b0d12]", "flex h-screen flex-col bg-paper-deep")}>
      {/* ── Top bar ──────────────────────────────────────────── */}
      <header className={th("flex h-12 shrink-0 items-center justify-between border-b border-white/10 bg-[#0e1119] px-4", "flex h-12 shrink-0 items-center justify-between border-b border-ink/10 bg-white px-4")}>
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/problems"
            className={th("flex items-center gap-1.5 rounded-md px-2 py-1 text-sm text-gray-400 transition-colors hover:text-gray-200", "flex items-center gap-1.5 rounded-md px-2 py-1 text-sm text-ink-soft transition-colors hover:text-ink")}
          >
            <ArrowLeft size={15} />
            Library
          </Link>
          <span className={th("h-4 w-px bg-white/10", "h-4 w-px bg-ink/10")} />
          <h1 className={th("truncate text-sm font-semibold text-gray-100", "truncate font-display text-sm font-bold tracking-tight text-ink")}>
            {problem.title}
          </h1>
          <span className={`text-xs font-medium ${DIFFICULTY_STYLE[problem.difficulty as Difficulty]}`}>
            {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
          </span>
          {problem.solved && (
            <span className="rounded-md border border-emerald-500/50 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">
              Solved
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle dark={dark} />
          <div className={th("flex gap-0.5 rounded-lg border border-white/10 bg-[#252540] p-0.5", "flex gap-0.5 rounded-lg border border-ink/10 bg-paper-deep p-0.5")}>
            {LANGS.map((l) => (
              <button
                key={l.key}
                onClick={() => handleLangChange(l.key)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                  lang === l.key
                    ? th("bg-white/10 text-gray-100", "bg-ink text-white")
                    : th("text-gray-500 hover:text-gray-300", "text-ink-faint hover:text-ink")
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          <button
            onClick={() => setAssistantOpen((o) => !o)}
            title="Toggle coach"
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
              assistantOpen
                ? "border-violet-400/50 bg-violet-500/15 text-violet-200"
                : th("border-white/10 bg-[#252540] text-gray-300 hover:border-white/20 hover:text-gray-100", "border-ink/10 bg-paper-deep text-ink-soft hover:border-ink/20 hover:text-ink")
            }`}
          >
            <Brain size={13} />
            Coach
          </button>
          <button
            onClick={run}
            disabled={running || submitting}
            className={th("flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-white/20 hover:text-gray-100 disabled:opacity-50", "flex items-center gap-1.5 rounded-lg border border-ink/10 bg-card px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:border-ink/20 hover:text-ink disabled:opacity-50")}
          >
            {running ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} />}
            Run
          </button>
          <button
            onClick={submit}
            disabled={running || submitting}
            className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-500 disabled:opacity-50"
          >
            {submitting ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
            Submit
          </button>
        </div>
      </header>

      {/* ── Dock workspace: every tab drags anywhere ─────────── */}
      <div className="dock-root min-h-0 flex-1">
        <DockContext.Provider value={dockValue}>
          <DockviewReact
            components={DOCK_COMPONENTS}
            onReady={onDockReady}
            theme={{
              name: "codequest",
              className: "dockview-theme-cq",
              gap: 10,
              dndTabIndicator: "line",
              tabAnimation: "smooth",
            }}
          />
        </DockContext.Provider>
      {/* ── Main content: two-panel split ────────────────────── */}
      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        {/* Left: problem description with tabs */}
        <section className="flex min-h-0 w-full flex-col border-b border-white/10 lg:w-[45%] lg:border-b-0 lg:border-r lg:border-white/10">
          {/* Left tabs */}
          <div className="flex shrink-0 border-b border-white/10 bg-[#1e1e30]">
            <button
              onClick={() => handleLeftTab("description")}
              className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-xs font-medium transition-colors ${
                leftTab === "description"
                  ? "border-emerald-400 text-emerald-400"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              }`}
            >
              <FileCode2 size={13} />
              Description
            </button>
            <button
              onClick={() => handleLeftTab("submissions")}
              className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-xs font-medium transition-colors ${
                leftTab === "submissions"
                  ? "border-emerald-400 text-emerald-400"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              }`}
            >
              <History size={13} />
              Submissions
              {submissions.length > 0 && leftTab !== "submissions" && (
                <span className="rounded-full bg-white/10 px-1.5 py-0.5 text-[10px] text-gray-400">
                  {submissions.length}
                </span>
              )}
            </button>
          </div>

          {/* Left tab content */}
          <div className="min-h-0 flex-1 overflow-y-auto p-5">
            {leftTab === "description" && (
              <>
                <DescriptionTab problem={problem} />
                {(problem.editorial_url || problem.video_url) && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {problem.editorial_url && (
                      <a
                        href={problem.editorial_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-emerald-400/40 hover:text-emerald-300"
                      >
                        <BookOpen size={13} />
                        Editorial
                      </a>
                    )}
                    {problem.video_url && (
                      <a
                        href={problem.video_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-emerald-400/40 hover:text-emerald-300"
                      >
                        <Play size={13} />
                        Video
                      </a>
                    )}
                  </div>
                )}
                <HintsSection
                  hintMeta={hintMeta}
                  revealedHints={revealedHints}
                  armedHint={armedHint}
                  loadingHint={loadingHint}
                  onHintClick={onHintClick}
                />
              </>
            )}
            {leftTab === "submissions" && (
              <SubmissionsTab submissions={submissions} loading={submissionsLoading} />
            )}
          </div>
        </section>

        {/* Right: code editor + console */}
        <section className="flex min-h-0 min-w-0 flex-1 flex-col">
          {/* Code editor */}
          <div className="min-h-0 flex-1 overflow-hidden">
            <CodeEditor value={code} language={lang} onChange={setCode} height="100%" />
          </div>

          {/* Console bar */}
          <div className="flex h-9 shrink-0 items-center justify-between border-t border-white/10 bg-[#1e1e30] px-4">
            <button
              onClick={() => setConsoleOpen((o) => !o)}
              className="flex items-center gap-1.5 text-xs font-medium text-gray-400 hover:text-gray-200"
            >
              Console
              {consoleOpen ? <ChevronDown size={13} /> : <ChevronUp size={13} />}
            </button>
            {shown && shownStatus && (
              <span className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[shownStatus]?.chip || "text-gray-400"}`}>
                {STATUS_STYLES[shownStatus]?.icon}
                {STATUS_STYLES[shownStatus]?.label}
              </span>
            )}
          </div>

          {/* Console panel */}
          {consoleOpen && (
            <div className="max-h-[45vh] shrink-0 overflow-y-auto border-t border-white/10 bg-[#16162a]">
              {/* Error banner */}
              {error && (
                <div className="border-b border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              {/* Tabs */}
              <div className="flex border-b border-white/10">
                <button
                  onClick={() => setConsoleTab("result")}
                  className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                    consoleTab === "result"
                      ? "border-emerald-400 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                  }`}
                >
                  Result
                </button>
                <button
                  onClick={() => setConsoleTab("custom")}
                  className={`flex items-center gap-1.5 border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                    consoleTab === "custom"
                      ? "border-emerald-400 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-gray-300"
                  }`}
                >
                  {customResult ? <Check size={12} className="text-emerald-400" /> : <SquareTerminal size={13} />}
                  Custom
                </button>
                {hasOutputTab && (
                  <button
                    onClick={() => setConsoleTab("output")}
                    className={`flex items-center gap-1.5 border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                      consoleTab === "output"
                        ? "border-emerald-400 text-emerald-400"
                        : "border-transparent text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {compileError ? (
                      <>
                        <XCircle size={12} className="text-red-400" />
                        Compile Error
                      </>
                    ) : (
                      "Output"
                    )}
                  </button>
                )}
              </div>

              {/* Result tab */}
              {shown && consoleTab === "result" && (
                <div className="p-4">
                  {/* Scope banner */}
                  <p className="mb-3 font-mono text-xs text-gray-500">
                    {runResult
                      ? `Run · ${runResult.test_results.length} visible case${runResult.test_results.length === 1 ? "" : "s"}`
                      : `Submit · all ${(submitResult?.test_results.length ?? 0)} cases (${problem.hidden_test_count} hidden)`}
                  </p>
                  {(shownStatus === "COMPILATION_ERROR" ||
                    shownStatus === "RUNTIME_ERROR") &&
                    compileError && (
                      <div className="mb-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                        <p className="flex items-center gap-2 font-mono text-[13px] font-bold text-red-300">
                          <XCircle size={14} className="shrink-0" />
                          {shownStatus === "COMPILATION_ERROR"
                            ? "Compilation Error"
                            : "Runtime Error"}
                        </p>
                        <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words font-mono text-[13px] leading-relaxed text-red-200">
                          {compileError}
                        </pre>
                      </div>
                    )}
                  {/* XP + badges */}
                  {submitResult && submitResult.xp_awarded > 0 && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-300">
                      <Zap size={14} />
                      +{submitResult.xp_awarded} XP earned
                      {submitResult.current_streak > 1 && (
                        <span className="ml-auto text-xs text-yellow-400/70">
                          Streak · {submitResult.current_streak}d
                        </span>
                      )}
                    </div>
                  )}
                  {submitResult && submitResult.xp_forfeited && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-400">
                      <Lightbulb size={13} className="text-yellow-400/70" />
                      First-solve XP forfeited — hints were used.
                    </div>
                  )}
                  {submitResult && submitResult.new_badges?.length > 0 && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm font-medium text-yellow-300">
                      <Award size={14} />
                      Badge unlocked: {submitResult.new_badges.join(", ")}
                    </div>
                  )}

                  {/* Test chips (submit) */}
                  {submitResult && (
                    <div className="mb-3">
                      <p className="mb-2 text-[13px] text-gray-500">
                        Tests · {submitResult.test_results.filter((t) => t.passed).length}/
                        {submitResult.test_results.length} passed
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {submitResult.test_results.map((t) => (
                          <TestChip key={t.index} index={t.index} passed={t.passed} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Failed visible case diffs (submit) */}
                  {submitResult &&
                    submitResult.test_results
                      .filter((t) => !t.passed && !t.hidden)
                      .map((t) => (
                        <div
                          key={t.index}
                          className="mt-2 rounded-lg border border-red-500/30 bg-red-500/5 p-3"
                        >
                          <p className="flex items-center gap-1.5 font-mono text-[13px] font-medium text-gray-400">
                            <XCircle size={12} className="text-red-400" />
                            Case {t.index + 1}
                            {t.status_key && (
                              <span>· {statusKeyLabel(t.status_key)}</span>
                            )}
                          </p>
                          <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Input
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[14px] text-gray-300">
                                {(t.input || "").trimEnd()}
                              </pre>
                            </div>
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Expected
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[14px] text-emerald-400">
                                {t.expected_output}
                              </pre>
                            </div>
                            <div className="sm:col-span-2">
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Your output
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[14px] text-red-300">
                                {t.actual_output || "(no output)"}
                              </pre>
                            </div>
                          </div>
                        </div>
                      ))}

                  {/* Failed hidden cases (submit) — pass/fail + status only */}
                  {submitResult &&
                    submitResult.test_results
                      .filter((t) => !t.passed && t.hidden)
                      .map((t) => (
                        <div
                          key={t.index}
                          className="mt-2 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3"
                        >
                          <EyeOff size={13} className="shrink-0 text-yellow-400/80" />
                          <p className="font-mono text-[13px] text-gray-400">
                            Hidden test #{t.index + 1} failed
                            {t.status_key && (
                              <span className="text-yellow-300/90">
                                {" "}· {statusKeyLabel(t.status_key)}
                              </span>
                            )}
                            <span className="text-gray-600"> (input is secret)</span>
                          </p>
                        </div>
                      ))}

                  {/* Runtime + memory */}
                  <div className="mb-3 font-mono text-[13px] text-gray-500">
                    {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
                  </div>

                  {/* AI review (submit, not accepted) */}
                  {submitResult && submitResult.status !== "ACCEPTED" && (
                    <div className="mt-3">
                      {review ? (
                        <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3">
                          <p className="flex items-center gap-2 text-sm font-semibold text-yellow-300">
                            <Sparkles size={14} />
                            AI review
                            <span className="rounded border border-yellow-500/30 px-1.5 py-0.5 text-[10px] font-normal text-yellow-400/80">
                              {review.bug_type}
                            </span>
                          </p>
                          <p className="mt-2 text-sm font-medium text-gray-200">{review.verdict}</p>
                          <article className="prose prose-invert prose-sm mt-2 max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.explanation}</Markdown>
                          </article>
                          <p className="mt-3 mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                            How to fix
                          </p>
                          <article className="prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.fix_hint}</Markdown>
                          </article>
                        </div>
                      ) : (
                        <button
                          onClick={fetchReview}
                          disabled={reviewLoading}
                          className="flex items-center gap-1.5 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs font-medium text-yellow-300 hover:bg-yellow-500/20 disabled:opacity-50"
                        >
                          {reviewLoading ? (
                            <Loader2 size={13} className="animate-spin" />
                          ) : (
                            <Sparkles size={13} />
                          )}
                          Get AI review
                        </button>
                      )}
                    </div>
                  )}

                  {/* Run test cases (platform-style toggles) */}
                  {runResult &&
                    runSel && (
                      <div className="mt-3">
                        {shownStatus === "ACCEPTED" && (
                          <p className="mb-3 text-sm text-emerald-400">
                            All sample cases passed.
                          </p>
                        )}
                        <div className="flex flex-wrap items-center gap-2">
                          {runResult.test_results.map((t, i) => (
                            <button
                              key={t.index}
                              type="button"
                              onClick={() => setCaseIdx(i)}
                              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 font-mono text-xs font-semibold transition-colors ${
                                i === caseIdx
                                  ? "border-[#d4a72c]/60 bg-[#d4a72c]/15 text-[#f5f5f5]"
                                  : "border-white/10 text-[#93a1bd] hover:border-white/25 hover:text-[#dce3f2]"
                              }`}
                            >
                              <span
                                className={`h-1.5 w-1.5 rounded-full ${
                                  t.passed ? "bg-emerald-400" : "bg-red-400"
                                }`}
                              />
                              Testcase {i + 1}
                            </button>
                          ))}
                        </div>

                          <div
                            className={`mt-2 overflow-hidden rounded-xl border bg-[#16162a] ${
                              runSel.passed
                                ? "border-emerald-500/25"
                                : "border-red-500/25"
                            }`}
                          >
                            <div
                              className={`flex items-center justify-between border-b px-3 py-1.5 ${
                                runSel.passed
                                  ? "border-emerald-500/25 bg-emerald-500/10"
                                  : "border-red-500/25 bg-red-500/10"
                              }`}
                            >
                              <span
                                className={`font-mono text-[11px] font-bold uppercase tracking-[0.14em] ${
                                  runSel.passed ? "text-emerald-400" : "text-red-300"
                                }`}
                              >
                                {runSel.passed ? "Testcase Passed" : "Testcase Failed"}
                              </span>
                              <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                                Case {runSel.index + 1} ·{" "}
                                {!runSel.passed && runSel.status_key === "ACCEPTED"
                                  ? "Wrong Answer"
                                  : statusKeyLabel(runSel.status_key)}
                              </span>
                            </div>
                            <div className="space-y-3 px-3 py-3">
                              <div>
                                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                                  Input (stdin)
                                </p>
                                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-[#1e1e30] p-2 font-mono text-[13px] leading-relaxed text-[#c3cde3]">
                                  {(runSel.input || "").trimEnd()}
                                </pre>
                              </div>
                              <div>
                                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                                  Your Output (stdout)
                                </p>
                                <pre
                                  className={`overflow-x-auto whitespace-pre-wrap break-words rounded-md border p-2 font-mono text-[13px] leading-relaxed ${
                                    runSel.passed
                                      ? "border-emerald-500/30 bg-[#1e1e30] text-emerald-400"
                                      : "border-red-500/30 bg-[#1e1e30] text-red-300"
                                  }`}
                                >
                                  {(runSel.actual_output ?? "(no output)").trimEnd()}
                                </pre>
                              </div>
                              <div>
                                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                                  Expected Output
                                </p>
                                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-[#1e1e30] p-2 font-mono text-[13px] leading-relaxed text-emerald-400">
                                  {(runSel.expected_output || "").trimEnd()}
                                </pre>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                </div>
              )}

              {/* Output tab (compile error / runtime error / stderr) */}
              {consoleTab === "output" && (
                <div className="p-4">
                  {compileError ? (
                    <div>
                      <div className="mb-3 flex items-center gap-2">
                        <XCircle size={14} className="text-red-400" />
                        <span className="text-sm font-medium text-red-300">
                          {shownStatus === "COMPILATION_ERROR"
                            ? "Compilation Error"
                            : "Runtime Error"}
                        </span>
                      </div>
                      <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[14px] leading-relaxed text-red-200">
                        {compileError}
                      </pre>
                    </div>
                  ) : error ? (
                    <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[14px] leading-relaxed text-red-200">
                      {error}
                    </pre>
                  ) : shown ? (
                    <div>
                      <p className="mb-2 text-[13px] text-gray-500">Standard output</p>
                      <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-white/10 bg-[#1a1a2e] p-4 font-mono text-[14px] leading-relaxed text-gray-300">
                        {(shown as RunResultOut).test_results
                          ?.filter((t) => t.actual_output != null)
                          .map((t) => `Case ${t.index + 1}:\n${t.actual_output}`)
                          .join("\n\n") || "(no output)"}
                      </pre>
                    </div>
                  ) : null}
                </div>
              )}

              {/* Custom tab (user stdin, not graded) */}
              {consoleTab === "custom" && (
                <div className="p-4">
                  <p className="mb-2 text-[13px] text-gray-500">
                    Run your code against your own input. This is not graded.
                  </p>
                  <textarea
                    value={customInput}
                    onChange={(e) => setCustomInput(e.target.value)}
                    rows={4}
                    spellCheck={false}
                    placeholder="Paste stdin input\u2026 each case on its own line"
                    className="w-full resize-y rounded-lg border border-white/10 bg-[#1a1a2e] p-3 font-mono text-[13px] text-gray-200 placeholder:text-gray-600 outline-none focus:border-emerald-400/50"
                  />
                  <button
                    type="button"
                    onClick={runCustom}
                    disabled={customRunning}
                    className="mt-3 flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-white/25 hover:text-gray-100 disabled:opacity-50"
                  >
                    {customRunning ? (
                      <Loader2 size={13} className="animate-spin" />
                    ) : (
                      <Play size={13} />
                    )}
                    Run custom
                  </button>

                  {error && consoleTab === "custom" && (
                    <div className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[14px] leading-relaxed text-red-200">
                      {error}
                    </div>
                  )}

                  {customResult && (
                    <div className="mt-3">
                      <div className="flex flex-wrap items-center gap-2">
                        {customResult.status ? (
                          <span
                            className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[customResult.status]?.chip || "text-gray-400"}`}
                          >
                            {STATUS_STYLES[customResult.status]?.icon}
                            {STATUS_STYLES[customResult.status]?.label}
                          </span>
                        ) : (
                          <span className="text-xs font-medium text-gray-400">
                            {customResult.status_key}
                          </span>
                        )}
                        <span className="font-mono text-xs text-gray-500">
                          {customResult.runtime_ms.toFixed(0)} ms ·{" "}
                          {(customResult.memory_kb / 1024).toFixed(1)} MB
                        </span>
                      </div>

                      <div className="mt-3">
                        <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                          Your Output (stdout)
                        </p>
                        <pre
                          className={`overflow-x-auto whitespace-pre-wrap break-words rounded-md border p-2 font-mono text-[13px] leading-relaxed ${
                            customResult.status === "ACCEPTED"
                              ? "border-emerald-500/30 bg-[#1e1e30] text-emerald-400"
                              : "border-red-500/30 bg-[#1e1e30] text-red-300"
                          }`}
                        >
                          {(customResult.stdout || "(no output)").trimEnd()}
                        </pre>
                      </div>

                      {(customResult.stderr || customResult.compile_output) && (
                        <div className="mt-3">
                          <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                            Error
                          </p>
                          <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md border border-red-500/30 bg-[#1e1e30] p-2 font-mono text-[13px] leading-relaxed text-red-300">
                            {customResult.stderr || customResult.compile_output}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Empty state */}
              {!shown && !error && consoleTab === "result" && (
                <div className="flex flex-col items-center justify-center gap-1 py-8 text-center">
                  <p className="text-sm text-gray-500">Run or submit your code to see results here.</p>
                  <p className="font-mono text-xs text-gray-600">
                    Run checks {problem.test_cases.length} visible case
                    {problem.test_cases.length === 1 ? "" : "s"} · Submit checks all{" "}
                    {problem.test_cases.length + problem.hidden_test_count} (
                    {problem.hidden_test_count} hidden)
                  </p>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
