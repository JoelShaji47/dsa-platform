import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Check,
  ChevronRight,
  Flame,
  Loader2,
  Lock,
  Maximize,
  Minus,
  Plus,
  Sparkles,
  Zap,
} from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import { TopBar, UserChip, DifficultyChip } from '../components/Shell'

// Canvas geometry for the DAG. Each node is W x H; top-left (x, y).
const W = 180
const H = 56
const NODE_POS = {
  'arrays-hashing': [430, 20],
  'two-pointers': [60, 210],
  'sliding-window': [430, 210],
  subarray: [800, 210],
  'linked-list': [190, 400],
  stack: [640, 400],
  queue: [60, 590],
  'dp-1d': [250, 590],
  'binary-tree': [430, 590],
  graph: [640, 590],
  'dp-2d': [340, 780],
}
// Edges are drawn bottom-center(source) -> top-center(target).
const EDGES = [
  ['arrays-hashing', 'two-pointers'],
  ['arrays-hashing', 'sliding-window'],
  ['arrays-hashing', 'subarray'],
  ['arrays-hashing', 'linked-list'],
  ['arrays-hashing', 'stack'],
  ['sliding-window', 'queue'],
  ['sliding-window', 'dp-1d'],
  ['stack', 'binary-tree'],
  ['binary-tree', 'graph'],
  ['binary-tree', 'dp-1d'],
  ['dp-1d', 'dp-2d'],
]
const CANVAS_W = 980
const CANVAS_H = 840

function edgePath(source, target) {
  const [sx, sy] = NODE_POS[source]
  const [tx, ty] = NODE_POS[target]
  const x1 = sx + W / 2
  const y1 = sy + H
  const x2 = tx + W / 2
  const y2 = ty
  const bend = Math.min(48, Math.abs(x2 - x1) * 0.5)
  return { x1, y1, x2, y2, d: `M ${x1} ${y1} C ${x1} ${y1 + bend}, ${x2} ${y2 - bend}, ${x2} ${y2}` }
}

function PatternNode({ pattern, locked, complete, isRecommended, selected, onClick }) {
  const [x, y] = NODE_POS[pattern.key]
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={locked}
      style={{
        left: x,
        top: y,
        width: W,
        height: H,
        transform: isRecommended
          ? 'translateY(-2px)'
          : selected
            ? 'translateY(-1px)'
            : undefined,
      }}
      className={`absolute flex flex-col items-center justify-center rounded-2xl px-3 text-left transition-all duration-150 ${
        locked
          ? 'cursor-not-allowed opacity-45'
          : selected
            ? 'shadow-card'
            : 'hover:-translate-y-1 hover:shadow-card'
      } ${isRecommended ? 'shadow-glow-sm' : 'shadow-card'}`}
    >
      {isRecommended && (
        <>
          <span className="absolute inset-0 -z-10 rounded-2xl bg-gold/20 animate-ping-slow" />
          <Sparkles size={15} className="absolute right-2 top-2 rotate-12 text-gold-deep" />
        </>
      )}
      <span className="flex items-center gap-1.5 font-display text-[0.82rem] font-bold leading-tight text-ink">
        {pattern.name}
        {complete ? (
          <Check size={14} strokeWidth={3} className="shrink-0 text-quest" />
        ) : null}
        {locked ? <Lock size={12} className="shrink-0 text-ink-faint" /> : null}
      </span>
      <span className="mt-1 font-mono text-[0.66rem] font-semibold text-ink-faint">
        {pattern.solved}/{pattern.total}
      </span>
    </button>
  )
}

