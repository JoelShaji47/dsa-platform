"use client";

import { useEffect, useRef, useState } from "react";
import { Trophy } from "lucide-react";

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

/** Polar-to-cartesian on the crest circle, 0° at the top, clockwise. */
function arcPath(cx: number, cy: number, r: number, from: number, to: number) {
  const point = (deg: number) => {
    const rad = ((deg - 90) * Math.PI) / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)] as const;
  };
  const [x0, y0] = point(from);
  const [x1, y1] = point(to);
  const large = to - from > 180 ? 1 : 0;
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
}

/**
 * The seven-world crest: one arc per tier, in that tier's own colour, with
 * cleared worlds lit, locked worlds dimmed, and the current one ringed.
 *
 * Sits on a fixed bone plate rather than the tier band. The plate keeps every
 * arc on a light surface, so each tier's `deep` colour holds its measured
 * contrast — a gold arc drawn straight onto a gold band would vanish.
 */
export function TierCrest({
  current,
  themes,
  size = 118,
}: {
  current: number;
  themes: { name: string; deep: string }[];
  size?: number;
}) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 8;
  const span = 360 / themes.length;
  const gap = 12;
  const active = Math.max(0, Math.min(current, themes.length - 1));

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-hidden
        className="block"
      >
        {themes.map((t, i) => {
          const isCurrent = i === active;
          const cleared = i < active;
          return (
            <path
              key={t.name}
              d={arcPath(cx, cy, r, i * span + gap / 2, (i + 1) * span - gap / 2)}
              fill="none"
              stroke={t.deep}
              strokeWidth={isCurrent ? 10 : 6.5}
              strokeLinecap="round"
              opacity={isCurrent ? 1 : cleared ? 0.8 : 0.18}
            />
          );
        })}
        <circle
          cx={cx}
          cy={cy}
          r={r - 13}
          fill="none"
          stroke={themes[active].deep}
          strokeWidth={1.5}
          opacity={0.18}
        />
      </svg>
      <span className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <Trophy
          size={Math.round(size * 0.22)}
          style={{ color: themes[active].deep }}
        />
      </span>
    </div>
  );
}

