"use client";

import { useMemo, useState } from "react";
import { FlaskConical } from "lucide-react";
import { lookupVisualizer, type RegistryItem } from "./registry";
import type { BaseStep } from "./trace-types";
import { useTracePlayer } from "./player/use-trace-player";
import { VizShell } from "./player/viz-shell";

/** Owns playback state. Keyed by applied input upstream, so a new input mounts
 * a fresh session at step 0 instead of syncing state in an effect. */
function TraceSession({ item, steps, error }: { item: RegistryItem; steps: BaseStep[]; error: string | null }) {
  const player = useTracePlayer(steps);
  return (
    <div
      className="h-full"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight") player.next();
        else if (e.key === "ArrowLeft") player.prev();
        else if (e.key === " ") {
          e.preventDefault();
          player.toggle();
        }
      }}
    >
    <VizShell
      title={item.entry.title}
      step={player.step}
      cursor={player.cursor}
      total={player.total}
      playing={player.playing}
      speed={player.speed}
      atEnd={player.atEnd}
      pseudocode={item.entry.pseudocode}
      vars={player.step?.vars ?? {}}
      error={error}
      onPlay={player.play}
      onPause={player.pause}
      onNext={player.next}
      onPrev={player.prev}
      onReset={player.reset}
      onSpeed={player.setSpeed}
    >
      {player.step && item.render(player.step)}
    </VizShell>
    </div>
  );
}

export function VisualizerView({ slug }: { slug: string }) {
  const item = lookupVisualizer(slug);

  const [raw, setRaw] = useState(item?.entry.defaultInput ?? "");
  const [applied, setApplied] = useState(item?.entry.defaultInput ?? "");
  const [error, setError] = useState<string | null>(null);

  // `applied` is validated before it is set, so parsing here should not throw;
  // the guard keeps a malformed value from crashing the visualizer.
  const steps = useMemo(() => {
    if (!item) return [];
    try {
      return item.entry.generate(item.entry.parse(applied));
    } catch {
      return [];
    }
  }, [item, applied]);

  if (!item) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 bg-[#0b0d12] p-8 text-center">
        <FlaskConical size={22} className="text-gray-500" />
        <p className="font-display text-lg font-bold text-gray-200">Visualization coming soon</p>
        <p className="max-w-sm text-sm text-gray-400">
          This problem doesn&apos;t have a step-by-step trace yet. The player, renderers and
          registry are ready — only its trace generator is missing.
        </p>
      </div>
    );
  }

  const apply = () => {
    try {
      item.entry.parse(raw);
      setApplied(raw);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid input");
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      {/* Input bar */}
      <div className="shrink-0 border-b border-white/10 bg-[#0e1119] px-4 py-2.5">
        <div className="flex flex-wrap items-center gap-2">
          <input
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") apply();
              e.stopPropagation();
            }}
            spellCheck={false}
            placeholder={item.entry.inputHint}
            aria-label="Visualization input"
            className="min-w-0 flex-1 rounded-lg border border-white/15 bg-black/40 px-3 py-1.5 font-mono text-xs text-gray-100 placeholder:text-gray-600"
          />
          <button
            type="button"
            onClick={apply}
            className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            Apply
          </button>
        </div>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {item.entry.presets.map((p) => (
            <button
              key={p.label}
              type="button"
              onClick={() => {
                setRaw(p.value);
                setApplied(p.value);
                setError(null);
              }}
              className="rounded-md border border-white/10 bg-white/[0.03] px-2 py-0.5 font-mono text-[11px] text-gray-400 hover:border-white/25 hover:text-gray-200"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Player — keyed by input so a new trace starts at step 0, paused. */}
      <div className="min-h-0 flex-1">
        <TraceSession key={applied} item={item} steps={steps} error={error} />
      </div>
    </div>
  );
}
