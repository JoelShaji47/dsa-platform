"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { BaseStep } from "../trace-types";

export type Speed = 0.5 | 1 | 1.5 | 2;

const INTERVAL_MS: Record<Speed, number> = {
  0.5: 1400,
  1: 800,
  1.5: 450,
  2: 250,
};

export function useTracePlayer(steps: BaseStep[]) {
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<Speed>(1);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = useCallback(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
  }, []);

  // Fresh input mounts a fresh session (parent keys by input), so no reset
  // effect is needed here — and the trace never auto-plays.
  // Timer cleanup on unmount only.
  useEffect(() => stop, [stop]);

  const atEnd = steps.length > 0 && cursor >= steps.length - 1;

  const pause = useCallback(() => {
    stop();
    setPlaying(false);
  }, [stop]);

  const next = useCallback(() => {
    pause();
    setCursor((c) => Math.min(c + 1, Math.max(0, steps.length - 1)));
  }, [pause, steps.length]);

  const prev = useCallback(() => {
    pause();
    setCursor((c) => Math.max(0, c - 1));
  }, [pause]);

  const reset = useCallback(() => {
    pause();
    setCursor(0);
  }, [pause]);

  const play = useCallback(() => {
    if (steps.length === 0) return;
    if (atEnd) setCursor(0);
    setPlaying(true);
    stop();
    timer.current = setInterval(() => {
      setCursor((c) => {
        if (c + 1 >= steps.length - 1) {
          stop();
          setPlaying(false);
          return steps.length - 1;
        }
        return c + 1;
      });
    }, INTERVAL_MS[speed]);
  }, [atEnd, speed, steps.length, stop]);

  const toggle = useCallback(() => {
    if (playing) pause();
    else play();
  }, [pause, play, playing]);

  return {
    cursor,
    step: steps[cursor] ?? null,
    total: steps.length,
    playing,
    speed,
    atEnd,
    play,
    pause,
    toggle,
    next,
    prev,
    reset,
    setSpeed,
    setCursor: (n: number) => {
      pause();
      setCursor(Math.max(0, Math.min(n, steps.length - 1)));
    },
  };
}
