"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Flame,
  Loader2,
  Lock,
  Sparkles,
  Swords,
  Trophy,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { DifficultyChip, TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { Difficulty } from "@/lib/types";
import { cn } from "@/lib/utils";
import RoadmapGraph from "./roadmap-graph";

const COLORS = {
  easy: "#00BFA5",
  medium: "#F0A000",
  hard: "#FF3B3B",
};

interface RoadmapProblem {
  slug: string;
  title: string;
  difficulty: Difficulty;
  solved: boolean;
  attempts: number;
  hints_used: number;
  solvable: boolean;
  recommended: boolean;
  sources: string[];
}

interface Pattern {
  key: string;
  name: string;
  order: number;
  prerequisites: string[];
  snippet: string;
  solved: number;
  total: number;
  mastery: number;
  complete: boolean;
  problems: RoadmapProblem[];
}

interface RoadmapData {
  patterns: Pattern[];
  totals: { solved: number; total: number };
}

interface ActivityDay {
  date: string;
  count: number;
}

function localIso(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function computeStreaks(activity: ActivityDay[] | null) {
  const set = new Set(
    (activity || []).filter((d) => d.count > 0).map((d) => d.date)
  );
  const off = (iso: string, n: number) => {
    const d = new Date(iso + "T00:00:00");
    d.setDate(d.getDate() + n);
    return localIso(d);
  };
  const today = localIso(new Date());
  const anchor = set.has(today) ? today : set.has(off(today, -1)) ? off(today, -1) : null;
  let current = 0;
  if (anchor) {
    let d = anchor;
    while (set.has(d)) {
      current += 1;
      d = off(d, -1);
    }
  }
  const dates = [...set].sort();
  let best = 0;
  let run = 0;
  let prev: string | null = null;
  for (const d of dates) {
    if (prev && off(prev, 1) === d) run += 1;
    else run = 1;
    if (run > best) best = run;
    prev = d;
  }
  return { current, best };
}

function useCountdownToMidnight(): string {
  const [left, setLeft] = useState("--:--:--");
  useEffect(() => {
    const tick = () => {
      const now = new Date();
      const end = new Date(now);
      end.setHours(24, 0, 0, 0);
      const s = Math.max(0, Math.floor((end.getTime() - now.getTime()) / 1000));
      const h = String(Math.floor(s / 3600)).padStart(2, "0");
      const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
      const sec = String(s % 60).padStart(2, "0");
      setLeft(`${h}:${m}:${sec}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return left;
}

function MonthCalendar({ activity }: { activity: ActivityDay[] | null }) {
  const now = new Date();
  const [cursor, setCursor] = useState({ y: now.getFullYear(), m: now.getMonth() });
  const byDate = useMemo(() => {
    const map = new Map<string, number>();
    (activity || []).forEach((d) => map.set(d.date, d.count));
    return map;
  }, [activity]);

  const first = new Date(cursor.y, cursor.m, 1);
  const startDay = first.getDay();
  const daysInMonth = new Date(cursor.y, cursor.m + 1, 0).getDate();
  const todayIso = localIso(new Date());
  const monthLabel = first.toLocaleString(undefined, { month: "long", year: "numeric" });
  const monthCount = useMemo(() => {
    let n = 0;
    byDate.forEach((c, date) => {
      if (date.startsWith(`${cursor.y}-${String(cursor.m + 1).padStart(2, "0")}`)) n += c;
    });
    return n;
  }, [byDate, cursor]);

  const cells: (string | null)[] = [
    ...Array<null>(startDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => {
      return localIso(new Date(cursor.y, cursor.m, i + 1));
    }),
  ];

  const level = (count: number | undefined) => {
    if (!count) return "bg-ink/[0.06]";
    if (count === 1) return "bg-quest/25";
    if (count <= 3) return "bg-quest/55";
    return "bg-quest text-white";
  };

  return (
    <div className="panel p-5">
      <div className="flex items-center gap-2">
        <CalendarDays size={15} className="text-ink-faint" />
        <h3 className="font-display text-sm font-bold uppercase tracking-[0.1em] text-ink">
          {monthLabel}
        </h3>
        <span className="ml-auto flex items-center gap-1">
          <button
            type="button"
            aria-label="Previous month"
            onClick={() =>
              setCursor((c) =>
                c.m === 0 ? { y: c.y - 1, m: 11 } : { y: c.y, m: c.m - 1 }
              )
            }
            className="rounded-md p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            type="button"
            aria-label="Next month"
            onClick={() =>
              setCursor((c) =>
                c.m === 11 ? { y: c.y + 1, m: 0 } : { y: c.y, m: c.m + 1 }
              )
            }
            className="rounded-md p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
          >
            <ChevronRight size={14} />
          </button>
        </span>
      </div>
      <p className="mt-1 font-mono text-[11px] text-ink-faint">
        {monthCount} solve{monthCount === 1 ? "" : "s"} this month
      </p>
      <div className="mt-3 grid grid-cols-7 gap-1 text-center font-mono text-[10px] font-semibold uppercase text-ink-faint">
        {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => (
          <span key={i} className="py-1">
            {d}
          </span>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((iso, i) => {
          if (!iso) return <span key={`b${i}`} />;
          const count = byDate.get(iso) ?? 0;
          const isToday = iso === todayIso;
          const day = Number(iso.slice(8));
          return (
            <span
              key={iso}
              title={`${iso}: ${count} solve${count === 1 ? "" : "s"}`}
              className={cn(
                "flex aspect-square items-center justify-center rounded-md font-mono text-[11px]",
                level(count),
                count ? "text-ink" : "text-ink-faint",
                isToday && "ring-2 ring-gold ring-offset-1 ring-offset-transparent"
              )}
            >
              {day}
            </span>
          );
        })}
      </div>
    </div>
  );
}

export default function RoadmapClient() {
  const { user } = useAuth();
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [activity, setActivity] = useState<ActivityDay[] | null>(null);
  const [daily, setDaily] = useState<{ slug: string; title: string } | null>(null);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [view, setView] = useState<"graph" | "list">("graph");
  const [loading, setLoading] = useState(true);
  const countdown = useCountdownToMidnight();

  useEffect(() => {
    let cancelled = false;
    client
      .get<RoadmapData>("/roadmap")
      .then((res) => {
        if (!cancelled) setRoadmap(res.data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    client
      .get<{ days: ActivityDay[] }>("/roadmap/activity", { params: { days: 365 } })
      .then((res) => {
        if (!cancelled) setActivity(res.data?.days || []);
      })
      .catch(() => {});
    client
      .get<{ problem: { slug: string; title: string } | null }>("/roadmap/daily")
      .then((res) => {
        if (!cancelled && res.data?.problem) setDaily(res.data.problem);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const unlocked = useMemo(() => {
    const open = new Set<string>();
    if (!roadmap) return open;
    let changed = true;
    while (changed) {
      changed = false;
      for (const p of roadmap.patterns) {
        if (open.has(p.key)) continue;
        const prereqs = (p.prerequisites || []).filter((k) =>
          roadmap.patterns.some((x) => x.key === k)
        );
        if (
          prereqs.every(
            (k) => open.has(k) || roadmap.patterns.find((x) => x.key === k)?.complete
          )
        ) {
          open.add(p.key);
          changed = true;
        }
      }
    }
    return open;
  }, [roadmap]);

  // Only runnable problems are listed — catalog shells stay out of sight.
  const patterns = useMemo(() => {
    if (!roadmap) return [];
    return [...roadmap.patterns]
      .map((p) => ({ ...p, problems: p.problems.filter((pr) => pr.solvable) }))
      .filter((p) => p.problems.length > 0)
      .sort((a, b) => a.order - b.order || a.name.localeCompare(b.name));
  }, [roadmap]);

  const scoped = useMemo(() => {
    let solved = 0;
    let total = 0;
    const diff: Record<string, { solved: number; total: number }> = {
      EASY: { solved: 0, total: 0 },
      MEDIUM: { solved: 0, total: 0 },
      HARD: { solved: 0, total: 0 },
    };
    patterns.forEach((p) => {
      p.problems.forEach((pr) => {
        total += 1;
        if (pr.solved) solved += 1;
        const bucket = diff[pr.difficulty];
        if (bucket) {
          bucket.total += 1;
          if (pr.solved) bucket.solved += 1;
        }
      });
    });
    return { solved, total, diff };
  }, [patterns]);

  const overallPct =
    scoped.total > 0 ? Math.round((scoped.solved / scoped.total) * 100) : 0;

  const { current, best } = useMemo(() => computeStreaks(activity), [activity]);

  return (
    <ProtectedRoute>
      <div className="atlas-bg min-h-screen">
        <TopBar active="roadmap">
          {user && <UserChip username={user.username} />}
        </TopBar>

        <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-10">
          {/* Header */}
          <div className="flex flex-wrap items-end gap-6">
            <div>
              <p className="eyebrow">Study plan</p>
              <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
                The DSA path
              </h1>
            </div>
            <div className="ml-auto flex items-center gap-6">
              {(
                [
                  { label: "Easy", ...scoped.diff.EASY, color: COLORS.easy },
                  { label: "Medium", ...scoped.diff.MEDIUM, color: COLORS.medium },
                  { label: "Hard", ...scoped.diff.HARD, color: COLORS.hard },
                ] as const
              ).map((r) => (
                <span key={r.label} className="flex items-center gap-2 text-sm">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: r.color }}
                  />
                  <span className="font-medium text-ink-soft">{r.label}</span>
                  <span className="font-mono font-semibold text-ink">
                    {r.solved}/{r.total}
                  </span>
                </span>
              ))}
              <span className="flex items-center gap-2 rounded-full border border-quest/40 bg-quest/10 px-3 py-1 font-mono text-sm font-bold text-quest">
                <Check size={14} strokeWidth={3} />
                {scoped.solved}/{scoped.total}
              </span>
            </div>
          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-ink/10">
            <div
              className="h-full rounded-full bg-quest transition-[width] duration-500"
              style={{ width: `${overallPct}%` }}
            />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-[1fr_340px]">
            <div>
              <div className="mb-3 flex w-fit gap-1 rounded-xl border border-ink/10 bg-card p-1 shadow-card">
                {(["graph", "list"] as const).map((v) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setView(v)}
                    className={cn(
                      "rounded-lg px-4 py-1.5 text-sm font-semibold capitalize transition-colors",
                      view === v
                        ? "bg-ink text-white"
                        : "text-ink-soft hover:text-ink"
                    )}
                  >
                    {v}
                  </button>
                ))}
              </div>
              {view === "graph" ? (
                <RoadmapGraph patterns={roadmap?.patterns ?? []} unlocked={unlocked} />
              ) : (
              <section className="panel overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center gap-2 py-16 text-sm text-ink-faint">
                  <Loader2 size={16} className="animate-spin" />
                  Charting your path…
                </div>
              ) : patterns.length === 0 ? (
                <p className="px-6 py-12 text-center text-sm text-ink-soft">
                  No patterns in this course yet.
                </p>
              ) : (
                <ul className="divide-y divide-ink/8">
                  {patterns.map((p) => {
                    const locked = !unlocked.has(p.key);
                    const open = openKey === p.key;
                    const inCourse = p.problems;
                    const solved = inCourse.filter((pr) => pr.solved).length;
                    const complete = inCourse.length > 0 && solved === inCourse.length;
                    const pct =
                      inCourse.length > 0
                        ? Math.round((solved / inCourse.length) * 100)
                        : 0;
                    return (
                      <li key={p.key}>
                        <button
                          type="button"
                          disabled={locked}
                          onClick={() => setOpenKey(open ? null : p.key)}
                          className="flex w-full items-center gap-3 px-5 py-3.5 text-left transition-colors hover:bg-ink/[0.03] disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-ink/10 bg-paper-deep text-ink-faint">
                            {complete ? (
                              <Check size={15} strokeWidth={3} className="text-quest" />
                            ) : locked ? (
                              <Lock size={14} />
                            ) : (
                              <BookOpen size={14} />
                            )}
                          </span>
                          <span className="min-w-0 flex-1">
                            <span className="block truncate font-display text-[15px] font-semibold text-ink">
                              {p.name}
                            </span>
                            <span className="mt-1 block h-1 overflow-hidden rounded-full bg-ink/10">
                              <span
                                className={cn(
                                  "block h-full rounded-full",
                                  complete ? "bg-quest" : "bg-gold"
                                )}
                                style={{ width: `${pct}%` }}
                              />
                            </span>
                          </span>
                          <span className="shrink-0 font-mono text-xs text-ink-faint">
                            {solved}/{inCourse.length}
                          </span>
                          <ChevronDown
                            size={15}
                            className={cn(
                              "shrink-0 text-ink-faint transition-transform",
                              open && "rotate-180"
                            )}
                          />
                        </button>
                        {open && !locked && (
                          <ul className="border-t border-ink/8 bg-paper px-5 py-2">
                            {inCourse.map((pr) => (
                              <li key={pr.slug}>
                                  <Link
                                    href={`/problems/${pr.slug}/solve`}
                                    className="group flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-ink/[0.04]"
                                  >
                                    <span
                                      className={cn(
                                        "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-[1.5px]",
                                        pr.solved
                                          ? "border-quest bg-quest/10 text-quest"
                                          : "border-ink/20 text-transparent"
                                      )}
                                    >
                                      <Check size={11} strokeWidth={4} />
                                    </span>
                                    <span
                                      className={cn(
                                        "flex-1 truncate text-sm",
                                        pr.solved
                                          ? "text-ink-faint line-through"
                                          : "text-ink group-hover:underline"
                                      )}
                                    >
                                      {pr.title}
                                    </span>
                                    {pr.recommended && (
                                      <span className="flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 font-mono text-[10px] font-semibold text-gold-deep">
                                        <Sparkles size={10} />
                                        Next
                                      </span>
                                    )}
                                    <DifficultyChip difficulty={pr.difficulty} />
                                  </Link>
                              </li>
                            ))}
                          </ul>
                        )}
                      </li>
                    );
                  })}
                </ul>
              )}
              </section>
              )}
            </div>

            {/* Right rail */}
            <aside className="space-y-5">
              {daily && (
                <div className="panel p-5">
                  <p className="eyebrow">Today&apos;s pick</p>
                  <Link
                    href={`/problems/${daily.slug}/solve`}
                    className="mt-1 block font-display text-lg font-bold leading-snug text-ink hover:underline"
                  >
                    {daily.title}
                  </Link>
                  <p className="mt-2 flex items-center gap-1.5 font-mono text-[11px] text-ink-faint">
                    <Swords size={12} />
                    Resets in {countdown}
                  </p>
                </div>
              )}

              <MonthCalendar activity={activity} />

              <div className="panel p-5">
                <div className="flex gap-3">
                  <div className="flex flex-1 flex-col items-center gap-1 rounded-xl border border-ink/10 bg-paper px-3 py-4">
                    <span className="text-xs font-medium text-ink-faint">
                      Current streak
                    </span>
                    <span className="flex items-center gap-1.5 font-display text-xl font-bold text-ink">
                      <Flame size={18} className="text-rust" />
                      {current}d
                    </span>
                  </div>
                  <div className="flex flex-1 flex-col items-center gap-1 rounded-xl border border-ink/10 bg-paper px-3 py-4">
                    <span className="text-xs font-medium text-ink-faint">
                      Best streak
                    </span>
                    <span className="flex items-center gap-1.5 font-display text-xl font-bold text-ink">
                      <Trophy size={18} className="text-gold-deep" />
                      {best}d
                    </span>
                  </div>
                </div>
                <p className="mt-3 text-center text-xs text-ink-faint">
                  Solve one problem a day to keep your streak
                </p>
              </div>
            </aside>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
