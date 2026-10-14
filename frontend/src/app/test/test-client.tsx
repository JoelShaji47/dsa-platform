"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Camera,
  Check,
  Loader2,
  ShieldAlert,
  Sparkles,
  Timer,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import {
  acquireCamera,
  getCameraStream,
  requestTestFullscreen,
} from "@/components/arena/proctoring";
import client from "@/lib/api";
import type { TestConfigOut, TestSession } from "@/lib/types";
import {
  errDetail,
  formatClock,
  topicLabel,
} from "@/components/arena/status-styles";

type CameraState = "idle" | "requesting" | "on" | "error";

export default function TestSetupClient() {
  return (
    <ProtectedRoute>
      <TestSetupScreen />
    </ProtectedRoute>
  );
}

function TestSetupScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [config, setConfig] = useState<TestConfigOut | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [cameraState, setCameraState] = useState<CameraState>("idle");
  const [cameraError, setCameraError] = useState<string | null>(null);
  // Custom timer + custom questions (one by one, both optional).
  const [duration, setDuration] = useState<number | null>(null);
  const [numQuestions, setNumQuestions] = useState(3);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<{ slug: string; title: string; difficulty: string }[]>([]);
  const [searching, setSearching] = useState(false);
  const [pickedSlugs, setPickedSlugs] = useState<{ slug: string; title: string }[]>([]);

  useEffect(() => {
    let cancelled = false;
    client
      .get<TestConfigOut>("/tests/config")
      .then((res) => {
        if (cancelled) return;
        setConfig(res.data);
        setSelected(res.data.topics.map((t) => t.topic));
        setDuration((prev) => prev ?? res.data.default_duration_seconds);
      })
      .catch((err) => {
        if (cancelled) return;
        if ((err as { response?: { status?: number } })?.response?.status === 401) {
          localStorage.removeItem("token");
          router.replace("/login");
          return;
        }
        setError(errDetail(err));
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  const reload = useCallback(async () => {
    setError(null);
    try {
      const res = await client.get<TestConfigOut>("/tests/config");
      setConfig(res.data);
      setSelected(res.data.topics.map((t) => t.topic));
    } catch (err) {
      setError(errDetail(err));
    }
  }, []);

  const toggle = (topic: string) =>
    setSelected((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );

  const allTopics = useMemo(
    () => (config ? config.topics.map((t) => t.topic) : []),
    [config]
  );
  const allSelected = allTopics.length > 0 && selected.length === allTopics.length;

  const durationOptions = config?.duration_options_seconds ?? [900, 1800, 2700, 3600, 5400, 7200];
  const maxQuestions = config?.max_questions ?? 6;
  const effectiveDuration = duration ?? config?.default_duration_seconds ?? 3600;
  const minutes = Math.round(effectiveDuration / 60);

  // Debounced problem search for the custom-question picker. Clearing happens
  // in the input's onChange (below), so this effect never sets state directly.
  useEffect(() => {
    const term = query.trim();
    if (term.length < 2) return;
    let cancelled = false;
    const id = setTimeout(() => {
      client
        .get("/problems", { params: { search: term } })
        .then((res) => {
          if (cancelled) return;
          setSearchResults(
            (res.data ?? []).slice(0, 8).map((p: { slug: string; title: string; difficulty: string }) => ({
              slug: p.slug,
              title: p.title,
              difficulty: p.difficulty,
            }))
          );
        })
        .catch(() => {
          if (!cancelled) setSearchResults([]);
        })
        .finally(() => {
          if (!cancelled) setSearching(false);
        });
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(id);
    };
  }, [query]);

  const onQueryChange = (value: string) => {
    setQuery(value);
    if (value.trim().length < 2) {
      setSearchResults([]);
      setSearching(false);
    } else {
      setSearching(true);
    }
  };

  const enableCamera = async () => {
    if (cameraState === "requesting") return;
    setCameraState("requesting");
    setCameraError(null);
    try {
      await acquireCamera();
      setCameraState("on");
    } catch (err) {
      const name = (err as DOMException)?.name;
      if (name === "NotAllowedError") {
        setCameraError(
          "Camera permission is required to start a proctored test. Allow camera access in your browser and retry."
        );
      } else if (name === "NotFoundError") {
        setCameraError("No camera was detected on this device.");
      } else {
        setCameraError(
          "Could not access the camera. Check your browser permissions."
        );
      }
      setCameraState("error");
    }
  };

  const start = async () => {
    if (!selected.length || starting || cameraState !== "on") return;
    setStarting(true);
    setError(null);
    try {
      await requestTestFullscreen();
    } catch (err) {
      setError(
        `Fullscreen is required for the proctored test. ${
          err instanceof Error ? err.message : "Enable fullscreen and retry."
        }`
      );
      setStarting(false);
      return;
    }
    try {
      const res = await client.post<TestSession>("/tests", {
        topics: selected,
        duration_seconds: effectiveDuration,
        ...(pickedSlugs.length > 0
          ? { problem_slugs: pickedSlugs.map((p) => p.slug) }
          : { num_questions: numQuestions }),
      });
      router.push(`/test/${res.data.id}`);
    } catch (err) {
      setError(errDetail(err));
      setStarting(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper">
      <TopBar active="test">
        {user && <UserChip username={user.username} />}
      </TopBar>

      <main className="mx-auto max-w-5xl px-5 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-gold">
              Mock interview
            </p>
            <h1 className="mt-2 font-display text-4xl font-bold tracking-tight text-ink">
              Take a Test
            </h1>
            <p className="mt-2 max-w-xl text-ink-soft">
              The test is {minutes} minutes
              {pickedSlugs.length > 0
                ? ` with ${pickedSlugs.length} hand-picked question${pickedSlugs.length > 1 ? "s" : ""}`
                : ` with ${numQuestions} question${numQuestions > 1 ? "s" : ""}`}
              . Submit each question before the timer runs out for it to be graded.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border border-ink/10 bg-card px-4 py-3 shadow-card">
            <Timer size={18} className="shrink-0 text-gold" />
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Duration
              </p>
              <p className="font-mono text-lg font-bold text-ink">
                {formatClock(effectiveDuration)}
              </p>
            </div>
          </div>
        </div>

        <section className="mt-6 rounded-2xl border border-ink/10 bg-card p-6 shadow-card">
          <h2 className="font-display text-lg font-bold text-ink">Custom timer</h2>
          <p className="mt-1 text-sm text-ink-soft">
            Step 1 — pick how long you want. The countdown is enforced server-side.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {durationOptions.map((s) => {
              const on = effectiveDuration === s;
              return (
                <button
                  key={s}
                  type="button"
                  onClick={() => setDuration(s)}
                  aria-pressed={on}
                  className={`rounded-xl border px-4 py-2 font-mono text-sm font-bold transition-all ${
                    on
                      ? "border-gold/50 bg-accent/40 text-ink shadow-glow"
                      : "border-ink/10 bg-paper/60 text-ink-soft hover:border-ink/25"
                  }`}
                >
                  {Math.round(s / 60)}m
                </button>
              );
            })}
          </div>
        </section>

        <section className="mt-6 rounded-2xl border border-ink/10 bg-card p-6 shadow-card">
          <h2 className="font-display text-lg font-bold text-ink">Custom questions</h2>
          <p className="mt-1 text-sm text-ink-soft">
            Step 2 — how many questions (1–{maxQuestions}, balanced E/M/H), or hand-pick
            exact problems below. Hand-picked wins when both are set.
          </p>
          <div className="mt-4 flex items-center gap-3">
            <button
              type="button"
              onClick={() => setNumQuestions((n) => Math.max(1, n - 1))}
              disabled={numQuestions <= 1}
              className="rounded-lg border border-ink/15 px-3 py-1.5 font-mono font-bold text-ink disabled:opacity-40"
              aria-label="Fewer questions"
            >
              −
            </button>
            <span className="font-mono text-lg font-bold text-ink">
              {pickedSlugs.length > 0 ? pickedSlugs.length : numQuestions} question{(pickedSlugs.length > 0 ? pickedSlugs.length : numQuestions) > 1 ? "s" : ""}
            </span>
            <button
              type="button"
              onClick={() => setNumQuestions((n) => Math.min(maxQuestions, n + 1))}
              disabled={numQuestions >= maxQuestions}
              className="rounded-lg border border-ink/15 px-3 py-1.5 font-mono font-bold text-ink disabled:opacity-40"
              aria-label="More questions"
            >
              +
            </button>
            {pickedSlugs.length > 0 && (
              <button
                type="button"
                onClick={() => setPickedSlugs([])}
                className="ml-2 text-sm font-semibold text-rust hover:underline"
              >
                Clear hand-picked
              </button>
            )}
          </div>

          <div className="mt-4">
            <input
              value={query}
              onChange={(e) => onQueryChange(e.target.value)}
              placeholder="Type to search problems (min 2 letters)…"
              className="w-full rounded-xl border border-ink/15 bg-paper/60 px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint"
            />
            {searching && <p className="mt-2 text-xs text-ink-faint">Searching…</p>}
            {searchResults.length > 0 && (
              <ul className="mt-2 divide-y divide-ink/8 overflow-hidden rounded-xl border border-ink/10">
                {searchResults.map((r) => {
                  const picked = pickedSlugs.some((p) => p.slug === r.slug);
                  const full = pickedSlugs.length >= maxQuestions;
                  return (
                    <li key={r.slug}>
                      <button
                        type="button"
                        disabled={(full && !picked) || picked}
                        onClick={() => {
                          if (pickedSlugs.length < maxQuestions) {
                            setPickedSlugs((prev) => [...prev, { slug: r.slug, title: r.title }]);
                            onQueryChange("");
                          }
                        }}
                        className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm hover:bg-paper/60 disabled:opacity-40"
                      >
                        <span className="min-w-0 flex-1 truncate text-ink">{r.title}</span>
                        <span className="font-mono text-[11px] uppercase text-ink-faint">{r.difficulty}</span>
                        <span className="font-mono text-[11px] text-gold">{picked ? "added" : "add"}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
            {pickedSlugs.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {pickedSlugs.map((p, i) => (
                  <span
                    key={p.slug}
                    className="flex items-center gap-2 rounded-full border border-gold/40 bg-accent/40 px-3 py-1 text-xs font-semibold text-ink"
                  >
                    {i + 1}. {p.title}
                    <button
                      type="button"
                      aria-label={`Remove ${p.title}`}
                      onClick={() => setPickedSlugs((prev) => prev.filter((x) => x.slug !== p.slug))}
                      className="font-mono text-rust hover:underline"
                    >
                      ✕
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>

        {error && (
          <div className="mt-6 flex items-center justify-between gap-4 rounded-2xl border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust">
            <span className="min-w-0 break-words">{error}</span>
            <button
              type="button"
              onClick={reload}
              className="shrink-0 whitespace-nowrap rounded-lg border border-rust/30 px-3 py-1 font-semibold leading-5 transition-colors hover:bg-rust/15"
            >
              Retry
            </button>
          </div>
        )}

        <section className="mt-8 rounded-2xl border border-ink/10 bg-card p-6 shadow-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">
                Topic focus
              </h2>
              <p className="mt-1 text-sm text-ink-soft">
                Pick the areas you want to be tested on.
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setSelected(allTopics)}
                disabled={allSelected}
                className="whitespace-nowrap rounded-lg border border-ink/15 px-3 py-1.5 text-sm font-medium leading-5 text-ink-soft transition-colors hover:border-ink/30 hover:text-ink disabled:opacity-40"
              >
                Select all
              </button>
              <button
                type="button"
                onClick={() => setSelected([])}
                disabled={selected.length === 0}
                className="whitespace-nowrap rounded-lg border border-ink/15 px-3 py-1.5 text-sm font-medium leading-5 text-ink-soft transition-colors hover:border-ink/30 hover:text-ink disabled:opacity-40"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="mt-5 grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
            {(config?.topics ?? []).map((t) => {
              const on = selected.includes(t.topic);
              return (
                <button
                  key={t.topic}
                  type="button"
                  onClick={() => toggle(t.topic)}
                  aria-pressed={on}
                  className={`flex items-center justify-between gap-3 rounded-xl border px-4 py-3 text-left transition-all ${
                    on
                      ? "border-gold/50 bg-accent/40 shadow-glow"
                      : "border-ink/10 bg-paper/60 hover:border-ink/25"
                  }`}
                >
                  <span
                    className={`truncate font-medium ${on ? "text-ink" : "text-ink-soft"}`}
                  >
                    {topicLabel(t.topic)}
                  </span>
                  {on && <Check size={16} className="shrink-0 text-gold" />}
                </button>
              );
            })}
          </div>

          {!config && !error && (
            <div className="flex items-center justify-center gap-2 py-10 text-sm text-ink-faint">
              <Loader2 size={16} className="animate-spin" />
              Loading available topics
            </div>
          )}

          <CoverageNote selectedCount={selected.length} />
        </section>

        <section className="mt-6 rounded-2xl border border-ink/10 bg-card p-6 shadow-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="flex items-center gap-2 font-display text-lg font-bold text-ink">
                <ShieldAlert size={18} className="text-rust" />
                Proctored test
              </h2>
              <p className="mt-1 text-sm text-ink-soft">
                The test runs in fullscreen. Leaving the window, switching tabs,
                or exiting fullscreen counts as a violation. Three violations
                and the test auto-submits. Copy, paste and right-click stay
                locked for the session, and your camera stays on the whole time.
              </p>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-4">
            {cameraState === "on" ? (
              <div className="flex items-center gap-3">
                <CameraPreview />
                <div>
                  <p className="flex items-center gap-1.5 text-sm font-semibold text-ink">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    Camera on
                  </p>
                  <p className="mt-0.5 text-xs text-ink-soft">
                    Three violations auto-submit your test, so stay in fullscreen
                    until you finish.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={enableCamera}
                  disabled={cameraState === "requesting"}
                  className="flex items-center gap-2 whitespace-nowrap rounded-xl border border-ink/15 bg-paper/60 px-4 py-2.5 text-sm font-semibold leading-5 text-ink transition-colors hover:border-ink/30 disabled:opacity-50"
                >
                  {cameraState === "requesting" ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Camera size={16} />
                  )}
                  {cameraState === "requesting" ? "Requesting camera" : "Enable camera"}
                </button>
                <p className="max-w-xs text-sm text-ink-soft">
                  The test cannot start until your camera is allowed.
                </p>
              </div>
            )}

            {cameraError && (
              <p className="w-full rounded-xl border border-rust/30 bg-rust/10 px-4 py-2.5 text-sm text-rust">
                {cameraError}
              </p>
            )}
          </div>
        </section>

        <div className="mt-6 flex justify-end rounded-2xl border border-ink/10 bg-card px-6 py-4 shadow-card">
          <div className="flex w-full flex-col items-end gap-2">
            {cameraState !== "on" && (
              <p className="text-xs text-ink-faint">
                Enable your camera to start the test.
              </p>
            )}
            <button
              type="button"
              onClick={start}
              disabled={
                selected.length === 0 || starting || !config || cameraState !== "on"
              }
              className="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-xl bg-primary px-6 py-3 font-semibold leading-6 text-primary-foreground transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {starting ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Sparkles size={16} />
              )}
              {starting ? "Starting" : "Start test"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

function CameraPreview() {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    const stream = getCameraStream();
    if (!video || !stream) return;
    video.srcObject = stream;
    void video.play().catch(() => undefined);
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="h-28 w-36 -scale-x-100 rounded-lg border border-ink/10 bg-black object-cover shadow-card"
    />
  );
}

function CoverageNote({ selectedCount }: { selectedCount: number }) {
  if (selectedCount === 0) {
    return (
      <p className="mt-5 rounded-xl border border-ink/10 bg-paper/70 px-4 py-3 text-sm text-ink-soft">
        Select at least one topic.
      </p>
    );
  }
  return (
    <p className="mt-5 rounded-xl border border-ink/10 bg-paper/70 px-4 py-3 text-sm text-ink-soft">
      {selectedCount} topic{selectedCount > 1 ? "s" : ""} selected.
    </p>
  );
}
