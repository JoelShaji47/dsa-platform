"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  ArrowLeftRight,
  ChevronUp,
  Crown,
  Flame,
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
import { TIER_THEMES, tierTheme, tierVars } from "./leagues-theme";
import { Aura, CountUp, TierCrest } from "./league-fx";

type Tab = "league" | "global" | "monthly" | "patterns";

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

/** A single status chip. Lives on the tier band, so it is white on the tier
 *  field (>= 6.3:1 at 90% white) rather than a themed badge. */
function BandChip({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-white/12 px-3 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-white ring-1 ring-inset ring-white/25">
      <span className="shrink-0">{icon}</span>
      {children}
    </span>
  );
}

function ZoneTag({ zone }: { zone: LeagueMember["zone"] }) {
  if (zone === "promote")
    return (
      <span className="flex items-center gap-1 font-mono text-[10px] font-semibold uppercase text-quest-deep">
        <ChevronUp size={11} strokeWidth={3} /> Up
      </span>
    );
  if (zone === "relegate")
    return (
      <span className="flex items-center gap-1 font-mono text-[10px] uppercase text-rust-deep">
        <TrendingDown size={11} /> Down
      </span>
    );
  return (
    <span className="flex items-center gap-1 font-mono text-[10px] uppercase text-ink-soft">
      <Minus size={11} /> Hold
    </span>
  );
}

/**
 * The seven worlds: one row per tier, each carrying its own colour.
 *
 * Every row re-declares the `--tier-*` properties for its own tier, so the
 * `tier-text` / `tier-swatch` classes resolve to that tier's colour and pick
 * the light or dark text variant from CSS instead of a JS theme branch.
 */
