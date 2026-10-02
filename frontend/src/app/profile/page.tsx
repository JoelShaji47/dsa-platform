"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Award,
  CalendarDays,
  CheckCircle2,
  Loader2,
  Lock,
  Swords,
  XCircle,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { DifficultyChip, TopBar, UserChip } from "@/components/shell";
import { Coin } from "@/components/coin";
import { formatClock, topicLabel } from "@/components/arena/status-styles";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import { cn } from "@/lib/utils";

type Tab = "submissions" | "tests" | "badges";

type Difficulty = "EASY" | "MEDIUM" | "HARD";

type ActivityDay = { date: string; count: number };

type ProfileOut = {
  user: {
    username: string;
    xp: number;
    current_streak: number;
    league_tier: number;
    league_name: string;
    created_at: string;
  };
  solved: { easy: number; medium: number; hard: number; total: number };
  total_tests: number;
  activity: ActivityDay[];
  submissions: {
    id: string;
    problem_title: string;
    problem_slug: string;
    difficulty: Difficulty;
    status: string;
    language: string;
    runtime_ms: number | null;
    submitted_at: string;
  }[];
  tests: {
    id: string;
    status: string;
    score: number;
    passed_count: number;
    total: number;
    violations: number;
    assigned_topics: string[];
    started_at: string;
    ended_at: string | null;
    time_taken_seconds: number;
  }[];
  badges: {
    criteria: string;
    name: string;
    description: string;
    earned: boolean;
    earned_at: string | null;
  }[];
};

const DIFF_COLORS: Record<Difficulty, string> = {
  EASY: "bg-quest",
  MEDIUM: "bg-gold",
  HARD: "bg-rust",
};

const TABS: { key: Tab; label: string }[] = [
  { key: "submissions", label: "Recent submissions" },
  { key: "tests", label: "Mock tests" },
  { key: "badges", label: "Badges" },
];

function levelClass(count: number) {
  if (!count) return "bg-ink/[0.06]";
  if (count === 1) return "bg-quest/25";
  if (count <= 3) return "bg-quest/55";
  return "bg-quest";
}

function formatWhen(iso: string) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function StatCard({
  eyebrow,
  value,
  unit,
  accent,
}: {
  eyebrow: string;
  value: React.ReactNode;
  unit?: string;
  accent: string;
}) {
  return (
    <div className="panel panel-hover p-5">
      <p className="eyebrow">{eyebrow}</p>
      <p className="mt-2 font-display text-[2.1rem] font-bold leading-none text-ink">
        {value}
        {unit && (
          <span className="ml-1 text-base font-semibold text-ink-faint">{unit}</span>
        )}
      </p>
      <div className={`mt-3 h-1 w-10 rounded-full ${accent}`} />
    </div>
  );
}

/**
 * Trailing-days grid. Dates are the backend's UTC "YYYY-MM-DD" strings, so
 * everything here stays string-based — parsing them into Date objects would
 * re-anchor them to the viewer's timezone and shift tiles by a day.
 */
