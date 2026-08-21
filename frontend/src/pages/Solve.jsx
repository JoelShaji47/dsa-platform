import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  Loader2,
  LogOut,
  Play,
  Send,
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
    banner: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
    icon: <CheckCircle2 size={20} />,
    label: 'Accepted',
  },
  WRONG_ANSWER: {
    banner: 'border-red-500/40 bg-red-500/10 text-red-300',
    icon: <XCircle size={20} />,
    label: 'Wrong Answer',
  },
  TLE: {
    banner: 'border-yellow-500/40 bg-yellow-500/10 text-yellow-300',
    icon: <XCircle size={20} />,
    label: 'Time Limit Exceeded',
  },
  RUNTIME_ERROR: {
    banner: 'border-orange-500/40 bg-orange-500/10 text-orange-300',
    icon: <XCircle size={20} />,
    label: 'Runtime Error',
  },
  COMPILATION_ERROR: {
    banner: 'border-purple-500/40 bg-purple-500/10 text-purple-300',
    icon: <XCircle size={20} />,
    label: 'Compilation Error',
  },
}

function TestChip({ passed, index }) {
  return (
    <span
      className={`flex h-7 w-7 items-center justify-center rounded-lg border text-xs font-bold ${
        passed
          ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-400'
          : 'border-red-500/40 bg-red-500/15 text-red-400'
      }`}
      title={`Test ${index + 1}: ${passed ? 'passed' : 'failed'}`}
    >
      {index + 1}
    </span>
  )
}

export default function Solve() {
  const { slug } = useParams()
  const { logout } = useAuth()
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

  useEffect(() => {
    let cancelled = false
    client
      .get(`/problems/${slug}`)
      .then((res) => {
        if (cancelled) return
        setProblem(res.data)
        setCode(res.data.starter_code.python)
        setPageStatus('ok')
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

  if (pageStatus === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 bg-slate-950 text-slate-400">
        <Loader2 size={20} className="animate-spin" />
        Loading...
      </div>
    )
  }

  if (pageStatus === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-950">
        <p className="text-slate-400">Problem not found.</p>
        <Link to="/problems" className="text-indigo-400 hover:text-indigo-300">
          Back to problems
        </Link>
      </div>
    )
  }

  const shown = submitResult || runResult

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <Link
            to={`/problems/${slug}`}
            className="flex items-center gap-1.5 text-sm text-slate-400 transition hover:text-white"
          >
            <ArrowLeft size={16} />
            {problem.title}
          </Link>
          <button
            onClick={() => {
              logout()
              navigate('/login')
            }}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 transition hover:border-red-500 hover:text-red-400"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 lg:grid-cols-2">
        <section className="min-w-0 overflow-y-auto lg:max-h-[calc(100vh-6rem)] lg:pr-2">
          <h1 className="text-2xl font-bold text-white">{problem.title}</h1>
          <article className="prose prose-invert mt-4 max-w-none prose-headings:text-white prose-strong:text-white prose-code:text-indigo-300">
            <Markdown remarkPlugins={[remarkGfm]}>{problem.description}</Markdown>
          </article>
        </section>

        <section className="flex min-w-0 flex-col gap-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex gap-1.5">
              {LANGS.map((l) => (
                <button
                  key={l.key}
                  onClick={() => setLang(l.key)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    lang === l.key
                      ? 'bg-indigo-500/20 text-indigo-300'
                      : 'text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <button
                onClick={run}
                disabled={running || submitting}
                className="flex items-center gap-1.5 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-500 disabled:opacity-50"
              >
                {running ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                Run
              </button>
              <button
                onClick={submit}
                disabled={running || submitting}
                className="flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-50"
              >
                {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                Submit
              </button>
            </div>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-800">
            <CodeMirror
              value={code}
              height="420px"
              theme={oneDark}
              extensions={[activeLang.ext]}
              onChange={setCode}
              basicSetup={{ tabSize: 4 }}
            />
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {shown && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
              <div
                className={`flex flex-wrap items-center gap-2 rounded-xl border p-3 ${
                  STATUS_STYLES[shown.status].banner
                }`}
              >
                {STATUS_STYLES[shown.status].icon}
                <span className="font-semibold">{STATUS_STYLES[shown.status].label}</span>
                <span className="ml-auto text-xs opacity-80">
                  {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
                </span>
              </div>

              {submitResult && submitResult.xp_awarded > 0 && (
                <div className="mt-3 flex items-center gap-2 rounded-xl border border-yellow-500/40 bg-yellow-500/10 p-3 text-sm text-yellow-300">
                  <Zap size={16} />
                  +{submitResult.xp_awarded} XP earned!
                  {submitResult.current_streak > 1 && (
                    <span className="ml-auto">Streak: {submitResult.current_streak} days</span>
                  )}
                </div>
              )}

              <div className="mt-4 space-y-3">
                {submitResult && (
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      All tests ({submitResult.test_results.filter((t) => t.passed).length}/
                      {submitResult.test_results.length} passed)
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {submitResult.test_results.map((t) => (
                        <TestChip key={t.index} index={t.index} passed={t.passed} />
                      ))}
                    </div>
                  </div>
                )}

                {runResult &&
                  runResult.test_results.map((t) => (
                    <div
                      key={t.index}
                      className={`rounded-xl border p-3 ${
                        t.passed
                          ? 'border-emerald-500/30 bg-emerald-500/5'
                          : 'border-red-500/30 bg-red-500/5'
                      }`}
                    >
                      <p className="flex items-center gap-2 text-xs font-medium">
                        {t.passed ? (
                          <CheckCircle2 size={14} className="text-emerald-400" />
                        ) : (
                          <XCircle size={14} className="text-red-400" />
                        )}
                        Case {t.index + 1}
                        {!t.passed && (
                          <span className="text-slate-500">· {STATUS_STYLES[shown.status]?.label}</span>
                        )}
                      </p>
                      {!t.passed && (
                        <div className="mt-2 grid grid-cols-2 gap-3 text-xs">
                          <div>
                            <p className="font-semibold uppercase tracking-wide text-slate-500">Input</p>
                            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-slate-300">
                              {t.input.trimEnd()}
                            </pre>
                            <p className="mt-2 font-semibold uppercase tracking-wide text-slate-500">Expected</p>
                            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-emerald-300">
                              {t.expected_output}
                            </pre>
                          </div>
                          <div>
                            <p className="font-semibold uppercase tracking-wide text-slate-500">Your output</p>
                            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-red-300">
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
        </section>
      </main>
    </div>
  )
}
