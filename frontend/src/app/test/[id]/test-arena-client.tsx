"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Circle,
  Loader2,
  LogOut,
  Play,
  Send,
  Square,
  SquareTerminal,
  Terminal,
  XCircle,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { Brand } from "@/components/shell";
import { CodeEditor, LanguagePicker } from "@/components/arena/code-editor";
import Countdown from "@/components/arena/countdown";
import { CameraFeed } from "@/components/arena/camera-feed";
import { useTestProctoring } from "@/components/arena/use-test-proctoring";
import { ProblemStatement } from "@/components/arena/problem-statement";
import TestChip from "@/components/arena/test-chip";
import {
  DIFFICULTY_STYLE,
  STATUS_STYLES,
  difficultyLabel,
  errDetail,
  statusKeyLabel,
  topicLabel,
} from "@/components/arena/status-styles";
import client from "@/lib/api";
import type {
  CustomRunOut,
  Language,
  RunResultOut,
  TestSession,
  TestSubmitOut,
} from "@/lib/types";

type Draft = { code: string; language: Language };
type Busy = "run" | "submit" | "end" | "abandon" | null;
type Verdict =
  | { kind: "run"; data: RunResultOut; visibleCount: number }
  | { kind: "submit"; data: TestSubmitOut; visibleCount: number };

