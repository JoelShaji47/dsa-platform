"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
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
  Route,
  Sparkles,
  Swords,
  Trophy,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { DifficultyChip, TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import { logImpressions } from "@/lib/telemetry";
import type { Difficulty } from "@/lib/types";
import { cn } from "@/lib/utils";
import RoadmapGraph from "./roadmap-graph";

const COLORS = {
  easy: "#6E9E8B",
  medium: "#C49A5F",
  hard: "#C97B63",
};

// ── Skill: scroll interpolation via IntersectionObserver (GPU: opacity+transform only) ──
function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      el.classList.add("is-visible");
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div
      ref={ref}
      className={cn("reveal", className)}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  );
}

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
  solvable_total?: number;
  mastery: number;
  /** Layer 1 student model: predicted solve rate + evidence behind it. */
  skill?: {
    theta: number;
    n: number;
    solve_rate: number;
    confidence: number;
  };
  complete: boolean;
  problems: RoadmapProblem[];
}

interface RoadmapData {
  patterns: Pattern[];
  pathway?: Pathway;
  totals: { solved: number; total: number };
  opportunity_id?: string | null;
}

interface PathwayStep {
  order: number;
  pattern_key: string;
  pattern_name: string;
  problems: number;
  predicted_solve_rate: number;
  expected_solves: number;
  expected_hours: number;
  value_per_hour: number;
  confidence: number;
  unlocks: string[];
}

interface Pathway {
  objective: string;
  steps: PathwayStep[];
  total_hours: number;
  hour_basis: string;
  remaining_patterns: string[];
}

interface SolvedRef {
  slug: string;
  title: string;
  difficulty: string;
}

interface ActivityDay {
  date: string;
  count: number;
  problems?: SolvedRef[];
}

interface DailyPick {
  slug: string;
  title: string;
  opportunity_id?: string;
  fromTitle?: string;
  fromHref?: string;
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

const GOAL_OPTIONS = [
  { key: "fundamentals", label: "Strong fundamentals" },
  { key: "interview_soon", label: "Interview soon" },
  { key: "company", label: "Target a company" },
  { key: "curious", label: "Just exploring" },
];

const LEVEL_OPTIONS = [
  { key: "never_started", label: "Never started" },
  { key: "basics", label: "Know the basics" },
  { key: "50_plus", label: "Solved 50+" },
  { key: "interview_ready", label: "Interview-ready" },
];

const DAY_PRESETS = [7, 14, 21, 30];
const MIN_PRESETS = [15, 30, 45, 60];

function PickRow<T extends string | number>({
  label,
  options,
  value,
  onChange,
  format,
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (v: T) => void;
  format?: (v: T) => string;
}) {
  return (
    <div>
      <p className="text-xs font-medium text-ink-faint">{label}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {options.map((o) => (
          <button
            key={String(o)}
            type="button"
            onClick={() => onChange(o)}
            className={cn(
              "fluid-ease rounded-full border px-4 py-1.5 text-sm transition-all duration-300 ease-out active:scale-[0.98]",
              value === o
                ? "border-quest/50 bg-quest/10 font-medium text-ink"
                : "border-ink/10 bg-card font-normal text-ink-soft hover:border-ink/20 hover:text-ink"
            )}
          >
            {format ? format(o) : String(o)}
          </button>
        ))}
      </div>
    </div>
  );
}

function PathGenerator() {
  const router = useRouter();
  const [goal, setGoal] = useState("fundamentals");
  const [level, setLevel] = useState("basics");
  const [company, setCompany] = useState("");
  const [days, setDays] = useState(21);
  const [mins, setMins] = useState(30);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await client.post("/roadmaps/custom", {
        level,
        goal,
        company: goal === "company" && company.trim() ? company.trim() : undefined,
        mins_per_day: mins,
        total_days: days,
      });
      router.push(`/roadmap/custom/${res.data.id}`);
    } catch (e) {
      const detail =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || "Couldn't generate your path. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="lux-shell">
      <div className="lux-core panel border-0 p-6 md:p-8">
        <p className="lux-eyebrow fluid-ease">
          <Route size={11} strokeWidth={1.5} />
          Start here
        </p>
        <h2 className="mt-3 font-display text-2xl font-medium tracking-tight text-ink md:text-[28px]">
          Let&apos;s build your study path
        </h2>
        <p className="mt-2 max-w-lg text-[15px] leading-relaxed text-ink-soft">
          Tell us where you stand and where you&apos;re headed. We&apos;ll map
          a day-by-day plan from the problem library — your daily pick and
          calendar grow from it.
        </p>

        <div className="mt-6 space-y-5">
          <PickRow
            label="Your goal"
            options={GOAL_OPTIONS.map((g) => g.key)}
            value={goal}
            onChange={setGoal}
            format={(k) => GOAL_OPTIONS.find((g) => g.key === k)?.label ?? k}
          />
          {goal === "company" && (
            <div>
              <p className="text-xs font-medium text-ink-faint">Company</p>
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g. Google, Stripe, a startup"
                maxLength={100}
                className="field mt-2 max-w-sm"
              />
            </div>
          )}
          <PickRow
            label="Your level"
            options={LEVEL_OPTIONS.map((l) => l.key)}
            value={level}
            onChange={setLevel}
            format={(k) => LEVEL_OPTIONS.find((l) => l.key === k)?.label ?? k}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <PickRow
              label="Plan length"
              options={DAY_PRESETS}
              value={days}
              onChange={setDays}
              format={(d) => `${d} days`}
            />
            <PickRow
              label="Minutes per day"
              options={MIN_PRESETS}
              value={mins}
              onChange={setMins}
              format={(m) => `${m} min`}
            />
          </div>
        </div>

        {error && <p className="mt-5 text-sm text-rust">{error}</p>}

        <div className="mt-7 flex flex-wrap items-center gap-4">
          <button
            type="button"
            onClick={submit}
            disabled={busy}
            className="btn-island group fluid-ease bg-quest text-sm text-white disabled:opacity-60"
          >
            {busy ? "Building your path…" : "Generate my path"}
            <span className="btn-island-icon">
              {busy ? (
                <Loader2 size={14} strokeWidth={1.5} className="animate-spin" />
              ) : (
                <ChevronRight size={14} strokeWidth={1.5} />
              )}
            </span>
          </button>
          <Link href="/problems" className="text-sm text-ink-soft hover:text-ink hover:underline">
            or browse all problems
          </Link>
        </div>
      </div>
    </div>
  );
}

