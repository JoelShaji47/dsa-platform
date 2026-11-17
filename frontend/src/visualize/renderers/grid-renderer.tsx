"use client";

import { Fragment } from "react";
import type { GridSnapshot } from "../trace-types";
import { cn } from "@/lib/utils";

function cellKey(row: number, col: number): string {
  return `${row},${col}`;
}

/** Rectangular grid stage for grid graphs and 2-D DP tables. */
export function GridRenderer({ snapshot }: { snapshot: GridSnapshot }) {
  const {
    cols,
    values,
    active,
    deps,
    settled,
    showIndices,
    rowLabels,
    colLabels,
    label,
  } = snapshot;
  const activeSet = new Set(active.map(([row, col]) => cellKey(row, col)));
  const depSet = new Set(deps.map(([row, col]) => cellKey(row, col)));
  const settledSet = new Set(settled.map(([row, col]) => cellKey(row, col)));

  return (
    <div className="flex flex-col items-center">
      <div className="overflow-x-auto pb-1">
        <div
          className="inline-grid gap-1"
          style={{
            gridTemplateColumns: showIndices
              ? `auto repeat(${cols}, minmax(0, 1fr))`
              : `repeat(${cols}, minmax(0, 1fr))`,
          }}
        >
          {showIndices && <span />}
          {showIndices &&
            Array.from({ length: cols }, (_, col) => (
              <span
                key={col}
                className="flex h-4 items-end justify-center font-mono text-[10px] text-gray-500"
              >
                {colLabels?.[col] ?? col}
              </span>
            ))}
          {values.map((row, rowIndex) => (
            <Fragment key={rowIndex}>
              {showIndices && (
                <span className="flex h-10 items-center justify-end pr-1 font-mono text-[10px] text-gray-500">
                  {rowLabels?.[rowIndex] ?? rowIndex}
                </span>
              )}
              {row.map((value, colIndex) => {
                const key = cellKey(rowIndex, colIndex);
                const isActive = activeSet.has(key);
                const isDep = depSet.has(key);
                const isSettled = settledSet.has(key);
                return (
                  <div
                    key={colIndex}
                    className={cn(
                      "flex h-10 min-w-10 items-center justify-center rounded-lg border px-1 font-mono text-xs font-bold transition-all duration-300",
                      isActive
                        ? "border-amber-300/80 bg-amber-400/15 text-amber-100 shadow-[0_0_12px_-2px_rgb(252_211_77/0.5)]"
                        : isDep
                          ? "border-sky-400/60 bg-sky-500/10 text-sky-200"
                          : isSettled
                            ? "border-emerald-400/60 bg-emerald-500/10 text-emerald-200"
                            : "border-white/15 bg-white/[0.03] text-gray-100"
                    )}
                  >
                    {value === "" ? <span className="text-gray-600">·</span> : value}
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
      {label && <span className="mt-1.5 font-mono text-[10px] text-gray-500">{label}</span>}
    </div>
  );
}
