"use client";

import { ArrowRight, Layers, Play } from "lucide-react";
import type { Approach } from "@/lib/types";
import { supportedSlugs } from "@/visualize/registry";

/** Traces are slug-keyed, so a rung's `trace_key` must be a real registry entry
 * to be playable. Resolved once at module load — the registry is static. */
const traceable = new Set(supportedSlugs());

function Chip({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex items-baseline gap-1 rounded-md border border-ink/10 bg-ink/[0.03] px-1.5 py-0.5 font-mono text-[11px] text-ink-soft">
      <span className="text-[10px] uppercase tracking-wide text-ink-faint">
        {label}
      </span>
      {value}
    </span>
  );
}

/** The solution ladder: cheapest rung first, optimal last.
 *
 * Content only for most problems — a rung hands off to the step-by-step
 * player only when its `trace_key` resolves to a registry entry. */
export function ApproachLadder({
  approaches,
  activeTraceKey,
  onVisualize,
}: {
  approaches: Approach[];
  activeTraceKey: string | null;
  onVisualize: (traceKey: string) => void;
}) {
  if (approaches.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 bg-paper p-8 text-center">
        <Layers size={20} className="text-ink-faint" />
        <p className="text-sm font-medium text-ink">No ladder authored yet</p>
        <p className="max-w-xs text-xs leading-relaxed text-ink-soft">
          This problem has no approach ladder. The schema, API and player are in
          place — only the authoring is missing.
        </p>
      </div>
    );
  }

  const optimal = approaches.length - 1;

  return (
    <div className="h-full overflow-y-auto bg-paper p-5">
      <p className="max-w-xl text-xs leading-relaxed text-ink-soft">
        Climb from the approach you would write under pressure to the one an
        interviewer wants. Each rung lists what it costs and where it loses.
      </p>

      <ol className="mt-4">
        {approaches.map((approach, i) => {
          const hasTrace = Boolean(
            approach.trace_key && traceable.has(approach.trace_key)
          );
          const isActive =
            Boolean(approach.trace_key) && approach.trace_key === activeTraceKey;
          const isOptimal = i === optimal;
          return (
            <li key={approach.name} className="relative flex gap-3 pb-2">
              {/* Rung connector — stops below the last node. */}
              {!isOptimal && (
                <span
                  aria-hidden
                  className="absolute left-[13px] top-8 -bottom-2 w-px bg-ink/10"
                />
              )}
              <span
                className={`relative z-10 mt-3 flex h-[27px] w-[27px] shrink-0 items-center justify-center rounded-full border font-mono text-[11px] font-semibold ${
                  isOptimal
                    ? "border-quest bg-quest text-white"
                    : "border-ink/10 bg-card text-ink-soft"
                }`}
              >
                {i + 1}
              </span>

              <div
                className={`panel min-w-0 flex-1 p-3.5 ${
                  isActive ? "ring-1 ring-quest/50" : ""
                }`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-ink">
                    {approach.name}
                  </h3>
                  {isOptimal && (
                    <span className="rounded-full bg-quest/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-quest">
                      Optimal
                    </span>
                  )}
                </div>

                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  <Chip label="time" value={approach.time_complexity} />
                  <Chip label="space" value={approach.space_complexity} />
                </div>

                <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">
                  {approach.idea}
                </p>

                {approach.tradeoff && (
                  <p className="mt-2 border-l-2 border-gold/40 pl-2 text-[12px] leading-relaxed text-ink-faint">
                    {approach.tradeoff}
                  </p>
                )}

                {hasTrace && (
                  <button
                    type="button"
                    onClick={() => onVisualize(approach.trace_key as string)}
                    className="mt-2.5 inline-flex items-center gap-1.5 rounded-lg bg-quest/10 px-2.5 py-1 text-xs font-medium text-quest transition-colors hover:bg-quest/20"
                  >
                    <Play size={12} />
                    {isActive ? "Playing in Visualize" : "Watch the trace"}
                    <ArrowRight size={12} />
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
