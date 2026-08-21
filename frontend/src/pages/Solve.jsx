import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Award,
  CheckCircle2,
  Lightbulb,
  Loader2,
  LogOut,
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
import { Brand } from '../components/Shell'

const LANGS = [
  { key: 'python', label: 'Python', ext: python() },
  { key: 'cpp', label: 'C++', ext: cpp() },
  { key: 'java', label: 'Java', ext: java() },
]

const STATUS_STYLES = {
  ACCEPTED: {
    chip: 'border-quest bg-quest/15 text-emerald-300',
    icon: <CheckCircle2 size={18} />,
    label: 'Accepted',
  },
  WRONG_ANSWER: {
    chip: 'border-rust bg-rust/15 text-red-300',
    icon: <XCircle size={18} />,
    label: 'Wrong answer',
  },
  TLE: {
    chip: 'border-gold bg-gold/15 text-yellow-200',
    icon: <XCircle size={18} />,
    label: 'Time limit exceeded',
  },
  RUNTIME_ERROR: {
    chip: 'border-orange-400/70 bg-orange-500/10 text-orange-300',
    icon: <XCircle size={18} />,
    label: 'Runtime error',
  },
  COMPILATION_ERROR: {
    chip: 'border-purple-400/70 bg-purple-500/10 text-purple-300',
    icon: <XCircle size={18} />,
    label: 'Compilation error',
  },
}

function TestChip({ passed, index }) {
  return (
    <span
      title={`Test ${index + 1}: ${passed ? 'passed' : 'failed'}`}
      className={`flex h-8 w-8 items-center justify-center rounded-lg border-[1.5px] font-mono text-xs font-bold ${
        passed
          ? 'border-quest/60 bg-quest/15 text-emerald-300'
          : 'border-rust/60 bg-rust/15 text-red-300'
      }`}
    >
      {index + 1}
    </span>
  )
}

