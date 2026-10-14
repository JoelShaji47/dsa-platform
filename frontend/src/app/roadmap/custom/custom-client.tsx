"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, Check, Loader2, Plus, Users } from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { CustomRoadmap } from "@/lib/types";
import { cn } from "@/lib/utils";

const LEVELS = [
  { key: "never_started", label: "Never started" },
  { key: "basics", label: "Know the basics" },
  { key: "50_plus", label: "Solved 50+" },
  { key: "interview_ready", label: "Interview-ready" },
];

const GOALS = [
  { key: "interview_soon", label: "Interview soon" },
  { key: "fundamentals", label: "Strong fundamentals" },
  { key: "company", label: "A specific company" },
  { key: "curious", label: "Just curious" },
];

const TIMES = [
  { mins: 30, label: "30 min", sub: "a focused session" },
  { mins: 60, label: "1 hour", sub: "the sweet spot" },
  { mins: 120, label: "2 hr+", sub: "going hard" },
];

const DURATIONS = [
  { days: 14, label: "2 weeks" },
  { days: 21, label: "3 weeks" },
  { days: 30, label: "1 month" },
  { days: 42, label: "6 weeks" },
];

export default function CustomRoadmapClient() {
  const { user } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<"build" | "join">("build");
  const [mine, setMine] = useState<CustomRoadmap[]>([]);
  const [quota, setQuota] = useState<{ used: number; limit: number; remaining: number } | null>(null);

  // Wizard state — four taps.
  const [step, setStep] = useState(1);
  const [level, setLevel] = useState("basics");
  const [goal, setGoal] = useState("fundamentals");
  const [company, setCompany] = useState("");
  const [mins, setMins] = useState(60);
  const [days, setDays] = useState(21);
  const [customDays, setCustomDays] = useState("");
  const [count, setCount] = useState("");
  const [kind, setKind] = useState("dsa_build");
  const [building, setBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [code, setCode] = useState("");
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      client.get<CustomRoadmap[]>("/roadmaps/custom"),
      client.get("/roadmaps/custom/quota"),
    ])
      .then(([list, q]) => {
        if (cancelled) return;
        setMine(list.data);
        setQuota(q.data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const effectiveDays = customDays ? Math.max(1, Math.min(180, Number(customDays) || days)) : days;

  const build = async () => {
    setBuilding(true);
    setError(null);
    try {
      const res = await client.post<CustomRoadmap>("/roadmaps/custom", {
        level,
        goal,
        company: goal === "company" ? company || undefined : undefined,
        mins_per_day: mins,
        total_days: effectiveDays,
        target_count: count ? Number(count) : undefined,
        kind,
      });
      router.push(`/roadmap/custom/${res.data.id}`);
    } catch (err) {
      const detail =
        (err as { response?: { data?: { detail?: string }; status?: number } })?.response?.data?.detail;
      setError(detail || "Could not build your roadmap. Try again.");
    } finally {
      setBuilding(false);
    }
  };

  const join = async () => {
    if (code.trim().length !== 6 || joining) return;
    setJoining(true);
    setError(null);
    try {
      const res = await client.post<CustomRoadmap>("/roadmaps/custom/join", {
        share_code: code.trim().toUpperCase(),
      });
      router.push(`/roadmap/custom/${res.data.id}`);
    } catch {
      setError("No roadmap found with that code. Check the 6 characters and retry.");
    } finally {
      setJoining(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="atlas-bg min-h-screen">
        <TopBar active="roadmap">{user && <UserChip username={user.username} />}</TopBar>
        <main className="mx-auto w-full max-w-4xl px-6 pb-16 pt-10">
          <p className="eyebrow">Four taps</p>
          <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
            Your roadmap, your pace
          </h1>
          <p className="mt-2 text-ink-soft">
            We draft the syllabus, order it so nothing depends on what you haven&apos;t learnt yet,
            and hand you one honest list each morning.
            {quota && (
              <span className="font-mono text-sm">
                {" "}· {quota.remaining}/{quota.limit} builds left this week
              </span>
            )}
          </p>

          <div className="mb-4 mt-6 flex w-fit gap-1 rounded-xl border border-ink/10 bg-card p-1 shadow-card">
            {(["build", "join"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={cn(
                  "rounded-lg px-4 py-1.5 text-sm font-semibold capitalize transition-colors",
                  tab === t ? "bg-ink text-paper" : "text-ink-soft hover:text-ink"
                )}
              >
                {t === "build" ? "Build your own" : "Join a friend"}
              </button>
            ))}
          </div>

          {error && (
            <p className="mb-4 rounded-xl border border-rust/30 bg-rust/10 px-4 py-2.5 text-sm text-rust">
              {error}
            </p>
          )}

          {tab === "build" ? (
            <section className="panel p-6">
              <div className="flex gap-1.5">
                {[1, 2, 3, 4].map((n) => (
                  <span
                    key={n}
                    className={cn("h-1.5 flex-1 rounded-full", n <= step ? "bg-quest" : "bg-ink/10")}
                  />
                ))}
              </div>

              {step === 1 && (
                <div>
                  <h2 className="mt-4 font-display text-lg font-bold text-ink">Where are you now?</h2>
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {LEVELS.map((l) => (
                      <button
                        key={l.key}
                        type="button"
                        onClick={() => { setLevel(l.key); setStep(2); }}
                        className={cn(
                          "rounded-xl border px-4 py-3 text-left font-semibold transition-all",
                          level === l.key
                            ? "border-gold/50 bg-accent/40 text-ink"
                            : "border-ink/10 text-ink-soft hover:border-ink/25"
                        )}
                      >
                        {l.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div>
                  <h2 className="mt-4 font-display text-lg font-bold text-ink">What are you aiming for?</h2>
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {GOALS.map((g) => (
                      <button
                        key={g.key}
                        type="button"
                        onClick={() => { setGoal(g.key); setStep(3); }}
                        className={cn(
                          "rounded-xl border px-4 py-3 text-left font-semibold transition-all",
                          goal === g.key
                            ? "border-gold/50 bg-accent/40 text-ink"
                            : "border-ink/10 text-ink-soft hover:border-ink/25"
                        )}
                      >
                        {g.label}
                      </button>
                    ))}
                  </div>
                  {goal === "company" && (
                    <input
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                      placeholder="Which company? (e.g. Google)"
                      className="field mt-3"
                    />
                  )}
                  <button type="button" onClick={() => setStep(1)} className="mt-4 text-sm text-ink-faint hover:underline">
                    ← Back
                  </button>
                </div>
              )}

              {step === 3 && (
                <div>
                  <h2 className="mt-4 font-display text-lg font-bold text-ink">Time per day</h2>
                  <div className="mt-3 grid gap-2 sm:grid-cols-3">
                    {TIMES.map((t) => (
                      <button
                        key={t.mins}
                        type="button"
                        onClick={() => { setMins(t.mins); setStep(4); }}
                        className={cn(
                          "rounded-xl border px-4 py-3 text-left transition-all",
                          mins === t.mins
                            ? "border-gold/50 bg-accent/40"
                            : "border-ink/10 hover:border-ink/25"
                        )}
                      >
                        <span className="block font-display font-bold text-ink">{t.label}</span>
                        <span className="text-xs text-ink-faint">{t.sub}</span>
                      </button>
                    ))}
                  </div>
                  <button type="button" onClick={() => setStep(2)} className="mt-4 text-sm text-ink-faint hover:underline">
                    ← Back
                  </button>
                </div>
              )}

              {step === 4 && (
                <div>
                  <h2 className="mt-4 font-display text-lg font-bold text-ink">How long have you got?</h2>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {DURATIONS.map((d) => (
                      <button
                        key={d.days}
                        type="button"
                        onClick={() => { setDays(d.days); setCustomDays(""); }}
                        className={cn(
                          "rounded-xl border px-4 py-2 font-semibold transition-all",
                          effectiveDays === d.days && !customDays
                            ? "border-gold/50 bg-accent/40 text-ink"
                            : "border-ink/10 text-ink-soft hover:border-ink/25"
                        )}
                      >
                        {d.label}
                      </button>
                    ))}
                    <input
                      value={customDays}
                      onChange={(e) => setCustomDays(e.target.value.replace(/[^0-9]/g, "").slice(0, 3))}
                      placeholder="or type days"
                      inputMode="numeric"
                      className="w-32 rounded-xl border border-ink/15 bg-paper px-3 py-2 text-sm"
                    />
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <input
                      value={count}
                      onChange={(e) => setCount(e.target.value.replace(/[^0-9]/g, "").slice(0, 3))}
                      placeholder="How many questions? (optional)"
                      inputMode="numeric"
                      className="w-60 rounded-xl border border-ink/15 bg-paper px-3 py-2 text-sm"
                    />
                    <div className="flex gap-2">
                      {["dsa_build", "video"].map((k) => (
                        <button
                          key={k}
                          type="button"
                          onClick={() => setKind(k)}
                          className={cn(
                            "rounded-xl border px-3 py-1.5 text-xs font-semibold",
                            kind === k ? "border-gold/50 bg-accent/40 text-ink" : "border-ink/10 text-ink-soft"
                          )}
                        >
                          {k === "dsa_build" ? "DSA & interviews" : "Video roadmap"}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="mt-5 flex items-center gap-3">
                    <button type="button" onClick={() => setStep(3)} className="text-sm text-ink-faint hover:underline">
                      ← Back
                    </button>
                    <button
                      type="button"
                      onClick={build}
                      disabled={building || (quota?.remaining ?? 1) <= 0}
                      className="btn btn-quest px-6 py-2.5 disabled:opacity-40"
                    >
                      {building ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                      Build my roadmap
                    </button>
                  </div>
                  {(quota?.remaining ?? 1) <= 0 && (
                    <p className="mt-2 text-sm text-rust">
                      You&apos;ve used your 2 builds this week — join a friend&apos;s roadmap below instead.
                    </p>
                  )}
                </div>
              )}
            </section>
          ) : (
            <section className="panel p-6">
              <h2 className="flex items-center gap-2 font-display text-lg font-bold text-ink">
                <Users size={18} /> Following a friend? Join their roadmap
              </h2>
              <p className="mt-1 text-sm text-ink-soft">
                Paste the six-character code they sent you — you&apos;ll both tick your own boxes
                and can see how the other is getting on.
              </p>
              <div className="mt-4 flex gap-2">
                <input
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 6))}
                  placeholder="ABC123"
                  className="field max-w-48 text-center font-mono text-lg font-bold tracking-[0.3em]"
                />
                <button
                  type="button"
                  onClick={join}
                  disabled={code.trim().length !== 6 || joining}
                  className="btn btn-ink px-6 py-2.5 disabled:opacity-40"
                >
                  {joining ? <Loader2 size={16} className="animate-spin" /> : <>Join <ArrowRight size={16} /></>}
                </button>
              </div>
            </section>
          )}

          {mine.length > 0 && (
            <section className="mt-8">
              <h2 className="font-display text-lg font-bold text-ink">Your roadmaps</h2>
              <ul className="mt-3 space-y-2">
                {mine.map((r) => (
                  <li key={r.id}>
                    <Link
                      href={`/roadmap/custom/${r.id}`}
                      className="panel panel-hover flex items-center gap-3 px-5 py-3.5"
                    >
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-ink/10 bg-paper-deep text-ink-faint">
                        {r.me_done === r.total && r.total > 0 ? <Check size={15} className="text-quest" /> : <Users size={14} />}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate font-display font-semibold text-ink">{r.title}</span>
                        <span className="font-mono text-xs text-ink-faint">
                          {r.me_done}/{r.total} · {r.share_code}
                          {r.friend_done != null && ` · friend ${r.friend_done}/${r.total}`}
                        </span>
                      </span>
                      <ArrowRight size={15} className="text-ink-faint" />
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
