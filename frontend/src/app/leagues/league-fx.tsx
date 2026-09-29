"use client";

import { useEffect, useRef, useState } from "react";

/** Animated number that counts up to `value` (Aceternity-style count-up). */
export function CountUp({
  value,
  duration = 900,
  className,
}: {
  value: number;
  duration?: number;
  className?: string;
}) {
  const [shown, setShown] = useState(0);
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      setShown(value);
      return;
    }
    const from = shown;
    const start = performance.now();
    let raf = 0;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(Math.round(from + (value - from) * eased));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);
  return <span className={className}>{shown.toLocaleString()}</span>;
}

/** Ambient drifting beams (thin blurred bars in the tier accent). */
export function Beams({ color }: { color: string }) {
  const bars = [
    { left: "6%", delay: "0s", dur: "11s", h: "38%" },
    { left: "22%", delay: "-4s", dur: "14s", h: "55%" },
    { left: "47%", delay: "-7s", dur: "10s", h: "30%" },
    { left: "68%", delay: "-2s", dur: "13s", h: "48%" },
    { left: "88%", delay: "-9s", dur: "12s", h: "36%" },
  ];
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {bars.map((b, i) => (
        <span
          key={i}
          className="beam"
          style={{
            left: b.left,
            height: b.h,
            backgroundColor: color,
            animationDelay: b.delay,
            animationDuration: b.dur,
          }}
        />
      ))}
    </div>
  );
}

/** Soft tier-colored aura behind the hero (blurred solid, no gradients). */
export function Aura({ color }: { color: string }) {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <span
        className="absolute -top-24 left-1/4 h-64 w-[42rem] rounded-full opacity-25 blur-3xl"
        style={{ backgroundColor: color }}
      />
    </div>
  );
}
