"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Check,
  Loader2,
  Plus,
  Route,
  Sparkles,
  Users,
} from "lucide-react";
import client from "@/lib/api";
import type { CustomRoadmap, CustomRoadmapStep } from "@/lib/types";
import { cn } from "@/lib/utils";

const DIFFICULTY_TONE: Record<string, string> = {
  EASY: "text-quest",
  MEDIUM: "text-gold-deep",
  HARD: "text-rust",
};

/**
 * "Your plan" — the active custom roadmap, surfaced on the roadmap overview
 * so the learner is tracked against it every day instead of the builder
 * being buried once a plan exists.
 */
export default function PlanPanel({
  plans,
  onChanged,
}: {
  plans: CustomRoadmap[];
  onChanged?: () => void;
}) {
  const active = plans[0] ?? null;
  const [today, setToday] = useState<CustomRoadmapStep[] | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!active) {
      setToday([]);
      return;
    }
    let cancelled = false;
    setToday(null);
    client
      .get<CustomRoadmap>(`/roadmaps/custom/${active.id}/today`)
      .then((res) => {
        if (!cancelled) setToday(res.data.steps ?? []);
      })
      .catch(() => {
        if (!cancelled) setToday([]);
      });
    return () => {
      cancelled = true;
    };
  }, [active?.id]);

  const toggle = async (step: CustomRoadmapStep) => {
    if (!active || pending) return;
    setPending(step.id);
    setError(null);
    setToday((prev) =>
      prev?.map((s) => (s.id === step.id ? { ...s, done: !s.done } : s)) ?? prev
    );
    try {
      if (step.done) {
        await client.delete(`/roadmaps/custom/${active.id}/ticks/${step.id}`);
      } else {
        await client.post(`/roadmaps/custom/${active.id}/ticks/${step.id}`);
      }
      onChanged?.();
    } catch {
      setError("Couldn't save that tick. Try again.");
      client
        .get<CustomRoadmap>(`/roadmaps/custom/${active.id}/today`)
        .then((res) => setToday(res.data.steps ?? []))
        .catch(() => {});
    } finally {
      setPending(null);
    }
  };

  if (!active) return null;

  const pct = active.total > 0 ? Math.round((active.me_done / active.total) * 100) : 0;
  const todayDone = (today ?? []).filter((s) => s.done).length;
  const todayTotal = today?.length ?? 0;
  const remaining = Math.max(0, active.total - active.me_done);

  // If the current day slice is empty (e.g. you finished today, or the plan
  // started earlier), fall back to the next unfinished steps so tracking
  // never dead-ends.
  const showToday = today !== null && today.length > 0;
  const fallback = active.steps.filter((s) => !s.done).slice(0, 5);
  const list = showToday ? today! : fallback;
  const heading = today === null || showToday ? "Today's list" : "Next up";

  return (
    <section className="lux-shell">
      <div className="lux-core panel border-0 p-6">
        <div className="flex flex-wrap items-start gap-x-4 gap-y-2">
          <div className="min-w-0 flex-1">
            <p className="lux-eyebrow fluid-ease">
              <Route size={11} strokeWidth={1.5} />
              Your plan
            </p>
            <h2 className="mt-2 truncate font-display text-xl font-medium tracking-tight text-ink">
              {active.title}
            </h2>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 stat-num text-[11px] text-ink-faint">
              <span>
                {active.me_done}/{active.total} done · {remaining} left
              </span>
              {active.friend_done != null && (
                <span className="inline-flex items-center gap-1">
                  <Users size={11} strokeWidth={1.5} />
                  friend {active.friend_done}/{active.total}
                </span>
              )}
              <span className="inline-flex items-center gap-1">
                <Sparkles size={11} strokeWidth={1.5} />
                ~{active.mins_per_day} min/day
              </span>
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <Link
              href={`/roadmap/custom/${active.id}`}
              className="btn-island group fluid-ease bg-ink text-sm text-paper"
            >
              Open plan
              <span className="btn-island-icon">
                <ArrowRight size={14} strokeWidth={1.5} />
              </span>
            </Link>
          </div>
        </div>

        <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-ink/10">
          <div
            className="h-full rounded-full bg-quest transition-[width] duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>

        <div className="mt-5 flex items-baseline justify-between gap-3">
          <h3 className="font-display text-sm font-bold uppercase tracking-[0.1em] text-ink">
            {heading}
          </h3>
          {showToday ? (
            <span className="stat-num text-[11px] text-ink-faint">
              {todayDone}/{todayTotal} ticked
            </span>
          ) : (
            remaining > 0 && (
              <span className="stat-num text-[11px] text-ink-faint">
                {remaining} step{remaining === 1 ? "" : "s"} left in plan
              </span>
            )
          )}
        </div>

        {today === null ? (
          <p className="mt-3 flex items-center gap-2 py-4 text-sm text-ink-faint">
            <Loader2 size={15} strokeWidth={1.5} className="animate-spin" />
            Loading today&apos;s list…
          </p>
        ) : list.length === 0 ? (
          <p className="mt-3 rounded-xl border border-quest/30 bg-quest/8 px-4 py-3 text-sm text-ink">
            Every step is ticked. Build a fresh path when you&apos;re ready for
            the next level.
          </p>
        ) : (
          <ul className="mt-2 divide-y divide-ink/8">
            {list.map((s) => (
              <li key={s.id} className="flex items-center gap-3 py-2.5">
                <button
                  type="button"
                  aria-label={s.done ? "Mark not done" : "Mark done"}
                  aria-pressed={s.done}
                  onClick={() => toggle(s)}
                  disabled={pending === s.id}
                  className={cn(
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-[1.5px] transition-all active:scale-90 disabled:opacity-60",
                    s.done
                      ? "border-quest bg-quest/10 text-quest"
                      : "border-ink/20 text-transparent hover:border-quest"
                  )}
                >
                  {pending === s.id ? (
                    <Loader2 size={12} strokeWidth={2} className="animate-spin text-ink-faint" />
                  ) : (
                    <Check size={13} strokeWidth={3} />
                  )}
                </button>
                {s.problem_slug ? (
                  <Link
                    href={`/problems/${s.problem_slug}/solve`}
                    className={cn(
                      "min-w-0 flex-1 truncate text-sm hover:underline",
                      s.done ? "text-ink-faint line-through" : "text-ink"
                    )}
                  >
                    {s.title}
                  </Link>
                ) : (
                  <span
                    className={cn(
                      "min-w-0 flex-1 truncate text-sm",
                      s.done && "text-ink-faint line-through"
                    )}
                  >
                    {s.title}
                  </span>
                )}
                {s.difficulty && (
                  <span
                    className={cn(
                      "shrink-0 stat-num text-[10px] font-semibold uppercase",
                      DIFFICULTY_TONE[s.difficulty] ?? "text-ink-faint"
                    )}
                  >
                    {s.difficulty}
                  </span>
                )}
                <span className="shrink-0 stat-num text-[10px] text-ink-faint">
                  {s.est_mins}m
                </span>
              </li>
            ))}
          </ul>
        )}

        {error && <p className="mt-3 text-sm text-rust">{error}</p>}

        <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-ink/8 pt-4">
          <Link
            href="/roadmap/custom"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-soft hover:text-ink hover:underline"
          >
            <Plus size={14} strokeWidth={1.5} />
            Build another path
          </Link>
          <Link
            href="/roadmap/custom"
            className="text-sm text-ink-faint hover:text-ink hover:underline"
          >
            Browse your roadmaps
          </Link>
          {plans.length > 1 && (
            <span className="stat-num text-[11px] text-ink-faint">
              +{plans.length - 1} more
            </span>
          )}
        </div>
      </div>
    </section>
  );
}
