"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Award,
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Clock,
  EyeOff,
  FileCode2,
  History,
  Lightbulb,
  Loader2,
  Play,
  Send,
  Sparkles,
  XCircle,
  Zap,
} from "lucide-react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { oneDark } from "@codemirror/theme-one-dark";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import client from "@/lib/api";
import AssistantPanel, {
  type CoachMessage,
} from "./assistant-panel";
import type {
  Difficulty,
  HintLevelInfo,
  HintMetaOut,
  Language,
  ProblemDetail,
  ReviewOut,
  RunResultOut,
  SubmissionHistoryItem,
  SubmissionResultOut,
  SubmissionStatus,
  VisibleTestResult,
} from "@/lib/types";

const LANGS: { key: Language; label: string; ext: () => unknown }[] = [
  { key: "python", label: "Python", ext: python },
  { key: "cpp", label: "C++", ext: cpp },
  { key: "java", label: "Java", ext: java },
];

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
  const statement = problem.description.replace(/^#\s+.+\r?\n+/, "");
  return (
    <article className="prose prose-invert max-w-none text-[14px] leading-relaxed prose-headings:text-gray-100 prose-p:text-gray-300 prose-strong:text-white prose-code:rounded prose-code:bg-white/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-emerald-400 prose-code:before:content-none prose-code:after:content-none">
      <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
    </article>
  );
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
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [consoleTab, setConsoleTab] = useState("result");

  const [leftTab, setLeftTab] = useState("description");
  const [submissions, setSubmissions] = useState<SubmissionHistoryItem[]>([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);

  const [assistantOpen, setAssistantOpen] = useState(false);
  const [coachMessages, setCoachMessages] = useState<CoachMessage[]>([]);
  const [coachLoading, setCoachLoading] = useState(false);
  const [coachProvider, setCoachProvider] = useState<string | null>(null);
  const [includeCode, setIncludeCode] = useState(true);

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

  const handleLangChange = useCallback(
    (next: Language) => {
      setLang(next);
      const starter = problem?.starter_code[next];
      if (starter) setCode(starter);
    },
    [problem]
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

  const handleLeftTab = useCallback(
    (tab: string) => {
      setLeftTab(tab);
      if (tab === "submissions") fetchSubmissions();
    },
    [fetchSubmissions]
  );

  const activeLang = useMemo(() => LANGS.find((l) => l.key === lang), [lang]);

  const run = useCallback(async () => {
    setRunning(true);
    setError(null);
    setSubmitResult(null);
    try {
      const res = await client.post<RunResultOut>(
        `/problems/${slug}/run`,
        { language: lang, source_code: code },
        { timeout: 120000 }
      );
      setRunResult(res.data);
      setConsoleOpen(true);
      setConsoleTab("result");
    } catch (err) {
      setError(errDetail(err));
      setConsoleOpen(true);
      setConsoleTab("output");
    } finally {
      setRunning(false);
    }
  }, [slug, lang, code]);

  const submit = useCallback(async () => {
    setSubmitting(true);
    setError(null);
    setRunResult(null);
    setReview(null);
    try {
      const res = await client.post<SubmissionResultOut>(
        `/problems/${slug}/submit`,
        { language: lang, source_code: code },
        { timeout: 120000 }
      );
      setSubmitResult(res.data);
      setConsoleOpen(true);
      setConsoleTab("result");
      fetchSubmissions();
    } catch (err) {
      setError(errDetail(err));
      setConsoleOpen(true);
      setConsoleTab("output");
    } finally {
      setSubmitting(false);
    }
  }, [slug, lang, code, fetchSubmissions]);

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
        setCoachProvider(res.data.provider);
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

  if (pageStatus === "loading") {
    return (
      <div className="flex h-screen items-center justify-center gap-2 bg-[#1a1a2e] text-gray-400">
        <Loader2 size={20} className="animate-spin" />
        Loading...
      </div>
    );
  }

  if (pageStatus === "error" || !problem) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-[#1a1a2e]">
        <p className="text-lg text-gray-300">This problem does not exist.</p>
        <Link href="/problems" className="font-semibold text-emerald-400 hover:underline">
          Back to the library
        </Link>
      </div>
    );
  }

  if (unavailable) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-[#1a1a2e] px-6 text-center">
        <p className="text-2xl font-bold text-gray-100">Coming soon</p>
        <p className="max-w-md text-gray-400">
          &quot;{problem.title}&quot; is in the roadmap catalog but hasn&apos;t been fully authored yet
          (no starter code or test cases). It will be solvable once it&apos;s added to the library.
        </p>
        <Link href="/problems" className="font-semibold text-emerald-400 hover:underline">
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
      ? (shown as RunResultOut).test_results?.find((t) => t.actual_output)?.actual_output
      : null;
  const hasOutputTab = error || compileError;

  return (
    <div className="flex h-screen flex-col bg-[#1a1a2e]">
      {/* ── Top bar ──────────────────────────────────────────── */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-white/10 bg-[#1e1e30] px-4">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/problems"
            className="flex items-center gap-1.5 rounded-md px-2 py-1 text-sm text-gray-400 transition-colors hover:text-gray-200"
          >
            <ArrowLeft size={15} />
            Library
          </Link>
          <span className="h-4 w-px bg-white/10" />
          <h1 className="truncate text-sm font-semibold text-gray-100">
            {problem.title}
          </h1>
          <span className={`text-xs font-medium ${DIFFICULTY_STYLE[problem.difficulty]}`}>
            {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
          </span>
          {problem.solved && (
            <span className="rounded-md border border-emerald-500/50 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">
              Solved
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-0.5 rounded-lg border border-white/10 bg-[#252540] p-0.5">
            {LANGS.map((l) => (
              <button
                key={l.key}
                onClick={() => handleLangChange(l.key)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                  lang === l.key
                    ? "bg-white/10 text-gray-100"
                    : "text-gray-500 hover:text-gray-300"
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
                : "border-white/10 bg-[#252540] text-gray-300 hover:border-white/20 hover:text-gray-100"
            }`}
          >
            <Brain size={13} />
            Coach
          </button>
          <button
            onClick={run}
            disabled={running || submitting}
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-white/20 hover:text-gray-100 disabled:opacity-50"
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
            <CodeMirror
              value={code}
              height="100%"
              style={{ fontSize: "14px", height: "100%" }}
              theme={oneDark}
              extensions={[(activeLang?.ext() ?? python()) as never]}
              onChange={(value: string) => setCode(value)}
              basicSetup={{ tabSize: 4 }}
            />
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
              {shown && (
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
                    onClick={() => setConsoleTab("testcase")}
                    className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                      consoleTab === "testcase"
                        ? "border-emerald-400 text-emerald-400"
                        : "border-transparent text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    Testcase
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
              )}

              {/* Result tab */}
              {shown && consoleTab === "result" && (
                <div className="p-4">
                  {/* Scope banner */}
                  <p className="mb-3 font-mono text-[11px] text-gray-500">
                    {runResult
                      ? `Run · ${runResult.test_results.length} visible case${runResult.test_results.length === 1 ? "" : "s"}`
                      : `Submit · all ${(submitResult?.test_results.length ?? 0)} cases (${problem.hidden_test_count} hidden)`}
                  </p>
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
                      <p className="mb-2 text-xs text-gray-500">
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
                          <p className="flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400">
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
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-gray-300">
                                {(t.input || "").trimEnd()}
                              </pre>
                            </div>
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Expected
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400">
                                {t.expected_output}
                              </pre>
                            </div>
                            <div className="sm:col-span-2">
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Your output
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300">
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
                          <p className="font-mono text-xs text-gray-400">
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
                  <div className="mb-3 font-mono text-xs text-gray-500">
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

                  {/* Failed test details (run) */}
                  {runResult &&
                    runResult.test_results.map((t: VisibleTestResult) => (
                      <div
                        key={t.index}
                        className={`mt-2 rounded-lg border p-3 ${
                          t.passed
                            ? "border-emerald-500/30 bg-emerald-500/5"
                            : "border-red-500/30 bg-red-500/5"
                        }`}
                      >
                        <p className="flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400">
                          {t.passed ? (
                            <CheckCircle2 size={12} className="text-emerald-400" />
                          ) : (
                            <XCircle size={12} className="text-red-400" />
                          )}
                          Case {t.index + 1}
                          {!t.passed && shownStatus && <span>· {STATUS_STYLES[shownStatus]?.label}</span>}
                        </p>
                        {!t.passed && t.input != null && (
                          <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Input
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-gray-300">
                                {(t.input || "").trimEnd()}
                              </pre>
                            </div>
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Expected
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400">
                                {t.expected_output}
                              </pre>
                            </div>
                            <div className="sm:col-span-2">
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Your output
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300">
                                {t.actual_output || "(no output)"}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}

              {/* Testcase tab */}
              {shown && consoleTab === "testcase" && runResult && (
                <div className="p-4">
                  <p className="mb-2 text-xs text-gray-500">Test case inputs (read-only)</p>
                  {runResult.test_results.map((t) => (
                    <div key={t.index} className="mb-2 rounded-lg border border-white/10 bg-[#1a1a2e] p-3">
                      <p className="mb-1 font-mono text-xs text-gray-500">Case {t.index + 1}</p>
                      <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-[12px] text-gray-300">
                        {(t.input || "").trimEnd()}
                      </pre>
                    </div>
                  ))}
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
                      <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[12px] leading-relaxed text-red-200">
                        {compileError}
                      </pre>
                    </div>
                  ) : error ? (
                    <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[12px] leading-relaxed text-red-200">
                      {error}
                    </pre>
                  ) : shown ? (
                    <div>
                      <p className="mb-2 text-xs text-gray-500">Standard output</p>
                      <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-white/10 bg-[#1a1a2e] p-4 font-mono text-[12px] leading-relaxed text-gray-300">
                        {(shown as RunResultOut).test_results
                          ?.filter((t) => t.actual_output != null)
                          .map((t) => `Case ${t.index + 1}:\n${t.actual_output}`)
                          .join("\n\n") || "(no output)"}
                      </pre>
                    </div>
                  ) : null}
                </div>
              )}

              {/* Empty state */}
              {!shown && !error && (
                <div className="flex flex-col items-center justify-center gap-1 py-8 text-center">
                  <p className="text-sm text-gray-500">Run or submit your code to see results here.</p>
                  <p className="font-mono text-[11px] text-gray-600">
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

        {assistantOpen && (
          <section className="flex min-h-[40vh] w-full flex-col border-t border-white/10 lg:min-h-0 lg:w-[340px] lg:shrink-0 lg:border-l lg:border-t-0">
            <AssistantPanel
              messages={coachMessages}
              loading={coachLoading}
              provider={coachProvider}
              includeCode={includeCode}
              contextNote={`${lang} · ${
                submitResult
                  ? `submit ${submitResult.test_results.filter((t) => t.passed).length}/${submitResult.test_results.length}`
                  : runResult
                    ? `run ${runResult.test_results.filter((t) => t.passed).length}/${runResult.test_results.length}`
                    : "no run yet"
              } · code ${includeCode ? "attached" : "off"}`}
              onToggleInclude={() => setIncludeCode((v) => !v)}
              onSend={sendCoach}
              onClear={() => {
                setCoachMessages([]);
                setCoachProvider(null);
              }}
              onClose={() => setAssistantOpen(false)}
            />
          </section>
        )}
      </div>
    </div>
  );
}
