"use client";

import Link from "next/link";
import { useCallback, useMemo, useRef, useState } from "react";
import {
  BookOpen,
  Check,
  Lock,
  Minus,
  Plus,
  Sparkles,
  X,
} from "lucide-react";
import { DifficultyChip } from "@/components/shell";
import type { Difficulty } from "@/lib/types";
import { cn } from "@/lib/utils";

export interface RoadmapProblem {
  slug: string;
  title: string;
  difficulty: Difficulty;
  solved: boolean;
  attempts: number;
  hints_used: number;
  solvable: boolean;
  recommended: boolean;
  sources: string[];
}

export interface Pattern {
  key: string;
  name: string;
  order: number;
  prerequisites: string[];
  snippet: string;
  solved: number;
  total: number;
  mastery: number;
  complete: boolean;
  problems: RoadmapProblem[];
}

// Slimmer, airier layout tokens (de-clunked from the old graph).
const W = 156;
const H = 50;
const NODE_GAP = 36;
const BAND_PAD = 64;
const BAND_GAP = 88;
const TOP_PAD = 48;
const BOTTOM_PAD = 72;

function computeLayout(patterns: Pattern[]) {
  const sorted = [...patterns].sort(
    (a, b) => a.order - b.order || a.name.localeCompare(b.name)
  );
  const byOrder: Record<number, Pattern[]> = {};
  sorted.forEach((p) => {
    (byOrder[p.order] ||= []).push(p);
  });
  const orders = Object.keys(byOrder)
    .map(Number)
    .sort((a, b) => a - b);

  let maxBandW = 0;
  orders.forEach((order) => {
    const band = byOrder[order];
    maxBandW = Math.max(maxBandW, band.length * W + (band.length - 1) * NODE_GAP);
  });
  const canvasW = maxBandW + 2 * BAND_PAD;

  const pos: Record<string, [number, number]> = {};
  let prevBottom = TOP_PAD;
  orders.forEach((order) => {
    const band = byOrder[order];
    const bandW = band.length * W + (band.length - 1) * NODE_GAP;
    const startX = (maxBandW - bandW) / 2 + BAND_PAD;
    const top = prevBottom === TOP_PAD ? TOP_PAD : prevBottom + BAND_GAP;
    band.forEach((p, i) => {
      pos[p.key] = [startX + i * (W + NODE_GAP), top];
    });
    prevBottom = top + H;
  });
  const canvasH = prevBottom + BOTTOM_PAD;

  const edges: [string, string][] = [];
  for (const p of patterns) {
    for (const pre of p.prerequisites || []) {
      if (pos[pre]) edges.push([pre, p.key]);
    }
  }
  return { pos, edges, canvasW, canvasH };
}

function edgePath(
  source: string,
  target: string,
  pos: Record<string, [number, number]>
) {
  const [sx, sy] = pos[source];
  const [tx, ty] = pos[target];
  const x1 = sx + W / 2;
  const y1 = sy + H;
  const x2 = tx + W / 2;
  const y2 = ty;
  const bend = Math.min(48, Math.abs(x2 - x1) * 0.5 + 24);
  return `M ${x1} ${y1} C ${x1} ${y1 + bend}, ${x2} ${y2 - bend}, ${x2} ${y2}`;
}

function GraphNode({
  pattern,
  locked,
  selected,
  onClick,
}: {
  pattern: Pattern & { pos: [number, number] };
  locked: boolean;
  selected: boolean;
  onClick: () => void;
}) {
  const [x, y] = pattern.pos;
  const solvable = pattern.problems.filter((p) => p.solvable);
  const solved = solvable.filter((p) => p.solved).length;
  const done = solvable.length > 0 && solved === solvable.length;
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={locked}
      style={{ left: x, top: y, width: W, height: H, touchAction: "none" }}
      className={cn(
        "roadmap-node absolute flex flex-col items-center justify-center px-3 text-center transition-all duration-150",
        locked
          ? "cursor-not-allowed opacity-40"
          : selected
            ? "-translate-y-0.5 border-gold-deep"
            : "hover:-translate-y-0.5"
      )}
    >
      <span className="flex items-center gap-1.5 font-display text-[13px] font-semibold leading-tight">
        {pattern.name}
        {done ? (
          <Check size={13} strokeWidth={3} className="shrink-0 text-quest" />
        ) : null}
        {locked ? <Lock size={11} className="shrink-0 opacity-60" /> : null}
      </span>
      <span className="mt-0.5 font-mono text-[11px] font-medium opacity-70">
        {solved}/{solvable.length}
      </span>
      {!locked && solved > 0 && (
        <span
          className={cn(
            "absolute inset-x-4 bottom-1 h-0.5 rounded-full",
            done ? "bg-quest" : "bg-gold"
          )}
        />
      )}
    </button>
  );
}

