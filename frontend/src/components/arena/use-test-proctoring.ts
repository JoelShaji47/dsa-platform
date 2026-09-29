"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import client from "@/lib/api";
import type { TestSession } from "@/lib/types";
import { VIOLATION_LIMIT } from "./proctoring";

const DEDUPE_MS = 2000;

export function useTestProctoring({
  sessionId,
  enabled,
  onAutoSubmit,
}: {
  sessionId: string;
  enabled: boolean;
  onAutoSubmit: (session: TestSession) => void;
}) {
  const [violations, setViolations] = useState(0);
  const reporting = useRef(false);
  const lastViolationAt = useRef(0);
  const onAutoSubmitRef = useRef(onAutoSubmit);
  onAutoSubmitRef.current = onAutoSubmit;

  const report = useCallback(async () => {
    if (reporting.current) return;
    reporting.current = true;
    try {
      const res = await client.post<TestSession>(
        `/tests/${sessionId}/violations`
      );
      setViolations(res.data.violations);
      if (res.data.status !== "IN_PROGRESS") {
        onAutoSubmitRef.current(res.data);
      }
    } catch {
      // Offline or already finalized; the poller redirects once it sees it.
    } finally {
      reporting.current = false;
    }
  }, [sessionId]);

  useEffect(() => {
    if (!enabled) return;

    const strike = () => {
      const now = Date.now();
      if (now - lastViolationAt.current < DEDUPE_MS) return;
      lastViolationAt.current = now;
      void report();
    };

    const onVisibility = () => {
      if (document.visibilityState === "hidden") strike();
    };

    const onFullscreen = () => {
      const doc = document as Document & {
        webkitFullscreenElement?: Element | null;
      };
      if (!document.fullscreenElement && !doc.webkitFullscreenElement) strike();
    };

    const onBlur = () => strike();

    const block = (event: Event) => event.preventDefault();

    const onKeyDown = (event: KeyboardEvent) => {
      if (
        (event.ctrlKey || event.metaKey) &&
        ["c", "x", "v"].includes(event.key.toLowerCase())
      ) {
        event.preventDefault();
      }
    };

    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFullscreen);
    document.addEventListener("webkitfullscreenchange", onFullscreen);
    window.addEventListener("blur", onBlur);
    window.addEventListener("keydown", onKeyDown, true);
    document.addEventListener("copy", block, true);
    document.addEventListener("cut", block, true);
    document.addEventListener("paste", block, true);
    document.addEventListener("contextmenu", block, true);

    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFullscreen);
      document.removeEventListener("webkitfullscreenchange", onFullscreen);
      window.removeEventListener("blur", onBlur);
      window.removeEventListener("keydown", onKeyDown, true);
      document.removeEventListener("copy", block, true);
      document.removeEventListener("cut", block, true);
      document.removeEventListener("paste", block, true);
      document.removeEventListener("contextmenu", block, true);
    };
  }, [enabled, report]);

  return { violations, limit: VIOLATION_LIMIT };
}