export default function Solve() {
  const { slug } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [problem, setProblem] = useState(null)
  const [pageStatus, setPageStatus] = useState('loading')
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

  useEffect(() => {
    let cancelled = false
    client
      .get(`/problems/${slug}`)
      .then((res) => {
        if (cancelled) return
        setProblem(res.data)
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
      <div className="arena-bg flex min-h-screen items-center justify-center gap-2 text-arena-dim">
        <Loader2 size={20} className="animate-spin" />
        Entering the arena…
      </div>
    )
  }

  if (pageStatus === 'error') {
    return (
      <div className="arena-bg flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-[1.05rem] text-arena-dim">This problem does not exist.</p>
        <Link to="/problems" className="font-semibold text-gold hover:underline">
          Back to the library
        </Link>
      </div>
    )
  }

  const shown = submitResult || runResult
  const statement = problem.description.replace(/^#\s+.+\r?\n+/, '')

  return (
    <div className="arena-bg flex min-h-screen flex-col lg:h-screen">
      <header className="flex h-16 shrink-0 items-center justify-between gap-3 border-b border-arena-line px-4 lg:px-6">
        <div className="flex min-w-0 items-center gap-4">
          <Brand dark />
          <span className="hidden h-5 w-px bg-arena-line sm:block" />
          <Link
            to={`/problems/${slug}`}
            aria-label="Back to problem overview"
            className="flex items-center gap-1.5 rounded-lg border border-arena-line px-2.5 py-1.5 text-sm text-arena-dim transition-colors hover:border-arena-dim hover:text-arena-text"
          >
            <ArrowLeft size={15} />
            Overview
          </Link>
        </div>
        <button
          onClick={() => {
            logout()
            navigate('/login')
          }}
          className="btn shrink-0 border border-arena-line px-3 py-1.5 text-sm text-arena-dim hover:border-rust hover:text-red-300"
        >
          <LogOut size={15} />
          Log out
        </button>
      </header>

      <main className="mx-auto flex w-full max-w-[1700px] flex-1 flex-col gap-5 p-4 lg:flex-row lg:gap-6 lg:overflow-hidden lg:p-5">
        <section className="min-h-0 w-full shrink-0 overflow-y-auto pr-1 lg:h-full lg:w-[44%] lg:max-w-[760px]">
          <div className="flex items-center gap-3">
            {problem.solved && (
              <span className="stamp-chip border-quest bg-quest/15 text-emerald-300">
                Solved
              </span>
            )}
            <span className="stamp-chip border-arena-line bg-arena-raised text-arena-dim">
              {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
            </span>
            <span className="stamp-chip border-arena-line bg-arena-raised text-arena-dim">
              {problem.topic.replace('_', ' ')}
            </span>
          </div>

          <h1 className="mt-3 font-display text-[1.9rem] font-bold leading-snug tracking-tight text-arena-text">
            {problem.title}
          </h1>

          <article className="prose prose-invert mt-5 max-w-none text-[1.0625rem] leading-[1.78] prose-headings:text-arena-text prose-strong:text-white prose-code:rounded prose-code:bg-arena-raised prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-gold prose-code:before:content-none prose-code:after:content-none">
            <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
          </article>

          {hintMeta && (
            <div className="arena-panel mt-7 p-5">
              <p className="flex flex-wrap items-center gap-2 font-display text-sm font-semibold uppercase tracking-wide text-arena-text">
                <Lightbulb size={16} className="text-gold" />
                Hints
                <span className="font-sans text-xs font-normal normal-case tracking-normal text-gold/90">
                  Viewing any hint forfeits first-solve XP
                </span>
              </p>
              <div className="mt-3.5 space-y-2">
                {hintMeta.levels.map((entry) => (
                  <div key={entry.level} className="overflow-hidden rounded-xl border border-arena-line">
                    <button
                      onClick={() => onHintClick(entry.level)}
                      disabled={loadingHint !== null}
                      className={`flex w-full items-center gap-2.5 px-4 py-3 text-left text-[0.95rem] transition-colors ${
                        entry.revealed || armedHint === entry.level
                          ? 'bg-gold/10 text-gold'
                          : 'text-arena-dim hover:bg-arena-raised hover:text-arena-text'
                      } disabled:opacity-50`}
                    >
                      {loadingHint === entry.level ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Lightbulb
                          size={16}
                          className={entry.revealed || armedHint === entry.level ? 'text-gold' : ''}
                        />
                      )}
                      Level {entry.level}: {entry.label}
                      {!entry.revealed && (
                        <span className="ml-auto text-xs font-medium">
                          {hintMeta.xp_forfeit_applies
                            ? armedHint === entry.level
                              ? 'Click again — XP will be forfeited'
                              : 'Reveal · costs XP'
                            : 'Reveal'}
                        </span>
                      )}
                    </button>
                    {revealedHints[entry.level] && (
                      <div className="border-t border-arena-line bg-arena/40 px-4 py-3">
                        <article className="prose prose-invert prose-base max-w-none text-[0.95rem] leading-relaxed prose-code:text-gold">
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

        <section className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex gap-1 rounded-xl border border-arena-line bg-arena-panel p-1">
              {LANGS.map((l) => (
                <button
                  key={l.key}
                  onClick={() => setLang(l.key)}
                  className={`rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors ${
                    lang === l.key
                      ? 'bg-arena-raised text-arena-text shadow-card'
                      : 'text-arena-dim hover:text-arena-text'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
            <div className="flex gap-2.5">
              <button
                onClick={run}
                disabled={running || submitting}
                className="btn border border-arena-line px-4 py-2.5 text-[0.95rem] text-arena-text hover:border-arena-dim disabled:opacity-50"
              >
                {running ? <Loader2 size={17} className="animate-spin" /> : <Play size={17} />}
                Run
              </button>
              <button
                onClick={submit}
                disabled={running || submitting}
                className="btn btn-quest px-4 py-2.5 text-[0.95rem]"
              >
                {submitting ? <Loader2 size={17} className="animate-spin" /> : <Send size={17} />}
                Submit
              </button>
            </div>
          </div>

          <div className="arena-panel min-h-[65vh] overflow-hidden lg:min-h-0 lg:flex-[5] lg:basis-0">
            <CodeMirror
              value={code}
              height="100%"
              style={{ fontSize: '17px', height: '100%' }}
              theme={oneDark}
              extensions={[activeLang.ext]}
              onChange={setCode}
              basicSetup={{ tabSize: 4 }}
            />
          </div>

          <div className="min-h-0 space-y-4 lg:flex-[2] lg:basis-0 lg:overflow-y-auto lg:pr-1">
            {error && (
              <div className="rounded-xl border border-rust/50 bg-rust/10 p-4 text-[0.95rem] text-red-300">
                {error}
              </div>
            )}

            {shown && (
              <div className="arena-panel p-4">
                <div className="flex flex-wrap items-center gap-3">
                  <span className={`stamp-chip stamp-tilt px-3 py-1.5 text-xs ${STATUS_STYLES[shown.status].chip}`}>
                    {STATUS_STYLES[shown.status].icon}
                    {STATUS_STYLES[shown.status].label}
                  </span>
                  <span className="ml-auto font-mono text-xs text-arena-dim">
                    {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
                  </span>
                </div>

                {submitResult && submitResult.xp_awarded > 0 && (
                  <div className="mt-3 flex items-center gap-2 rounded-xl border border-gold/45 bg-gold/10 p-3 text-[0.95rem] text-gold">
                    <Zap size={16} />
                    +{submitResult.xp_awarded} XP earned
                    {submitResult.current_streak > 1 && (
                      <span className="ml-auto font-mono text-xs text-gold/80">
                        Streak · {submitResult.current_streak}d
                      </span>
                    )}
                  </div>
                )}

                {submitResult && submitResult.xp_forfeited && (
                  <div className="mt-3 flex items-center gap-2 rounded-xl border border-arena-line bg-arena-raised p-3 text-sm text-arena-dim">
                    <Lightbulb size={15} className="text-gold/70" />
                    First-solve XP forfeited — hints were used on this problem.
                  </div>
                )}

                {submitResult && submitResult.new_badges?.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 rounded-xl border border-gold/45 bg-gold/10 p-3 text-[0.95rem] font-medium text-gold">
                    <Award size={16} />
                    Badge unlocked: {submitResult.new_badges.join(', ')}
                  </div>
                )}

                <div className="mt-4 space-y-4">
                  {submitResult && (
                    <div>
                      <p className="eyebrow !text-arena-dim">
                        Tests · {submitResult.test_results.filter((t) => t.passed).length}/
                        {submitResult.test_results.length} passed
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {submitResult.test_results.map((t) => (
                          <TestChip key={t.index} index={t.index} passed={t.passed} />
                        ))}
                      </div>
                    </div>
                  )}

                  {submitResult && submitResult.status !== 'ACCEPTED' && (
                    <div>
                      {review ? (
                        <div className="rounded-xl border border-gold/40 bg-gold/[0.06] p-4">
                          <p className="flex flex-wrap items-center gap-2 font-display text-sm font-semibold uppercase tracking-wide text-gold">
                            <Sparkles size={16} />
                            AI review
                            <span className="rounded-md border border-gold/40 px-2 py-0.5 font-sans text-xs normal-case tracking-normal">
                              {review.bug_type}
                            </span>
                          </p>
                          <p className="mt-2.5 text-[0.95rem] font-semibold text-arena-text">
                            {review.verdict}
                          </p>
                          <article className="prose prose-invert prose-sm mt-2 max-w-none text-[0.95rem] leading-relaxed prose-code:text-gold">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.explanation}</Markdown>
                          </article>
                          <p className="eyebrow mt-4 mb-1 !text-arena-dim">How to fix</p>
                          <article className="prose prose-invert prose-sm max-w-none text-[0.95rem] leading-relaxed prose-code:text-emerald-300">
                            <Markdown remarkPlugins={[remarkGfm]}>{review.fix_hint}</Markdown>
                          </article>
                        </div>
                      ) : (
                        <button
                          onClick={fetchReview}
                          disabled={reviewLoading}
                          className="btn border border-gold/50 bg-gold/10 px-4 py-2.5 text-[0.95rem] text-gold hover:bg-gold/20 disabled:opacity-50"
                        >
                          {reviewLoading ? (
                            <Loader2 size={16} className="animate-spin" />
                          ) : (
                            <Sparkles size={16} />
                          )}
                          Get AI review of this attempt
                        </button>
                      )}
                    </div>
                  )}

                  {runResult &&
                    runResult.test_results.map((t) => (
                      <div
                        key={t.index}
                        className={`rounded-xl border p-3.5 ${
                          t.passed
                            ? 'border-quest/35 bg-quest/[0.07]'
                            : 'border-rust/40 bg-rust/[0.08]'
                        }`}
                      >
                        <p className="flex items-center gap-2 font-mono text-xs font-medium text-arena-dim">
                          {t.passed ? (
                            <CheckCircle2 size={14} className="text-emerald-300" />
                          ) : (
                            <XCircle size={14} className="text-red-300" />
                          )}
                          Case {t.index + 1}
                          {!t.passed && <span>· {STATUS_STYLES[shown.status]?.label}</span>}
                        </p>
                        {!t.passed && (
                          <div className="mt-2.5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div className="space-y-2.5 font-mono text-[13px]">
                              <div>
                                <p className="eyebrow !text-arena-dim mb-1">Input</p>
                                <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-arena p-2.5 text-arena-text">
                                  {t.input.trimEnd()}
                                </pre>
                              </div>
                              <div>
                                <p className="eyebrow !text-arena-dim mb-1">Expected</p>
                                <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-arena p-2.5 text-emerald-300">
                                  {t.expected_output}
                                </pre>
                              </div>
                            </div>
                            <div>
                              <p className="eyebrow !text-arena-dim mb-1">Your output</p>
                              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-rust/30 bg-arena p-2.5 font-mono text-[13px] text-red-300">
                                {t.actual_output ?? '(no output)'}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
