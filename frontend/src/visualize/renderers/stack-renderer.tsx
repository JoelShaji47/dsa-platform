"use client";

import type { StackSnapshot } from "../trace-types";
import { cn } from "@/lib/utils";

/** Vertical stack stage: bottom item renders first, top glows. CSS-only motion. */
export function StackRenderer({ snapshot }: { snapshot: StackSnapshot }) {
  const { values, active, settled, label } = snapshot;
  const top = values.length - 1;

  return (
    <div className="flex flex-col items-center">
      <div className="flex min-h-24 w-20 flex-col-reverse justify-start gap-1.5 sm:w-24">
        {values.length === 0 ? (
          <div className="flex h-12 items-center justify-center rounded-lg border border-dashed border-white/15 font-mono text-[10px] text-gray-500">
            empty
          </div>
        ) : (
          values.map((v, k) => {
            const isTop = k === top;
            const isActive = active.includes(k);
            const isSettled = settled.includes(k);
            return (
              <div key={k} className="flex flex-col items-center">
                {isTop && (
                  <span className="mb-0.5 font-mono text-[10px] font-bold text-amber-300">
                    top
                  </span>
                )}
                <div
                  className={cn(
                    "flex h-11 w-full items-center justify-center rounded-lg border font-mono text-sm font-bold transition-all duration-300 sm:h-12",
                    isActive
                      ? "border-amber-300/80 bg-amber-400/15 text-amber-100 shadow-[0_0_12px_-2px_rgb(252_211_77/0.5)]"
                      : isSettled
                        ? "border-emerald-400/60 bg-emerald-500/10 text-emerald-200"
                        : "border-white/15 bg-white/[0.03] text-gray-100"
                  )}
                >
                  {v}
                </div>
              </div>
            );
          })
        )}
      </div>
      {label && (
        <span className="mt-1.5 font-mono text-[10px] text-gray-500">{label}</span>
      )}
    </div>
  );
}