function MonthCalendar({ activity }: { activity: ActivityDay[] | null }) {
  const now = new Date();
  const [cursor, setCursor] = useState({ y: now.getFullYear(), m: now.getMonth() });
  const byDay = useMemo(() => {
    const map = new Map<string, ActivityDay>();
    (activity || []).forEach((d) => map.set(d.date, d));
    return map;
  }, [activity]);
  const byDate = useMemo(() => {
    const map = new Map<string, number>();
    byDay.forEach((d, date) => map.set(date, d.count));
    return map;
  }, [byDay]);

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
    <div className="lux-shell">
    <div className="lux-core panel border-0 p-5">
      <div className="flex items-center gap-2">
        <CalendarDays size={15} strokeWidth={1.5} className="text-ink-faint" />
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
            <ChevronLeft size={14} strokeWidth={1.5} />
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
            <ChevronRight size={14} strokeWidth={1.5} />
          </button>
        </span>
      </div>
      <p className="mt-1 stat-num text-[11px] text-ink-faint">
        {monthCount} solve{monthCount === 1 ? "" : "s"} this month
      </p>
      <div className="mt-3 grid grid-cols-7 gap-1 text-center stat-num text-[10px] font-semibold uppercase text-ink-faint">
        {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => (
          <span key={i} className="py-1">
            {d}
          </span>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((iso, i) => {
          if (!iso) return <span key={`b${i}`} />;
          const info = byDay.get(iso);
          const count = info?.count ?? 0;
          const problems = info?.problems ?? [];
          const isToday = iso === todayIso;
          const day = Number(iso.slice(8));
          const shown = problems.slice(0, 4);
          const extra = problems.length - shown.length;
          return (
            <span
              key={iso}
              tabIndex={count > 0 ? 0 : undefined}
              className={cn(
                "group relative flex aspect-square items-center justify-center rounded-md stat-num text-[11px] outline-none",
                level(count),
                count ? "text-ink" : "text-ink-faint",
                isToday && "ring-2 ring-gold ring-offset-1 ring-offset-transparent",
                count > 0 && "focus-visible:ring-2 focus-visible:ring-quest"
              )}
            >
              {day}
              {count > 0 && (
                <span className="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 hidden w-60 -translate-x-1/2 group-hover:block group-focus-within:block">
                  <span className="block overflow-hidden rounded-xl border border-ink/10 bg-card p-3 text-left shadow-lift">
                    <span className="stat-num block text-[11px] font-medium text-ink-soft">
                      {count} solved · {iso}
                    </span>
                    <span className="mt-1.5 block space-y-1">
                      {shown.map((p) => (
                        <span key={p.slug} className="flex items-center gap-1.5">
                          <span
                            className="h-1.5 w-1.5 shrink-0 rounded-full"
                            style={{
                              backgroundColor:
                                COLORS[p.difficulty.toLowerCase() as keyof typeof COLORS] ?? "#9aa3ad",
                            }}
                          />
                          <span className="truncate text-[12px] text-ink">
                            {p.title}
                          </span>
                        </span>
                      ))}
                      {extra > 0 && (
                        <span className="block text-[11px] text-ink-faint">
                          +{extra} more
                        </span>
                      )}
                    </span>
                  </span>
                </span>
              )}
            </span>
          );
        })}
      </div>
    </div>
    </div>
  );
}

