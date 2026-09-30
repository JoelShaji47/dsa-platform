"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

const POLL_MS = 3000;
const SHOW_AFTER_MS = 800;
const GIVE_UP_MS = 90000;

async function pingBackend(): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 8000);
    // /auth/me without a token answers 401 when the server is awake.
    // Anything 5xx (dead proxy, cold backend) or no response at all
    // means it is still waking.
    const res = await fetch("/api/v1/auth/me", {
      signal: ctrl.signal,
      cache: "no-store",
    });
    clearTimeout(timer);
    return res.status < 500;
  } catch {
    return false;
  }
}

function PulsatingDots() {
  return (
    <div className="flex items-center justify-center" aria-hidden>
      <div className="flex space-x-2">
        <span className="wake-dot h-3 w-3 rounded-full bg-gold" />
        <span className="wake-dot h-3 w-3 rounded-full bg-gold" />
        <span className="wake-dot h-3 w-3 rounded-full bg-gold" />
      </div>
    </div>
  );
}

/** Blocks the whole site behind a wake-up gate: polls the backend until
 *  it acks, then mounts the app once. Children (auth included) never
 *  mount against a sleeping server, so there is no 401 noise or bounce
 *  to /login during Render cold starts. */
export default function ServerWakeGate({ children }: { children: ReactNode }) {
  const [acked, setAcked] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [waitedSecs, setWaitedSecs] = useState(0);
  const [retrying, setRetrying] = useState(false);
  const startedAt = useRef(Date.now());

  useEffect(() => {
    let cancelled = false;
    let interval = 0;
    const showTimer = window.setTimeout(() => {
      if (!cancelled) setShowOverlay(true);
    }, SHOW_AFTER_MS);
    const tick = window.setInterval(() => {
      if (!cancelled) setWaitedSecs(Math.floor((Date.now() - startedAt.current) / 1000));
    }, 1000);

    const check = async () => {
      if (cancelled) return;
      if (await pingBackend()) {
        if (cancelled) return;
        window.clearInterval(interval);
        window.clearInterval(tick);
        window.clearTimeout(showTimer);
        setAcked(true);
      }
    };
    void check();
    interval = window.setInterval(check, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
      window.clearInterval(tick);
      window.clearTimeout(showTimer);
    };
  }, []);

  const retryNow = () => {
    setRetrying(true);
    window.location.reload();
  };

  if (acked) return <>{children}</>;
  if (!showOverlay) return null;

  const givenUp = waitedSecs * 1000 >= GIVE_UP_MS;

  return (
    <div
      role="status"
      aria-live="polite"
      className="atlas-bg fixed inset-0 z-[100] flex min-h-[100dvh] flex-col items-center justify-center gap-5 px-6 text-center"
    >
      <p className="font-display text-[1.05rem] font-bold uppercase tracking-[0.12em]">
        Code<span className="text-gold">Quest</span>
      </p>
      <PulsatingDots />
      <div>
        <p className="font-display text-xl font-bold text-ink">
          {givenUp ? "The server is taking a while" : "Waking up the server…"}
        </p>
        <p className="mx-auto mt-1 max-w-sm text-sm text-ink-soft">
          {givenUp
            ? `No answer after ${waitedSecs}s. The free tier can sleep deeply — retry to knock again.`
            : "Cold starts take ~30–60s on the free tier. Your quest resumes on its own."}
        </p>
        <p className="mt-2 font-mono text-xs text-ink-faint">{waitedSecs}s elapsed</p>
      </div>
      {givenUp && (
        <button
          type="button"
          onClick={retryNow}
          disabled={retrying}
          className="btn btn-ink px-5 py-2.5 text-sm"
        >
          {retrying ? "Retrying…" : "Retry now"}
        </button>
      )}
    </div>
  );
}
