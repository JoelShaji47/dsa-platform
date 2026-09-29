"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Loader2,
  RotateCcw,
  XCircle,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { Brand } from "@/components/shell";
import { formatClock, topicLabel } from "@/components/arena/status-styles";
import client from "@/lib/api";
import type { TestResultItem, TestResults } from "@/lib/types";

const DIFF_CLASS: Record<string, string> = {
  EASY: "text-quest",
  MEDIUM: "text-[#b57b12]",
  HARD: "text-rust",
};

export default function TestResultsClient() {
  return (
    <ProtectedRoute>
      <TestResultsScreen />
    </ProtectedRoute>
  );
}

function TestResultsScreen() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const sessionId = params.id;

  const [results, setResults] = useState<TestResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    client
      .get<TestResults>(`/tests/${sessionId}/results`)
      .then((res) => {
        if (cancelled) return;
        setResults(res.data);
      })
      .catch((err) => {
        if (cancelled) return;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 401) {
          localStorage.removeItem("token");
          router.replace("/login");
          return;
        }
        if (status === 409) {
          router.replace(`/test/${sessionId}`);
          return;
        }
        const detail = (
          err as { response?: { data?: { detail?: string } } }
        )?.response?.data?.detail;
        setError(detail ?? "Could not load results.");
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId, router]);

  if (error) {
    return (
      <Shell>
        <div className="mx-auto max-w-3xl px-5 py-20 text-center">
          <p className="text-sm text-rust">{error}</p>
          <Link
            href="/test"
            className="mt-6 inline-block whitespace-nowrap rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold leading-6 text-primary-foreground"
          >
            Back to setup
          </Link>
        </div>
      </Shell>
    );
  }

  if (!results) {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 bg-paper text-sm text-ink-faint">
        <Loader2 size={16} className="animate-spin" />
        Scoring your test
      </div>
    );
  }

  const expired = results.status === "EXPIRED";
  const perfect = results.score === results.total;

  return (
    <Shell>
      <main className="mx-auto max-w-3xl px-5 py-10">
        <div className="text-center">
          <p className="font-mono text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-gold">
            {expired ? "Time expired" : "Test complete"}
          </p>
          <h1 className="mt-2 font-display text-5xl font-bold tracking-tight text-ink">
            {results.score}
            <span className="text-2xl text-ink-faint">/{results.total}</span>
          </h1>
          <p className="mt-3 text-ink-soft">
            {perfect
              ? "A clean sweep across every difficulty."
              : `${results.passed_count} of ${results.total} questions passed.`}
          </p>
        </div>

        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Score" value={`${results.score}/${results.total}`} />
          <Stat label="Time taken" value={formatClock(results.time_taken_seconds)} />
          <Stat label="Topics" value={String(results.assigned_topics.length)} />
          <Stat label="Outcome" value={expired ? "Expired" : "Submitted"} />
        </div>

        <section className="mt-8 space-y-3">
          <h2 className="font-display text-lg font-bold text-ink">
            Question breakdown
          </h2>
          {results.results.map((r) => (
            <QuestionRow key={r.position} item={r} />
          ))}
        </section>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link
            href="/test"
            className="flex items-center gap-2 whitespace-nowrap rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold leading-6 text-primary-foreground transition-opacity hover:opacity-90"
          >
            <RotateCcw size={15} className="shrink-0" />
            Take another test
          </Link>
          <Link
            href="/roadmap"
            className="flex items-center gap-2 whitespace-nowrap rounded-xl border border-ink/15 bg-card px-5 py-2.5 text-sm font-semibold leading-6 text-ink-soft transition-colors hover:border-ink/30 hover:text-ink"
          >
            <ArrowLeft size={15} className="shrink-0" />
            Back to roadmap
          </Link>
        </div>
      </main>
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-ink/10 bg-card/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-5 py-4">
          <Link
            href="/roadmap"
            className="flex items-center gap-2 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
          >
            <ArrowLeft size={16} />
            Roadmap
          </Link>
          <Brand />
        </div>
      </header>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-ink/10 bg-card px-4 py-3 shadow-card">
      <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
        {label}
      </p>
      <p className="mt-1 font-mono text-lg font-bold text-ink">{value}</p>
    </div>
  );
}

function QuestionRow({ item }: { item: TestResultItem }) {
  const unattempted = item.attempts === 0;
  return (
    <div className="flex items-start gap-4 rounded-2xl border border-ink/10 bg-card p-5 shadow-card">
      <div className="mt-0.5 shrink-0">
        {unattempted ? (
          <Clock size={20} className="text-ink-faint" />
        ) : item.passed ? (
          <CheckCircle2 size={20} className="text-quest" />
        ) : (
          <XCircle size={20} className="text-rust" />
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
            Q{item.position}
          </span>
          <span
            className={`font-mono text-[0.6rem] font-bold uppercase tracking-[0.14em] ${DIFF_CLASS[item.difficulty]}`}
          >
            {item.difficulty}
          </span>
          <span className="rounded-md border border-ink/10 bg-paper px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-ink-soft">
            {topicLabel(item.category)}
          </span>
        </div>

        <p className="mt-1.5 font-medium text-ink">{item.title}</p>

        <p className="mt-1 font-mono text-xs text-ink-faint">
          {unattempted
            ? "Not submitted · scored 0"
            : `${item.attempts} attempt${item.attempts > 1 ? "s" : ""} · ${
                item.status ?? "FAILED"
              }${
                item.runtime_ms != null
                  ? ` · ${Math.round(item.runtime_ms)}ms`
                  : ""
              }`}
        </p>
      </div>
    </div>
  );
}
