"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Check,
  Loader2,
  Sparkles,
  Timer,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { Brand } from "@/components/shell";
import client from "@/lib/api";
import type { TestConfigOut, TestSession } from "@/lib/types";
import {
  errDetail,
  formatClock,
  topicLabel,
} from "@/components/arena/status-styles";

export default function TestSetupClient() {
  return (
    <ProtectedRoute>
      <TestSetupScreen />
    </ProtectedRoute>
  );
}

function TestSetupScreen() {
  const router = useRouter();
  const [config, setConfig] = useState<TestConfigOut | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    client
      .get<TestConfigOut>("/tests/config")
      .then((res) => {
        if (cancelled) return;
        setConfig(res.data);
        setSelected(res.data.topics.map((t) => t.topic));
      })
      .catch((err) => {
        if (cancelled) return;
        if ((err as { response?: { status?: number } })?.response?.status === 401) {
          localStorage.removeItem("token");
          router.replace("/login");
          return;
        }
        setError(errDetail(err));
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  const reload = useCallback(async () => {
    setError(null);
    try {
      const res = await client.get<TestConfigOut>("/tests/config");
      setConfig(res.data);
      setSelected(res.data.topics.map((t) => t.topic));
    } catch (err) {
      setError(errDetail(err));
    }
  }, []);

  const toggle = (topic: string) =>
    setSelected((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );

  const allTopics = useMemo(
    () => (config ? config.topics.map((t) => t.topic) : []),
    [config]
  );
  const allSelected = allTopics.length > 0 && selected.length === allTopics.length;

  const duration = config?.default_duration_seconds ?? 3600;
  const minutes = Math.round(duration / 60);

  const start = async () => {
    if (!selected.length || starting) return;
    setStarting(true);
    setError(null);
    try {
      const res = await client.post<TestSession>("/tests", {
        topics: selected,
        duration_seconds: duration,
      });
      router.push(`/test/${res.data.id}`);
    } catch (err) {
      setError(errDetail(err));
      setStarting(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-ink/10 bg-card/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-5 py-4">
          <Link
            href="/roadmap"
            className="flex shrink-0 items-center gap-2 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
          >
            <ArrowLeft size={16} />
            Roadmap
          </Link>
          <Brand />
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-5 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-gold">
              Mock interview
            </p>
            <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-ink">
              Take a Test
            </h1>
            <p className="mt-2 max-w-xl text-ink-soft">
              The test is {minutes} minutes. Submit each question before the
              timer runs out for it to be graded.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border border-ink/10 bg-card px-4 py-3 shadow-card">
            <Timer size={18} className="shrink-0 text-gold" />
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Duration
              </p>
              <p className="font-mono text-lg font-bold text-ink">
                {formatClock(duration)}
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-6 flex items-center justify-between gap-4 rounded-2xl border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust">
            <span className="min-w-0 break-words">{error}</span>
            <button
              type="button"
              onClick={reload}
              className="shrink-0 whitespace-nowrap rounded-lg border border-rust/30 px-3 py-1 font-semibold leading-5 transition-colors hover:bg-rust/15"
            >
              Retry
            </button>
          </div>
        )}

        <section className="mt-8 rounded-2xl border border-ink/10 bg-card p-6 shadow-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">
                Topic focus
              </h2>
              <p className="mt-1 text-sm text-ink-soft">
                Pick the areas you want to be tested on.
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setSelected(allTopics)}
                disabled={allSelected}
                className="whitespace-nowrap rounded-lg border border-ink/15 px-3 py-1.5 text-sm font-medium leading-5 text-ink-soft transition-colors hover:border-ink/30 hover:text-ink disabled:opacity-40"
              >
                Select all
              </button>
              <button
                type="button"
                onClick={() => setSelected([])}
                disabled={selected.length === 0}
                className="whitespace-nowrap rounded-lg border border-ink/15 px-3 py-1.5 text-sm font-medium leading-5 text-ink-soft transition-colors hover:border-ink/30 hover:text-ink disabled:opacity-40"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="mt-5 grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
            {(config?.topics ?? []).map((t) => {
              const on = selected.includes(t.topic);
              return (
                <button
                  key={t.topic}
                  type="button"
                  onClick={() => toggle(t.topic)}
                  aria-pressed={on}
                  className={`flex items-center justify-between gap-3 rounded-xl border px-4 py-3 text-left transition-all ${
                    on
                      ? "border-gold/50 bg-accent/40 shadow-glow"
                      : "border-ink/10 bg-paper/60 hover:border-ink/25"
                  }`}
                >
                  <span
                    className={`truncate font-medium ${on ? "text-ink" : "text-ink-soft"}`}
                  >
                    {topicLabel(t.topic)}
                  </span>
                  {on && <Check size={16} className="shrink-0 text-gold" />}
                </button>
              );
            })}
          </div>

          {!config && !error && (
            <div className="flex items-center justify-center gap-2 py-10 text-sm text-ink-faint">
              <Loader2 size={16} className="animate-spin" />
              Loading available topics
            </div>
          )}

          <CoverageNote selectedCount={selected.length} />
        </section>

        <div className="mt-6 flex justify-end rounded-2xl border border-ink/10 bg-card px-6 py-4 shadow-card">
          <button
            type="button"
            onClick={start}
            disabled={selected.length === 0 || starting || !config}
            className="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-xl bg-primary px-6 py-3 font-semibold leading-6 text-primary-foreground transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {starting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Sparkles size={16} />
            )}
            {starting ? "Starting" : "Start test"}
          </button>
        </div>
      </main>
    </div>
  );
}

function CoverageNote({ selectedCount }: { selectedCount: number }) {
  if (selectedCount === 0) {
    return (
      <p className="mt-5 rounded-xl border border-ink/10 bg-paper/70 px-4 py-3 text-sm text-ink-soft">
        Select at least one topic.
      </p>
    );
  }
  return (
    <p className="mt-5 rounded-xl border border-ink/10 bg-paper/70 px-4 py-3 text-sm text-ink-soft">
      {selectedCount} topic{selectedCount > 1 ? "s" : ""} selected.
    </p>
  );
}