function PatternDetail({
  pattern,
  onClose,
}: {
  pattern: Pattern;
  onClose: () => void;
}) {
  const solvable = pattern.problems.filter((p) => p.solvable);
  return (
    <div className="absolute right-4 top-4 z-30 max-h-[calc(100%-2rem)] w-[320px] max-w-[86vw] overflow-y-auto rounded-2xl border border-ink/10 bg-card p-5 shadow-lift">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Pattern</p>
          <h3 className="mt-1 font-display text-xl font-bold leading-tight text-ink">
            {pattern.name}
          </h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close pattern details"
          className="rounded-lg border border-ink/10 p-1.5 text-ink-faint transition-colors hover:text-ink"
        >
          <X size={14} />
        </button>
      </div>
      <p className="mt-2 text-[13px] leading-relaxed text-ink-soft">
        {pattern.snippet}
      </p>
      <p className="mt-3 font-mono text-[11px] text-ink-faint">
        {solvable.filter((p) => p.solved).length}/{solvable.length} solved ·{" "}
        {pattern.mastery}% mastered
      </p>
      <ul className="mt-3 space-y-1">
        {solvable.map((pr) => (
          <li key={pr.slug}>
            <Link
              href={`/problems/${pr.slug}/solve`}
              className="group flex items-center gap-2.5 rounded-lg px-2.5 py-2 transition-colors hover:bg-ink/[0.04]"
            >
              <span
                className={cn(
                  "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-[1.5px]",
                  pr.solved
                    ? "border-quest bg-quest/10 text-quest"
                    : "border-ink/20 text-transparent"
                )}
              >
                <Check size={11} strokeWidth={4} />
              </span>
              <span
                className={cn(
                  "flex-1 truncate text-[13px]",
                  pr.solved ? "text-ink-faint line-through" : "text-ink"
                )}
              >
                {pr.title}
              </span>
              {pr.recommended && (
                <span className="flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 font-mono text-[10px] font-semibold text-gold-deep">
                  <Sparkles size={10} />
                  Next
                </span>
              )}
              <DifficultyChip difficulty={pr.difficulty} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function RoadmapGraph({
  patterns,
  unlocked,
}: {
  patterns: Pattern[];
  unlocked: Set<string>;
}) {
  // Graph shows structure: only patterns with runnable problems.
  const visible = useMemo(
    () => patterns.filter((p) => p.problems.some((pr) => pr.solvable)),
    [patterns]
  );
  const layout = useMemo(() => computeLayout(visible), [visible]);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [zoom, setZoom] = useState(0.85);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const sessionRef = useRef<{
    startX: number;
    startY: number;
    panX: number;
    panY: number;
  } | null>(null);

  const byKey = useMemo(() => {
    const map: Record<string, Pattern> = {};
    visible.forEach((p) => (map[p.key] = p));
    return map;
  }, [visible]);

  const clampZoom = useCallback((z: number) => {
    setZoom(Math.min(1.5, Math.max(0.3, Number(z.toFixed(3)))));
  }, []);

  const selected = selectedKey ? byKey[selectedKey] : null;

  return (
    <div className="panel relative min-h-[540px] overflow-hidden">
      <div
        className="roadmap-canvas h-[540px] cursor-grab overflow-auto active:cursor-grabbing"
        onPointerDown={(e) => {
          if (e.button !== 0 || sessionRef.current) return;
          sessionRef.current = {
            startX: e.clientX,
            startY: e.clientY,
            panX: pan.x,
            panY: pan.y,
          };
        }}
        onPointerMove={(e) => {
          const s = sessionRef.current;
          if (!s) return;
          setPan({
            x: s.panX + (e.clientX - s.startX),
            y: s.panY + (e.clientY - s.startY),
          });
        }}
        onPointerUp={() => (sessionRef.current = null)}
        onPointerCancel={() => (sessionRef.current = null)}
        onWheel={(e) => clampZoom(zoom * (e.deltaY < 0 ? 1.1 : 0.9))}
      >
        <div
          style={{
            width: layout.canvasW * zoom,
            height: (layout.canvasH + 40) * zoom,
          }}
          className="relative"
        >
          <div
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: "0 0",
              width: layout.canvasW,
              height: layout.canvasH,
            }}
            className="relative"
          >
            <svg
              width={layout.canvasW}
              height={layout.canvasH}
              className="absolute inset-0"
              aria-hidden
            >
              <defs>
                <marker
                  id="roadmap-arrow"
                  viewBox="0 0 8 8"
                  refX="7"
                  refY="4"
                  markerWidth="5"
                  markerHeight="5"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 8 4 L 0 8 z" fill="#c9a227" />
                </marker>
              </defs>
              {layout.edges.map(([s, t], i) => (
                <path
                  key={i}
                  d={edgePath(s, t, layout.pos)}
                  className="roadmap-edge"
                  markerEnd="url(#roadmap-arrow)"
                />
              ))}
            </svg>
            {visible.map((p) => (
              <GraphNode
                key={p.key}
                pattern={{ ...p, pos: layout.pos[p.key] }}
                locked={!unlocked.has(p.key)}
                selected={selectedKey === p.key}
                onClick={() =>
                  setSelectedKey(selectedKey === p.key ? null : p.key)
                }
              />
            ))}
          </div>
        </div>
      </div>

      <div className="absolute left-4 top-4 z-30 flex items-center gap-1 rounded-xl border border-ink/10 bg-card/90 px-1.5 py-1 shadow-card backdrop-blur-md">
        <button
          type="button"
          title="Zoom out"
          onClick={() => clampZoom(zoom * 0.9)}
          className="rounded-lg p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
        >
          <Minus size={14} />
        </button>
        <button
          type="button"
          title="Reset view"
          onClick={() => {
            setZoom(0.85);
            setPan({ x: 0, y: 0 });
          }}
          className="rounded-lg px-2 py-1.5 font-mono text-[11px] text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
        >
          {Math.round(zoom * 100)}%
        </button>
        <button
          type="button"
          title="Zoom in"
          onClick={() => clampZoom(zoom * 1.1)}
          className="rounded-lg p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink"
        >
          <Plus size={14} />
        </button>
      </div>

      <p className="flex items-center gap-1.5 border-t border-ink/10 bg-card px-5 py-2.5 text-[11px] text-ink-faint">
        <BookOpen size={12} />
        Drag to pan · scroll to zoom · click a node for its problems
      </p>

      {selected && (
        <PatternDetail pattern={selected} onClose={() => setSelectedKey(null)} />
      )}
    </div>
  );
}
