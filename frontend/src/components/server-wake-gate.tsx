"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Compass, Database, Server, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const POLL_MS = 3000;
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

const TIPS = [
  "Cold starts take ~30–60s on the free tier.",
  "Your progress, streaks and XP are safe while we wake things up.",
  "Judge0 warms up right after the API answers.",
];

function BootStep({
  icon,
  label,
  detail,
  state,
}: {
  icon: ReactNode;
  label: string;
  detail: string;
  state: "done" | "active" | "pending";
}) {
  return (
    <li className="flex items-center gap-3">
      <span
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition-colors",
          state === "done" &&
            "border-quest/40 bg-quest/10 text-quest",
          state === "active" &&
            "border-gold/50 bg-gold/10 text-gold-deep shadow-glow-sm",
          state === "pending" && "border-ink/10 text-ink-faint"
        )}
      >
        {icon}
      </span>
      <span className="min-w-0 text-left">
        <span
          className={cn(
            "block text-sm font-semibold",
            state === "pending" ? "text-ink-faint" : "text-ink"
          )}
        >
          {label}
        </span>
        <span className="block truncate text-xs text-ink-soft">{detail}</span>
      </span>
      <span className="ml-auto flex shrink-0 items-center" aria-hidden>
        {state === "active" ? (
          <span className="flex space-x-1">
            <span className="wake-dot h-1.5 w-1.5 rounded-full bg-gold" />
            <span className="wake-dot h-1.5 w-1.5 rounded-full bg-gold" />
            <span className="wake-dot h-1.5 w-1.5 rounded-full bg-gold" />
          </span>
        ) : state === "done" ? (
          <svg
            viewBox="0 0 24 24"
            className="h-4 w-4 text-quest"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
          >
            <path
              d="M5 13l4 4L19 7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          <span className="h-1.5 w-1.5 rounded-full bg-ink/15" />
        )}
      </span>
    </li>
  );
}

/** Blocks the whole site behind a wake-up gate: polls the backend until
 *  it acks, then mounts the app once. Children (auth included) never
 *  mount against a sleeping server, so there is no 401 noise, no bounce
 *  to /login, and no 502s during Render cold starts. Renders a full
 *  initialising scene immediately — no blank flash. */
export default function ServerWakeGate({ children }: { children: ReactNode }) {
  const [acked, setAcked] = useState(false);
  const [waitedSecs, setWaitedSecs] = useState(0);
  const [retrying, setRetrying] = useState(false);
  const startedAt = useRef(Date.now());

  useEffect(() => {
    let cancelled = false;
    let interval = 0;
    const tick = window.setInterval(() => {
      if (!cancelled)
        setWaitedSecs(Math.floor((Date.now() - startedAt.current) / 1000));
    }, 1000);

    const check = async () => {
      if (cancelled) return;
      if (await pingBackend()) {
        if (cancelled) return;
        window.clearInterval(interval);
        window.clearInterval(tick);
        setAcked(true);
      }
    };
    void check();
    interval = window.setInterval(check, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
      window.clearInterval(tick);
    };
  }, []);

  const retryNow = () => {
    setRetrying(true);
    window.location.reload();
  };

  if (acked) return <>{children}</>;

  const givenUp = waitedSecs * 1000 >= GIVE_UP_MS;
  // Staged boot checklist driven by elapsed time, so the scene feels alive
  // while the proxy keeps returning 5xx.
  const stage = waitedSecs < 8 ? 0 : waitedSecs < 25 ? 1 : 2;
  const tip = TIPS[Math.floor(waitedSecs / 6) % TIPS.length];

  return (
    <div
      role="status"
      aria-live="polite"
      className="atlas-bg fixed inset-0 z-[100] flex min-h-[100dvh] flex-col items-center justify-center gap-6 overflow-y-auto px-6 py-10 text-center"
    >
      <div className="wake-rise flex flex-col items-center gap-6">
        <div className="relative flex h-20 w-20 items-center justify-center text-gold">
          <span
            className="animate-ping-slow absolute inset-0 rounded-2xl border border-gold/50"
            aria-hidden
          />
          <span
            className="absolute inset-0 rounded-2xl bg-ink shadow-lift"
            aria-hidden
          />
          <Compass size={32} strokeWidth={2.25} className="relative" aria-hidden />
        </div>

        <div>
          <p className="font-display text-[0.7rem] font-bold uppercase tracking-[0.28em] text-gold-deep">
            Initialising
          </p>
          <p className="mt-1 font-display text-[1.05rem] font-bold uppercase tracking-[0.12em] text-ink">
            Code<span className="text-gold">Quest</span>
          </p>
        </div>

        <div className="panel w-full max-w-sm p-5 text-left sm:p-6">
          <p className="font-display text-lg font-bold text-ink">
            {givenUp ? "The server is taking a while" : "Waking up the server…"}
          </p>
          <p className="mt-1 text-sm text-ink-soft">
            {givenUp
              ? `No answer after ${waitedSecs}s. The free tier can sleep deeply — retry to knock again.`
              : "Hold tight while the backend, database and judge come online. This page clears on its own."}
          </p>

          <div
            className="mt-4 h-1.5 overflow-hidden rounded-full bg-ink/10"
            aria-hidden
          >
            <div className="wake-bar h-full w-1/3 rounded-full bg-gold" />
          </div>

          <ul className="mt-5 space-y-3.5">
            <BootStep
              icon={<Server size={16} />}
              label="API server"
              detail="Contacting…"
              state="active"
            />
            <BootStep
              icon={<Database size={16} />}
              label="Database & session"
              detail={stage >= 1 ? "Warming…" : "Queued after API"}
              state={stage >= 1 ? "active" : "pending"}
            />
            <BootStep
              icon={<Sparkles size={16} />}
              label="Judge & AI tutor"
              detail={stage === 2 ? "Warming…" : "Queued after database"}
              state={stage === 2 ? "active" : "pending"}
            />
          </ul>

          <div className="mt-5 flex items-start justify-between gap-4 border-t border-ink/8 pt-3">
            <p className="shrink-0 font-mono text-xs text-ink-faint">
              {waitedSecs}s elapsed
            </p>
            {givenUp ? (
              <button
                type="button"
                onClick={retryNow}
                disabled={retrying}
                className="btn btn-ink px-4 py-2 text-sm"
              >
                {retrying ? "Retrying…" : "Retry now"}
              </button>
            ) : (
              <p className="text-right text-xs leading-snug text-ink-faint">
                {tip}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
