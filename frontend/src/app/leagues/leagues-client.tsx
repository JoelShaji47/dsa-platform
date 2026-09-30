"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  ChevronUp,
  Crown,
  Flame,
  Loader2,
  LogOut,
  Medal,
  Minus,
  Swords,
  Target,
  TrendingDown,
  TrendingUp,
  Trophy,
  Zap,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { LeagueInfo, LeagueMember, StatsOut } from "@/lib/types";
import { Coin } from "@/components/coin";
import { cn } from "@/lib/utils";
import { tierTheme } from "./leagues-theme";
import { Aura, Beams, CountUp } from "./league-fx";

type Tab = "league" | "global" | "monthly" | "patterns";

const TIERS = ["Bronze", "Silver", "Gold", "Sapphire", "Ruby", "Emerald", "Diamond"];

const TIER_COLORS = [
  "text-orange-700",
  "text-slate-500",
  "text-gold-deep",
  "text-sky-600",
  "text-rust",
  "text-quest",
  "text-violet-600",
];

const XP_BY_DIFFICULTY = [
  { label: "Easy", xp: 10 },
  { label: "Medium", xp: 20 },
  { label: "Hard", xp: 40 },
] as const;

const CLIMB_STEPS = [
  {
    icon: Swords,
    title: "Solve anything",
    text: "Every accepted solution banks week XP — easy or hard, it all counts.",
  },
  {
    icon: Zap,
    title: "Stack XP daily",
    text: "Streaks multiply earnings up to +50%. A little each day beats a weekend binge.",
  },
  {
    icon: Target,
    title: "Hold the top 10",
    text: "Cohorts of 30 at a similar pace. Finish top 10 to climb a tier.",
  },
  {
    icon: Medal,
    title: "Promote Monday",
    text: "Seasons reset weekly. Rank 1 takes the Weekly Champion badge.",
  },
] as const;

function useCountdownToMonday(): string {
  const [left, setLeft] = useState("--:--:--");
  useEffect(() => {
    const tick = () => {
      const now = new Date();
      const end = new Date(now);
      end.setDate(now.getDate() + ((8 - now.getDay()) % 7 || 7));
      end.setHours(0, 0, 0, 0);
      const s = Math.max(0, Math.floor((end.getTime() - now.getTime()) / 1000));
      const d = Math.floor(s / 86400);
      const h = String(Math.floor((s % 86400) / 3600)).padStart(2, "0");
      const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
      setLeft(`${d}d ${h}:${m}`);
    };
    tick();
    const id = setInterval(tick, 30000);
    return () => clearInterval(id);
  }, []);
  return left;
}

function ZoneTag({ zone }: { zone: LeagueMember["zone"] }) {
  if (zone === "promote")
    return (
      <span className="flex items-center gap-1 font-mono text-[10px] font-semibold uppercase text-quest">
        <ChevronUp size={11} strokeWidth={3} /> Up
      </span>
    );
  if (zone === "relegate")
    return (
      <span className="flex items-center gap-1 font-mono text-[10px] uppercase text-rust">
        <TrendingDown size={11} /> Down
      </span>
    );
  return (
    <span className="flex items-center gap-1 font-mono text-[10px] uppercase text-ink-faint">
      <Minus size={11} /> Hold
    </span>
  );
}

/** Vertical climb rail: spine + tier medallions, current tier ringed in accent. */
function TierLadder({ current }: { current: number }) {
  return (
    <div className="panel p-5">
      <p className="eyebrow">The climb</p>
      <p className="mt-1 text-xs text-ink-soft">
        Seven tiers. One solve at a time — everyone starts in Bronze.
      </p>
      <ol className="relative mt-4 space-y-1">
        <span
          aria-hidden
          className="absolute bottom-4 left-[26px] top-4 w-px bg-ink/10"
        />
        {TIERS.map((name, i) => {
          const active = i === current;
          const passed = i < current;
          return (
            <li
              key={name}
              className={cn(
                "relative flex items-center gap-3 rounded-lg px-3 py-2 transition-colors",
                active && "bg-gold/10 ring-1 ring-gold/40"
              )}
            >
              <span
                className={cn(
                  "relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border bg-card",
                  active
                    ? "border-gold/60"
                    : passed
                      ? "border-quest/50"
                      : "border-ink/10"
                )}
              >
                <Trophy
                  size={12}
                  className={cn(
                    TIER_COLORS[i],
                    !active && !passed && "opacity-40"
                  )}
                />
              </span>
              <span
                className={cn(
                  "font-display text-sm font-bold",
                  active ? "text-ink" : "text-ink-soft"
                )}
              >
                {name}
              </span>
              <span className="ml-auto font-mono text-[10px] uppercase">
                {active ? (
                  <span className="rounded-full bg-gold/15 px-2 py-0.5 font-bold text-gold-deep">
                    You
                  </span>
                ) : passed ? (
                  <span className="text-quest">Cleared</span>
                ) : (
                  <span className="text-ink-faint">Locked</span>
                )}
              </span>
            </li>
          );
        })}
      </ol>
      <Separator className="my-3" />
      <p className="text-xs leading-relaxed text-ink-faint">
        Top 10 each week climb a tier · bottom 5 drop · rank 1 takes Weekly
        Champion.
      </p>
    </div>
  );
}

