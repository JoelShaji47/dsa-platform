import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Loader2, LogOut, Play } from 'lucide-react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

const LANGS = [
  { key: 'python', label: 'Python' },
  { key: 'cpp', label: 'C++' },
  { key: 'java', label: 'Java' },
]

export default function ProblemDetail() {
  const { slug } = useParams()
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [problem, setProblem] = useState(null)
  const [status, setStatus] = useState('loading')
  const [lang, setLang] = useState('python')

  useEffect(() => {
    let cancelled = false
    client
      .get(`/problems/${slug}`)
      .then((res) => {
        if (cancelled) return
        setProblem(res.data)
        setStatus('ok')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [slug])

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 bg-slate-950 text-slate-400">
        <Loader2 size={20} className="animate-spin" />
        Loading problem...
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-950">
        <p className="text-slate-400">Problem not found.</p>
        <Link to="/problems" className="text-indigo-400 hover:text-indigo-300">
          Back to problems
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link
            to="/problems"
            className="flex items-center gap-1.5 text-sm text-slate-400 transition hover:text-white"
          >
            <ArrowLeft size={16} />
            All problems
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

      <main className="mx-auto max-w-5xl px-6 py-8">
        <div className="flex flex-wrap items-center gap-3">
          {problem.solved && (
            <span className="flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
              <CheckCircle2 size={14} />
              Solved
            </span>
          )}
          <span
            className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${
              problem.difficulty === 'EASY'
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                : problem.difficulty === 'MEDIUM'
                  ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400'
                  : 'border-red-500/30 bg-red-500/10 text-red-400'
            }`}
          >
            {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
          </span>
          <span className="rounded-full border border-slate-700 px-2.5 py-0.5 text-xs text-slate-400">
            {problem.topic.replace('_', ' ')}
          </span>
        </div>

        <h1 className="mt-3 text-3xl font-bold text-white">{problem.title}</h1>

        <article className="prose prose-invert mt-6 max-w-none prose-headings:text-white prose-strong:text-white prose-code:text-indigo-300">
          <Markdown remarkPlugins={[remarkGfm]}>{problem.description}</Markdown>
        </article>

        <section className="mt-8">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Example Tests</h3>
          <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
            {problem.test_cases.map((tc, i) => (
              <div key={i} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Input</p>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-sm text-slate-200">
                  {tc.input.trimEnd()}
                </pre>
                <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Output</p>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap font-mono text-sm text-emerald-300">
                  {tc.expected_output}
                </pre>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Starter Code</h3>
            <div className="flex gap-1.5">
              {LANGS.map((l) => (
                <button
                  key={l.key}
                  onClick={() => setLang(l.key)}
                  className={`rounded-lg px-3 py-1 text-xs font-medium transition ${
                    lang === l.key
                      ? 'bg-indigo-500/20 text-indigo-300'
                      : 'text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>
          <pre className="mt-3 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900 p-4 font-mono text-sm leading-relaxed text-slate-200">
            {problem.starter_code[lang]}
          </pre>
        </section>

        <div className="mt-8 pb-4">
          <button
            onClick={() => navigate(`/problems/${problem.slug}/solve`)}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3.5 font-semibold text-white transition hover:bg-indigo-500"
          >
            <Play size={18} />
            Solve this problem
          </button>
        </div>
      </main>
    </div>
  )
}
