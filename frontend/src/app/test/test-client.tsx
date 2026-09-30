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

  useEffect(() => {
    let cancelled = false;
    client
      .get<TestConfigOut>("/tests/config")
      .then((res) => {
        if (cancelled) return;
        setConfig(res.data);
        setSelected(res.data.topics.map((t) => t.topic));
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

  const duration = config?.default_duration_seconds ?? 3600;
  const minutes = Math.round(duration / 60);

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
        duration_seconds: duration,
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
              The test is {minutes} minutes. Submit each question before the
              timer runs out for it to be graded.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border border-ink/10 bg-card px-4 py-3 shadow-card">
            <Timer size={18} className="shrink-0 text-gold" />
            <div>
              <p className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-ink-faint">
                Duration
              </p>
              <p className="font-mono text-lg font-bold text-ink">
                {formatClock(duration)}
              </p>
            </div>
          </div>
        </div>

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
