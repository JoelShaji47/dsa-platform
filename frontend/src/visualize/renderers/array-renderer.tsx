"use client";

import { useTheme } from "@/context/theme-context";
import type { ArraySnapshot, PointerName } from "../trace-types";
import { cn } from "@/lib/utils";

const POINTER_ORDER: PointerName[] = [
  "low",
  "mid",
  "high",
  "left",
  "right",
  "slow",
  "fast",
  "i",
  "j",
  "k",
  "parent",
  "child",
];

const POINTER_COLOR_DARK: Record<PointerName, string> = {
  low: "text-sky-300",
  mid: "text-amber-300",
  high: "text-sky-300",
  left: "text-emerald-300",
  right: "text-emerald-300",
  slow: "text-violet-300",
  fast: "text-orange-300",
  i: "text-amber-300",
  j: "text-fuchsia-300",
  k: "text-fuchsia-300",
  parent: "text-sky-300",
  child: "text-orange-300",
};

const POINTER_COLOR_LIGHT: Record<PointerName, string> = {
  low: "text-sky-700",
  mid: "text-amber-700",
  high: "text-sky-700",
  left: "text-emerald-700",
  right: "text-emerald-700",
  slow: "text-violet-700",
  fast: "text-orange-700",
  i: "text-amber-700",
  j: "text-fuchsia-700",
  k: "text-fuchsia-700",
  parent: "text-sky-700",
  child: "text-orange-700",
};

/** Array stage: thin outlines, index row, pointer labels, CSS-only motion. */
export function ArrayRenderer({ snapshot }: { snapshot: ArraySnapshot }) {
  const dark = useTheme() === "dark";
  const pointerColor = dark ? POINTER_COLOR_DARK : POINTER_COLOR_LIGHT;
  const { values, active, settled, eliminated, deps = [], pointers, label } = snapshot;
  const byIndex = new Map<number, PointerName[]>();
  (Object.entries(pointers) as [PointerName, number | undefined][]).forEach(([name, idx]) => {
    if (idx == null || idx < 0 || idx >= values.length) return;
    const arr = byIndex.get(idx) ?? [];
    arr.push(name);
    byIndex.set(idx, arr);
  });

  return (
    <div className="flex flex-col items-center">
      <div className="overflow-x-auto pb-1">
        <div className="flex min-w-fit gap-1.5">
          {values.map((v, k) => {
            const isActive = active.includes(k);
            const isDep = deps.includes(k);
            const isSettled = settled.includes(k);
            const isOut = eliminated.includes(k);
            const tags = (byIndex.get(k) ?? []).sort(
              (a, b) => POINTER_ORDER.indexOf(a) - POINTER_ORDER.indexOf(b)
            );
            return (
              <div key={k} className="flex w-12 shrink-0 flex-col items-center sm:w-14">
                {/* Pointer labels */}
                <div className="flex h-5 items-end gap-1 font-mono text-[10px] font-bold">
                  {tags.map((t) => (
                    <span key={t} className={pointerColor[t]}>
                      {t}
                    </span>
                  ))}
                </div>
                {/* Cell */}
                <div
                  className={cn(
                    "flex h-12 w-full items-center justify-center rounded-lg border font-mono text-sm font-bold transition-all duration-300 sm:h-14",
                    isActive
                      ? dark
                        ? "border-amber-300/80 bg-amber-400/15 text-amber-100 shadow-[0_0_12px_-2px_rgb(252_211_77/0.5)]"
                        : "border-gold-deep/60 bg-gold/15 text-ink"
                      : isDep
                        ? dark
                          ? "border-sky-400/60 bg-sky-500/10 text-sky-200"
                          : "border-sky-600/50 bg-sky-500/10 text-sky-800"
                        : isSettled
                          ? dark
                            ? "border-emerald-400/60 bg-emerald-500/10 text-emerald-200"
                            : "border-quest/60 bg-quest/10 text-emerald-800"
                          : isOut
                            ? dark
                              ? "border-white/5 bg-black/30 text-gray-600 line-through"
                              : "border-ink/10 bg-ink/[0.03] text-ink-faint line-through"
                            : dark
                              ? "border-white/15 bg-white/[0.03] text-gray-100"
                              : "border-ink/15 bg-white text-ink"
                  )}
                >
                  {v === "" ? <span className={dark ? "text-gray-600" : "text-ink-faint"}>·</span> : v}
                </div>
                {/* Index */}
                <span
                  className={
                    dark
                      ? "mt-1 font-mono text-[10px] text-gray-500"
                      : "mt-1 font-mono text-[10px] text-ink-faint"
                  }
                >
                  {k}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      {label && (
        <span
          className={
            dark
              ? "mt-1.5 font-mono text-[10px] text-gray-500"
              : "mt-1.5 font-mono text-[10px] text-ink-faint"
          }
        >
          {label}
        </span>
      )}
    </div>
  );
}
