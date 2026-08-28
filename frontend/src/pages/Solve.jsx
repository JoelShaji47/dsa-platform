import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Award,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Loader2,
  Play,
  Send,
  Sparkles,
  XCircle,
  Zap,
} from 'lucide-react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { cpp } from '@codemirror/lang-cpp'
import { java } from '@codemirror/lang-java'
import { oneDark } from '@codemirror/theme-one-dark'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

const LANGS = [
  { key: 'python', label: 'Python', ext: python() },
  { key: 'cpp', label: 'C++', ext: cpp() },
  { key: 'java', label: 'Java', ext: java() },
]

const STATUS_STYLES = {
  ACCEPTED: {
    chip: 'border-emerald-500/50 bg-emerald-500/15 text-emerald-400',
    icon: <CheckCircle2 size={16} />,
    label: 'Accepted',
  },
  WRONG_ANSWER: {
    chip: 'border-red-500/50 bg-red-500/15 text-red-400',
    icon: <XCircle size={16} />,
    label: 'Wrong Answer',
  },
  TLE: {
    chip: 'border-yellow-500/50 bg-yellow-500/15 text-yellow-300',
    icon: <XCircle size={16} />,
    label: 'Time Limit Exceeded',
  },
  RUNTIME_ERROR: {
    chip: 'border-orange-500/50 bg-orange-500/15 text-orange-300',
    icon: <XCircle size={16} />,
    label: 'Runtime Error',
  },
  COMPILATION_ERROR: {
    chip: 'border-purple-500/50 bg-purple-500/15 text-purple-300',
    icon: <XCircle size={16} />,
    label: 'Compilation Error',
  },
}

const DIFFICULTY_STYLE = {
  EASY: 'text-emerald-400',
  MEDIUM: 'text-yellow-300',
  HARD: 'text-red-400',
}

function TestChip({ passed, index }) {
  return (
    <span
      title={`Test ${index + 1}: ${passed ? 'passed' : 'failed'}`}
      className={`flex h-7 w-7 items-center justify-center rounded-md border font-mono text-xs font-bold ${
        passed
          ? 'border-emerald-500/50 bg-emerald-500/15 text-emerald-400'
          : 'border-red-500/50 bg-red-500/15 text-red-400'
      }`}
    >
      {index + 1}
    </span>
  )
}

