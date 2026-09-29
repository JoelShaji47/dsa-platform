"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ChevronUp,
  Crown,
  Loader2,
  Minus,
  Swords,
  TrendingDown,
  Trophy,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { LeagueInfo, LeagueMember } from "@/lib/types";
import { cn } from "@/lib/utils";

type Tab = "league" | "global" | "monthly";

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

export default function LeaguesClient() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("league");
  const [league, setLeague] = useState<LeagueInfo | null>(null);
  const [members, setMembers] = useState<LeagueMember[]>([]);
  const [rows, setRows] = useState<
    { rank: number; username: string; xp?: number; solved?: number }[]
  >([]);
  const [loading, setLoading] = useState(true);
  const countdown = useCountdownToMonday();

  useEffect(() => {
    setLoading(true);
    const url =
      tab === "league"
        ? "/leagues/me"
        : tab === "global"
          ? "/leagues/global"
          : "/leagues/monthly";
    client
      .get(url)
      .then((res) => {
        if (tab === "league") {
          setLeague(res.data.league);
          setMembers(res.data.members);
          setRows([]);
        } else {
          setRows(res.data.board);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tab]);

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

  return (
    <ProtectedRoute>
      <div className="atlas-bg min-h-screen">
        <TopBar active="leagues">
          {user && <UserChip username={user.username} />}
        </TopBar>
        <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-10">
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <p className="eyebrow">Ranked play</p>
              <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
                Leagues
              </h1>
            </div>
            {league && tab === "league" && (
              <div className="ml-auto flex items-center gap-3">
                <span
                  className={cn(
                    "flex items-center gap-1.5 rounded-full border border-ink/10 bg-card px-3 py-1.5 font-display text-sm font-bold",
                    TIER_COLORS[league.tier] ?? "text-ink"
                  )}
                >
                  <Trophy size={14} />
                  {league.tier_name}
                </span>
                <span className="flex items-center gap-1.5 font-mono text-xs text-ink-faint">
                  <Swords size={12} />
                  Season ends in {countdown}
                </span>
              </div>
            )}
          </div>

          <div className="mt-5 flex gap-1 rounded-xl border border-ink/10 bg-card p-1 shadow-card sm:w-fit">
            {(["league", "global", "monthly"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={cn(
                  "rounded-lg px-4 py-1.5 text-sm font-semibold capitalize transition-colors",
                  tab === t ? "bg-ink text-white" : "text-ink-soft hover:text-ink"
                )}
              >
                {t === "league" ? "My league" : t}
              </button>
            ))}
          </div>

          <div className="panel mt-5 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center gap-2 py-16 text-sm text-ink-faint">
                <Loader2 size={16} className="animate-spin" />
                Seeding your league…
              </div>
            ) : boardRows.length === 0 ? (
              <p className="px-6 py-12 text-center text-sm text-ink-soft">
                No standings yet — solve something to enter the ranks.
              </p>
            ) : (
              <ul className="divide-y divide-ink/8">
                {boardRows.map((r) => {
                  const score = "xp" in r && r.xp !== undefined ? r.xp : null;
                  const solved =
                    !("xp" in r && r.xp !== undefined) && "solved" in r
                      ? (r.solved ?? 0)
                      : null;
                  return (
                  <li
                    key={`${r.rank}-${r.username}`}
                    className={cn(
                      "flex items-center gap-3 px-5 py-3",
                      r.me && "bg-gold/10"
                    )}
                  >
                    <span
                      className={cn(
                        "w-7 shrink-0 text-center font-mono text-sm font-bold",
                        r.rank === 1 ? "text-gold-deep" : "text-ink-faint"
                      )}
                    >
                      {r.rank === 1 ? <Crown size={15} className="mx-auto" /> : r.rank}
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
                    <span className="shrink-0 font-mono text-sm font-bold text-ink">
                      {score !== null ? `${score} XP` : `${solved} solved`}
                    </span>
                  </li>
                  );
                })}
              </ul>
            )}
          </div>
          {tab === "league" && (
            <p className="mt-3 text-xs text-ink-faint">
              Top 10 promote a tier · bottom 5 relegated · rank 1 takes the
              Weekly Champion badge. Seasons reset every Monday.
            </p>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
