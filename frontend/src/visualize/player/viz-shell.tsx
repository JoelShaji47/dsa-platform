"use client";

import type { ReactNode } from "react";
import { Check, ChevronLeft, ChevronRight, Pause, Play, RotateCcw } from "lucide-react";
import { useTheme } from "@/context/theme-context";
import type { BaseStep } from "../trace-types";
import type { Speed } from "./use-trace-player";
import { cn } from "@/lib/utils";

const SPEEDS: Speed[] = [0.5, 1, 1.5, 2];

interface Props {
  title: string;
  step: BaseStep | null;
  cursor: number;
  total: number;
  playing: boolean;
  speed: Speed;
  atEnd: boolean;
  pseudocode: string[];
  vars: Record<string, string | number>;
  error: string | null;
  onPlay: () => void;
  onPause: () => void;
  onNext: () => void;
  onPrev: () => void;
  onReset: () => void;
  onSpeed: (s: Speed) => void;
  children: ReactNode;
}

export function VizShell(props: Props) {
  const { step, cursor, total } = props;
  const pct = total > 1 ? Math.round((cursor / (total - 1)) * 100) : 0;
  const dark = useTheme() === "dark";
  const th = (dc: string, l: string) => (dark ? dc : l);

  return (
    <div className={th("flex h-full min-h-0 flex-col bg-[#0b0d12] text-gray-100", "flex h-full min-h-0 flex-col bg-paper text-ink")}>
      {/* Stage */}
      <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-5">
        {props.error ? (
          <p className={th(
            "rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300",
            "rounded-xl border border-red-600/30 bg-red-600/[0.07] px-4 py-3 text-sm text-red-700"
          )}>
            {props.error}
          </p>
        ) : (
          <>
            <div className="flex flex-wrap items-center gap-2">
              <span className={th(
                "rounded-md border border-white/15 bg-white/5 px-2 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-amber-300",
                "rounded-md border border-gold/40 bg-gold/10 px-2 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-gold-deep"
              )}>
                {step?.op ?? "Ready"}
              </span>
              <span className={th("font-mono text-[11px] text-gray-500", "font-mono text-[11px] text-ink-faint")}>
                step {total === 0 ? 0 : cursor + 1} / {total}
              </span>
              {props.atEnd && step?.done && (
                <span className={th(
                  "flex items-center gap-1 rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-300",
                  "flex items-center gap-1 rounded-md border border-emerald-600/40 bg-emerald-600/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-700"
                )}>
                  <Check size={12} /> Complete
                </span>
              )}
            </div>
            <div className="mt-3">{props.children}</div>
            <p className={th("mt-3 max-w-2xl text-sm leading-relaxed text-gray-300", "mt-3 max-w-2xl text-sm leading-relaxed text-ink-soft")}>
              {step?.explanation ?? "Press play or step forward to start the trace."}
            </p>
            {step?.result && (
              <p className={th("mt-2 font-mono text-sm font-bold text-emerald-300", "mt-2 font-mono text-sm font-bold text-emerald-700")}>{step.result}</p>
            )}
          </>
        )}

        {/* Pseudocode + vars */}
        {!props.error && props.pseudocode.length > 0 && (
          <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_220px]">
            <pre className={th(
              "overflow-x-auto rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[12px] leading-6",
              "overflow-x-auto rounded-xl border border-ink/10 bg-white p-3 font-mono text-[12px] leading-6"
            )}>
              {props.pseudocode.map((line, i) => (
                <div
                  key={i}
                  className={cn(
                    "rounded px-2",
                    i === step?.line
                      ? th("bg-amber-400/15 text-amber-200", "bg-gold/15 text-ink")
                      : th("text-gray-400", "text-ink-soft")
                  )}
                >
                  <span className={th("mr-2 select-none text-gray-600", "mr-2 select-none text-ink-faint")}>{i + 1}</span>
                  {line}
                </div>
              ))}
            </pre>
            <div className={th(
              "rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[12px]",
              "rounded-xl border border-ink/10 bg-white p-3 font-mono text-[12px]"
            )}>
              <p className={th("mb-2 text-[10px] uppercase tracking-widest text-gray-500", "mb-2 text-[10px] uppercase tracking-widest text-ink-faint")}>variables</p>
              {Object.keys(props.vars).length === 0 ? (
                <p className={th("text-gray-600", "text-ink-faint")}>—</p>
              ) : (
                Object.entries(props.vars).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-2 py-0.5">
                    <span className={th("text-sky-300", "text-sky-700")}>{k}</span>
                    <span className={th("text-gray-200", "text-ink")}>{String(v)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className={th("shrink-0 border-t border-white/10 bg-[#0e1119] px-4 py-2.5", "shrink-0 border-t border-ink/10 bg-card px-4 py-2.5")}>
        <div className={th("mb-2 h-1 overflow-hidden rounded-full bg-white/10", "mb-2 h-1 overflow-hidden rounded-full bg-ink/10")}>
          <div className="h-full rounded-full bg-quest transition-[width] duration-200" style={{ width: `${pct}%` }} />
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={props.onReset}
            aria-label="Reset"
            className={th(
              "rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100",
              "rounded-md p-2 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
            )}
          >
            <RotateCcw size={15} />
          </button>
          <button
            type="button"
            onClick={props.onPrev}
            disabled={cursor === 0}
            aria-label="Previous step"
            className={th(
              "rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100 disabled:opacity-30",
              "rounded-md p-2 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink disabled:opacity-30"
            )}
          >
            <ChevronLeft size={16} />
          </button>
          <button
            type="button"
            onClick={props.playing ? props.onPause : props.onPlay}
            aria-label={props.playing ? "Pause" : "Play"}
            className="rounded-md bg-quest p-2 text-white transition-opacity hover:opacity-90"
          >
            {props.playing ? <Pause size={15} /> : <Play size={15} />}
          </button>
          <button
            type="button"
            onClick={props.onNext}
            disabled={props.atEnd}
            aria-label="Next step"
            className={th(
              "rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100 disabled:opacity-30",
              "rounded-md p-2 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink disabled:opacity-30"
            )}
          >
            <ChevronRight size={16} />
          </button>
          <div className={th(
            "ml-auto flex gap-0.5 rounded-lg border border-white/10 bg-black/30 p-0.5",
            "ml-auto flex gap-0.5 rounded-lg border border-ink/10 bg-paper-deep p-0.5"
          )}>
            {SPEEDS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => props.onSpeed(s)}
                className={cn(
                  "rounded-md px-2 py-1 font-mono text-[11px] transition-colors",
                  props.speed === s
                    ? th("bg-white/15 text-gray-100", "bg-ink text-paper")
                    : th("text-gray-500 hover:text-gray-300", "text-ink-faint hover:text-ink")
                )}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