export default function Solve() {
  const { slug } = useParams()
  const { user } = useAuth()
  const [problem, setProblem] = useState(null)
  const [pageStatus, setPageStatus] = useState('loading')
  const [unavailable, setUnavailable] = useState(false)
  const [lang, setLang] = useState('python')
  const [code, setCode] = useState('')
  const [running, setRunning] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [runResult, setRunResult] = useState(null)
  const [submitResult, setSubmitResult] = useState(null)
  const [error, setError] = useState(null)
  const [hintMeta, setHintMeta] = useState(null)
  const [revealedHints, setRevealedHints] = useState({})
  const [armedHint, setArmedHint] = useState(null)
  const [loadingHint, setLoadingHint] = useState(null)
  const [review, setReview] = useState(null)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [consoleOpen, setConsoleOpen] = useState(false)
  const [consoleTab, setConsoleTab] = useState('result')

  useEffect(() => {
    let cancelled = false
    client
      .get(`/problems/${slug}`)
      .then((res) => {
        if (cancelled) return
        setProblem(res.data)
        setUnavailable(!res.data.solvable)
        setCode(res.data.starter_code.python)
        setPageStatus('ok')
        return client.get(`/problems/${slug}/hints`)
      })
      .then((res) => {
        if (cancelled || !res) return
        setHintMeta(res.data)
      })
      .catch(() => {
        if (!cancelled) setPageStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [slug])

  useEffect(() => {
    if (problem && problem.starter_code[lang]) {
      setCode(problem.starter_code[lang])
    }
  }, [lang, problem])

  const activeLang = useMemo(() => LANGS.find((l) => l.key === lang), [lang])

  const run = useCallback(async () => {
    setRunning(true)
    setError(null)
    setSubmitResult(null)
    try {
      const res = await client.post(
        `/problems/${slug}/run`,
        { language: lang, source_code: code },
        { timeout: 120000 },
      )
      setRunResult(res.data)
      setConsoleOpen(true)
      setConsoleTab('result')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not reach the judge. Try again.')
    } finally {
      setRunning(false)
    }
  }, [slug, lang, code])

  const submit = useCallback(async () => {
    setSubmitting(true)
    setError(null)
    setRunResult(null)
    setReview(null)
    try {
      const res = await client.post(
        `/problems/${slug}/submit`,
        { language: lang, source_code: code },
        { timeout: 120000 },
      )
      setSubmitResult(res.data)
      setConsoleOpen(true)
      setConsoleTab('result')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not reach the judge. Try again.')
    } finally {
      setSubmitting(false)
    }
  }, [slug, lang, code])

  const revealHint = useCallback(
    async (level) => {
      setLoadingHint(level)
      setError(null)
      try {
        const res = await client.post(`/problems/${slug}/hints/${level}`)
        setRevealedHints((prev) => ({ ...prev, [level]: res.data.content }))
        setHintMeta((prev) =>
          prev
            ? {
                ...prev,
                levels: prev.levels.map((l) =>
                  l.level === level ? { ...l, revealed: true } : l,
                ),
              }
            : prev,
        )
        setArmedHint(null)
      } catch (err) {
        setError(err.response?.data?.detail || 'Could not load the hint. Try again.')
      } finally {
        setLoadingHint(null)
      }
    },
    [slug],
  )

  const onHintClick = useCallback(
    (level) => {
      if (revealedHints[level]) {
        return
      }
      if (hintMeta?.xp_forfeit_applies && armedHint !== level) {
        setArmedHint(level)
        return
      }
      revealHint(level)
    },
    [revealedHints, hintMeta, armedHint, revealHint],
  )

  const fetchReview = useCallback(async () => {
    if (!submitResult) return
    setReviewLoading(true)
    setError(null)
    try {
      const res = await client.post(`/submissions/${submitResult.submission_id}/review`)
      setReview(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not get an AI review. Try again.')
    } finally {
      setReviewLoading(false)
    }
  }, [submitResult])

  if (pageStatus === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center gap-2 bg-[#1a1a2e] text-gray-400">
        <Loader2 size={20} className="animate-spin" />
        Loading...
      </div>
    )
  }

  if (pageStatus === 'error') {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-[#1a1a2e]">
        <p className="text-lg text-gray-300">This problem does not exist.</p>
        <Link to="/problems" className="font-semibold text-emerald-400 hover:underline">
          Back to the library
        </Link>
      </div>
    )
  }

  if (unavailable) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-[#1a1a2e] px-6 text-center">
        <p className="text-2xl font-bold text-gray-100">Coming soon</p>
        <p className="max-w-md text-gray-400">
          "{problem.title}" is in the roadmap catalog but hasn't been fully authored yet
          (no starter code or test cases). It will be solvable once it's added to the library.
        </p>
        <Link to="/problems" className="font-semibold text-emerald-400 hover:underline">
          Back to library
        </Link>
      </div>
    )
  }

  const shown = submitResult || runResult
  const statement = problem.description.replace(/^#\s+.+\r?\n+/, '')

  return (
    <div className="flex h-screen flex-col bg-[#1a1a2e]">
      {/* ── Top bar ──────────────────────────────────────────── */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-white/10 bg-[#1e1e30] px-4">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            to="/problems"
            className="flex items-center gap-1.5 rounded-md px-2 py-1 text-sm text-gray-400 transition-colors hover:text-gray-200"
          >
            <ArrowLeft size={15} />
            Library
          </Link>
          <span className="h-4 w-px bg-white/10" />
          <h1 className="truncate text-sm font-semibold text-gray-100">
            {problem.title}
          </h1>
          <span className={`text-xs font-medium ${DIFFICULTY_STYLE[problem.difficulty]}`}>
            {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
          </span>
          {problem.solved && (
            <span className="rounded-md border border-emerald-500/50 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">
              Solved
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Language selector */}
          <div className="flex gap-0.5 rounded-lg border border-white/10 bg-[#252540] p-0.5">
            {LANGS.map((l) => (
              <button
                key={l.key}
                onClick={() => setLang(l.key)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                  lang === l.key
                    ? 'bg-white/10 text-gray-100'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          {/* Run + Submit */}
          <button
            onClick={run}
            disabled={running || submitting}
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#252540] px-3 py-1.5 text-xs font-medium text-gray-300 transition-colors hover:border-white/20 hover:text-gray-100 disabled:opacity-50"
          >
            {running ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} />}
            Run
          </button>
          <button
            onClick={submit}
            disabled={running || submitting}
            className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-500 disabled:opacity-50"
          >
            {submitting ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
            Submit
          </button>
        </div>
      </header>

      {/* ── Main content: two-panel split ────────────────────── */}
      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        {/* Left: problem description */}
        <section className="min-h-0 w-full overflow-y-auto border-b border-white/10 p-5 lg:w-[45%] lg:border-b-0 lg:border-r lg:border-white/10">
          <article className="prose prose-invert max-w-none text-[15px] leading-relaxed prose-headings:text-gray-100 prose-p:text-gray-300 prose-strong:text-white prose-code:rounded prose-code:bg-white/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-emerald-400 prose-code:before:content-none prose-code:after:content-none">
            <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
          </article>

          {/* Hints */}
          {hintMeta && (
            <div className="mt-6 rounded-xl border border-white/10 bg-[#1e1e30] p-4">
              <p className="flex items-center gap-2 text-sm font-semibold text-gray-200">
                <Lightbulb size={15} className="text-yellow-400" />
                Hints
                <span className="text-xs font-normal text-gray-500">
                  Viewing any hint forfeits first-solve XP
                </span>
              </p>
              <div className="mt-3 space-y-1.5">
                {hintMeta.levels.map((entry) => (
                  <div key={entry.level} className="overflow-hidden rounded-lg border border-white/10">
                    <button
                      onClick={() => onHintClick(entry.level)}
                      disabled={loadingHint !== null}
                      className={`flex w-full items-center gap-2 px-3 py-2.5 text-left text-sm transition-colors ${
                        entry.revealed || armedHint === entry.level
                          ? 'bg-yellow-500/10 text-yellow-300'
                          : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                      } disabled:opacity-50`}
                    >
                      {loadingHint === entry.level ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Lightbulb
                          size={14}
                          className={entry.revealed || armedHint === entry.level ? 'text-yellow-400' : ''}
                        />
                      )}
                      Level {entry.level}: {entry.label}
                      {!entry.revealed && (
                        <span className="ml-auto text-xs text-gray-500">
                          {hintMeta.xp_forfeit_applies
                            ? armedHint === entry.level
                              ? 'Click again — XP will be forfeited'
                              : 'Reveal · costs XP'
                            : 'Reveal'}
                        </span>
                      )}
                    </button>
                    {revealedHints[entry.level] && (
                      <div className="border-t border-white/10 bg-white/[0.02] px-3 py-2.5">
                        <article className="prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                          <Markdown remarkPlugins={[remarkGfm]}>
                            {revealedHints[entry.level]}
                          </Markdown>
                        </article>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Right: code editor + console */}
        <section className="flex min-h-0 min-w-0 flex-1 flex-col">
          {/* Code editor */}
          <div className="min-h-0 flex-1 overflow-hidden">
            <CodeMirror
              value={code}
              height="100%"
              style={{ fontSize: '14px', height: '100%' }}
              theme={oneDark}
              extensions={[activeLang.ext]}
              onChange={setCode}
              basicSetup={{ tabSize: 4 }}
            />
          </div>

          {/* Console bar */}
          <div className="flex h-9 shrink-0 items-center justify-between border-t border-white/10 bg-[#1e1e30] px-4">
            <button
              onClick={() => setConsoleOpen((o) => !o)}
              className="flex items-center gap-1.5 text-xs font-medium text-gray-400 hover:text-gray-200"
            >
              Console
              {consoleOpen ? <ChevronDown size={13} /> : <ChevronUp size={13} />}
            </button>
            {shown && (
              <span className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[shown.status]?.chip || 'text-gray-400'}`}>
                {STATUS_STYLES[shown.status]?.icon}
                {STATUS_STYLES[shown.status]?.label}
              </span>
            )}
          </div>

          {/* Console panel */}
          {consoleOpen && (
            <div className="max-h-[40vh] shrink-0 overflow-y-auto border-t border-white/10 bg-[#16162a]">
              {/* Error */}
              {error && (
                <div className="border-b border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              {/* Tabs */}
              {shown && (
                <div className="flex border-b border-white/10">
                  <button
                    onClick={() => setConsoleTab('result')}
                    className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                      consoleTab === 'result'
                        ? 'border-emerald-400 text-emerald-400'
                        : 'border-transparent text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    Result
                  </button>
                  <button
                    onClick={() => setConsoleTab('testcase')}
                    className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
                      consoleTab === 'testcase'
                        ? 'border-emerald-400 text-emerald-400'
                        : 'border-transparent text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    Testcase
                  </button>
                </div>
              )}

              {/* Result tab content */}
              {shown && consoleTab === 'result' && (
                <div className="p-4">
                  {/* XP + badges (submit only) */}
                  {submitResult && submitResult.xp_awarded > 0 && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-300">
                      <Zap size={14} />
                      +{submitResult.xp_awarded} XP earned
                      {submitResult.current_streak > 1 && (
                        <span className="ml-auto text-xs text-yellow-400/70">
                          Streak · {submitResult.current_streak}d
                        </span>
                      )}
                    </div>
                  )}

                  {submitResult && submitResult.xp_forfeited && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-400">
                      <Lightbulb size={13} className="text-yellow-400/70" />
                      First-solve XP forfeited — hints were used.
                    </div>
                  )}

                  {submitResult && submitResult.new_badges?.length > 0 && (
                    <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm font-medium text-yellow-300">
                      <Award size={14} />
                      Badge unlocked: {submitResult.new_badges.join(', ')}
                    </div>
                  )}

                  {/* Test chips (submit) */}
                  {submitResult && (
                    <div className="mb-3">
                      <p className="mb-2 text-xs text-gray-500">
                        Tests · {submitResult.test_results.filter((t) => t.passed).length}/
                        {submitResult.test_results.length} passed
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {submitResult.test_results.map((t) => (
                          <TestChip key={t.index} index={t.index} passed={t.passed} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Runtime + memory */}
                  <div className="mb-3 font-mono text-xs text-gray-500">
                    {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
                  </div>

                  {/* AI review (submit, not accepted) */}
                  {submitResult && submitResult.status !== 'ACCEPTED' && (
                    <div className="mt-3">
                      {review ? (
                        <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3">
                          <p className="flex items-center gap-2 text-sm font-semibold text-yellow-300">
                            <Sparkles size={14} />
                            AI review
                            <span className="rounded border border-yellow-500/30 px-1.5 py-0.5 text-[10px] font-normal text-yellow-400/80">
                              {review.bug_type}
                            </span>
                          </p>
                          <p className="mt-2 text-sm font-medium text-gray-200">{review.verdict}</p>
                          <article className="prose prose-invert prose-sm mt-2 max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.explanation}</Markdown>
                          </article>
                          <p className="mt-3 mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                            How to fix
                          </p>
                          <article className="prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.fix_hint}</Markdown>
                          </article>
                        </div>
                      ) : (
                        <button
                          onClick={fetchReview}
                          disabled={reviewLoading}
                          className="flex items-center gap-1.5 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs font-medium text-yellow-300 hover:bg-yellow-500/20 disabled:opacity-50"
                        >
                          {reviewLoading ? (
                            <Loader2 size={13} className="animate-spin" />
                          ) : (
                            <Sparkles size={13} />
                          )}
                          Get AI review
                        </button>
                      )}
                    </div>
                  )}

                  {/* Failed test details (run) */}
                  {runResult &&
                    runResult.test_results.map((t) => (
                      <div
                        key={t.index}
                        className={`mt-2 rounded-lg border p-3 ${
                          t.passed
                            ? 'border-emerald-500/30 bg-emerald-500/5'
                            : 'border-red-500/30 bg-red-500/5'
                        }`}
                      >
                        <p className="flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400">
                          {t.passed ? (
                            <CheckCircle2 size={12} className="text-emerald-400" />
                          ) : (
                            <XCircle size={12} className="text-red-400" />
                          )}
                          Case {t.index + 1}
                          {!t.passed && <span>· {STATUS_STYLES[shown.status]?.label}</span>}
                        </p>
                        {!t.passed && (
                          <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Input
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-gray-300">
                                {t.input.trimEnd()}
                              </pre>
                            </div>
                            <div>
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Expected
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400">
                                {t.expected_output}
                              </pre>
                            </div>
                            <div className="sm:col-span-2">
                              <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500">
                                Your output
                              </p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300">
                                {t.actual_output ?? '(no output)'}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}

              {/* Testcase tab content */}
              {shown && consoleTab === 'testcase' && (
                <div className="p-4">
                  <p className="mb-2 text-xs text-gray-500">Test case inputs (read-only)</p>
                  {shown.test_results.map((t) => (
                    <div key={t.index} className="mb-2 rounded-lg border border-white/10 bg-[#1a1a2e] p-3">
                      <p className="mb-1 font-mono text-xs text-gray-500">Case {t.index + 1}</p>
                      <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-[12px] text-gray-300">
                        {t.input.trimEnd()}
                      </pre>
                    </div>
                  ))}
                </div>
              )}

              {/* Empty state */}
              {!shown && !error && (
                <div className="flex items-center justify-center py-8 text-sm text-gray-500">
                  Run or submit your code to see results here.
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
