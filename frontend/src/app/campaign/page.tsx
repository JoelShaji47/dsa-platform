"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Award,
  CheckCircle2,
  Flag,
  History,
  Loader2,
  Lock,
  Play,
  Shield,
  ShoppingBag,
  Swords,
  XCircle,
  Zap,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { Coin } from "@/components/coin";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type {
  BadgeOut,
  Bucket,
  LeagueInfo,
  LeagueMember,
  ReviewDueItem,
  ShopStatus,
  StatsOut,
} from "@/lib/types";

const TOPIC_ORDER = [
  "ARRAY",
  "STRING",
  "LINKED_LIST",
  "STACK",
  "QUEUE",
  "TREE",
  "GRAPH",
  "DP",
];

const DIFF_COLORS: Record<string, string> = {
  EASY: "bg-quest",
  MEDIUM: "bg-gold",
  HARD: "bg-rust",
};

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

function TrailNode({ pct }: { pct: number }) {
  const r = 13;
  const c = 2 * Math.PI * r;
  return (
    <span className="relative flex h-9 w-9 shrink-0 items-center justify-center">
      <svg viewBox="0 0 32 32" className="h-9 w-9 -rotate-90">
        <circle cx="16" cy="16" r={r} fill="#fff" stroke="rgb(22 35 59 / 0.12)" strokeWidth="2.5" />
        <circle
          cx="16"
          cy="16"
          r={r}
          fill="none"
          stroke="var(--color-gold)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - pct / 100)}
        />
      </svg>
    </span>
  );
}

