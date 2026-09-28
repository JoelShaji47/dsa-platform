"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  BookOpen,
  Check,
  ChevronRight,
  Flame,
  HelpCircle,
  Info,
  Loader2,
  Lock,
  LogOut,
  Minus,
  Plus,
  RefreshCcw,
  Settings2,
  Shuffle,
  Sparkles,
  Timer,
  Trash2,
  Trophy,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { Brand, DifficultyChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import type { Difficulty } from "@/lib/types";

// ── Layout tokens ──────────────────────────────────────────────────────────
const W = 172;
const H = 54;
const NODE_GAP = 26;
const BAND_PAD = 56;
const BAND_GAP = 64;
const SWAY = 22;
const TOP_PAD = 40;
const BOTTOM_PAD = 64;
const LEFT_OFFSET = 180;

const COLORS = {
  easy: "#00BFA5",
  medium: "#F0A000",
  hard: "#FF3B3B",
};

interface RoadmapProblem {
  slug: string;
  title: string;
  difficulty: Difficulty;
  solved: boolean;
  attempts: number;
  hints_used: number;
  solvable: boolean;
  recommended: boolean;
}

interface Pattern {
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

interface RoadmapData {
  patterns: Pattern[];
  totals: { solved: number; total: number };
}

interface DailyProblem {
  slug: string;
  title: string;
  solvable: boolean;
}

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
  const canvasW = LEFT_OFFSET + maxBandW + 2 * BAND_PAD;

  const pos: Record<string, [number, number]> = {};
  let prevBottom = TOP_PAD;
  orders.forEach((order, idx) => {
    const band = byOrder[order];
    const bandW = band.length * W + (band.length - 1) * NODE_GAP;
    const sway = idx % 2 ? SWAY : -SWAY;
    const startX = LEFT_OFFSET + (maxBandW - bandW) / 2 + sway;
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
  const bend = Math.min(56, Math.abs(x2 - x1) * 0.5);
  return {
    x1,
    y1,
    x2,
    y2,
    d: `M ${x1} ${y1} C ${x1} ${y1 + bend}, ${x2} ${y2 - bend}, ${x2} ${y2}`,
  };
}

function PatternNode({
  pattern,
  locked,
  selected,
  onClick,
}: {
  pattern: Pattern & { pos: [number, number] };
  locked: boolean;
  selected: boolean;
  highlighted: boolean;
  complete?: boolean;
  onClick: () => void;
}) {
  const [x, y] = pattern.pos;
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={locked}
      style={{ left: x, top: y, width: W, height: H, touchAction: "none" }}
      className={`roadmap-node absolute flex flex-col items-center justify-center px-3 text-center transition-all duration-150 ${
        locked
          ? "cursor-not-allowed opacity-40"
          : selected
            ? "-translate-y-0.5 border-[#d4a72c]"
            : "hover:-translate-y-1"
      }`}
    >
      <span className="flex items-center gap-1.5 font-display text-[0.8rem] font-semibold leading-tight text-[#f5f5f5]">
        {pattern.name}
        {pattern.complete ? <Check size={14} strokeWidth={3} className="shrink-0 text-[#00BFA5]" /> : null}
        {locked ? <Lock size={12} className="shrink-0 text-[#6f7c91]" /> : null}
      </span>
      <span className="mt-1 font-mono text-[0.68rem] font-semibold text-[#a6aebc]">
        {pattern.solved}/{pattern.total}
      </span>
      {!locked && (pattern.solved > 0 || pattern.complete) && (
        <span
          className={`absolute inset-x-3 bottom-1.5 h-0.5 rounded-full ${
            pattern.complete ? "bg-[#00BFA5]" : "bg-[#d4a72c]"
          }`}
        />
      )}
    </button>
  );
}

function polar(cx: number, cy: number, r: number, a: number): [number, number] {
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}
function arcPath(cx: number, cy: number, r: number, a0: number, a1: number) {
  const large = a1 - a0 > Math.PI ? 1 : 0;
  const [x0, y0] = polar(cx, cy, r, a0);
  const [x1, y1] = polar(cx, cy, r, a1);
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
}

function CircularProgress({ solved, total }: { solved: number; total: number }) {
  const size = 96;
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 8;
  const TAU = Math.PI * 2;
  const start = -Math.PI / 2;
  const frac = total > 0 ? Math.min(solved / total, 1) : 0;
  const end = start + frac * TAU;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <path
          d={arcPath(cx, cy, r, start, start + TAU)}
          fill="none"
          stroke="rgb(255 255 255 / 0.09)"
          strokeWidth={9}
          strokeLinecap="round"
        />
        {frac > 0 && (
          <path
            d={arcPath(cx, cy, r, start, end)}
            fill="none"
            stroke="#00BFA5"
            strokeWidth={9}
            strokeLinecap="round"
          />
        )}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[26px] font-bold leading-none text-[#f5f5f5]">
          {solved}
        </span>
        <span className="mt-0.5 font-mono text-[11px] text-[#9aa1ad]">/{total}</span>
      </div>
    </div>
  );
}

interface ActivityDay {
  date: string;
  count: number;
}

function computeStreaks(activity: ActivityDay[] | null) {
  const set = new Set(
    (activity || []).filter((d) => d.count > 0).map((d) => d.date)
  );
  const off = (iso: string, n: number) => {
    const d = new Date(iso + "T00:00:00");
    d.setDate(d.getDate() + n);
    return d.toISOString().slice(0, 10);
  };
  const today = new Date().toISOString().slice(0, 10);
  const anchor = set.has(today) ? today : set.has(off(today, -1)) ? off(today, -1) : null;
  let current = 0;
  if (anchor) {
    let d = anchor;
    while (set.has(d)) {
      current += 1;
      d = off(d, -1);
    }
  }
  const dates = [...set].sort();
  let best = 0;
  let run = 0;
  let prev: string | null = null;
  for (const d of dates) {
    if (prev && off(prev, 1) === d) run += 1;
    else run = 1;
    if (run > best) best = run;
    prev = d;
  }
  return { current, best };
}

function StatsDashboard({
  totals,
  diff,
  actionHandlers,
}: {
  totals: { solved: number; total: number } | undefined;
  diff: Record<string, number>;
  actionHandlers: (() => void)[];
}) {
  const rows = [
    { label: "Easy", solved: diff.EASY, total: diff.EASY_TOTAL, color: COLORS.easy },
    { label: "Medium", solved: diff.MEDIUM, total: diff.MEDIUM_TOTAL, color: COLORS.medium },
    { label: "Hard", solved: diff.HARD, total: diff.HARD_TOTAL, color: COLORS.hard },
  ];
  const solved = totals?.solved ?? 0;
  const total = totals?.total ?? 0;

  return (
    <div className="flex h-full flex-col gap-5 overflow-y-auto">
      <div className="rounded-[22px] border border-white/10 bg-[#242424] px-6 pb-6 pt-10 shadow-[0_20px_50px_-20px_rgb(0_0_0/0.7)]">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-4">
            {rows.map((r) => (
              <div key={r.label} className="flex items-baseline gap-6">
                <span className="flex items-center gap-2 text-[21px] font-semibold text-[#f5f5f5]">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: r.color }}
                  />
                  {r.label}
                </span>
                <span className="ml-auto pl-6 font-mono text-[19px] font-semibold text-[#b8b8b8]">
                  {r.solved}/{r.total}
                </span>
              </div>
            ))}
          </div>
          <CircularProgress solved={solved} total={total} />
        </div>

        <div className="mt-6 flex items-center justify-center gap-[18px]">
          {[
            { icon: Shuffle, tip: "Shuffle" },
            { icon: RefreshCcw, tip: "Reset" },
            { icon: Trash2, tip: "Delete" },
            { icon: HelpCircle, tip: "Help" },
            { icon: Settings2, tip: "Settings" },
          ].map(({ icon: Icon, tip }, i) => (
            <button
              key={tip}
              type="button"
              title={tip}
              onClick={actionHandlers[i]}
              className="flex h-[60px] w-[54px] items-center justify-center rounded-[14px] border border-white/10 bg-[#2a2a2a] text-[#b8b8b8] transition-all duration-150 hover:border-white/25 hover:bg-[#333] hover:text-[#f5f5f5]"
            >
              <Icon size={26} strokeWidth={1.8} />
            </button>
          ))}
        </div>
      </div>

      <StreakCard />
    </div>
  );
}