function TestArenaScreen() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const sessionId = params.id;

  const [session, setSession] = useState<TestSession | null>(null);
  const [index, setIndex] = useState(0);
  const [local, setLocal] = useState<Record<string, Draft>>({});
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [terminalOpen, setTerminalOpen] = useState(true);
  const [busy, setBusy] = useState<Busy>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [confirmExit, setConfirmExit] = useState(false);
  const [termTab, setTermTab] = useState<"result" | "custom">("result");
  const [customInput, setCustomInput] = useState("");
  const [customResult, setCustomResult] = useState<CustomRunOut | null>(null);
  const [customRunning, setCustomRunning] = useState(false);

  const draftTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const leavingRef = useRef(false);

  const questions = useMemo(() => session?.problems ?? [], [session]);
  const current = questions[index] ?? null;

  const hydrate = useCallback((data: TestSession) => {
    setSession(data);
    setTimeRemaining(data.time_remaining_seconds);
    setLocal((prev) => {
      const next = { ...prev };
      for (const q of data.problems) {
        if (next[q.id]) continue;
        const lang = (q.language ?? "python") as Language;
        next[q.id] = { code: q.code ?? q.starter_code?.[lang] ?? "", language: lang };
      }
      return next;
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    client
      .get<TestSession>(`/tests/${sessionId}`)
      .then((res) => {
        if (cancelled) return;
        if (res.data.status !== "IN_PROGRESS") {
          router.replace(`/test/${sessionId}/results`);
          return;
        }
        hydrate(res.data);
      })
      .catch((err) => {
        if (cancelled) return;
        if ((err as { response?: { status?: number } })?.response?.status === 401) {
          localStorage.removeItem("token");
          router.replace("/login");
          return;
        }
        setError(errDetail(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId, router, hydrate]);

  useEffect(() => {
    const id = setInterval(() => {
      if (leavingRef.current) return;
      client
        .get<TestSession>(`/tests/${sessionId}`)
        .then((res) => {
          if (res.data.status !== "IN_PROGRESS") {
            leavingRef.current = true;
            router.replace(`/test/${sessionId}/results`);
            return;
          }
          setTimeRemaining(res.data.time_remaining_seconds);
          setSession((prev) =>
            prev
              ? {
                  ...prev,
                  status: res.data.status,
                  time_remaining_seconds: res.data.time_remaining_seconds,
                  problems: res.data.problems,
                }
              : prev
          );
        })
        .catch(() => undefined);
    }, 20000);
    return () => clearInterval(id);
  }, [sessionId, router]);

  const persistDraft = useCallback(
    (qid: string, code: string, language: Language) => {
      if (!code.trim()) return;
      client
        .put(`/tests/${sessionId}/questions/${qid}/draft`, {
          language,
          source_code: code,
        })
        .catch(() => undefined);
    },
    [sessionId]
  );

  const queueDraft = useCallback(
    (qid: string, code: string, language: Language) => {
      if (draftTimer.current) clearTimeout(draftTimer.current);
      draftTimer.current = setTimeout(() => persistDraft(qid, code, language), 900);
    },
    [persistDraft]
  );

  useEffect(() => {
    const flush = () => {
      const q = questions[index];
      if (!q) return;
      const draft = local[q.id];
      if (!draft?.code.trim()) return;
      const token = localStorage.getItem("token");
      if (!token) return;
      void fetch(`/api/v1/tests/${sessionId}/questions/${q.id}/draft`, {
        method: "PUT",
        keepalive: true,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          language: draft.language,
          source_code: draft.code,
        }),
      }).catch(() => undefined);
    };
    window.addEventListener("pagehide", flush);
    return () => window.removeEventListener("pagehide", flush);
  }, [sessionId, questions, index, local]);

  const draft = current ? local[current.id] : undefined;

  const setCode = (value: string) => {
    if (!current) return;
    const d = local[current.id];
    setLocal((prev) => ({ ...prev, [current.id]: { ...d, code: value } }));
    queueDraft(current.id, value, d.language);
  };

  const setLanguage = (language: Language) => {
    if (!current) return;
    setLocal((prev) => {
      const d = prev[current.id];
      const code = d.language === language ? d.code : current.starter_code?.[language] ?? "";
      persistDraft(current.id, code, language);
      return { ...prev, [current.id]: { code, language } };
    });
  };

  const flushCurrent = () => {
    if (!current) return;
    const d = local[current.id];
    if (d?.code.trim()) persistDraft(current.id, d.code, d.language);
  };

  const go = (next: number) => {
    if (draftTimer.current) clearTimeout(draftTimer.current);
    flushCurrent();
    setIndex(next);
  };

  const run = async () => {
    if (!current || !draft || busy) return;
    setBusy("run");
    setError(null);
    try {
      if (draftTimer.current) clearTimeout(draftTimer.current);
      const res = await client.post<RunResultOut>(
        `/tests/${sessionId}/questions/${current.id}/run`,
        { language: draft.language, source_code: draft.code }
      );
      setVerdict({
        kind: "run",
        data: res.data,
        visibleCount: current.test_cases.length,
      });
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setBusy(null);
    }
  };

  const runCustom = async () => {
    if (!current || !draft || busy) return;
    setCustomRunning(true);
    setCustomResult(null);
    setError(null);
    try {
      const res = await client.post<CustomRunOut>("/custom-run", {
        language: draft.language,
        source_code: draft.code,
        stdin: customInput,
      });
      setCustomResult(res.data);
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setCustomRunning(false);
    }
  };

  const submit = async () => {
    if (!current || !draft || busy) return;
    setBusy("submit");
    setError(null);
    try {
      if (draftTimer.current) clearTimeout(draftTimer.current);
      const res = await client.post<TestSubmitOut>(
        `/tests/${sessionId}/questions/${current.id}/submit`,
        { language: draft.language, source_code: draft.code }
      );
      setVerdict({
        kind: "submit",
        data: res.data,
        visibleCount: current.test_cases.length,
      });
      setSession((prev) =>
        prev
          ? {
              ...prev,
              problems: prev.problems.map((q) =>
                q.id === current.id
                  ? {
                      ...q,
                      attempts: res.data.attempts,
                      status: res.data.status,
                      passed: res.data.passed,
                      runtime_ms: res.data.runtime_ms,
                      memory_kb: res.data.memory_kb,
                    }
                  : q
              ),
            }
          : prev
      );
      if (index < questions.length - 1) {
        window.setTimeout(() => go(index + 1), 900);
      }
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setBusy(null);
    }
  };

  const endTest = async () => {
    if (busy) return;
    if (!window.confirm("End the test now? Unsubmitted questions score zero.")) return;
    leavingRef.current = true;
    setBusy("end");
    try {
      await client.post(`/tests/${sessionId}/end`);
      router.replace(`/test/${sessionId}/results`);
    } catch (err) {
      setError(errDetail(err));
      setBusy(null);
      leavingRef.current = false;
    }
  };

  const abandon = async () => {
    leavingRef.current = true;
    setBusy("abandon");
    try {
      await client.post(`/tests/${sessionId}/abandon`);
      router.replace("/test");
    } catch (err) {
      setError(errDetail(err));
      setBusy(null);
      leavingRef.current = false;
    }
  };

  const onExpire = useCallback(() => {
    if (leavingRef.current) return;
    leavingRef.current = true;
    router.replace(`/test/${sessionId}/results`);
  }, [router, sessionId]);

  const answered = useMemo(
    () => questions.filter((q) => q.attempts > 0).length,
    [questions]
  );
  const passed = useMemo(
    () => questions.filter((q) => q.passed === true).length,
    [questions]
  );

  const onProctorAutoSubmit = useCallback(
    (data: TestSession) => {
      if (leavingRef.current) return;
      leavingRef.current = true;
      router.replace(`/test/${data.id}/results`);
    },
    [router]
  );

  const procActive = session?.status === "IN_PROGRESS" && !!current;
  const { violations, limit } = useTestProctoring({
    sessionId,
    enabled: procActive,
    onAutoSubmit: onProctorAutoSubmit,
  });

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 bg-[#1a1a2e] text-sm text-[#93a1bd]">
        <Loader2 size={16} className="animate-spin" />
        Loading your test
      </div>
    );
  }

  if (!session || !current || !draft) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#1a1a2e] px-6 text-center text-[#93a1bd]">
        <p className="text-sm">{error ?? "This test could not be loaded."}</p>
        <Link
          href="/test"
          className="whitespace-nowrap rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold leading-5 text-[#dce3f2] transition-colors hover:bg-white/5"
        >
          Back to setup
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#1a1a2e] text-[#dce3f2]">
      <header className="sticky top-0 z-30 border-b border-white/10 bg-[#1e1e30]/95 backdrop-blur-md">
          <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3">
            <div className="flex items-center gap-4">
              <Brand dark />
              <span className="hidden h-5 w-px bg-white/10 sm:block" />
              <div className="hidden sm:block">
                <p className="font-mono text-[0.58rem] uppercase tracking-[0.16em] text-[#93a1bd]">
                  Mock test
                </p>
                <p className="font-mono text-xs font-semibold text-[#dce3f2]">
                  {answered}/3 answered · {passed} passed
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <StrikeMeter violations={violations} limit={limit} />
              <Countdown
                key={timeRemaining}
                timeRemainingSeconds={timeRemaining}
                onExpire={onExpire}
              />
              <button
                type="button"
                onClick={endTest}
                disabled={busy !== null}
                className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-semibold text-[#dce3f2] transition-colors hover:border-white/25 hover:bg-[#2b2b4a] disabled:opacity-40"
              >
                <Square size={12} />
                End test
              </button>
              <button
                type="button"
                onClick={() => setConfirmExit(true)}
                disabled={busy !== null}
                title="Abandon test"
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 text-[#93a1bd] transition-colors hover:border-red-500/50 hover:text-red-400 disabled:opacity-40"
              >
                <LogOut size={14} />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto border-t border-white/5 px-5 py-2.5">
            {questions.map((q, i) => (
              <button
                key={q.id}
                type="button"
                onClick={() => go(i)}
                className={`flex shrink-0 items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
                  i === index
                    ? "border-[#d4a72c]/60 bg-[#d4a72c]/15 text-[#f5f5f5]"
                    : "border-white/10 text-[#93a1bd] hover:border-white/25 hover:text-[#dce3f2]"
                }`}
              >
                {q.passed === true ? (
                  <CheckCircle2 size={13} className="text-emerald-400" />
                ) : q.passed === false ? (
                  <XCircle size={13} className="text-red-400" />
                ) : q.attempts > 0 ? (
                  <Circle size={13} className="text-yellow-300" />
                ) : (
                  <span className="h-2 w-2 rounded-full bg-white/20" />
                )}
                Q{i + 1}
                <span
                  className={`font-mono text-[0.6rem] font-bold ${DIFFICULTY_STYLE[q.difficulty]}`}
                >
                  {difficultyLabel(q.difficulty)}
                </span>
              </button>
            ))}
            <div className="ml-auto hidden items-center gap-1.5 pl-4 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#93a1bd] md:flex">
              Topics
              {Array.from(new Set(session.assigned_topics)).map((t) => (
                <span
                  key={t}
                  className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5"
                >
                  {topicLabel(t)}
                </span>
              ))}
            </div>
          </div>
        </header>

        {error && (
          <div className="flex items-center justify-between gap-3 border-b border-red-500/25 bg-red-500/10 px-5 py-2.5 text-sm text-red-300">
            <span className="flex items-center gap-2">
              <AlertTriangle size={14} />
              {error}
            </span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-xs font-semibold underline-offset-2 hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="grid min-h-0 flex-1 gap-4 overflow-y-auto p-4 lg:grid-cols-[minmax(0,420px)_1fr] lg:overflow-hidden">
          <section className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#1e1e30]">
            <div className="border-b border-white/10 px-5 py-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#93a1bd]">
                  {topicLabel(current.category)}
                </span>
                <span
                  className={`font-mono text-[0.6rem] font-bold uppercase tracking-[0.14em] ${DIFFICULTY_STYLE[current.difficulty]}`}
                >
                  {difficultyLabel(current.difficulty)}
                </span>
                {current.attempts > 0 && (
                  <span className="font-mono text-[0.6rem] text-[#93a1bd]">
                    {current.attempts} attempt{current.attempts > 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <h1 className="mt-2 font-display text-xl font-bold leading-snug tracking-tight">
                {current.title}
              </h1>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
              <ProblemStatement text={current.description} />
            </div>

            <div className="border-t border-white/10 px-5 py-3">
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#93a1bd]">
                {current.test_cases.length} sample case
                {current.test_cases.length === 1 ? "" : "s"} ·{" "}
                {current.hidden_test_count} hidden
              </p>
            </div>
          </section>

          <section className="flex min-h-0 flex-col gap-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <LanguagePicker
                value={draft.language}
                onChange={setLanguage}
              />
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={run}
                  disabled={busy !== null || !draft.code.trim()}
                  className="flex items-center gap-1.5 rounded-lg border border-white/15 bg-[#252540] px-3.5 py-1.5 text-sm font-semibold text-[#dce3f2] transition-colors hover:border-white/30 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {busy === "run" ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Play size={14} />
                  )}
                  Run
                </button>
                <button
                  type="button"
                  onClick={submit}
                  disabled={busy !== null || !draft.code.trim()}
                  className="flex items-center gap-1.5 rounded-lg bg-[#d4a72c] px-3.5 py-1.5 text-sm font-bold text-[#1a1a2e] transition-colors hover:bg-[#e0b53c] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {busy === "submit" ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Send size={14} />
                  )}
                  Submit
                </button>
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-hidden rounded-2xl border border-white/10 bg-[#1e1e30]">
              <CodeEditor
                value={draft.code}
                language={draft.language}
                onChange={setCode}
              />
            </div>

            <div className="flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => go(Math.max(0, index - 1))}
                disabled={index === 0}
                className="flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-[#93a1bd] transition-colors hover:border-white/25 hover:text-[#dce3f2] disabled:opacity-30"
              >
                <ChevronLeft size={13} />
                Previous
              </button>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-[#93a1bd]">
                Draft saved automatically
              </p>
              <button
                type="button"
                onClick={() => go(Math.min(questions.length - 1, index + 1))}
                disabled={index >= questions.length - 1}
                className="flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-[#93a1bd] transition-colors hover:border-white/25 hover:text-[#dce3f2] disabled:opacity-30"
              >
                Next
                <ChevronRight size={13} />
              </button>
            </div>

            <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#1e1e30]">
              <button
                type="button"
                onClick={() => setTerminalOpen((v) => !v)}
                className="flex w-full items-center justify-between px-4 py-2.5 text-left transition-colors hover:bg-white/5"
              >
                <span className="flex items-center gap-2 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.14em] text-[#93a1bd]">
                  <Terminal size={13} />
                  Terminal
                </span>
                {terminalOpen ? (
                  <ChevronDown size={14} className="text-[#93a1bd]" />
                ) : (
                  <ChevronUp size={14} className="text-[#93a1bd]" />
                )}
              </button>
              {terminalOpen && (
                <div className="border-t border-white/10">
                  <div className="flex gap-1 border-b border-white/10 px-5 py-2">
                    <button
                      type="button"
                      onClick={() => setTermTab("result")}
                      className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                        termTab === "result"
                          ? "bg-white/10 text-[#dce3f2]"
                          : "text-[#93a1bd] hover:bg-white/5 hover:text-[#dce3f2]"
                      }`}
                    >
                      <Terminal size={12} />
                      Results
                    </button>
                    <button
                      type="button"
                      onClick={() => setTermTab("custom")}
                      className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                        termTab === "custom"
                          ? "bg-white/10 text-[#dce3f2]"
                          : "text-[#93a1bd] hover:bg-white/5 hover:text-[#dce3f2]"
                      }`}
                    >
                      {customResult ? (
                        <Check size={12} className="text-emerald-400" />
                      ) : (
                        <SquareTerminal size={12} />
                      )}
                      Custom
                    </button>
                  </div>
                  <div className="max-h-72 overflow-y-auto px-5 py-3">
                    {termTab === "result" ? (
                      error ? (
                        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                          <p className="flex items-center gap-2 font-mono text-[13px] font-semibold text-red-300">
                            <AlertTriangle size={14} className="shrink-0" />
                            {error}
                          </p>
                        </div>
                      ) : busy === "run" || busy === "submit" ? (
                        <p className="flex items-center gap-2 text-sm text-[#93a1bd]">
                          <Loader2 size={13} className="animate-spin" />
                          Running test cases…
                        </p>
                      ) : verdict ? (
                        <div className="space-y-3">
                          {verdictError(verdict) && (
                            <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3">
                              <p className="flex items-center gap-2 font-mono text-[13px] font-bold text-red-300">
                                <XCircle size={14} className="shrink-0" />
                                {verdictError(verdict)?.label}
                              </p>
                              <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words font-mono text-[13px] leading-relaxed text-red-200">
                                {verdictError(verdict)?.output}
                              </pre>
                            </div>
                          )}
                          <VerdictPanel verdict={verdict} />
                        </div>
                      ) : (
                        <p className="text-sm text-[#93a1bd]">
                          Run or submit to see results here.
                        </p>
                      )
                    ) : (
                      <div>
                        <p className="text-[13px] text-[#93a1bd]">
                          Run your code against your own input. This is not graded.
                        </p>
                        <textarea
                          value={customInput}
                          onChange={(e) => setCustomInput(e.target.value)}
                          rows={4}
                          spellCheck={false}
                          placeholder="Paste stdin input\u2026 each case on its own line"
                          className="mt-2 w-full resize-y rounded-lg border border-white/10 bg-[#12121f] p-3 font-mono text-[13px] text-[#dce3f2] placeholder:text-[#3c4a63] outline-none focus:border-emerald-400/50"
                        />
                        <button
                          type="button"
                          onClick={runCustom}
                          disabled={customRunning || busy !== null || !draft?.code.trim()}
                          className="mt-3 flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-[#dce3f2] transition-colors hover:border-white/25 hover:bg-white/10 disabled:opacity-50"
                        >
                          {customRunning ? (
                            <Loader2 size={13} className="animate-spin" />
                          ) : (
                            <Play size={13} />
                          )}
                          Run custom
                        </button>

                        {customResult && (
                          <div className="mt-3">
                            <div className="flex flex-wrap items-center gap-2">
                              {customResult.status ? (
                                <span
                                  className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[customResult.status]?.chip || "text-[#93a1bd]"}`}
                                >
                                  {STATUS_STYLES[customResult.status]?.icon}
                                  {STATUS_STYLES[customResult.status]?.label}
                                </span>
                              ) : (
                                <span className="text-xs font-medium text-[#93a1bd]">
                                  {customResult.status_key}
                                </span>
                              )}
                              <span className="font-mono text-xs text-[#93a1bd]">
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
                                    ? "border-emerald-500/30 text-emerald-400"
                                    : "border-red-500/30 text-red-300"
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
                                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md border border-red-500/30 p-2 font-mono text-[13px] leading-relaxed text-red-300">
                                  {customResult.stderr || customResult.compile_output}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>

        {confirmExit && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-6 backdrop-blur-sm">
            <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-[#1e1e30] p-6 shadow-2xl">
              <h2 className="font-display text-lg font-bold text-[#f5f5f5]">
                Abandon this test?
              </h2>
              <p className="mt-2 text-sm text-[#93a1bd]">
                Your answers are discarded and nothing is recorded. This cannot be
                undone.
              </p>
              <div className="mt-5 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setConfirmExit(false)}
                  className="whitespace-nowrap rounded-lg border border-white/10 px-4 py-2 text-sm font-medium leading-5 text-[#dce3f2] transition-colors hover:bg-white/5"
                >
                  Keep going
                </button>
                <button
                  type="button"
                  onClick={abandon}
                  disabled={busy === "abandon"}
                  className="flex items-center gap-2 whitespace-nowrap rounded-lg bg-red-500/90 px-4 py-2 text-sm font-bold leading-5 text-white transition-colors hover:bg-red-500 disabled:opacity-50"
                >
                  {busy === "abandon" && <Loader2 size={14} className="animate-spin" />}
                  Abandon
                </button>
              </div>
            </div>
          </div>
        )}

        {procActive && <CameraFeed />}
      </div>
  );
}

export default function TestArenaClient() {
  return (
    <ProtectedRoute>
      <TestArenaScreen />
    </ProtectedRoute>
  );
}

function verdictError(
  verdict: Verdict
): { label: string; output: string } | null {
  const { data } = verdict;
  if (data.status !== "COMPILATION_ERROR" && data.status !== "RUNTIME_ERROR") {
    return null;
  }
  const withOutput = data.test_results.find((r) => {
    const err = (r as { stderr?: string | null }).stderr;
    return typeof err === "string" && err.length > 0;
  });
  const output = (withOutput as { stderr?: string | null }).stderr;
  if (!output) return null;
  const style = STATUS_STYLES[data.status];
  return { label: style?.label ?? data.status, output };
}

function StrikeMeter({
  violations,
  limit,
}: {
  violations: number;
  limit: number;
}) {
  return (
    <div
      className="flex items-center gap-1.5"
      title={`${violations} of ${limit} proctoring violations`}
    >
      <span className="font-mono text-[0.58rem] uppercase tracking-[0.16em] text-[#93a1bd]">
        Focus
      </span>
      {Array.from({ length: limit }).map((_, i) => {
        const used = i < violations;
        return (
          <span
            key={i}
            className={`h-2 w-2 rounded-full ${violations >= limit ? "bg-red-500" : used ? "bg-amber-400" : "bg-white/15"}`}
          />
        );
      })}
    </div>
  );
}

function VerdictPanel({ verdict }: { verdict: Verdict }) {
  const [caseIndex, setCaseIndex] = useState(0);

  useEffect(() => {
    if (verdict.kind === "run") {
      const firstFailed = verdict.data.test_results
        .slice(0, verdict.visibleCount)
        .findIndex((r) => !r.passed);
      setCaseIndex(firstFailed === -1 ? 0 : firstFailed);
    }
  }, [verdict]);

  if (verdict.kind === "submit") {
    const { data } = verdict;
    const style = STATUS_STYLES[data.status] ?? STATUS_STYLES.WRONG_ANSWER;
    return (
      <div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-semibold ${style.chip}`}
          >
            {style.icon}
            {data.passed ? "Accepted" : style.label}
          </span>
          <div className="flex items-center gap-2">
            {data.test_results.map((r) => (
              <TestChip key={r.index} passed={r.passed} index={r.index} />
            ))}
          </div>
          <span className="font-mono text-[13px] text-[#93a1bd]">
            {Math.round(data.runtime_ms)}ms · {Math.round(data.memory_kb / 1024)}
            MB
          </span>
        </div>
        <p className="mt-3 text-sm text-[#93a1bd]">
          Attempt {data.attempts} recorded.
        </p>
      </div>
    );
  }

  const { data } = verdict;
  const style = STATUS_STYLES[data.status] ?? STATUS_STYLES.WRONG_ANSWER;
  const visible = data.test_results.slice(0, verdict.visibleCount);
  const selected = visible[Math.min(caseIndex, visible.length - 1)] ?? visible[0];

  if (!selected) return null;

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span
          className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-semibold ${style.chip}`}
        >
          {style.icon}
          {style.label}
        </span>
        <div className="flex items-center gap-2">
          {visible.map((r) => (
            <TestChip key={r.index} passed={r.passed} index={r.index} />
          ))}
        </div>
      </div>

      {data.status === "ACCEPTED" && (
        <p className="mb-3 text-sm text-emerald-400">All sample cases passed.</p>
      )}

      <div className="mt-3">
        <div className="flex flex-wrap items-center gap-2">
          {visible.map((r, i) => (
            <button
              key={r.index}
              type="button"
              onClick={() => setCaseIndex(i)}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 font-mono text-xs font-semibold transition-colors ${
                i === caseIndex
                  ? "border-[#d4a72c]/60 bg-[#d4a72c]/15 text-[#f5f5f5]"
                  : "border-white/10 text-[#93a1bd] hover:border-white/25 hover:text-[#dce3f2]"
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  r.passed ? "bg-emerald-400" : "bg-red-400"
                }`}
              />
              Testcase {i + 1}
            </button>
          ))}
        </div>

          <div
            className={`mt-2 overflow-hidden rounded-xl border bg-[#16162a] ${
              selected.passed ? "border-emerald-500/25" : "border-red-500/25"
            }`}
          >
            <div
              className={`flex items-center justify-between border-b px-3 py-1.5 ${
                selected.passed
                  ? "border-emerald-500/25 bg-emerald-500/10"
                  : "border-red-500/25 bg-red-500/10"
              }`}
            >
              <span
                className={`font-mono text-[11px] font-bold uppercase tracking-[0.14em] ${
                  selected.passed ? "text-emerald-400" : "text-red-300"
                }`}
              >
                {selected.passed ? "Testcase Passed" : "Testcase Failed"}
              </span>
              <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                Case {selected.index + 1} ·{" "}
                {!selected.passed && selected.status_key === "ACCEPTED"
                  ? "Wrong Answer"
                  : statusKeyLabel(selected.status_key)}
              </span>
            </div>
            <div className="space-y-3 px-3 py-3">
              <div>
                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                  Input (stdin)
                </p>
                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-[#1e1e30] p-2 font-mono text-[13px] leading-relaxed text-[#c3cde3]">
                  {(selected.input || "").trimEnd()}
                </pre>
              </div>
              <div>
                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                  Your Output (stdout)
                </p>
                <pre
                  className={`overflow-x-auto whitespace-pre-wrap break-words rounded-md border p-2 font-mono text-[13px] leading-relaxed ${
                    selected.passed
                      ? "border-emerald-500/30 bg-[#1e1e30] text-emerald-400"
                      : "border-red-500/30 bg-[#1e1e30] text-red-300"
                  }`}
                >
                  {(selected.actual_output ?? "(no output)").trimEnd()}
                </pre>
              </div>
              <div>
                <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#93a1bd]">
                  Expected Output
                </p>
                <pre className="overflow-x-auto whitespace-pre-wrap break-words rounded-md bg-[#1e1e30] p-2 font-mono text-[13px] leading-relaxed text-emerald-400">
                  {(selected.expected_output || "").trimEnd()}
                </pre>
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}
