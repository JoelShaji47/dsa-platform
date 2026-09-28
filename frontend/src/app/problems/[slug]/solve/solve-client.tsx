"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  ArrowLeftRight,
  BookOpen,
  Brain,
  Code2,
  Columns2,
  Loader2,
  Play,
  Send,
} from "lucide-react";
import {
  Group,
  Panel,
  Separator,
  usePanelRef,
} from "react-resizable-panels";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import client from "@/lib/api";
import type {
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
import AssistantPanel, { type CoachMessage } from "./assistant-panel";
import QuestionPane from "./question-pane";
import WorkPane from "./work-pane";
import { DIFFICULTY_STYLE, errDetail } from "./status-utils";

const LANGS: { key: Language; label: string; ext: () => unknown }[] = [
  { key: "python", label: "Python", ext: python },
  { key: "cpp", label: "C++", ext: cpp },
  { key: "java", label: "Java", ext: java },
];

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
  const [consoleOpen, setConsoleOpen] = useState(true);
  const [consoleTab, setConsoleTab] = useState("testcase");
  const [runCount, setRunCount] = useState(0);

  const [leftTab, setLeftTab] = useState("description");
  const [submissions, setSubmissions] = useState<SubmissionHistoryItem[]>([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);

  const [assistantOpen, setAssistantOpen] = useState(false);
  const [coachMessages, setCoachMessages] = useState<CoachMessage[]>([]);
  const [coachLoading, setCoachLoading] = useState(false);
  const [coachProvider, setCoachProvider] = useState<string | null>(null);
  const [includeCode, setIncludeCode] = useState(true);
  const [hFlip, setHFlip] = useState(false);

  const leftRef = usePanelRef();
  const rightRef = usePanelRef();
  const editorRef = usePanelRef();
  const consoleRef = usePanelRef();

  const layoutDefault = useCallback(() => {
    leftRef.current?.expand();
    rightRef.current?.expand();
    leftRef.current?.resize(42);
    editorRef.current?.expand();
    editorRef.current?.resize(62);
    consoleRef.current?.resize(38);
  }, []);

  const layoutFocusCode = useCallback(() => {
    leftRef.current?.collapse();
    rightRef.current?.expand();
    editorRef.current?.expand();
  }, []);

  const layoutFocusText = useCallback(() => {
    leftRef.current?.expand();
    leftRef.current?.resize(62);
    rightRef.current?.collapse();
  }, []);

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
      setConsoleOpen(true);
      setConsoleTab("result");
    } catch (err) {
      setError(errDetail(err));
      setConsoleOpen(true);
      setConsoleTab("output");
    } finally {
      setRunning(false);
    }
  }, [slug, lang, code, mode]);

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
  }, [slug, lang, code, mode, fetchSubmissions]);

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

  const shown: RunResultOut | SubmissionResultOut | null =
    submitResult || runResult;
  const shownStatus: SubmissionStatus | undefined = shown?.status;

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
          <div className="hidden items-center gap-0.5 rounded-lg border border-white/10 bg-[#252540] p-0.5 md:flex">
            <button
              onClick={layoutDefault}
              title="Split layout"
              className="rounded-md p-1.5 text-gray-500 transition-colors hover:text-gray-200"
            >
              <Columns2 size={13} />
            </button>
            <button
              onClick={layoutFocusCode}
              title="Focus code"
              className="rounded-md p-1.5 text-gray-500 transition-colors hover:text-gray-200"
            >
              <Code2 size={13} />
            </button>
            <button
              onClick={layoutFocusText}
              title="Focus question"
              className="rounded-md p-1.5 text-gray-500 transition-colors hover:text-gray-200"
            >
              <BookOpen size={13} />
            </button>
            <button
              onClick={() => setHFlip((v) => !v)}
              title="Swap question and code sides"
              className={`rounded-md p-1.5 transition-colors ${
                hFlip ? "text-quest" : "text-gray-500 hover:text-gray-200"
              }`}
            >
              <ArrowLeftRight size={13} />
            </button>
          </div>
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

      {/* ── Resizable workspace (LeetCode-style) ─────────────── */}
      <div className="min-h-0 flex-1">
        <Group orientation="horizontal" className="h-full">
          {!hFlip ? (
            <>
              <QuestionPane
                panelRef={leftRef}
                problem={problem}
                leftTab={leftTab}
                onLeftTab={handleLeftTab}
                submissions={submissions}
                submissionsLoading={submissionsLoading}
                hintMeta={hintMeta}
                revealedHints={revealedHints}
                armedHint={armedHint}
                loadingHint={loadingHint}
                onHintClick={onHintClick}
              />
              <Separator className="group flex w-2 cursor-col-resize items-center justify-center bg-[#1a1a2e] outline-none">
                <span className="h-10 w-[3px] rounded-full bg-white/10 transition-colors group-hover:bg-quest group-data-[separator-active]:bg-quest" />
              </Separator>
              <WorkPane
                panelRef={rightRef}
                editorRef={editorRef}
                consoleRef={consoleRef}
                lang={lang}
                mode={mode}
                problem={problem}
                code={code}
                runCount={runCount}
                onCode={setCode}
                onModeChange={handleModeChange}
                consoleOpen={consoleOpen}
                setConsoleOpen={setConsoleOpen}
                shown={shown}
                shownStatus={shownStatus}
                error={error}
                runResult={runResult}
                submitResult={submitResult}
                consoleTab={consoleTab}
                setConsoleTab={setConsoleTab}
                review={review}
                reviewLoading={reviewLoading}
                fetchReview={fetchReview}
              />
            </>
          ) : (
            <>
              <WorkPane
                panelRef={rightRef}
                editorRef={editorRef}
                consoleRef={consoleRef}
                lang={lang}
                mode={mode}
                problem={problem}
                code={code}
                runCount={runCount}
                onCode={setCode}
                onModeChange={handleModeChange}
                consoleOpen={consoleOpen}
                setConsoleOpen={setConsoleOpen}
                shown={shown}
                shownStatus={shownStatus}
                error={error}
                runResult={runResult}
                submitResult={submitResult}
                consoleTab={consoleTab}
                setConsoleTab={setConsoleTab}
                review={review}
                reviewLoading={reviewLoading}
                fetchReview={fetchReview}
              />
              <Separator className="group flex w-2 cursor-col-resize items-center justify-center bg-[#1a1a2e] outline-none">
                <span className="h-10 w-[3px] rounded-full bg-white/10 transition-colors group-hover:bg-quest group-data-[separator-active]:bg-quest" />
              </Separator>
              <QuestionPane
                panelRef={leftRef}
                problem={problem}
                leftTab={leftTab}
                onLeftTab={handleLeftTab}
                submissions={submissions}
                submissionsLoading={submissionsLoading}
                hintMeta={hintMeta}
                revealedHints={revealedHints}
                armedHint={armedHint}
                loadingHint={loadingHint}
                onHintClick={onHintClick}
              />
            </>
          )}
          {assistantOpen && (
            <>
              <Separator className="group flex w-2 cursor-col-resize items-center justify-center bg-[#1a1a2e] outline-none">
                <span className="h-10 w-[3px] rounded-full bg-white/10 transition-colors group-hover:bg-violet-400 group-data-[separator-active]:bg-violet-400" />
              </Separator>
              <Panel
                key="c"
                defaultSize={24}
                minSize={16}
                collapsible
                className="min-h-0"
              >
                <AssistantPanel
                  messages={coachMessages}
                  loading={coachLoading}
                  provider={coachProvider}
                  includeCode={includeCode}
                  contextNote={`${lang} · ${mode} · ${
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
              </Panel>
            </>
          )}
        </Group>
      </div>
    </div>
  );
}
