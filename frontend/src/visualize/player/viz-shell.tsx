"use client";

import type { ReactNode } from "react";
import { Check, ChevronLeft, ChevronRight, Pause, Play, RotateCcw } from "lucide-react";
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

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#0b0d12] text-gray-100">
      {/* Stage */}
      <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-5">
        {props.error ? (
          <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {props.error}
          </p>
        ) : (
          <>
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md border border-white/15 bg-white/5 px-2 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-amber-300">
                {step?.op ?? "Ready"}
              </span>
              <span className="font-mono text-[11px] text-gray-500">
                step {total === 0 ? 0 : cursor + 1} / {total}
              </span>
              {props.atEnd && step?.done && (
                <span className="flex items-center gap-1 rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-300">
                  <Check size={12} /> Complete
                </span>
              )}
            </div>
            <div className="mt-3">{props.children}</div>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-gray-300">
              {step?.explanation ?? "Press play or step forward to start the trace."}
            </p>
            {step?.result && (
              <p className="mt-2 font-mono text-sm font-bold text-emerald-300">{step.result}</p>
            )}
          </>
        )}

        {/* Pseudocode + vars */}
        {!props.error && props.pseudocode.length > 0 && (
          <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_220px]">
            <pre className="overflow-x-auto rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[12px] leading-6">
              {props.pseudocode.map((line, i) => (
                <div
                  key={i}
                  className={cn(
                    "rounded px-2",
                    i === step?.line ? "bg-amber-400/15 text-amber-200" : "text-gray-400"
                  )}
                >
                  <span className="mr-2 select-none text-gray-600">{i + 1}</span>
                  {line}
                </div>
              ))}
            </pre>
            <div className="rounded-xl border border-white/10 bg-black/40 p-3 font-mono text-[12px]">
              <p className="mb-2 text-[10px] uppercase tracking-widest text-gray-500">variables</p>
              {Object.keys(props.vars).length === 0 ? (
                <p className="text-gray-600">—</p>
              ) : (
                Object.entries(props.vars).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-2 py-0.5">
                    <span className="text-sky-300">{k}</span>
                    <span className="text-gray-200">{String(v)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="shrink-0 border-t border-white/10 bg-[#0e1119] px-4 py-2.5">
        <div className="mb-2 h-1 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-emerald-500 transition-[width] duration-200" style={{ width: `${pct}%` }} />
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={props.onReset}
            aria-label="Reset"
            className="rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100"
          >
            <RotateCcw size={15} />
          </button>
          <button
            type="button"
            onClick={props.onPrev}
            disabled={cursor === 0}
            aria-label="Previous step"
            className="rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100 disabled:opacity-30"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            type="button"
            onClick={props.playing ? props.onPause : props.onPlay}
            aria-label={props.playing ? "Pause" : "Play"}
            className="rounded-md bg-emerald-600 p-2 text-white transition-colors hover:bg-emerald-500"
          >
            {props.playing ? <Pause size={15} /> : <Play size={15} />}
          </button>
          <button
            type="button"
            onClick={props.onNext}
            disabled={props.atEnd}
            aria-label="Next step"
            className="rounded-md p-2 text-gray-400 transition-colors hover:bg-white/10 hover:text-gray-100 disabled:opacity-30"
          >
            <ChevronRight size={16} />
          </button>
          <div className="ml-auto flex gap-0.5 rounded-lg border border-white/10 bg-black/30 p-0.5">
            {SPEEDS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => props.onSpeed(s)}
                className={cn(
                  "rounded-md px-2 py-1 font-mono text-[11px] transition-colors",
                  props.speed === s ? "bg-white/15 text-gray-100" : "text-gray-500 hover:text-gray-300"
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