type BoardRow = {
  rank: number;
  username: string;
  xp?: number;
  solved?: number;
  zone?: LeagueMember["zone"];
  me: boolean;
};

export default function LeaguesClient() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("league");
  const [league, setLeague] = useState<LeagueInfo | null>(null);
  const [optedOut, setOptedOut] = useState(false);
  const [lastMovement, setLastMovement] = useState<number | null>(null);
  const [members, setMembers] = useState<LeagueMember[]>([]);
  const [stats, setStats] = useState<StatsOut | null>(null);
  const [rows, setRows] = useState<
    { rank: number; username: string; xp?: number; solved?: number }[]
  >([]);
  const [patterns, setPatterns] = useState<{ key: string; name: string }[]>([]);
  const [pattern, setPattern] = useState("");
  const [loading, setLoading] = useState(true);
  const countdown = useCountdownToMonday();

  const loadLeague = () => {
    setLoading(true);
    // Independent reads go out together — no waterfall.
    Promise.all([
      client.get("/leagues/me"),
      client.get<StatsOut>("/stats/me").catch(() => null),
    ])
      .then(([res, statsRes]) => {
        setLeague(res.data.league);
        setMembers(res.data.members ?? []);
        setOptedOut(!!res.data.opted_out && !res.data.league);
        setLastMovement(res.data.league ? null : (res.data.last_movement ?? null));
        if (res.data.league?.last_week_movement !== undefined) {
          setLastMovement(res.data.league.last_week_movement);
        }
        if (statsRes) setStats(statsRes.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (tab === "league") {
      loadLeague();
    } else if (tab === "patterns") {
      setLoading(true);
      client
        .get("/roadmap")
        .then((res) => {
          const list = (res.data.patterns ?? []).map((p: { key: string; name: string }) => ({
            key: p.key,
            name: p.name,
          }));
          setPatterns(list);
          if (!pattern && list.length) setPattern(list[0].key);
        })
        .catch(() => {});
    } else {
      setLoading(true);
      const url = tab === "global" ? "/leagues/global" : "/leagues/monthly";
      client
        .get(url)
        .then((res) => setRows(res.data.board))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  useEffect(() => {
    if (tab !== "patterns" || !pattern) return;
    setLoading(true);
    client
      .get(`/leagues/pattern/${pattern}`)
      .then((res) => setRows(res.data.board))
      .catch(() => {})
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pattern]);

  const leave = async () => {
    await client.delete("/leagues/me").catch(() => {});
    loadLeague();
  };
  const rejoin = async () => {
    await client.post("/leagues/rejoin").catch(() => {});
    loadLeague();
  };

  const boardRows: BoardRow[] = useMemo(
    () =>
      tab === "league"
        ? members.map((m) => ({
            rank: m.rank,
            username: m.username + (m.is_me ? " (you)" : ""),
            xp: m.xp,
            zone: m.zone,
            me: m.is_me,
          }))
        : rows.map((r) => ({ ...r, me: r.username === user?.username })),
    [tab, members, rows, user?.username]
  );

  const theme = tierTheme(league?.tier ?? 0);
  const myRow = boardRows.find((r) => r.me);
  const xpOf = (r: BoardRow | undefined) =>
    r && r.xp !== undefined ? r.xp : 0;
  const myXp = xpOf(myRow);
  const leaderXp = boardRows.length ? xpOf(boardRows[0]) : 0;
  const cutoffXp = boardRows.length > 10 ? xpOf(boardRows[9]) : myXp;
  const relegationXp =
    boardRows.length > 5 ? xpOf(boardRows[boardRows.length - 5]) : 0;
  const promoLine =
    tab === "league" && myRow && boardRows.length > 10
      ? myRow.rank <= 10
        ? { safe: true, text: `Safe by ${myXp - xpOf(boardRows[10])} XP` }
        : { safe: false, text: `${cutoffXp - myXp + 1} XP to climb` }
      : null;
  const cutoffProgress =
    cutoffXp > 0 ? Math.min(100, Math.round((myXp / cutoffXp) * 100)) : 0;
  const leaderProgress =
    leaderXp > 0 ? Math.min(100, Math.round((myXp / leaderXp) * 100)) : 0;
  const inDanger =
    tab === "league" &&
    !!myRow &&
    boardRows.length >= 30 &&
    myRow.rank > boardRows.length - 5;
  const nextTier = TIERS[Math.min((league?.tier ?? 0) + 1, TIERS.length - 1)];
  const streak = stats?.current_streak ?? user?.current_streak ?? 0;
  const solved = stats?.total_solved ?? 0;

  return (
    <ProtectedRoute>
      <div className="atlas-bg relative min-h-screen overflow-hidden">
        {/* Tier wash over the whole page */}
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <span
            className="absolute -top-32 left-1/2 h-96 w-[60rem] -translate-x-1/2 rounded-full opacity-20 blur-3xl"
            style={{ backgroundColor: theme.accent }}
          />
          <span
            className="absolute bottom-0 right-0 h-72 w-72 rounded-full opacity-10 blur-3xl"
            style={{ backgroundColor: theme.accent }}
          />
        </div>
        <div className="relative">
        <TopBar active="leagues">
          {user && <UserChip username={user.username} />}
        </TopBar>
        <main className="mx-auto w-full max-w-6xl px-4 pb-16 pt-10 sm:px-6">
          <div>
            <p className="eyebrow">Ranked play · everyone climbs</p>
            <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
              Leagues
            </h1>
            <p className="mt-1 max-w-[65ch] text-sm leading-relaxed text-ink-soft">
              The whole point of CodeQuest: solve a little every day, bank XP
              with every question, and outclimb last week&apos;s you. Cohorts of
              30 race at a similar pace — nobody starts ahead, nobody gets left
              behind.
            </p>
          </div>

          {/* ── Split hero: climb status + tier medallion ─────────── */}
          <div
            className="rise-in relative mt-6 overflow-hidden rounded-2xl border border-ink/10 bg-card p-6 shadow-card sm:p-8"
            style={{ boxShadow: theme.glow }}
          >
            <Beams color={theme.accent} />
            <Aura color={theme.accent} />
            <div className="relative grid gap-6 md:grid-cols-[1.5fr_1fr]">
              <div>
                <p className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint">
                  <Swords size={12} />
                  Season ends in {countdown}
                  {league && (
                    <span className="ml-auto hidden sm:inline">
                      {league.size} racers · week of {league.week_start}
                    </span>
                  )}
                </p>
                <h2
                  className="mt-2 font-display text-5xl font-bold tracking-tight sm:text-6xl"
                  style={{ color: theme.accent }}
                >
                  {tab === "league" ? theme.name : "Rankings"}
                </h2>
                {tab === "league" && myRow ? (
                  <dl className="mt-3 flex flex-wrap gap-x-8 gap-y-3">
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        Rank
                      </dt>
                      <dd className="font-display text-2xl font-bold text-ink">
                        #{myRow.rank}
                      </dd>
                    </div>
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        Week XP
                      </dt>
                      <dd className="font-display text-2xl font-bold text-ink">
                        <CountUp value={myXp} />
                      </dd>
                    </div>
                    {promoLine && (
                      <div>
                        <dt className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                          {promoLine.safe ? "Cushion" : "To climb"}
                        </dt>
                        <dd
                          className={cn(
                            "font-display text-2xl font-bold",
                            promoLine.safe ? "text-quest" : "text-gold-deep"
                          )}
                        >
                          {promoLine.text}
                        </dd>
                      </div>
                    )}
                    <div>
                      <dt className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        Day streak
                      </dt>
                      <dd className="flex items-center gap-1.5 font-display text-2xl font-bold text-ink">
                        <Flame size={18} className="text-rust" />
                        {streak}
                      </dd>
                    </div>
                  </dl>
                ) : (
                  <p className="mt-3 max-w-[52ch] text-sm text-ink-soft">
                    Join this week&apos;s cohort and every solve starts moving
                    you up the board from your very first Easy.
                  </p>
                )}
                {tab === "league" && boardRows.length > 1 && (
                  <div className="mt-4 space-y-2">
                    <div>
                      <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        <span>To the promotion line</span>
                        <span>
                          {myXp}/{cutoffXp} XP · {cutoffProgress}%
                        </span>
                      </div>
                      <div
                        className="mt-1 h-2 overflow-hidden rounded-full bg-ink/8"
                        role="progressbar"
                        aria-valuenow={cutoffProgress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label="Progress to promotion line"
                      >
                        <div
                          className="h-full rounded-full transition-[width] duration-700"
                          style={{
                            width: `${cutoffProgress}%`,
                            backgroundColor: theme.accent,
                          }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        <span>To the leader</span>
                        <span>
                          {myXp}/{leaderXp} XP · {leaderProgress}%
                        </span>
                      </div>
                      <div
                        className="mt-1 h-1.5 overflow-hidden rounded-full bg-ink/8"
                        role="progressbar"
                        aria-valuenow={leaderProgress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label="Progress to leader"
                      >
                        <div
                          className="h-full rounded-full bg-gold transition-[width] duration-700"
                          style={{ width: `${leaderProgress}%` }}
                        />
                      </div>
                    </div>
                    {inDanger && (
                      <p className="flex items-center gap-1.5 text-xs font-medium text-rust">
                        <TrendingDown size={13} />
                        You&apos;re {myXp - relegationXp} XP above the drop zone
                        — one more solve steadies the ship.
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Tier medallion — double-bezel hardware card */}
              <div className="rounded-[2rem] bg-ink/5 p-1.5 ring-1 ring-ink/10 md:justify-self-end md:w-full md:max-w-[300px]">
                <div className="rounded-[calc(2rem-0.375rem)] bg-card p-5 shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]">
                  <div className="flex items-center gap-3">
                    <span
                      className="flex h-14 w-14 items-center justify-center rounded-full ring-2"
                      style={{
                        backgroundColor: `${theme.accent}14`,
                        // @ts-expect-error CSS var for ring color
                        "--tw-ring-color": `${theme.accent}66`,
                      }}
                    >
                      <Trophy size={24} style={{ color: theme.accent }} />
                    </span>
                    <div>
                      <p className="eyebrow">Your tier</p>
                      <p
                        className="font-display text-xl font-bold leading-tight"
                        style={{ color: theme.accent }}
                      >
                        {theme.name}
                      </p>
                      <p className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                        Tier {(league?.tier ?? 0) + 1} of {TIERS.length} · next:{" "}
                        {nextTier}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {lastMovement !== null && lastMovement !== undefined ? (
                      <Badge
                        variant="outline"
                        className={cn(
                          "gap-1",
                          lastMovement > 0 && "border-quest/50 text-quest",
                          lastMovement < 0 && "border-rust/50 text-rust"
                        )}
                      >
                        {lastMovement > 0 ? (
                          <>
                            <TrendingUp size={12} /> Promoted last week
                          </>
                        ) : lastMovement < 0 ? (
                          <>
                            <TrendingDown size={12} /> Relegated — climb back
                          </>
                        ) : (
                          "Held tier last week"
                        )}
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="gap-1">
                        <SparklesFallback /> First race in {theme.name}
                      </Badge>
                    )}
                    <Badge variant="secondary" className="gap-1">
                      <Flame size={12} /> {streak}-day streak
                    </Badge>
                  </div>
                  <Separator className="my-3" />
                  <p className="text-xs leading-relaxed text-ink-soft">
                    One Medium a day (~20 XP) clears most promotion lines by
                    Sunday. Consistency beats intensity.
                  </p>
                  {tab === "league" &&
                    (league ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={leave}
                        className="mt-3 hover:border-rust hover:text-rust"
                      >
                        <LogOut size={13} />
                        Sit this week out
                      </Button>
                    ) : (
                      !loading && (
                        <Button size="sm" onClick={rejoin} className="mt-3">
                          Rejoin the climb
                        </Button>
                      )
                    ))}
                </div>
              </div>
            </div>
          </div>

          {/* ── How the climb works ─────────────────────────────── */}
          <section aria-label="How the climb works" className="mt-5">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {CLIMB_STEPS.map((s, i) => (
                <div
                  key={s.title}
                  className="rise-in panel p-4"
                  style={{ animationDelay: `${i * 90}ms` }}
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
                      style={{ backgroundColor: `${theme.accent}14` }}
                    >
                      <s.icon size={17} style={{ color: theme.accent }} />
                    </span>
                    <p className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                      Step {i + 1}
                    </p>
                  </div>
                  <p className="mt-2.5 font-display text-sm font-bold text-ink">
                    {s.title}
                  </p>
                  <p className="mt-0.5 text-xs leading-relaxed text-ink-soft">
                    {s.text}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* ── Every question moves you ────────────────────────── */}
          <section
            aria-label="XP per question"
            className="rise-in panel mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-3.5"
            style={{ animationDelay: "120ms" }}
          >
            <p className="flex items-center gap-2 text-sm font-semibold text-ink">
              <Coin size={15} />
              Every question moves you
            </p>
            <div className="flex flex-wrap items-center gap-1.5">
              {XP_BY_DIFFICULTY.map((d) => (
                <Badge key={d.label} variant="secondary" className="gap-1.5 font-mono">
                  {d.label} · {d.xp} XP
                </Badge>
              ))}
            </div>
            <p className="w-full text-xs text-ink-faint sm:w-auto sm:flex-1 sm:text-right">
              Streaks to +50% · clean first-tries +25% · weak patterns +25%
            </p>
          </section>

          <div className="mt-5 flex gap-1 overflow-x-auto rounded-xl border border-ink/10 bg-card p-1 shadow-card sm:w-fit">
            {(["league", "global", "monthly", "patterns"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={cn(
                  "whitespace-nowrap rounded-lg px-4 py-1.5 text-sm font-semibold capitalize transition-colors",
                  tab === t ? "text-white" : "text-ink-soft hover:text-ink"
                )}
                style={
                  tab === t ? { backgroundColor: theme.accent } : undefined
                }
              >
                {t === "league" ? "My league" : t}
              </button>
            ))}
          </div>

          {tab === "patterns" && patterns.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-1.5">
              {patterns.map((p) => (
                <button
                  key={p.key}
                  type="button"
                  onClick={() => setPattern(p.key)}
                  className={cn(
                    "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                    pattern === p.key
                      ? "border-quest bg-quest/10 text-quest"
                      : "border-ink/10 text-ink-soft hover:text-ink"
                  )}
                >
                  {p.name}
                </button>
              ))}
            </div>
          )}

          <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-[1fr_300px]">
            <div className="panel overflow-hidden">
              {loading ? (
                <div className="space-y-2 px-4 py-5 sm:px-5" aria-label="Loading standings">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <Skeleton className="h-5 w-7" />
                      <Skeleton className="h-5 flex-1" />
                      <Skeleton className="h-5 w-14" />
                    </div>
                  ))}
                </div>
              ) : tab === "league" && !league ? (
                <div className="px-6 py-12 text-center">
                  <ArrowLeftRight size={28} className="mx-auto text-ink-faint" />
                  <p className="mt-3 font-display text-lg font-bold text-ink">
                    You&apos;re out this week
                  </p>
                  <p className="mx-auto mt-1 max-w-sm text-sm text-ink-soft">
                    Ranked play is better together — rejoin and we&apos;ll seed
                    you into a cohort of 30 at your pace. Your tier and streak
                    are safe.
                  </p>
                  <Button onClick={rejoin} className="mx-auto mt-4">
                    Rejoin the climb
                  </Button>
                  {optedOut ? null : null}
                </div>
              ) : boardRows.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <Trophy size={28} className="mx-auto text-ink-faint" />
                  <p className="mt-3 font-display text-lg font-bold text-ink">
                    No standings yet
                  </p>
                  <p className="mx-auto mt-1 max-w-sm text-sm text-ink-soft">
                    Solve any problem and you&apos;ll appear here — your first
                    10 XP already moves you off the bottom.
                  </p>
                </div>
              ) : (
                <ul className="divide-y divide-ink/8">
                  {boardRows.map((r, idx) => {
                    const score =
                      "xp" in r && r.xp !== undefined ? r.xp : null;
                    const solvedCount =
                      score === null && "solved" in r ? (r.solved ?? 0) : null;
                    const prevXp =
                      idx > 0 && boardRows[idx - 1].xp !== undefined
                        ? (boardRows[idx - 1].xp as number)
                        : null;
                    const gap =
                      prevXp !== null && score !== null && idx > 0
                        ? prevXp - score
                        : null;
                    const showPromoCut =
                      tab === "league" && idx === 9 && boardRows.length > 10;
                    const showDangerCut =
                      tab === "league" &&
                      boardRows.length >= 30 &&
                      idx === boardRows.length - 6;
                    return (
                      <li key={`${r.rank}-${r.username}`}>
                        {showDangerCut && (
                          <p className="flex items-center gap-2 bg-rust/5 px-4 py-1.5 font-mono text-[10px] uppercase tracking-widest text-rust sm:px-5">
                            <TrendingDown size={11} /> Drop zone below — final 5
                            fall a tier
                          </p>
                        )}
                        <div
                          className={cn(
                            "flex items-center gap-3 px-4 py-3 sm:px-5",
                            r.me && theme.soft
                          )}
                          style={
                            r.rank === 1 && tab === "league"
                              ? { boxShadow: `inset 3px 0 0 ${theme.accent}` }
                              : r.me
                                ? { boxShadow: `inset 3px 0 0 ${theme.accent}55` }
                                : undefined
                          }
                        >
                          <span
                            className={cn(
                              "w-7 shrink-0 text-center font-mono text-sm font-bold",
                              r.rank === 1 ? "text-gold-deep" : "text-ink-faint"
                            )}
                          >
                            {r.rank <= 3 ? (
                              <Trophy
                                size={15}
                                className={cn(
                                  "mx-auto",
                                  r.rank === 1
                                    ? "text-gold-deep"
                                    : r.rank === 2
                                      ? "text-slate-400"
                                      : "text-orange-700"
                                )}
                              />
                            ) : (
                              r.rank
                            )}
                          </span>
                          <span
                            className={cn(
                              "min-w-0 flex-1 truncate text-sm font-medium",
                              r.me ? "text-ink" : "text-ink-soft"
                            )}
                          >
                            {r.username}
                            {gap !== null && gap > 0 && (
                              <span className="ml-2 font-mono text-[10px] text-ink-faint">
                                +{gap} to pass
                              </span>
                            )}
                          </span>
                          {"zone" in r && r.zone ? (
                            <ZoneTag zone={r.zone as LeagueMember["zone"]} />
                          ) : null}
                          <span className="flex shrink-0 items-center gap-1.5 font-mono text-sm font-bold text-ink">
                            {score !== null ? (<><Coin size={13} />{score}</>) : `${solvedCount} solved`}
                          </span>
                        </div>
                        {showPromoCut && (
                          <p className="flex items-center gap-2 bg-quest/5 px-4 py-1.5 font-mono text-[10px] uppercase tracking-widest text-quest sm:px-5">
                            <ChevronUp size={11} strokeWidth={3} /> Promotion
                            line — above this climbs a tier
                          </p>
                        )}
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

            <aside className="space-y-5">
              <TierLadder current={league?.tier ?? 0} />
              <div className="panel p-5">
                <p className="eyebrow">This week&apos;s stakes</p>
                <ul className="mt-3 space-y-2.5 text-sm">
                  <li className="flex items-start gap-2.5">
                    <Crown size={15} className="mt-0.5 shrink-0 text-gold-deep" />
                    <span className="text-ink-soft">
                      <span className="font-semibold text-ink">
                        Weekly Champion
                      </span>{" "}
                      — rank 1 earns the badge forever.
                    </span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <ChevronUp
                      size={15}
                      strokeWidth={3}
                      className="mt-0.5 shrink-0 text-quest"
                    />
                    <span className="text-ink-soft">
                      <span className="font-semibold text-ink">Top 10 climb</span>{" "}
                      — a tier up on Monday morning.
                    </span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <Flame size={15} className="mt-0.5 shrink-0 text-rust" />
                    <span className="text-ink-soft">
                      <span className="font-semibold text-ink">
                        {solved} solved · {streak}-day streak
                      </span>{" "}
                      — every day you show up, multipliers grow.
                    </span>
                  </li>
                </ul>
                <Separator className="my-3" />
                <p className="text-xs leading-relaxed text-ink-faint">
                  Fell behind? The drop is only one tier, and cohorts re-seed
                  by pace — your comeback week is always winnable.
                </p>
              </div>
            </aside>
          </div>
          {tab === "league" && league && (
            <p className="mt-3 text-xs text-ink-faint">
              Top 10 promote a tier · bottom 5 relegated · rank 1 takes the
              Weekly Champion badge. Seasons reset every Monday.
            </p>
          )}
        </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function SparklesFallback() {
  return (
    <span className="flex items-center gap-1">
      <Crown size={12} /> New season
    </span>
  );
}
