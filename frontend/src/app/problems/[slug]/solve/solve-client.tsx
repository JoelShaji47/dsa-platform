"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Brain, Loader2, Play, Send } from "lucide-react";
import { DockviewReact } from "dockview-react";
import type { DockviewApi, DockviewReadyEvent } from "dockview-core";
import "./dockview-base.css";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import client from "@/lib/api";
import { ThemeToggle } from "@/context/theme-context";
import type {
  AnalyzeOut,
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
import AnalysisView from "./analysis-view";
import type { EditableCase } from "./console-panel";
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
  const [runCount, setRunCount] = useState(0);
  const [caseEdits, setCaseEdits] = useState<EditableCase[] | null>(null);
  const [editableRunning, setEditableRunning] = useState(false);

  const [submissions, setSubmissions] = useState<SubmissionHistoryItem[]>([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);

  const [coachMessages, setCoachMessages] = useState<CoachMessage[]>([]);
  const [coachLoading, setCoachLoading] = useState(false);
  const [coachProvider, setCoachProvider] = useState<string | null>(null);
  const [includeCode, setIncludeCode] = useState(true);

  const [dockApi, setDockApi] = useState<DockviewApi | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalyzeOut | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

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

  const editableCases: EditableCase[] = useMemo(
    () =>
      caseEdits ??
      (problem?.test_cases ?? []).map((c) => ({
        input: c.input,
        expected_output: c.expected_output,
      })),
    [caseEdits, problem]
  );

  const onEditCase = useCallback(
    (index: number, field: "input" | "expected_output", value: string) => {
      const base =
        caseEdits ??
        (problem?.test_cases ?? []).map((c) => ({
          input: c.input,
          expected_output: c.expected_output,
        }));
      setCaseEdits(base.map((c, i) => (i === index ? { ...c, [field]: value } : c)));
    },
    [caseEdits, problem]
  );

  const onResetEditableCases = useCallback(() => {
    setCaseEdits(null);
  }, []);

  const runEditedCases = useCallback(async () => {
    if (running || submitting || editableRunning || !code.trim()) return;
    if (editableCases.length === 0) return;
    setEditableRunning(true);
    setError(null);
    setSubmitResult(null);
    try {
      const res = await client.post<RunResultOut>(
        `/problems/${slug}/run-cases`,
        { language: lang, source_code: code, mode, test_cases: editableCases },
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
      setEditableRunning(false);
    }
  }, [slug, lang, code, mode, editableCases, running, submitting, editableRunning, focusConsole]);

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

  const runAnalyze = useCallback(async () => {
    setIsAnalyzing(true);
    setAnalyzing(true);
    setAnalyzeError(null);
    setAnalysis(null);
    try {
      const res = await client.post<AnalyzeOut>(`/problems/${slug}/analyze`, {
        source_code: code,
        language: lang,
      });
      setAnalysis(res.data);
    } catch (err) {
      setAnalyzeError(
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Could not analyze your solution. Try again."
      );
    } finally {
      setAnalyzing(false);
    }
  }, [slug, code, lang]);

  const closeAnalyze = useCallback(() => {
    setIsAnalyzing(false);
    setAnalyzing(false);
  }, []);

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

  const openCoach = useCallback(() => {
    if (!dockApi) return;
    try {
      const existing = dockApi.getPanel("coach");
      if (existing) {
        existing.focus();
        return;
      }
    } catch {
    }
    try {
      dockApi.addPanel({
        id: "coach",
        title: "Coach",
        component: "coach",
        position: { referencePanel: "code", direction: "within" },
      });
    } catch {
    }
  }, [dockApi]);

  const closeCoach = useCallback(() => {
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
    api.addPanel({
      id: "coach",
      title: "Coach",
      component: "coach",
      position: { referencePanel: "code", direction: "within" },
    });
    try {
      // Coach lands selected — put Code back on top, keep focus on description.
      api.getPanel("code")?.api.setActive();
      api.getPanel("description")?.focus();
    } catch {
    }
    setDockApi(api);
  }, []);

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
    editableCases,
    onEditCase,
    onRunEditableCases: runEditedCases,
    editableRunning,
    onResetEditableCases,
    review,
    reviewLoading,
    fetchReview,
    runAnalyze,
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

  return (
    <div className="flex h-screen flex-col bg-[#0b0d12]">
      {/* ── Top bar ──────────────────────────────────────────── */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-white/10 bg-[#0e1119] px-4">
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
          <span className={`text-xs font-medium ${DIFFICULTY_STYLE[problem.difficulty as Difficulty]}`}>
            {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
          </span>
          {problem.solved && (
            <span className="rounded-md border border-emerald-500/50 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">
              Solved
            </span>
          )}
        </div>
        <div className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto pl-2">
          <ThemeToggle dark />
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
            onClick={openCoach}
            title="Open coach"
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-white/20 hover:text-gray-100"
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

      {/* ── Dock workspace: every tab drags anywhere ─────────── */}
      {isAnalyzing ? (
        <div className="dock-root min-h-0 flex-1 overflow-hidden">
          <AnalysisView
            analysis={analysis}
            loading={analyzing}
            error={analyzeError}
            onClose={closeAnalyze}
          />
        </div>
      ) : (
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
        </div>
      )}
    </div>
  );
}