function ActivityHeatmap({ activity }: { activity: ActivityDay[] }) {
  const cells = useMemo(() => {
    const byDate = new Map(activity.map((d) => [d.date, d.count]));
    if (activity.length === 0) return { byDate, cells: [] as (string | null)[] };

    const [y, m, d] = activity[0].date.split("-").map(Number);
    const lead = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
    const padded: (string | null)[] = [
      ...Array<null>(lead).fill(null),
      ...activity.map((a) => a.date),
    ];
    while (padded.length % 7 !== 0) padded.push(null);
    return { byDate, cells: padded };
  }, [activity]);

  if (cells.cells.length === 0) {
    return <p className="text-[0.95rem] text-ink-faint">No activity yet.</p>;
  }

  const total = activity.reduce((sum, a) => sum + a.count, 0);

  return (
    <div>
      <div className="flex gap-2">
        <div className="grid grid-rows-7 gap-1 pt-0.5 font-mono text-[10px] font-semibold text-ink-faint">
          {["", "M", "", "W", "", "F", ""].map((label, i) => (
            <span key={i} className="flex h-4 items-center">
              {label}
            </span>
          ))}
        </div>
        <div className="grid flex-1 grid-flow-col grid-rows-7 gap-1">
          {cells.cells.map((iso, i) => {
            if (!iso) return <span key={`b${i}`} className="h-4" />;
            const count = cells.byDate.get(iso) ?? 0;
            return (
              <span
                key={iso}
                title={`${iso}: ${count} solve${count === 1 ? "" : "s"}`}
                className={cn("h-4 w-4 rounded-[3px]", levelClass(count))}
              />
            );
          })}
        </div>
      </div>
      <p className="mt-3 font-mono text-[11px] text-ink-faint">
        {total} solve{total === 1 ? "" : "s"} over the last {activity.length} days ·
        dates in UTC
      </p>
    </div>
  );
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileOut | null>(null);
  const [tab, setTab] = useState<Tab>("submissions");

  useEffect(() => {
    client
      .get<ProfileOut>("/profile")
      .then((res) => setProfile(res.data))
      .catch(() => {});
  }, []);

  const earnedCount = profile?.badges.filter((b) => b.earned).length ?? 0;

  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <TopBar active="profile">
          {user && <UserChip username={user.username} />}
        </TopBar>

        <main className="mx-auto max-w-6xl space-y-8 px-6 py-10">
          {!profile ? (
            <div className="flex items-center justify-center gap-2 py-24 text-ink-soft">
              <Loader2 size={20} className="animate-spin" />
              Loading your profile…
            </div>
          ) : (
            <>
              <section className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="eyebrow">Profile</p>
                  <h1 className="mt-1.5 font-display text-4xl font-bold tracking-tight text-ink">
                    {profile.user.username}
                  </h1>
                  <p className="mt-1 flex items-center gap-2 text-[1.05rem] text-ink-soft">
                    <Swords size={16} className="text-gold-deep" />
                    {profile.user.league_name} · Tier {profile.user.league_tier}
                  </p>
                </div>
                <Link href="/roadmap" className="btn btn-ink px-5 py-3 text-base">
                  Back to roadmap
                </Link>
              </section>

              <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                  eyebrow="Total XP"
                  value={
                    <span className="inline-flex items-center gap-2">
                      <Coin size={26} />
                      {profile.user.xp}
                    </span>
                  }
                  accent="bg-gold"
                />
                <StatCard
                  eyebrow="Streak"
                  value={profile.user.current_streak}
                  unit="days"
                  accent="bg-rust"
                />
                <StatCard
                  eyebrow="Solved"
                  value={profile.solved.total}
                  accent="bg-quest"
                />
                <StatCard
                  eyebrow="Tests taken"
                  value={profile.total_tests}
                  accent="bg-ink"
                />
              </section>

              <section className="grid grid-cols-1 gap-4 lg:grid-cols-5">
                <div className="panel p-6">
                  <p className="eyebrow">Solved by difficulty</p>
                  {profile.solved.total === 0 ? (
                    <p className="mt-3 text-sm text-ink-faint">
                      Solve your first problem to chart difficulty.
                    </p>
                  ) : (
                    <>
                      <div className="mt-4 flex h-3.5 w-full gap-0.5 overflow-hidden rounded-full bg-paper-deep">
                        {(["EASY", "MEDIUM", "HARD"] as const).map((key) => {
                          const value =
                            key === "EASY"
                              ? profile.solved.easy
                              : key === "MEDIUM"
                                ? profile.solved.medium
                                : profile.solved.hard;
                          return value > 0 ? (
                            <div
                              key={key}
                              className={DIFF_COLORS[key]}
                              style={{ width: `${(value / profile.solved.total) * 100}%` }}
                              title={`${key}: ${value}`}
                            />
                          ) : null;
                        })}
                      </div>
                      <div className="mt-4 grid grid-cols-3 gap-3">
                        {(["EASY", "MEDIUM", "HARD"] as const).map((key) => {
                          const value =
                            key === "EASY"
                              ? profile.solved.easy
                              : key === "MEDIUM"
                                ? profile.solved.medium
                                : profile.solved.hard;
                          return (
                            <div key={key}>
                              <p className="flex items-center gap-2 text-sm text-ink-soft">
                                <span
                                  className={`inline-block h-2 w-2 rounded-full ${DIFF_COLORS[key]}`}
                                />
                                {key.charAt(0) + key.slice(1).toLowerCase()}
                              </p>
                              <p className="mt-0.5 font-mono text-lg font-bold text-ink">
                                {value}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    </>
                  )}
                </div>

                <div className="panel p-6 lg:col-span-3">
                  <p className="eyebrow">Activity</p>
                  <h2 className="mt-1 flex items-center gap-2 font-display text-xl font-bold text-ink">
                    <CalendarDays size={17} className="text-ink-faint" />
                    Solve streak
                  </h2>
                  <div className="mt-4 overflow-x-auto">
                    <ActivityHeatmap activity={profile.activity} />
                  </div>
                </div>
              </section>

              <section>
                <div className="flex gap-1 overflow-x-auto rounded-xl border border-ink/10 bg-card p-1 shadow-card sm:w-fit">
                  {TABS.map((t) => (
                    <button
                      key={t.key}
                      type="button"
                      onClick={() => setTab(t.key)}
                      className={cn(
                        "whitespace-nowrap rounded-lg px-4 py-1.5 text-sm font-semibold transition-colors",
                        tab === t.key
                          ? "bg-ink text-paper"
                          : "text-ink-soft hover:text-ink"
                      )}
                    >
                      {t.label}
                      {t.key === "badges" && ` · ${earnedCount}/${profile.badges.length}`}
                    </button>
                  ))}
                </div>

                <div className="panel mt-4 p-6">
                  {tab === "submissions" &&
                    (profile.submissions.length === 0 ? (
                      <p className="text-[0.95rem] text-ink-faint">
                        Nothing yet — pick a problem and make your mark.
                      </p>
                    ) : (
                      <ul className="divide-y divide-ink/6">
                        {profile.submissions.map((sub) => (
                          <li
                            key={sub.id}
                            className="flex flex-wrap items-center gap-3 py-3 sm:flex-nowrap sm:justify-between"
                          >
                            <Link
                              href={`/problems/${sub.problem_slug}/solve`}
                              className="min-w-0 flex-1 truncate text-[0.95rem] font-medium text-ink hover:text-gold-deep"
                            >
                              {sub.problem_title}
                            </Link>
                            <span className="flex shrink-0 items-center gap-2.5">
                              <DifficultyChip difficulty={sub.difficulty} />
                              <span className="font-mono text-xs text-ink-faint">
                                {sub.runtime_ms != null
                                  ? `${Math.round(sub.runtime_ms)}ms`
                                  : "—"}
                                <span className="ml-1.5 uppercase">{sub.language}</span>
                              </span>
                              <span className="hidden w-28 shrink-0 text-right font-mono text-xs text-ink-faint sm:inline">
                                {formatWhen(sub.submitted_at)}
                              </span>
                              {sub.status === "ACCEPTED" ? (
                                <CheckCircle2 size={15} className="shrink-0 text-quest" />
                              ) : (
                                <XCircle size={15} className="shrink-0 text-rust" />
                              )}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ))}

                  {tab === "tests" &&
                    (profile.tests.length === 0 ? (
                      <p className="text-[0.95rem] text-ink-faint">
                        No mock tests yet — take one to see your history here.
                      </p>
                    ) : (
                      <ul className="divide-y divide-ink/6">
                        {profile.tests.map((t) => (
                          <li key={t.id}>
                            <Link
                              href={`/test/${t.id}/results`}
                              className="flex flex-wrap items-center gap-3 py-3 hover:bg-ink/[0.02] sm:flex-nowrap sm:justify-between"
                            >
                              <span className="flex min-w-0 flex-1 items-center gap-3">
                                <span className="font-mono text-lg font-bold text-ink">
                                  {t.score}
                                  <span className="text-ink-faint">/{t.total}</span>
                                </span>
                                <span className="min-w-0">
                                  <span className="block truncate text-[0.95rem] font-medium text-ink">
                                    Mock test
                                  </span>
                                  <span className="block truncate font-mono text-xs text-ink-faint">
                                    {t.assigned_topics.length > 0
                                      ? t.assigned_topics.map(topicLabel).join(" · ")
                                      : "No topics"}
                                  </span>
                                </span>
                              </span>
                              <span className="flex shrink-0 flex-col items-end gap-1 font-mono text-xs">
                                <span className="flex items-center gap-2">
                                  {t.violations > 0 && (
                                    <span className="flex items-center gap-1 text-rust">
                                      <AlertTriangle size={12} />
                                      {t.violations} violation
                                      {t.violations === 1 ? "" : "s"}
                                    </span>
                                  )}
                                  <span
                                    className={cn(
                                      "uppercase",
                                      t.status === "SUBMITTED"
                                        ? "text-quest"
                                        : "text-ink-faint"
                                    )}
                                  >
                                    {t.status.replace(/_/g, " ").toLowerCase()}
                                  </span>
                                </span>
                                <span className="text-ink-faint">
                                  {formatWhen(t.started_at)} ·{" "}
                                  {formatClock(t.time_taken_seconds)}
                                </span>
                              </span>
                            </Link>
                          </li>
                        ))}
                      </ul>
                    ))}

                  {tab === "badges" && (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
                      {profile.badges.map((badge) => (
                        <div
                          key={badge.criteria}
                          title={badge.description}
                          className={cn(
                            "panel panel-hover flex flex-col items-center p-4 text-center",
                            !badge.earned && "opacity-55"
                          )}
                          style={
                            badge.earned
                              ? { boxShadow: "var(--shadow-glow)" }
                              : { borderStyle: "dashed" }
                          }
                        >
                          {badge.earned ? (
                            <Award size={22} className="text-gold" strokeWidth={2.25} />
                          ) : (
                            <Lock size={19} className="text-ink-faint" />
                          )}
                          <p
                            className={cn(
                              "mt-2 font-display text-[0.8rem] font-semibold uppercase tracking-wide",
                              badge.earned ? "text-ink" : "text-ink-faint"
                            )}
                          >
                            {badge.name}
                          </p>
                          <p className="mt-1 line-clamp-2 text-xs leading-snug text-ink-faint">
                            {badge.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
