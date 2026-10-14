"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Check, Loader2, Users } from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { CustomRoadmap } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function DetailClient() {
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : (params.id as string);
  const { user } = useAuth();
  const [roadmap, setRoadmap] = useState<CustomRoadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [todayOnly, setTodayOnly] = useState(true);

  useEffect(() => {
    let cancelled = false;
    client
      .get<CustomRoadmap>(`/roadmaps/custom/${id}${todayOnly ? "/today" : ""}`)
      .then((res) => {
        if (cancelled) return;
        if (!todayOnly) {
          setRoadmap(res.data);
          setLoading(false);
          return;
        }
        // /today trims steps but keeps totals; fetch full for the header counts.
        client
          .get<CustomRoadmap>(`/roadmaps/custom/${id}`)
          .then((full) => {
            if (cancelled) return;
            setRoadmap({ ...full.data, steps: res.data.steps });
            setLoading(false);
          })
          .catch(() => {
            if (!cancelled) {
              setRoadmap(null);
              setLoading(false);
            }
          });
      })
      .catch(() => {
        if (!cancelled) {
          setRoadmap(null);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id, todayOnly]);

  const toggle = async (stepId: string, done: boolean) => {
    setRoadmap((prev) =>
      prev
        ? {
            ...prev,
            steps: prev.steps.map((s) => (s.id === stepId ? { ...s, done: !done } : s)),
            me_done: prev.me_done + (!done ? 1 : -1),
          }
        : prev
    );
    try {
      if (done) {
        await client.delete(`/roadmaps/custom/${id}/ticks/${stepId}`);
      } else {
        await client.post(`/roadmaps/custom/${id}/ticks/${stepId}`);
      }
    } catch {
      client
        .get<CustomRoadmap>(`/roadmaps/custom/${id}`)
        .then((res) => setRoadmap(res.data))
        .catch(() => {});
    }
  };

  const groups = useMemo(() => {
    const map = new Map<number, NonNullable<typeof roadmap>["steps"]>();
    (roadmap?.steps ?? []).forEach((s) => {
      const arr = map.get(s.day_index) ?? [];
      arr.push(s);
      map.set(s.day_index, arr);
    });
    return [...map.entries()].sort((a, b) => a[0] - b[0]);
  }, [roadmap]);

  const pct = roadmap?.total ? Math.round((roadmap.me_done / roadmap.total) * 100) : 0;

  return (
    <ProtectedRoute>
      <div className="atlas-bg min-h-screen">
        <TopBar active="roadmap">{user && <UserChip username={user.username} />}</TopBar>
        <main className="mx-auto w-full max-w-4xl px-6 pb-16 pt-10">
          <Link href="/roadmap/custom" className="flex items-center gap-1.5 text-sm text-ink-faint hover:text-ink">
            <ArrowLeft size={15} /> All roadmaps
          </Link>
          {loading ? (
            <p className="flex items-center gap-2 py-16 text-sm text-ink-faint">
              <Loader2 size={16} className="animate-spin" /> Loading your list…
            </p>
          ) : !roadmap ? (
            <p className="py-16 text-center text-ink-soft">Roadmap not found.</p>
          ) : (
            <>
              <div className="mt-2 flex flex-wrap items-end gap-4">
                <div>
                  <h1 className="font-display text-3xl font-bold text-ink">{roadmap.title}</h1>
                  <p className="mt-1 font-mono text-xs text-ink-faint">
                    {roadmap.me_done}/{roadmap.total} done · share code{" "}
                    <span className="font-bold tracking-[0.2em]">{roadmap.share_code}</span>
                    {roadmap.friend_done != null && (
                      <span className="ml-2 inline-flex items-center gap-1">
                        <Users size={12} /> friend {roadmap.friend_done}/{roadmap.total}
                      </span>
                    )}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setTodayOnly((v) => !v)}
                  className="ml-auto rounded-xl border border-ink/10 bg-card px-4 py-2 text-sm font-semibold text-ink-soft"
                >
                  {todayOnly ? "Show full plan" : "Show today's list"}
                </button>
              </div>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-ink/10">
                <div className="h-full rounded-full bg-quest transition-[width] duration-500" style={{ width: `${pct}%` }} />
              </div>

              {groups.map(([day, steps]) => (
                <section key={day} className="panel mt-5 overflow-hidden">
                  <header className="border-b border-ink/8 px-5 py-3 font-display text-sm font-bold uppercase tracking-wider text-ink">
                    Day {day}
                  </header>
                  <ul className="divide-y divide-ink/8">
                    {steps.map((s) => (
                      <li key={s.id} className="flex items-center gap-3 px-5 py-3">
                        <button
                          type="button"
                          aria-label={s.done ? "Untick" : "Tick done"}
                          onClick={() => toggle(s.id, s.done)}
                          className={cn(
                            "flex h-6 w-6 shrink-0 scale-100 items-center justify-center rounded-full border-[1.5px] transition-transform active:scale-90",
                            s.done ? "border-quest bg-quest/10 text-quest" : "border-ink/20 text-transparent hover:border-quest"
                          )}
                        >
                          <Check size={13} strokeWidth={4} />
                        </button>
                        {s.problem_slug ? (
                          <Link
                            href={`/problems/${s.problem_slug}/solve`}
                            className={cn(
                              "flex-1 truncate text-sm",
                              s.done ? "text-ink-faint line-through" : "text-ink hover:underline"
                            )}
                          >
                            {s.title}
                          </Link>
                        ) : (
                          <span className={cn("flex-1 truncate text-sm", s.done && "line-through text-ink-faint")}>
                            {s.title}
                          </span>
                        )}
                        <span className="font-mono text-[11px] uppercase text-ink-faint">
                          {s.difficulty} · {s.est_mins}m
                        </span>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
