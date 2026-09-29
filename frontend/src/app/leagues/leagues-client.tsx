"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  ChevronUp,
  Crown,
  Loader2,
  LogOut,
  Minus,
  Swords,
  TrendingDown,
  TrendingUp,
  Trophy,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { LeagueInfo, LeagueMember } from "@/lib/types";
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
      <span className="flex items-center gap-1 font-mono text-[10px] font-semibold uppercase text-rust">
        <TrendingDown size={11} /> Down
      </span>
    );
  return (
    <span className="flex items-center gap-1 font-mono text-[10px] uppercase text-ink-faint">
      <Minus size={11} /> Hold
    </span>
  );
}

function TierLadder({ current }: { current: number }) {
  return (
    <div className="panel p-5">
      <p className="eyebrow">The climb</p>
      <ol className="mt-3 space-y-1.5">
        {TIERS.map((name, i) => {
          const active = i === current;
          const passed = i < current;
          return (
            <li
              key={name}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2",
                active && "bg-gold/10 ring-1 ring-gold/40"
              )}
            >
              <Trophy
                size={14}
                className={cn(TIER_COLORS[i], !active && !passed && "opacity-40")}
              />
              <span
                className={cn(
                  "font-display text-sm font-bold",
                  active ? "text-ink" : "text-ink-soft"
                )}
              >
                {name}
              </span>
              {active && (
                <span className="ml-auto rounded-full bg-gold/15 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-gold-deep">
                  You
                </span>
              )}
              {passed && !active && (
                <span className="ml-auto font-mono text-[10px] uppercase text-quest">
                  Cleared
                </span>
              )}
            </li>
          );
        })}
      </ol>
      <p className="mt-3 text-xs text-ink-faint">
        Top 10 each week climb a tier · bottom 5 drop · rank 1 takes Weekly
        Champion.
      </p>
    </div>
  );
}

export default function LeaguesClient() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("league");
  const [league, setLeague] = useState<LeagueInfo | null>(null);
  const [optedOut, setOptedOut] = useState(false);
  const [lastMovement, setLastMovement] = useState<number | null>(null);
  const [members, setMembers] = useState<LeagueMember[]>([]);
  const [rows, setRows] = useState<
    { rank: number; username: string; xp?: number; solved?: number }[]
  >([]);
  const [patterns, setPatterns] = useState<{ key: string; name: string }[]>([]);
  const [pattern, setPattern] = useState("");
  const [loading, setLoading] = useState(true);
  const countdown = useCountdownToMonday();

  const loadLeague = () => {
    setLoading(true);
    client
      .get("/leagues/me")
      .then((res) => {
        setLeague(res.data.league);
        setMembers(res.data.members ?? []);
        setOptedOut(!!res.data.opted_out && !res.data.league);
        setLastMovement(res.data.league ? null : (res.data.last_movement ?? null));
        if (res.data.league?.last_week_movement !== undefined) {
          setLastMovement(res.data.league.last_week_movement);
        }
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

  const boardRows = useMemo(
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
    [tab, members, rows, user]
  );

  const theme = tierTheme(league?.tier ?? 0);
  const myRow = boardRows.find((r) => r.me);
  const xpOf = (r: (typeof boardRows)[number] | undefined) =>
    r && "xp" in r && r.xp !== undefined ? r.xp : 0;
  const myXp = xpOf(myRow);
  const promoLine =
    tab === "league" && myRow && boardRows.length > 10
      ? myRow.rank <= 10
        ? { safe: true, text: `Safe by ${myXp - xpOf(boardRows[10])} XP` }
        : { safe: false, text: `${xpOf(boardRows[9]) - myXp + 1} XP to promotion` }
      : null;

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
            <p className="eyebrow">Ranked play</p>
            <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
              Leagues
            </h1>
          </div>

          <div
            className="rise-in relative mt-6 overflow-hidden rounded-2xl border border-ink/10 bg-card p-6 shadow-card sm:p-8"
            style={{ boxShadow: theme.glow }}
          >
            <Beams color={theme.accent} />
            <Aura color={theme.accent} />
            <div className="relative">
              <p className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint">
                <Swords size={12} />
                Season ends in {countdown}
                {league && (
                  <span className="ml-auto hidden sm:inline">
                    {league.size} racers · week of {league.week_start}
                  </span>
                )}
              </p>
              <div className="mt-2 flex flex-wrap items-end gap-x-8 gap-y-4">
                <h2
                  className="font-display text-5xl font-bold tracking-tight sm:text-6xl"
                  style={{ color: theme.accent }}
                >
                  {tab === "league" ? theme.name : "Rankings"}
                </h2>
                {tab === "league" && myRow && (
                  <dl className="flex gap-6 pb-1">
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
                  </dl>
                )}
                {tab === "league" && (
                  <button
                    onClick={leave}
                    title="Leave this week's league"
                    className="btn mb-1 ml-auto border border-ink/12 px-3 py-1.5 text-xs text-ink-soft hover:text-rust"
                  >
                    <LogOut size={13} />
                    Leave
                  </button>
                )}
              </div>
            </div>
          </div>

          {lastMovement !== null && lastMovement !== undefined && tab === "league" && (
            <p
              className={cn(
                "mt-3 flex w-fit items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
                lastMovement > 0
                  ? "bg-quest/10 text-quest"
                  : lastMovement < 0
                    ? "bg-rust/10 text-rust"
                    : "bg-ink/5 text-ink-soft"
              )}
            >
              {lastMovement > 0 ? (
                <>
                  <TrendingUp size={13} /> Promoted last week
                </>
              ) : lastMovement < 0 ? (
                <>
                  <TrendingDown size={13} /> Relegated last week — climb back
                </>
              ) : (
                "Held your tier last week"
              )}
            </p>
          )}

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
                <div className="flex items-center justify-center gap-2 py-16 text-sm text-ink-faint">
                  <Loader2 size={16} className="animate-spin" />
                  Seeding your league…
                </div>
              ) : tab === "league" && !league ? (
                <div className="px-6 py-12 text-center">
                  <ArrowLeftRight size={28} className="mx-auto text-ink-faint" />
                  <p className="mt-3 font-display text-lg font-bold text-ink">
                    You&apos;re out this week
                  </p>
                  <p className="mx-auto mt-1 max-w-sm text-sm text-ink-soft">
                    You left (or were removed from) ranked play. Rejoin to get
                    seeded into a cohort.
                  </p>
                  <button
                    onClick={rejoin}
                    className="btn btn-quest mx-auto mt-4 px-5 py-2.5 text-sm"
                  >
                    Rejoin league
                  </button>
                </div>
              ) : boardRows.length === 0 ? (
                <p className="px-6 py-12 text-center text-sm text-ink-soft">
                  No standings yet — solve something to enter the ranks.
                </p>
              ) : (
                <ul className="divide-y divide-ink/8">
                  {boardRows.map((r) => {
                    const score =
                      "xp" in r && r.xp !== undefined ? r.xp : null;
                    const solved =
                      score === null && "solved" in r ? (r.solved ?? 0) : null;
                    return (
                      <li
                        key={`${r.rank}-${r.username}`}
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
                        </span>
                        {"zone" in r && r.zone ? (
                          <ZoneTag zone={r.zone as LeagueMember["zone"]} />
                        ) : null}
                        <span className="flex shrink-0 items-center gap-1.5 font-mono text-sm font-bold text-ink">
                          {score !== null ? (<><Coin size={13} />{score}</>) : `${solved} solved`}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

            <aside className="space-y-5">
              <TierLadder current={league?.tier ?? 0} />
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