function SevenWorlds({ current }: { current: number }) {
  return (
    <div className="panel overflow-hidden">
      <div className="px-5 pt-5">
        <p className="eyebrow">The seven worlds</p>
        <p className="mt-1 text-xs leading-relaxed text-ink-soft">
          Everyone starts in Bronze. Top 10 climb on Monday.
        </p>
      </div>
      <ol className="mt-3">
        {TIER_THEMES.map((t, i) => {
          const active = i === current;
          const cleared = i < current;
          return (
            <li
              key={t.name}
              style={tierVars(t)}
              className={cn(
                "relative flex items-center gap-3 px-5 py-2.5",
                active && "tier-soft"
              )}
            >
              {active && (
                <span
                  aria-hidden
                  className="tier-rail absolute inset-y-0 left-0 w-[3px]"
                />
              )}
              <span
                aria-hidden
                className={cn(
                  "h-3.5 w-3.5 shrink-0 rounded-[4px]",
                  active || cleared
                    ? "tier-swatch"
                    : "border border-dashed border-ink/25"
                )}
              />
              <span className="tier-text font-display text-sm font-bold">
                {t.name}
              </span>
              <span className="ml-auto font-mono text-[10px] uppercase tracking-widest">
                {active ? (
                  <span className="rounded-full bg-ink/8 px-2 py-0.5 font-bold text-ink">
                    You
                  </span>
                ) : cleared ? (
                  <span className="text-quest-deep">Cleared</span>
                ) : (
                  <span className="text-ink-faint">Locked</span>
                )}
              </span>
            </li>
          );
        })}
      </ol>
      <Separator />
      <p className="px-5 py-3 text-xs leading-relaxed text-ink-faint">
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

  const tier = league?.tier ?? 0;
  const theme = tierTheme(tier);
  const atTopTier = tier >= TIER_THEMES.length - 1;
  const nextTier = atTopTier ? null : TIER_THEMES[tier + 1].name;
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
  const streak = stats?.current_streak ?? user?.current_streak ?? 0;
  const solved = stats?.total_solved ?? 0;

  return (
    <ProtectedRoute>
      <div
        className="atlas-bg relative min-h-screen overflow-hidden"
        style={tierVars(theme)}
      >
        <div className="relative">
          <TopBar active="leagues">
            {user && <UserChip username={user.username} />}
          </TopBar>

          {/* ── Tier world band: full-bleed, one saturated field ──────────
              The band is fixed in both themes — it is the tier's world, not a
              themed surface — which is what lets every band colour carry white
              text at a measured >= 5.9:1. Everything below follows the theme. */}
          <section className="tier-band relative overflow-hidden">
            <Aura color="rgba(255,255,255,0.85)" />
            <span
              aria-hidden
              className="tier-rail absolute inset-x-0 bottom-0 h-1"
            />
            <div className="relative mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
              <div className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-x-5 gap-y-6 sm:gap-x-7">
                {/* Crest plate — a fixed bone badge so all seven arcs hold
                    their measured contrast in either theme. */}
                <div className="self-start rounded-[2rem] bg-white/15 p-1.5 ring-1 ring-white/25">
                  <div className="rounded-[calc(2rem-0.375rem)] bg-[#f7f5f0] px-3 py-2.5 shadow-[inset_0_1px_1px_rgba(255,255,255,0.7)]">
                    <TierCrest current={tier} themes={TIER_THEMES} size={96} />
                    <p className="mt-1.5 text-center font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-[#66727e]">
                      {league || loading
                        ? `Tier ${tier + 1} / ${TIER_THEMES.length}`
                        : "Not racing"}
                    </p>
                  </div>
                </div>

                <div className="min-w-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                    <h1 className="eyebrow flex items-center gap-1.5 text-white/90">
                      <Swords size={12} /> Leagues
                      <span className="hidden sm:inline">· ranked play</span>
                    </h1>
                    <span className="w-full font-mono text-[10px] uppercase tracking-[0.16em] text-white/90 sm:w-auto">
                      Season ends in {countdown}
                    </span>
                  </div>
                  <h2 className="mt-2 font-display text-4xl font-bold leading-none tracking-tight text-white sm:text-5xl">
                    {tab !== "league"
                      ? "Rankings"
                      : league || loading
                        ? theme.name
                        : "Sitting out"}
                  </h2>
                  <p className="mt-2.5 font-mono text-[10px] uppercase leading-relaxed tracking-[0.14em] text-white/90">
                    {!league && !loading
                      ? "Rejoin to be seeded at your pace"
                      : atTopTier
                        ? "Final tier"
                        : `Next: ${nextTier}`}
                    {league ? (
                      <span className="hidden sm:inline">
                        {` · ${league.size} racers · week of ${league.week_start}`}
                      </span>
                    ) : null}
                  </p>
                </div>

                <div className="col-span-2">
                  {tab === "league" && myRow ? (
                    <dl className="grid grid-cols-2 gap-x-6 gap-y-4 border-t border-white/20 pt-5 sm:grid-cols-4">
                      <div>
                        <dt className="font-mono text-[10px] uppercase tracking-widest text-white/90">
                          Rank
                        </dt>
                        <dd className="mt-0.5 font-display text-2xl font-bold text-white">
                          #{myRow.rank}
                        </dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase tracking-widest text-white/90">
                          Week XP
                        </dt>
                        <dd className="mt-0.5 font-display text-2xl font-bold text-white">
                          <CountUp value={myXp} />
                        </dd>
                      </div>
                      {promoLine && (
                        <div>
                          <dt className="font-mono text-[10px] uppercase tracking-widest text-white/90">
                            {promoLine.safe ? "Cushion" : "To climb"}
                          </dt>
                          <dd className="mt-0.5 font-display text-xl font-bold text-white sm:text-2xl">
                            {promoLine.text}
                          </dd>
                        </div>
                      )}
                      <div>
                        <dt className="font-mono text-[10px] uppercase tracking-widest text-white/90">
                          Day streak
                        </dt>
                        <dd className="mt-0.5 flex items-center gap-1.5 font-display text-2xl font-bold text-white">
                          <Flame size={17} className="text-white/90" />
                          {streak}
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="border-t border-white/20 pt-5 text-sm leading-relaxed text-white/90">
                      {loading
                        ? "Loading this week's cohort…"
                        : league
                          ? "No XP banked yet this week — your first accepted solve puts you on the board."
                          : "Join this week's cohort and every solve starts moving you up the board from your very first Easy."}
                    </p>
                  )}

                  {tab === "league" && boardRows.length > 1 && (
                    <div className="mt-5 space-y-2.5">
                      <div>
                        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-white/90">
                          <span>To the promotion line</span>
                          <span>
                            {myXp}/{cutoffXp} XP · {cutoffProgress}%
                          </span>
                        </div>
                        <div
                          className="mt-1 h-2 overflow-hidden rounded-full bg-white/20"
                          role="progressbar"
                          aria-valuenow={cutoffProgress}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label="Progress to promotion line"
                        >
                          <div
                            className="h-full rounded-full bg-white transition-[width] duration-700"
                            style={{ width: `${cutoffProgress}%` }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-white/90">
                          <span>To the leader</span>
                          <span>
                            {myXp}/{leaderXp} XP · {leaderProgress}%
                          </span>
                        </div>
                        <div
                          className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/20"
                          role="progressbar"
                          aria-valuenow={leaderProgress}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label="Progress to leader"
                        >
                          <div
                            className="h-full rounded-full bg-white/55 transition-[width] duration-700"
                            style={{ width: `${leaderProgress}%` }}
                          />
                        </div>
                      </div>
                      {inDanger && (
                        <p className="flex items-center gap-1.5 text-xs font-medium text-white/90">
                          <TrendingDown size={13} />
                          You&apos;re {myXp - relegationXp} XP above the drop zone
                          — one more solve steadies the ship.
                        </p>
                      )}
                    </div>
                  )}

                  <div className="mt-5 flex flex-wrap items-center gap-2">
                    {lastMovement !== null && lastMovement !== undefined ? (
                      lastMovement > 0 ? (
                        <BandChip icon={<TrendingUp size={12} />}>
                          Promoted last week
                        </BandChip>
                      ) : lastMovement < 0 ? (
                        <BandChip icon={<TrendingDown size={12} />}>
                          Relegated — climb back
                        </BandChip>
                      ) : (
                        <BandChip icon={<Minus size={12} />}>
                          Held tier last week
                        </BandChip>
                      )
                    ) : (
                      <BandChip icon={<Crown size={12} />}>
                        First race in {theme.name}
                      </BandChip>
                    )}
                    <BandChip icon={<Flame size={12} />}>
                      {streak}-day streak
                    </BandChip>
                    <div className="ml-auto">
                      {tab === "league" &&
                        (league ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={leave}
                            className="border-white/30 bg-white/5 text-white hover:border-white/60 hover:bg-white/10 hover:text-white"
                          >
                            <LogOut size={13} />
                            Sit this week out
                          </Button>
                        ) : (
                          !loading && (
                            <Button
                              size="sm"
                              onClick={rejoin}
                              className="bg-white text-[#3b4753] hover:bg-white/90"
                            >
                              Rejoin the climb
                            </Button>
                          )
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <main className="mx-auto w-full max-w-6xl px-4 pb-16 pt-8 sm:px-6">
            <p className="max-w-[72ch] text-sm leading-relaxed text-ink-soft">
              Solve a little every day, bank XP with every question, and
              outclimb last week&apos;s you. Cohorts of 30 race at a similar
              pace — nobody starts ahead, nobody gets left behind.
            </p>

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
                      <span className="tier-soft flex h-9 w-9 shrink-0 items-center justify-center rounded-xl">
                        <s.icon size={17} className="tier-text" />
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
                    tab === t ? "tier-band" : "text-ink-soft hover:text-ink"
                  )}
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
                        ? "border-quest-deep bg-quest/10 text-quest-deep"
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
                      // The promotion banner renders after its row, so idx 9
                      // puts it directly below rank 10. The drop banner renders
                      // before its row, so it starts at the first relegated rank.
                      const showPromoCut =
                        tab === "league" && idx === 9 && boardRows.length > 10;
                      const showDangerCut =
                        tab === "league" &&
                        boardRows.length >= 30 &&
                        idx === boardRows.length - 5;
                      // Zones are places, not labels: the board shades the
                      // promotion and drop bands so the cut is visible without
                      // reading every rank.
                      const podium = tab === "league" && r.rank <= 3;
                      const inPromoZone =
                        tab === "league" && r.rank <= 10 && boardRows.length > 10;
                      const inDropZone =
                        tab === "league" &&
                        boardRows.length >= 30 &&
                        r.rank > boardRows.length - 5;
                      return (
                        <li key={`${r.rank}-${r.username}`}>
                          {showDangerCut && (
                            <p className="flex items-center gap-2 border-y border-rust/25 bg-rust/12 px-4 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-widest text-rust-deep sm:px-5">
                              <TrendingDown size={11} /> Drop zone below — final
                              5 fall a tier
                            </p>
                          )}
                          <div
                            className={cn(
                              "relative flex items-center gap-3 px-4 py-3 sm:px-5",
                              r.me
                                ? "tier-soft"
                                : podium
                                  ? r.rank === 1
                                    ? "bg-gold/12"
                                    : "bg-ink/[0.035]"
                                  : inPromoZone
                                    ? "bg-quest/12"
                                    : inDropZone && "bg-rust/12"
                            )}
                          >
                            {(r.me || (podium && r.rank === 1)) && (
                              <span
                                aria-hidden
                                className={cn(
                                  "absolute inset-y-0 left-0 w-[3px]",
                                  r.me ? "tier-rail" : "bg-gold"
                                )}
                              />
                            )}
                            <span
                              className={cn(
                                "w-7 shrink-0 text-center font-mono text-sm font-bold",
                                r.rank === 1 ? "text-gold-deep" : "text-ink-soft"
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
                                        ? "text-slate-500"
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
                                r.me ? "font-semibold text-ink" : "text-ink-soft"
                              )}
                            >
                              {r.username}
                              {r.me && gap !== null && gap > 0 && (
                                <span className="ml-2 font-mono text-[10px] text-ink-soft">
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
                            <p className="flex items-center gap-2 border-y border-quest/25 bg-quest/12 px-4 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-widest text-quest-deep sm:px-5">
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
                <SevenWorlds current={tier} />
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
                        className="mt-0.5 shrink-0 text-quest-deep"
                      />
                      <span className="text-ink-soft">
                        <span className="font-semibold text-ink">Top 10 climb</span>{" "}
                        — a tier up on Monday morning.
                      </span>
                    </li>
                    <li className="flex items-start gap-2.5">
                      <Flame size={15} className="mt-0.5 shrink-0 text-rust-deep" />
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