export default function CampaignPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<StatsOut | null>(null);
  const [badges, setBadges] = useState<BadgeOut[]>([]);
  const [reviewDue, setReviewDue] = useState<ReviewDueItem[] | null>(null);
  const [league, setLeague] = useState<LeagueInfo | null>(null);
  const [myZone, setMyZone] = useState<LeagueMember["zone"] | null>(null);
  const [shop, setShop] = useState<ShopStatus | null>(null);
  const [buying, setBuying] = useState(false);
  const [shopMsg, setShopMsg] = useState<string | null>(null);

  useEffect(() => {
    client.get<StatsOut>("/stats/me").then((res) => setStats(res.data)).catch(() => {});
    client.get<BadgeOut[]>("/badges/me").then((res) => setBadges(res.data)).catch(() => {});
    client
      .get<{ review_due: ReviewDueItem[] }>("/roadmap/review-due")
      .then((res) => setReviewDue(res.data.review_due))
      .catch(() => setReviewDue([]));
    client
      .get<{ league: LeagueInfo | null; members: LeagueMember[] }>("/leagues/me")
      .then((res) => {
        setLeague(res.data.league);
        const me = res.data.members.find((m) => m.is_me);
        setMyZone(me?.zone ?? null);
      })
      .catch(() => {});
    client
      .get<ShopStatus>("/shop")
      .then((res) => setShop(res.data))
      .catch(() => {});
  }, []);

  const buyFreeze = async () => {
    setBuying(true);
    setShopMsg(null);
    try {
      const res = await client.post<{ freezes: number; xp: number; cost: number }>(
        "/shop/freeze"
      );
      setShop((prev) =>
        prev ? { ...prev, freezes: res.data.freezes, xp: res.data.xp } : prev
      );
      setShopMsg(`Freeze stocked (${res.data.freezes} held)`);
      client.get<StatsOut>("/stats/me").then((r) => setStats(r.data)).catch(() => {});
    } catch (err) {
      const detail = (
        err as { response?: { data?: { detail?: string }; status?: number } }
      )?.response?.data?.detail;
      setShopMsg(detail || "Couldn't buy that right now.");
    } finally {
      setBuying(false);
    }
  };

  const topics = stats
    ? TOPIC_ORDER.filter((t) => stats.solved_by_topic[t]).map((t) => ({
        name: t,
        ...(stats.solved_by_topic[t] as Bucket),
      }))
    : [];

  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <TopBar active="dashboard">
          {user && <UserChip username={user.username} />}
        </TopBar>

        <main className="mx-auto max-w-6xl space-y-8 px-6 py-10">
          {!stats ? (
            <div className="flex items-center justify-center gap-2 py-24 text-ink-soft">
              <Loader2 size={20} className="animate-spin" />
              Unfurling your map…
            </div>
          ) : (
            <>
              <section className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="eyebrow">Campaign</p>
                  <h1 className="mt-1.5 font-display text-4xl font-bold tracking-tight text-ink">
                    Welcome back, {user?.username}
                  </h1>
                  <p className="mt-1 text-[1.05rem] text-ink-soft">Here is where you stand.</p>
                </div>
                <Link href="/roadmap" className="btn btn-ink px-5 py-3 text-base">
                  <Play size={17} />
                  Continue the quest
                </Link>
              </section>

              <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard eyebrow="Total XP" value={<span className="inline-flex items-center gap-2"><Coin size={26} />{stats.xp}</span>} accent="bg-gold" />
                <StatCard eyebrow="Streak" value={stats.current_streak} unit="days" accent="bg-rust" />
                <StatCard eyebrow="Solved" value={stats.total_solved} accent="bg-quest" />
                <StatCard eyebrow="Acceptance" value={`${stats.acceptance_rate}%`} accent="bg-ink" />
              </section>

              <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="panel p-6">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="eyebrow">Ranked play</p>
                      <h2 className="mt-1 flex items-center gap-2 font-display text-xl font-bold text-ink">
                        <Swords size={18} className="text-gold-deep" />
                        {league ? `${league.tier_name} League` : "Leagues"}
                      </h2>
                    </div>
                    <Link href="/leagues" className="btn btn-ink px-4 py-2 text-sm">
                      Open board
                    </Link>
                  </div>
                  {league ? (
                    <p className="mt-3 text-sm text-ink-soft">
                      Rank{" "}
                      <span className="font-mono font-bold text-ink">
                        #{league.my_rank ?? "–"}
                      </span>{" "}
                      of {league.size}
                      {myZone === "promote" && (
                        <span className="ml-2 font-semibold text-quest">· promotion zone</span>
                      )}
                      {myZone === "relegate" && (
                        <span className="ml-2 font-semibold text-rust">· danger zone</span>
                      )}
                    </p>
                  ) : (
                    <p className="mt-3 text-sm text-ink-faint">
                      Solve to get seeded into this week&apos;s cohort.
                    </p>
                  )}
                </div>

                <div className="panel p-6">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="eyebrow">XP shop</p>
                      <h2 className="mt-1 flex items-center gap-2 font-display text-xl font-bold text-ink">
                        <ShoppingBag size={18} className="text-gold-deep" />
                        Streak freezes
                      </h2>
                    </div>
                    <button
                      onClick={buyFreeze}
                      disabled={buying || !shop}
                      className="btn btn-quest px-4 py-2 text-sm"
                    >
                      {buying ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Zap size={14} />
                      )}
                      <Coin size={14} />
                      Buy · 100
                    </button>
                  </div>
                  <p className="mt-3 flex items-center gap-2 text-sm text-ink-soft">
                    <Shield size={14} className="text-quest" />
                    Holding {shop?.freezes ?? 0}/3
                    <span className="ml-auto inline-flex items-center gap-1.5 font-mono font-bold text-ink">
                      <Coin size={14} />
                      {shop?.xp ?? stats.xp}
                    </span>
                  </p>
                  {shopMsg && (
                    <p className="mt-2 text-xs text-ink-faint">{shopMsg}</p>
                  )}
                </div>
              </section>

              <section className="grid grid-cols-1 gap-8 lg:grid-cols-5">
                <div className="panel p-6 lg:col-span-3">
                  <p className="eyebrow">The Trail</p>
                  <h2 className="mt-1 font-display text-xl font-bold text-ink">Topic waypoints</h2>
                  <div className="relative mt-5">
                    {topics.length > 1 && (
                      <span
                        aria-hidden
                        className="absolute bottom-5 left-[1.05rem] top-5 border-l-2 border-dashed border-ink/15"
                      />
                    )}
                    <ul className="space-y-4">
                      {topics.map((t) => {
                        const pct = t.total ? Math.round((t.solved / t.total) * 100) : 0;
                        const last = t === topics[topics.length - 1];
                        return (
                          <li key={t.name} className="relative flex items-center gap-4">
                            <TrailNode pct={pct} />
                            <div className="min-w-0 flex-1">
                              <div className="flex items-baseline justify-between gap-3">
                                <Link
                                  href={`/problems?topic=${t.name}`}
                                  className="font-display text-[0.95rem] font-semibold uppercase tracking-wide text-ink hover:text-gold-deep"
                                >
                                  {t.name.replace("_", " ")}
                                </Link>
                                <span className="font-mono text-xs text-ink-faint">
                                  {t.solved}/{t.total}
                                </span>
                              </div>
                              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-paper-deep">
                                <div
                                  className={`h-full rounded-full ${pct === 100 ? "bg-quest" : "bg-gold"}`}
                                  style={{ width: `${pct}%`, transition: "width 0.4s ease-out" }}
                                />
                              </div>
                            </div>
                            {last ? (
                              <Flag size={18} className="shrink-0 text-rust" />
                            ) : null}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                </div>

                <div className="space-y-8 lg:col-span-2">
                  <div className="panel p-6">
                    <p className="eyebrow">Difficulty breakdown</p>
                    {(() => {
                      const entries = Object.entries(stats.solved_by_difficulty);
                      const totalAll = entries.reduce((sum, [, b]) => sum + b.total, 0);
                      return totalAll === 0 ? (
                        <p className="mt-3 text-sm text-ink-faint">
                          Solve your first problem to chart difficulty.
                        </p>
                      ) : (
                        <>
                          <div className="mt-4 flex h-3.5 w-full gap-0.5 overflow-hidden rounded-full bg-paper-deep">
                            {entries.map(([key, bucket]) =>
                              bucket.total > 0 ? (
                                <div
                                  key={key}
                                  className={DIFF_COLORS[key]}
                                  style={{
                                    width: `${(bucket.solved / Math.max(totalAll, 1)) * 100}%`,
                                    minWidth: bucket.solved > 0 ? "6px" : 0,
                                  }}
                                  title={`${key}: ${bucket.solved}/${bucket.total}`}
                                />
                              ) : null
                            )}
                          </div>
                          <div className="mt-4 space-y-1.5">
                            {entries.map(([key, bucket]) => (
                              <div key={key} className="flex items-center justify-between text-sm">
                                <span className="flex items-center gap-2 text-ink-soft">
                                  <span className={`inline-block h-2 w-2 rounded-full ${DIFF_COLORS[key]}`} />
                                  {key.charAt(0) + key.slice(1).toLowerCase()}
                                </span>
                                <span className="font-mono text-xs text-ink-faint">
                                  {bucket.solved}/{bucket.total}
                                </span>
                              </div>
                            ))}
                          </div>
                        </>
                      );
                    })()}
                  </div>

                  <div className="panel p-6">
                    <p className="eyebrow">Recent submissions</p>
                    {stats.recent_submissions.length === 0 ? (
                      <p className="mt-3 text-[0.95rem] text-ink-faint">
                        Nothing yet — pick a problem and make your mark.
                      </p>
                    ) : (
                      <ul className="mt-3 divide-y divide-ink/6">
                        {stats.recent_submissions.map((sub) => (
                          <li key={sub.id} className="flex items-center justify-between gap-3 py-2.5">
                            <Link
                              href={`/problems/${sub.problem_slug}/solve`}
                              className="truncate text-[0.95rem] font-medium text-ink hover:text-gold-deep"
                            >
                              {sub.problem_title}
                            </Link>
                            <span className="flex shrink-0 items-center gap-2.5 font-mono text-xs text-ink-faint">
                              {sub.runtime_ms != null && `${Math.round(sub.runtime_ms)}ms`}
                              <span className="uppercase">{sub.language}</span>
                              {sub.status === "ACCEPTED" ? (
                                <CheckCircle2 size={15} className="text-quest" />
                              ) : (
                                <XCircle size={15} className="text-rust" />
                              )}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </section>

            {reviewDue !== null && reviewDue.length > 0 && (
              <section className="panel p-6">
                <p className="eyebrow">Due for review · {reviewDue.length}</p>
                <h2 className="mt-1 font-display text-xl font-bold text-ink">
                  Spaced repetition
                </h2>
                <p className="mt-1 text-sm text-ink-soft">
                  You solved these a while ago with hints or extra attempts.
                  Re-solve to lock them in.
                </p>
                <ul className="mt-4 divide-y divide-ink/6">
                  {reviewDue.slice(0, 5).map((item) => (
                    <li key={item.slug} className="flex items-center gap-3 py-2.5">
                      <History size={15} className="shrink-0 text-gold-deep" />
                      <Link
                        href={`/problems/${item.slug}/solve`}
                        className="truncate text-[0.95rem] font-medium text-ink hover:text-gold-deep"
                      >
                        {item.title}
                      </Link>
                      <span className="ml-auto shrink-0 font-mono text-xs text-ink-faint">
                        {item.hints_used > 0
                          ? `${item.hints_used} hint${item.hints_used === 1 ? "" : "s"}`
                          : `${item.attempts} attempts`}
                      </span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            <section className="panel p-6">
              <p className="eyebrow">
                Trophies · {badges.filter((b) => b.earned).length}/{badges.length}
              </p>
                <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
                  {badges.map((badge) => (
                    <div
                      key={badge.criteria}
                      title={badge.description}
                      className={`panel panel-hover flex flex-col items-center p-4 text-center ${
                        badge.earned ? "" : "opacity-55"
                      }`}
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
                        className={`mt-2 font-display text-[0.8rem] font-semibold uppercase tracking-wide ${
                          badge.earned ? "text-ink" : "text-ink-faint"
                        }`}
                      >
                        {badge.name}
                      </p>
                      <p className="mt-1 line-clamp-2 text-xs leading-snug text-ink-faint">
                        {badge.description}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