export default function Roadmap() {
  const { user } = useAuth()
  const [roadmap, setRoadmap] = useState(null)
  const [selectedKey, setSelectedKey] = useState('arrays-hashing')
  const [zoom, setZoom] = useState(0.9)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    client.get('/roadmap')
      .then((res) => {
        if (!cancelled) setRoadmap(res.data)
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Which patterns are reachable given prerequisites.
  const unlocked = useMemo(() => {
    const open = new Set()
    if (!roadmap) return open
    let changed = true
    while (changed) {
      changed = false
      for (const p of roadmap.patterns) {
        if (open.has(p.key)) continue
        const prereqs = (p.prerequisites || []).filter((k) =>
          roadmap.patterns.some((x) => x.key === k),
        )
        if (prereqs.every((k) => open.has(k) || roadmap.patterns.find((x) => x.key === k)?.complete)) {
          open.add(p.key)
          changed = true
        }
      }
    }
    return open
  }, [roadmap])

  const totals = roadmap?.totals
  const byPattern = useMemo(() => {
    const map = {}
    roadmap?.patterns.forEach((p) => (map[p.key] = p))
    return map
  }, [roadmap])

  const recommendedPatternKey = useMemo(() => {
    if (!roadmap) return null
    let found = null
    for (const p of roadmap.patterns)
      for (const pr of p.problems)
        if (pr.recommended) {
          found = p.key
          break
        }
    return found
  }, [roadmap])

  // Difficulty totals across the whole roadmap.
  const diffTotals = useMemo(() => {
    const counts = { EASY: 0, MEDIUM: 0, HARD: 0 }
    roadmap?.patterns.forEach((p) =>
      p.problems.forEach((pr) => {
        if (counts[pr.difficulty] != null) counts[pr.difficulty] += 1
      }),
    )
    return counts
  }, [roadmap])

  const diffSolved = useMemo(() => {
    const counts = { EASY: 0, MEDIUM: 0, HARD: 0 }
    roadmap?.patterns.forEach((p) =>
      p.problems.forEach((pr) => {
        if (pr.solved && counts[pr.difficulty] != null) counts[pr.difficulty] += 1
      }),
    )
    return counts
  }, [roadmap])

  const selectedPattern = roadmap?.patterns.find((p) => p.key === selectedKey) ?? roadmap?.patterns[0]
  const overallPct = totals ? Math.round((totals.solved / totals.total) * 100) : 0
  const zoomStep = 0.15

  const edges = useMemo(() => EDGES.map(([s, t]) => edgePath(s, t)), [])

  const clampZoom = useCallback((z) => {
    setZoom(Math.min(1.6, Math.max(0.5, Number(z.toFixed(2)))))
  }, [])

  return (
    <div className="min-h-screen">
      <TopBar active="roadmap">
        <UserChip username={user.username} />
      </TopBar>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* ── Header ─────────────────────────────────────────── */}
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Roadmap</p>
            <h1 className="mt-1.5 font-display text-4xl font-bold tracking-tight text-ink">
              The DSA roadmap
            </h1>
            <p className="mt-1 max-w-2xl text-[1.02rem] text-ink-soft">
              Work through the patterns — each unlocks the next. Your tutor highlights the single
              best problem to tackle next.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="panel flex items-center gap-3 px-4 py-2.5">
              <Flame size={18} className="text-rust" />
              <div>
                <p className="font-mono text-[0.62rem] uppercase tracking-wide text-ink-faint">Streak</p>
                <p className="font-display text-lg font-bold leading-none text-ink">
                  {user.current_streak ?? 0} days
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* ── Progress summary bar ───────────────────────────── */}
        <section className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-3 rounded-2xl border border-ink/10 bg-paper px-5 py-4">
          <div className="flex min-w-[120px] flex-1 items-center gap-4">
            <div className="w-full">
              <div className="flex items-baseline justify-between">
                <span className="eyebrow">Solved</span>
                <span className="font-mono text-sm font-bold text-ink">
                  {totals?.solved}/{totals?.total}
                </span>
              </div>
              <div className="mt-1.5 h-2.5 w-full overflow-hidden rounded-full bg-paper-deep">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-gold to-quest transition-[width] duration-500"
                  style={{ width: `${overallPct}%` }}
                />
              </div>
            </div>
          </div>
          <DifficultyStat label="Easy" color="bg-quest" solved={diffSolved.EASY} total={diffTotals.EASY} />
          <DifficultyStat label="Medium" color="bg-gold" solved={diffSolved.MEDIUM} total={diffTotals.MEDIUM} />
          <DifficultyStat label="Hard" color="bg-rust" solved={diffSolved.HARD} total={diffTotals.HARD} />
        </section>

        {/* ── Graph canvas ───────────────────────────────────── */}
        <section className="relative mt-6 overflow-hidden rounded-2xl border border-ink/10 bg-paper">
          {/* zoom controls */}
          <div className="absolute right-4 top-4 z-20 flex items-center gap-1 rounded-xl border border-ink/10 bg-white p-1 shadow-card">
            <button
              type="button"
              onClick={() => clampZoom(zoom - zoomStep)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-soft hover:bg-paper-deep hover:text-ink"
              title="Zoom out"
            >
              <Minus size={16} />
            </button>
            <span className="w-10 text-center font-mono text-xs font-bold text-ink">
              {Math.round(zoom * 100)}%
            </span>
            <button
              type="button"
              onClick={() => clampZoom(zoom + zoomStep)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-soft hover:bg-paper-deep hover:text-ink"
              title="Zoom in"
            >
              <Plus size={16} />
            </button>
            <button
              type="button"
              onClick={() => setZoom(0.9)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-soft hover:bg-paper-deep hover:text-ink"
              title="Reset view"
            >
              <Maximize size={15} />
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center gap-2 py-32 text-ink-soft">
              <Loader2 size={20} className="animate-spin" />
              Charting your path…
            </div>
          ) : (
            <div className="overflow-auto" style={{ maxHeight: '70vh' }}>
              <div
                style={{
                  width: CANVAS_W,
                  height: CANVAS_H,
                  transform: `scale(${zoom})`,
                  transformOrigin: 'top left',
                }}
                className="relative"
              >
                <svg
                  width={CANVAS_W}
                  height={CANVAS_H}
                  className="absolute inset-0"
                  aria-hidden
                >
                  <defs>
                    <marker
                      id="arrow"
                      viewBox="0 0 10 10"
                      refX="8"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="rgb(201 162 39 / 0.6)" />
                    </marker>
                  </defs>
                  {edges.map((e, i) => (
                    <path
                      key={i}
                      d={e.d}
                      fill="none"
                      stroke="rgb(201 162 39 / 0.55)"
                      strokeWidth={2}
                      strokeLinecap="round"
                      markerEnd="url(#arrow)"
                    />
                  ))}
                </svg>

                {roadmap?.patterns.map((pattern) => {
                  const locked = !unlocked.has(pattern.key)
                  const isRecommended = pattern.key === recommendedPatternKey
                  return (
                    <PatternNode
                      key={pattern.key}
                      pattern={pattern}
                      locked={locked}
                      complete={pattern.complete}
                      isRecommended={isRecommended}
                      selected={selectedKey === pattern.key}
                      onClick={() => setSelectedKey(pattern.key)}
                    />
                  )
                })}
              </div>
            </div>
          )}
        </section>

        {/* ── Selected pattern detail ────────────────────────── */}
        <section className="mt-6 panel p-6">
          {selectedPattern ? (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="eyebrow">{selectedPattern.key.split('-').join(' · ')}</p>
                  <h2 className="mt-1 font-display text-2xl font-bold text-ink">
                    {selectedPattern.name}
                  </h2>
                  <p className="mt-1 text-sm text-ink-soft">{selectedPattern.snippet}</p>
                </div>
                <div className="flex items-center gap-2 font-mono text-sm text-ink-faint">
                  {selectedPattern.solved}/{selectedPattern.total} solved ·{' '}
                  {selectedPattern.mastery}% mastered
                  {selectedPattern.complete && (
                    <span className="stamp-chip border-quest bg-quest/10 text-quest">Mastered</span>
                  )}
                </div>
              </div>

              <ul className="mt-5 overflow-hidden rounded-xl border border-ink/10">
                <li className="grid grid-cols-[40px_1fr_auto] items-center gap-3 bg-paper-deep px-4 py-2 font-mono text-[0.62rem] uppercase tracking-wider text-ink-faint">
                  <span>Done</span>
                  <span>Problem</span>
                  <span>Difficulty</span>
                </li>
                {selectedPattern.problems.map((problem) => {
                  const isRec = problem.recommended
                  return (
                    <li
                      key={problem.slug}
                      className={`grid grid-cols-[40px_1fr_auto] items-center gap-3 border-t border-ink/6 px-4 py-3 transition-colors ${
                        isRec ? 'bg-gold/10' : 'hover:bg-paper-deep'
                      }`}
                    >
                      <span className="flex items-center justify-center">
                        {problem.solved ? (
                          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-quest">
                            <Check size={12} strokeWidth={3.5} className="text-white" />
                          </span>
                        ) : (
                          <span
                            className={`h-5 w-5 rounded-full border-2 ${
                              problem.difficulty === 'EASY'
                                ? 'border-quest'
                                : problem.difficulty === 'MEDIUM'
                                  ? 'border-gold'
                                  : 'border-rust'
                            }`}
                          />
                        )}
                      </span>
                      <Link
                        to={`/problems/${problem.slug}/solve`}
                        className="flex items-center gap-2 text-[0.95rem] font-medium text-ink hover:text-gold-deep"
                      >
                        <span className="truncate">{problem.title}</span>
                        {isRec && (
                          <span className="stamp-chip shrink-0 border-gold bg-gold/15 text-gold-deep">
                            <Sparkles size={11} className="mr-1 inline" />Next
                          </span>
                        )}
                        <ChevronRight size={15} className="shrink-0 text-ink-faint" />
                      </Link>
                      <div className="flex justify-end">
                        <DifficultyChip difficulty={problem.difficulty} />
                      </div>
                    </li>
                  )
                })}
              </ul>
            </>
          ) : (
            <p className="py-8 text-center text-ink-soft">Select a pattern to see its problems.</p>
          )}
        </section>
      </main>
    </div>
  )
}

function DifficultyStat({ label, color, solved, total }) {
  return (
    <div className="flex min-w-[104px] items-center gap-2.5">
      <span className={`h-3 w-3 shrink-0 rounded-full ${color}`} />
      <div>
        <p className="font-mono text-[0.6rem] uppercase tracking-wide text-ink-faint">{label}</p>
        <p className="font-mono text-sm font-bold leading-tight text-ink">
          {solved}/{total}
        </p>
      </div>
    </div>
  )
}
