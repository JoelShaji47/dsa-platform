"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { formatClock } from "./status-styles";

export default function Countdown({
  timeRemainingSeconds,
  onExpire,
}: {
  timeRemainingSeconds: number;
  onExpire?: () => void;
}) {
  const [anchor] = useState(() => Date.now() + timeRemainingSeconds * 1000);
  const [left, setLeft] = useState(timeRemainingSeconds);

  useEffect(() => {
    let fired = false;
    const id = setInterval(() => {
      const next = Math.max(0, Math.round((anchor - Date.now()) / 1000));
      setLeft(next);
      if (next === 0 && !fired) {
        fired = true;
        onExpire?.();
      }
    }, 250);
    return () => clearInterval(id);
  }, [anchor, onExpire]);

  const tone =
    left <= 300
      ? "text-red-400 border-red-500/40 bg-red-500/10"
      : left <= 600
        ? "text-yellow-300 border-yellow-500/40 bg-yellow-500/10"
        : "text-gray-200 border-white/10 bg-[#252540]";

  return (
    <div
      className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 font-mono text-sm font-bold tabular-nums ${tone}`}
      title="Time remaining"
    >
      <Clock size={13} />
      {formatClock(left)}
    </div>
  );
}
