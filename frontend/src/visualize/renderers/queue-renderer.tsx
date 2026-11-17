"use client";

import type { QueueSnapshot } from "../trace-types";
import { cn } from "@/lib/utils";

/** Horizontal queue/deque stage. The leftmost item is the front. */
export function QueueRenderer({ snapshot }: { snapshot: QueueSnapshot }) {
  const { values, front, back, active, settled, label } = snapshot;

  return (
    <div className="flex flex-col items-center">
      <div className="overflow-x-auto pb-1">
        <div className="flex min-w-fit gap-1.5">
          {values.length === 0 ? (
            <div className="flex h-12 w-28 items-center justify-center rounded-lg border border-dashed border-white/15 font-mono text-[10px] text-gray-500">
              empty
            </div>
          ) : (
            values.map((v, k) => {
              const isFront = k === front;
              const isBack = k === back;
              const isActive = active.includes(k);
              const isSettled = settled.includes(k);
              const marks =
                isFront && isBack ? ["front/back"] : isFront ? ["front"] : isBack ? ["back"] : [];
              return (
                <div key={k} className="flex w-16 shrink-0 flex-col items-center sm:w-20">
                  <div className="flex h-5 items-end gap-1 font-mono text-[10px] font-bold">
                    {marks.map((mark) => (
                      <span
                        key={mark}
                        className={mark === "back" ? "text-sky-300" : "text-amber-300"}
                      >
                        {mark}
                      </span>
                    ))}
                  </div>
                  <div
                    className={cn(
                      "flex h-12 w-full items-center justify-center rounded-lg border font-mono text-sm font-bold transition-all duration-300 sm:h-14",
                      isActive
                        ? "border-amber-300/80 bg-amber-400/15 text-amber-100 shadow-[0_0_12px_-2px_rgb(252_211_77/0.5)]"
                        : isSettled
                          ? "border-emerald-400/60 bg-emerald-500/10 text-emerald-200"
                          : "border-white/15 bg-white/[0.03] text-gray-100"
                    )}
                  >
                    {v}
                  </div>
                  <span className="mt-1 font-mono text-[10px] text-gray-500">{k}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
      {label && <span className="mt-1.5 font-mono text-[10px] text-gray-500">{label}</span>}
    </div>
  );
}
