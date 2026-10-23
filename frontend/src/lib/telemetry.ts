// Privacy-conscious recommendation telemetry (Phase B frontend wiring).
//
// Sends only ids, ranks, versions and counters — never source code,
// keystrokes, secrets or personal data. Every call is fire-and-forget:
// telemetry failures are swallowed so analytics can never break the UI.

import { useEffect, useRef } from "react";
import client from "@/lib/api";

export type ImpressionItem = {
  slug: string;
  rank: number;
  source?: string;
  rendered?: boolean;
};

/** Report actually-rendered recommendations for one opportunity. */
export function logImpressions(
  opportunityId: string,
  items: ImpressionItem[]
): void {
  if (!opportunityId || items.length === 0) return;
  client
    .post("/roadmap/impressions", {
      opportunity_id: opportunityId,
      items: items.map((i) => ({
        slug: i.slug,
        rank: i.rank,
        source: i.source ?? "roadmap",
        rendered: i.rendered ?? true,
      })),
    })
    .catch(() => {});
}

function newClientSessionId(): string {
  try {
    return crypto.randomUUID();
  } catch {
    return `sess-${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
  }
}

/**
 * Solve-session lifecycle for the solve page: start on mount, heartbeat
 * every 60s while the tab is visible, finish on unmount.
 *
 * The finish ping uses fetch with keepalive so it survives page unload;
 * everything else goes through the shared axios client. Never throws.
 */
export function useSolveSession(slug: string | undefined): void {
  const sessionId = useRef<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;
    const clientSessionId = newClientSessionId();

    client
      .post<{ session: { id: string } }>("/roadmap/sessions", {
        problem_slug: slug,
        client_session_id: clientSessionId,
      })
      .then((res) => {
        if (cancelled) return;
        sessionId.current = res.data?.session?.id ?? null;
        timer = setInterval(() => {
          if (document.visibilityState !== "visible") return;
          const id = sessionId.current;
          if (!id) return;
          client.post(`/roadmap/sessions/${id}/heartbeat`).catch(() => {});
        }, 60000);
      })
      .catch(() => {});

    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
      const id = sessionId.current;
      sessionId.current = null;
      if (!id) return;
      try {
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("token")
            : null;
        fetch(`/api/v1/roadmap/sessions/${id}/finish`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({}),
          keepalive: true,
        }).catch(() => {});
      } catch {
        // never break unload
      }
    };
  }, [slug]);
}