function StreakCard() {
  const [activity, setActivity] = useState<ActivityDay[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    client
      .get<{ days: ActivityDay[] }>("/roadmap/activity")
      .then((res) => {
        if (!cancelled) setActivity(res.data?.days || null);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const { current, best } = useMemo(() => computeStreaks(activity), [activity]);

  return (
    <div className="rounded-[22px] border border-white/10 bg-[#242424] px-5 pb-5 pt-6 shadow-[0_20px_50px_-20px_rgb(0_0_0/0.7)]">
      <div className="flex gap-3">
        <StreakMini label="Current Streak" value={current} icon={<Flame size={22} className="text-[#FF7A00]" />} />
        <StreakMini label="Best Streak" value={best} icon={<Trophy size={22} className="text-[#F0B900]" />} />
      </div>
      <p className="mt-4 flex items-center justify-center gap-1.5 text-center text-[15px] text-[#b8b8b8]">
        <Info size={15} className="shrink-0 text-[#9aa1ad]" />
        Solve one problem a day to keep your streak
      </p>
    </div>
  );
}

function StreakMini({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {
  return (
    <div className="flex h-[120px] flex-1 flex-col items-center justify-center gap-1 rounded-[14px] border border-white/10 bg-[#1f1f1f]">
      <span className="text-[14px] font-medium text-[#9aa1ad]">{label}</span>
      <span className="flex items-center gap-1.5 pt-1 font-display text-[24px] font-bold text-[#f5f5f5]">
        {icon}
        {value} days
      </span>
    </div>
  );
}

export default function RoadmapClient() {
  const { logout } = useAuth();
  const router = useRouter();
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [zoom, setZoom] = useState(0.8);
  const [loading, setLoading] = useState(true);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const sessionRef = useRef<{
    mode: string;
    startX: number;
    startY: number;
    panX: number;
    panY: number;
  } | null>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    client
      .get<RoadmapData>("/roadmap")
      .then((res) => {
        if (!cancelled) {
          setRoadmap(res.data);
          setSelectedKey(null);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const unlocked = useMemo(() => {
    const open = new Set<string>();
    if (!roadmap) return open;
    let changed = true;
    while (changed) {
      changed = false;
      for (const p of roadmap.patterns) {
        if (open.has(p.key)) continue;
        const prereqs = (p.prerequisites || []).filter((k) =>
          roadmap.patterns.some((x) => x.key === k)
        );
        if (
          prereqs.every(
            (k) => open.has(k) || roadmap.patterns.find((x) => x.key === k)?.complete
          )
        ) {
          open.add(p.key);
          changed = true;
        }
      }
    }
    return open;
  }, [roadmap]);

  const layout = useMemo(
    () => (roadmap ? computeLayout(roadmap.patterns) : null),
    [roadmap]
  );

  const byPattern = useMemo(() => {
    const map: Record<string, Pattern> = {};
    roadmap?.patterns.forEach((p) => (map[p.key] = p));
    return map;
  }, [roadmap]);

  const prereqPatterns = useMemo(() => {
    if (!roadmap || !selectedKey) return [];
    const sel = byPattern[selectedKey];
    if (!sel) return [];
    return (sel.prerequisites || [])
      .map((k) => byPattern[k])
      .filter(Boolean) as Pattern[];
  }, [roadmap, selectedKey, byPattern]);

  const totals = roadmap?.totals;
  const overallPct = totals && totals.total > 0 ? Math.round((totals.solved / totals.total) * 100) : 0;

  const diffTotals = useMemo(() => {
    const counts: Record<string, number> = { EASY: 0, MEDIUM: 0, HARD: 0 };
    roadmap?.patterns.forEach((p) =>
      p.problems.forEach((pr) => {
        if (counts[pr.difficulty] != null) counts[pr.difficulty] += 1;
      })
    );
    return counts;
  }, [roadmap]);

  const diffSolved = useMemo(() => {
    const counts: Record<string, number> = { EASY: 0, MEDIUM: 0, HARD: 0 };
    roadmap?.patterns.forEach((p) =>
      p.problems.forEach((pr) => {
        if (pr.solved && counts[pr.difficulty] != null) counts[pr.difficulty] += 1;
      })
    );
    return counts;
  }, [roadmap]);

  const diff = useMemo(
    () => ({
      EASY: diffSolved.EASY,
      MEDIUM: diffSolved.MEDIUM,
      HARD: diffSolved.HARD,
      EASY_TOTAL: diffTotals.EASY,
      MEDIUM_TOTAL: diffTotals.MEDIUM,
      HARD_TOTAL: diffTotals.HARD,
    }),
    [diffSolved, diffTotals]
  );

  const selectedPattern = selectedKey ? byPattern[selectedKey] : null;

  const handleSelect = (key: string) => setSelectedKey(key);

  const clampZoom = useCallback((z: number) => {
    setZoom(Math.min(1.5, Math.max(0.3, Number(z.toFixed(3)))));
  }, []);

  const fitView = () => {
    setZoom(0.8);
    setPan({ x: 0, y: 0 });
  };

  const onContainerPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.button !== 0 || sessionRef.current) return;
    sessionRef.current = {
      mode: "pan",
      startX: e.clientX,
      startY: e.clientY,
      panX: pan.x,
      panY: pan.y,
    };
    e.preventDefault();
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const s = sessionRef.current;
    if (!s) return;
    if (s.mode === "pan") {
      setPan({ x: s.panX + (e.clientX - s.startX), y: s.panY + (e.clientY - s.startY) });
    }
  };

  const onPointerEnd = () => {
    sessionRef.current = null;
  };

  const onWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    clampZoom(zoom * (e.deltaY < 0 ? 1.1 : 0.9));
  };

  const positions = useMemo(() => {
    if (!layout) return {};
    const out: Record<string, [number, number]> = {};
    for (const key of Object.keys(layout.pos)) {
      out[key] = layout.pos[key];
    }
    return out;
  }, [layout]);

  const edges = layout ? layout.edges.map(([s, t]) => edgePath(s, t, positions)) : [];

  const cardActions = [
    () => {},
    () => fitView(),
    () => {},
    () => {},
    () => {},
  ];

  return (
    <ProtectedRoute>
      <div className="relative h-screen w-full overflow-hidden bg-[#1e1e1e] text-[#f5f5f5]">
        <div
          ref={viewportRef}
          className="roadmap-canvas absolute inset-0 cursor-grab overflow-auto"
          onPointerDown={onContainerPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerEnd}
          onPointerCancel={onPointerEnd}
          onWheel={onWheel}
        >
          {loading ? (
            <div className="flex h-full items-center justify-center gap-2 text-[#9aa1ad]">
              <Loader2 size={20} className="animate-spin" />
              Charting your path…
            </div>
          ) : (
            layout &&
            roadmap && (
              <div
                style={{ width: layout.canvasW * zoom, height: (layout.canvasH + 40) * zoom }}
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
                  <svg width={layout.canvasW} height={layout.canvasH} className="absolute inset-0" aria-hidden>
                    <defs>
                      <marker
                        id="arrow"
                        viewBox="0 0 8 8"
                        refX="7"
                        refY="4"
                        markerWidth="5"
                        markerHeight="5"
                        orient="auto-start-reverse"
                      >
                        <path d="M 0 0 L 8 4 L 0 8 z" fill="#d4a72c" />
                      </marker>
                    </defs>
                    {edges.map((e, i) => (
                      <path key={i} d={e.d} className="roadmap-edge" markerEnd="url(#arrow)" />
                    ))}
                  </svg>
                  {roadmap.patterns.map((pattern) => {
                    const locked = !unlocked.has(pattern.key);
                    return (
                      <PatternNode
                        key={pattern.key}
                        pattern={{ ...pattern, pos: positions[pattern.key] }}
                        locked={locked}
                        complete={pattern.complete}
                        selected={selectedKey === pattern.key}
                        highlighted={prereqPatterns.some((p) => p.key === pattern.key)}
                        onClick={() => handleSelect(pattern.key)}
                      />
                    );
                  })}
                </div>
              </div>
            )
          )}
        </div>

        <div className="absolute left-4 top-4 z-30 flex items-center gap-3 rounded-2xl border border-white/10 bg-[#242424]/90 py-2.5 pl-4 pr-3 shadow-xl backdrop-blur-md">
          <Brand dark />
          <button
            type="button"
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="ml-1 flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 text-[#b8b8b8] transition-colors hover:border-[#FF3B3B]/50 hover:text-[#FF3B3B]"
            title="Log out"
          >
            <LogOut size={15} />
          </button>
        </div>

        <div className="absolute left-1/2 top-4 z-30 flex max-w-[92vw] -translate-x-1/2 items-center gap-4 rounded-2xl border border-white/10 bg-[#242424]/90 px-5 py-3 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div>
              <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-[#8b93a1]">
                Roadmap
              </p>
              <h1 className="mt-0.5 font-display text-lg font-bold leading-tight tracking-tight text-[#f5f5f5]">
                The DSA path
              </h1>
            </div>
          </div>

          <div className="flex min-w-[160px] flex-1 items-center gap-3">
            <div className="h-2 max-w-[380px] flex-1 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-[#d4a72c] transition-[width] duration-500"
                style={{ width: `${overallPct}%` }}
              />
            </div>
            <span className="font-mono text-sm font-bold text-[#f5f5f5]">
              {totals?.solved}/{totals?.total}
            </span>
          </div>

          <div className="flex items-center gap-5">
            <DifficultyStat label="Easy" color={COLORS.easy} solved={diffSolved.EASY} total={diffTotals.EASY} />
            <DifficultyStat label="Med" color={COLORS.medium} solved={diffSolved.MEDIUM} total={diffTotals.MEDIUM} />
            <DifficultyStat label="Hard" color={COLORS.hard} solved={diffSolved.HARD} total={diffTotals.HARD} />
          </div>

          <DailyQuestionChip />

          <Link
            href="/test"
            className="flex h-9 shrink-0 items-center gap-2 whitespace-nowrap rounded-[18px] border border-[#d4a72c]/40 bg-[#d4a72c]/15 px-3.5 text-sm font-semibold leading-none text-[#e8c860] transition-colors hover:bg-[#d4a72c]/25"
          >
            <Timer size={14} className="shrink-0" />
            Take a Test
          </Link>

          <div className="flex h-9 items-center gap-1 rounded-[18px] border border-white/10 bg-[#2a2a2a] px-1.5">
            <button type="button" onClick={fitView} className="flex h-7 w-7 items-center justify-center rounded-full text-[#b8b8b8] hover:bg-white/10 hover:text-[#f5f5f5]" title="Fit view">
              <RefreshCcw size={13} />
            </button>
            <button type="button" onClick={() => clampZoom(zoom - 0.1)} className="flex h-7 w-7 items-center justify-center rounded-full text-[#b8b8b8] hover:bg-white/10 hover:text-[#f5f5f5]" title="Zoom out">
              <Minus size={13} />
            </button>
            <button type="button" onClick={() => clampZoom(zoom + 0.1)} className="flex h-7 w-7 items-center justify-center rounded-full text-[#b8b8b8] hover:bg-white/10 hover:text-[#f5f5f5]" title="Zoom in">
              <Plus size={13} />
            </button>
          </div>
        </div>

        <aside className="absolute bottom-4 right-4 top-20 z-30 w-[340px] max-w-[92vw] overflow-hidden rounded-[22px] border border-white/10 bg-[#242424] shadow-[0_30px_70px_-30px_rgb(0_0_0/0.8)]">
          {selectedPattern ? (
            <div className="flex h-full flex-col">
              <PanelHeader
                pattern={selectedPattern}
                isRoot={!selectedPattern.prerequisites?.length}
                onClose={() => setSelectedKey(null)}
              />
              <div className="flex-1 overflow-y-auto px-5 pb-6">
                <PatternStats pattern={selectedPattern} />
                <ProblemList pattern={selectedPattern} />
              </div>
            </div>
          ) : (
            <StatsDashboard totals={totals} diff={diff} actionHandlers={cardActions} />
          )}
        </aside>
      </div>
    </ProtectedRoute>
  );
}

function PanelHeader({
  pattern,
  isRoot,
  onClose,
}: {
  pattern: Pattern | null;
  isRoot: boolean;
  onClose: () => void;
}) {
  if (!pattern) return null;
  return (
    <div className="border-b border-white/10 px-5 py-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-[#8b93a1]">
            {isRoot ? "Start here" : "Pattern"}
          </p>
          <h2 className="mt-1 font-display text-2xl font-bold leading-tight text-[#f5f5f5]">
            {pattern.name}
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 text-[#b8b8b8] transition-colors hover:border-white/25 hover:text-[#f5f5f5]"
          title="Back to dashboard"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M1 1l12 12M13 1L1 13" />
          </svg>
        </button>
      </div>
      <p className="mt-2 text-sm text-[#b8b8b8]">{pattern.snippet}</p>
      <Prerequisites pattern={pattern} />
      <div className="mt-3 flex items-center gap-3 font-mono text-xs text-[#9aa1ad]">
        <span>
          {pattern.solved}/{pattern.total} solved
        </span>
        <span className="text-white/15">·</span>
        <span>{pattern.mastery}% mastered</span>
        {pattern.complete && (
          <span className="rounded-md border border-[#00BFA5]/50 bg-[#00BFA5]/10 px-2 py-0.5 text-[#00BFA5]">
            Mastered
          </span>
        )}
      </div>
    </div>
  );
}

function PatternStats({ pattern }: { pattern: Pattern }) {
  const counts: Record<string, number> = { EASY: 0, MEDIUM: 0, HARD: 0 };
  pattern.problems.forEach((p) => {
    if (counts[p.difficulty] != null) counts[p.difficulty] += 1;
  });
  const solvedCounts: Record<string, number> = { EASY: 0, MEDIUM: 0, HARD: 0 };
  pattern.problems.forEach((p) => {
    if (p.solved && solvedCounts[p.difficulty] != null) solvedCounts[p.difficulty] += 1;
  });
  const stats = [
    { label: "Easy", solved: solvedCounts.EASY, total: counts.EASY, color: COLORS.easy },
    { label: "Medium", solved: solvedCounts.MEDIUM, total: counts.MEDIUM, color: COLORS.medium },
    { label: "Hard", solved: solvedCounts.HARD, total: counts.HARD, color: COLORS.hard },
  ];
  return (
    <div className="mb-4 mt-4 flex items-center gap-4 rounded-xl border border-white/10 bg-[#1f1f1f] px-4 py-3">
      {stats.map((s) => (
        <div key={s.label} className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: s.color }} />
          <span className="font-mono text-xs text-[#b8b8b8]">
            {s.label}{" "}
            <span className="font-bold text-[#f5f5f5]">{s.solved}/{s.total}</span>
          </span>
        </div>
      ))}
    </div>
  );
}

function Prerequisites({ pattern }: { pattern: Pattern }) {
  const prereqs = pattern.prerequisites || [];
  if (!prereqs.length) {
    return (
      <p className="mt-3 flex items-center gap-2 rounded-lg border border-[#d4a72c]/30 bg-[#d4a72c]/10 px-3 py-2 text-xs text-[#e8c96a]">
        <Sparkles size={13} className="text-[#d4a72c]" />
        Foundation pattern — no prerequisites. Kick off the roadmap here.
      </p>
    );
  }
  return (
    <div className="mt-3">
      <p className="mb-1.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-[#8b93a1]">
        Prerequisites
      </p>
      <div className="flex flex-wrap gap-1.5">
        {prereqs.map((p) => (
          <span
            key={p}
            className="flex items-center gap-1 rounded-md border border-[#d4a72c]/30 bg-[#d4a72c]/10 px-2 py-1 font-mono text-[0.7rem] font-semibold text-[#e8c96a]"
          >
            <BookOpen size={11} />
            {p.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
          </span>
        ))}
      </div>
    </div>
  );
}

function ProblemList({ pattern }: { pattern: Pattern }) {
  const solvableCount = pattern.problems.filter((p) => p.solvable).length;
  return (
    <div className="mt-4">
      <p className="mb-2 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-[#8b93a1]">
        Problems
      </p>
      <ul className="space-y-1.5">
        {pattern.problems.map((problem, i) => {
          const solvable = problem.solvable;
          const isRec = problem.recommended && solvable;
          return (
            <li
              key={problem.slug}
              className={`flex items-center gap-3 rounded-xl px-3 py-2 transition-colors ${
                isRec ? "bg-[#d4a72c]/10" : "hover:bg-white/5"
              }`}
            >
              {problem.solved ? (
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#00BFA5] text-sm font-bold text-[#0d1216] shadow-sm">
                  <Check size={15} strokeWidth={3.5} />
                </span>
              ) : (
                <span
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 font-mono text-sm font-bold ${
                    problem.difficulty === "EASY"
                      ? "border-[#00BFA5] text-[#00BFA5]"
                      : problem.difficulty === "MEDIUM"
                        ? "border-[#F0A000] text-[#F0A000]"
                        : "border-[#FF3B3B] text-[#FF3B3B]"
                  }`}
                >
                  {i + 1}
                </span>
              )}

              {solvable ? (
                <Link
                  href={`/problems/${problem.slug}/solve`}
                  className="flex min-w-0 flex-1 items-center justify-between gap-2 text-[0.9rem] font-medium text-[#f5f5f5] hover:text-[#e8c96a]"
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <span className="truncate">{problem.title}</span>
                    {isRec && (
                      <span className="flex items-center gap-1 rounded-md border border-[#d4a72c] bg-[#d4a72c]/15 px-1.5 py-0.5 text-[0.6rem] font-bold text-[#e8c96a]">
                        <Sparkles size={10} />Next
                      </span>
                    )}
                  </span>
                  <DifficultyChip difficulty={problem.difficulty} />
                </Link>
              ) : (
                <div className="flex min-w-0 flex-1 items-center justify-between gap-2 text-[0.9rem] font-medium text-[#9aa1ad]">
                  <span className="flex min-w-0 items-center gap-2">
                    <span className="truncate">{problem.title}</span>
                    <span className="rounded-md border border-white/10 bg-white/5 px-1.5 py-0.5 text-[0.6rem] font-semibold text-[#9aa1ad]">
                      Coming soon
                    </span>
                  </span>
                  <DifficultyChip difficulty={problem.difficulty} />
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {solvableCount < pattern.problems.length && (
        <p className="mt-3 border-t border-white/10 px-3 py-2 text-[0.7rem] text-[#9aa1ad]">
          {pattern.problems.length - solvableCount} more problem
          {pattern.problems.length - solvableCount === 1 ? "" : "s"} queued for authoring.
        </p>
      )}
    </div>
  );
}

function DailyQuestionChip() {
  const [daily, setDaily] = useState<DailyProblem | null>(null);
  useEffect(() => {
    let cancelled = false;
    client
      .get<{ problem: DailyProblem | null }>("/roadmap/daily")
      .then((res) => {
        if (!cancelled && res.data?.problem) setDaily(res.data.problem);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);
  if (!daily) return null;
  return (
    <Link
      href={daily.solvable ? `/problems/${daily.slug}/solve` : `/problems/${daily.slug}`}
      className="group flex h-9 shrink-0 items-center gap-2 whitespace-nowrap rounded-[18px] border border-[#d4a72c]/30 bg-[#d4a72c]/10 px-3 transition-colors hover:bg-[#d4a72c]/15"
      title={`Daily question: ${daily.title}`}
    >
      <Flame size={15} className="shrink-0 text-[#FF7A00]" />
      <span className="font-display text-[0.66rem] font-bold uppercase tracking-wider text-[#e8c96a]">
        Daily
      </span>
      <span className="hidden max-w-[140px] truncate text-sm font-medium text-[#f5f5f5] xl:block">
        {daily.title}
      </span>
      <ChevronRight size={13} className="shrink-0 text-[#9aa1ad] transition-transform group-hover:translate-x-0.5" />
    </Link>
  );
}

function DifficultyStat({
  label,
  color,
  solved,
  total,
}: {
  label: string;
  color: string;
  solved: number;
  total: number;
}) {
  return (
    <div className="flex min-w-[64px] items-center gap-2">
      <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: color }} />
      <div>
        <p className="font-mono text-[0.58rem] uppercase tracking-wider text-[#8b93a1]">{label}</p>
        <p className="font-mono text-[0.85rem] font-bold leading-tight text-[#f5f5f5]">
          {solved}/{total}
        </p>
      </div>
    </div>
  );
}