export default function RoadmapClient() {
  const { user } = useAuth();
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [activity, setActivity] = useState<ActivityDay[] | null>(null);
  const [daily, setDaily] = useState<DailyPick | null>(null);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [view, setView] = useState<"graph" | "list">("graph");
  const [loading, setLoading] = useState(true);
  const countdown = useCountdownToMidnight();

  useEffect(() => {
    let cancelled = false;
    client
      .get<RoadmapData>("/roadmap")
      .then((res) => {
        if (!cancelled) {
          setRoadmap(res.data);
          // Impression ping for the highlighted "Recommended next" node.
          // Duplicates are idempotent server-side (recorded: 0 on retry).
          const opp = res.data?.opportunity_id;
          const flagged = res.data?.patterns
            ?.flatMap((p) => p.problems ?? [])
            .find((pr) => pr.recommended);
          if (opp && flagged) {
            logImpressions(opp, [
              { slug: flagged.slug, rank: 0, source: "roadmap", rendered: true },
            ]);
          }
        }
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
      .get<{ problem: { slug: string; title: string; opportunity_id?: string } | null }>("/roadmap/daily")
      .then((res) => {
        if (cancelled) return;
        if (res.data?.problem) {
          setDaily(res.data.problem);
          // Impression ping: the daily card was rendered (fire-and-forget).
          const p = res.data.problem;
          if (p.opportunity_id) {
            logImpressions(p.opportunity_id, [
              { slug: p.slug, rank: 0, source: "daily", rendered: true },
            ]);
          }
          return;
        }
        // No catalog daily (e.g. fresh account, empty library): fall back to
        // the newest generated path's slice for today, so the card still
        // teaches from the student's own plan.
        client
          .get<{ id: string; title: string }[]>("/roadmaps/custom")
          .then((list) => {
            const newest = Array.isArray(list.data) ? list.data[0] : null;
            if (cancelled || !newest) return;
            client
              .get<{ steps: { problem_slug: string | null; title: string; done: boolean }[] }>(
                `/roadmaps/custom/${newest.id}/today`
              )
              .then((t) => {
                if (cancelled) return;
                const steps = t.data?.steps || [];
                const step =
                  steps.find((s) => s.problem_slug && !s.done) ||
                  steps.find((s) => s.problem_slug);
                if (step?.problem_slug) {
                  setDaily({
                    slug: step.problem_slug,
                    title: step.title,
                    fromTitle: newest.title,
                    fromHref: `/roadmap/custom/${newest.id}`,
                  });
                }
              })
              .catch(() => {});
          })
          .catch(() => {});
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
      <div className="atlas-bg min-h-[100dvh]">
        <TopBar active="roadmap">
          {user && <UserChip username={user.username} />}
        </TopBar>

        {/* Fixed film-grain: pointer-events-none, never on scroll content */}
        <div aria-hidden className="lux-grain" />

        <main className="mx-auto w-full max-w-6xl px-4 pb-20 pt-10 md:px-6 md:pt-14">
          {/* Slim status header: progress at a glance, no hero noise. */}
          <Reveal>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
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
                  <span className="stat-num font-semibold text-ink">
                    {r.solved}/{r.total}
                  </span>
                </span>
              ))}
              <span className="fluid-ease ml-auto flex items-center gap-2 rounded-full border border-quest/40 bg-quest/10 px-3 py-1 stat-num text-sm font-semibold text-quest">
                <Check size={14} strokeWidth={1.5} />
                {scoped.solved}/{scoped.total}
              </span>
            </div>
          </Reveal>

          {/* Quiet meter: transform scaleX instead of width */}
          <Reveal delay={100}>
            <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-ink/10">
              <div
                className="lux-meter-fill h-full w-full rounded-full bg-quest"
                style={{ transform: `scaleX(${overallPct / 100})` }}
              />
            </div>
          </Reveal>

          {/* Main column: path views, or the path builder when there's no path. */}
          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-12">
            <Reveal delay={150} className="lg:col-span-8">
              {loading ? (
                <div className="lux-shell">
                  <div className="lux-core panel flex items-center justify-center gap-2 border-0 py-20 text-sm text-ink-faint">
                    <Loader2 size={16} strokeWidth={1.5} className="animate-spin" />
                    Charting your path…
                  </div>
                </div>
              ) : patterns.length === 0 ? (
                <PathGenerator />
              ) : (
              <>
              <div className="fluid-ease mb-4 flex w-fit items-center gap-1 rounded-full border border-ink/10 bg-card p-1 shadow-card">
                {(["graph", "list"] as const).map((v) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setView(v)}
                    className={cn(
                      "fluid-ease rounded-full px-5 py-2 text-sm font-medium capitalize transition-all duration-300 active:scale-[0.99]",
                      view === v
                        ? "bg-ink text-paper"
                        : "text-ink-soft hover:text-ink"
                    )}
                  >
                    {v}
                  </button>
                ))}
              </div>
              {view === "graph" ? (
                <div className="lux-shell">
                  <div className="lux-core relative">
                    <RoadmapGraph patterns={roadmap?.patterns ?? []} unlocked={unlocked} />
                  </div>
                </div>
              ) : (
              <div className="lux-shell">
              <section className="lux-core panel overflow-hidden border-0">
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
                          className="fluid-ease flex w-full items-center gap-3 px-5 py-3.5 text-left transition-all duration-300 ease-out hover:bg-ink/[0.03] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-ink/10 bg-paper-deep text-ink-faint">
                            {complete ? (
                              <Check size={15} strokeWidth={1.5} className="text-quest" />
                            ) : locked ? (
                              <Lock size={14} strokeWidth={1.5} />
                            ) : (
                              <BookOpen size={14} strokeWidth={1.5} />
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
                          <span className="shrink-0 stat-num text-xs text-ink-faint">
                            {solved}/{inCourse.length}
                          </span>
                            <ChevronDown
                              size={15}
                              strokeWidth={1.5}
                              className={cn(
                                "fluid-ease shrink-0 text-ink-faint transition-all duration-300 ease-out",
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
                                    className="group fluid-ease flex items-center gap-3 rounded-lg px-3 py-2 transition-all duration-300 ease-out hover:bg-ink/[0.04] active:scale-[0.99]"
                                  >
                                    <span
                                      className={cn(
                                        "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-[1.5px]",
                                        pr.solved
                                          ? "border-quest bg-quest/10 text-quest"
                                          : "border-ink/20 text-transparent"
                                      )}
                                    >
                                      <Check size={11} strokeWidth={1.5} />
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
                                      <span className="flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 stat-num text-[10px] font-semibold text-gold-deep">
                                        <Sparkles size={10} strokeWidth={1.5} />
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
              </section>
              </div>
              )}
              </>
              )}
            </Reveal>

            {/* Right rail — stacked double-bezel instruments */}
            <aside className="space-y-6 lg:col-span-4">
              {daily && (
                <Reveal delay={200}>
                <div className="lux-shell">
                <div className="lux-core panel border-0 p-5">
                  <p className="lux-eyebrow fluid-ease">Today&apos;s pick</p>
                  <Link
                    href={`/problems/${daily.slug}/solve`}
                    className="mt-3 block font-display text-xl font-medium leading-snug text-ink hover:underline"
                  >
                    {daily.title}
                  </Link>
                  {daily.fromTitle ? (
                    <p className="mt-2 text-[12px] text-ink-faint">
                      Due today from{" "}
                      <Link href={daily.fromHref || "/roadmap/custom"} className="text-ink-soft underline decoration-ink/20 underline-offset-2 hover:text-ink">
                        {daily.fromTitle}
                      </Link>
                    </p>
                  ) : (
                    <p className="mt-2 flex items-center gap-1.5 stat-num text-[11px] text-ink-faint">
                      <Swords size={12} strokeWidth={1.5} />
                      Resets in {countdown}
                    </p>
                  )}
                  <Link
                    href={`/problems/${daily.slug}/solve`}
                    className="btn-island group fluid-ease mt-4 bg-ink text-sm text-paper"
                  >
                    Open challenge
                    <span className="btn-island-icon">
                      <ChevronRight size={14} strokeWidth={1.5} />
                    </span>
                  </Link>
                </div>
                </div>
                </Reveal>
              )}

              <MonthCalendar activity={activity} />

              {roadmap?.pathway && roadmap.pathway.steps.length > 0 && (
                <Reveal delay={220}>
                  <div className="lux-shell">
                    <div className="lux-core panel border-0 p-5">
                      <p className="lux-eyebrow fluid-ease">Your pathway</p>
                      <p className="mt-2 text-[12px] text-ink-faint">
                        Ordered by learning signal per hour, prerequisites first.
                      </p>
                      <ol className="mt-3 space-y-2">
                        {roadmap.pathway.steps.slice(0, 4).map((step) => (
                          <li key={step.pattern_key} className="flex items-baseline gap-2">
                            <span className="stat-num w-4 shrink-0 text-[11px] text-ink-faint">
                              {step.order}
                            </span>
                            <span className="flex-1 truncate text-[13px] text-ink">
                              {step.pattern_name}
                            </span>
                            <span className="stat-num shrink-0 text-[11px] text-ink-faint">
                              {step.problems} left · ~{Math.max(1, Math.round(step.expected_hours))}h
                            </span>
                          </li>
                        ))}
                      </ol>
                      {roadmap.pathway.steps.length > 4 && (
                        <p className="mt-3 stat-num text-[11px] text-ink-faint">
                          +{roadmap.pathway.steps.length - 4} more ·{" "}
                          {Math.round(roadmap.pathway.total_hours)}h to the end of the plan
                        </p>
                      )}
                    </div>
                  </div>
                </Reveal>
              )}

              <Reveal delay={250}>
              <div className="lux-shell">
              <div className="lux-core panel border-0 p-5">
                <div className="flex gap-3">
                  <div className="flex flex-1 flex-col items-center gap-1 rounded-xl border border-ink/10 bg-paper px-3 py-4">
                    <span className="text-xs font-medium text-ink-faint">
                      Current streak
                    </span>
                    <span className="flex items-center gap-1.5 font-display text-xl font-medium text-ink">
                      <Flame size={18} strokeWidth={1.5} className="text-rust" />
                      {current}d
                    </span>
                  </div>
                  <div className="flex flex-1 flex-col items-center gap-1 rounded-xl border border-ink/10 bg-paper px-3 py-4">
                    <span className="text-xs font-medium text-ink-faint">
                      Best streak
                    </span>
                    <span className="flex items-center gap-1.5 font-display text-xl font-medium text-ink">
                      <Trophy size={18} strokeWidth={1.5} className="text-gold-deep" />
                      {best}d
                    </span>
                  </div>
                </div>
                <p className="mt-3 text-center text-xs text-ink-faint">
                  Solve one problem a day to keep your streak
                </p>
              </div>
              </div>
              </Reveal>
            </aside>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
