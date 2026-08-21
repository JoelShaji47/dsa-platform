import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Loader2, Play } from 'lucide-react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import { TopBar, UserChip, DifficultyChip, SealCheck } from '../components/Shell'

const LANGS = [
  { key: 'python', label: 'Python' },
  { key: 'cpp', label: 'C++' },
  { key: 'java', label: 'Java' },
]

export default function ProblemDetail() {
  const { slug } = useParams()
  const { user } = useAuth()
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
      <div className="flex min-h-screen items-center justify-center gap-2 text-ink-soft">
        <Loader2 size={20} className="animate-spin" />
        Loading problem…
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-[1.05rem] text-ink-soft">This problem does not exist.</p>
        <Link to="/problems" className="font-semibold text-gold-deep hover:underline">
          Back to the library
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <TopBar active="problems">
        <UserChip username={user.username} />
      </TopBar>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <Link
          to="/problems"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
        >
          <ArrowLeft size={15} />
          All problems
        </Link>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          {problem.solved && <SealCheck title="Solved" />}
          <DifficultyChip difficulty={problem.difficulty} />
          <span className="stamp-chip border-ink/15 bg-white text-ink-soft">
            {problem.topic.replace('_', ' ')}
          </span>
        </div>

        <h1 className="mt-4 font-display text-[2.35rem] font-bold leading-tight tracking-tight text-ink">
          {problem.title}
        </h1>

        <article className="prose prose-slate mt-6 max-w-none text-[1.0625rem] leading-[1.75] prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-paper-deep prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-gold-deep prose-code:before:content-none prose-code:after:content-none">
          <Markdown remarkPlugins={[remarkGfm]}>
            {problem.description.replace(/^#\s+.+\r?\n+/, '')}
          </Markdown>
        </article>

        <section className="mt-10">
          <p className="eyebrow">Example tests</p>
          <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
            {problem.test_cases.map((tc, i) => (
              <div key={i} className="panel overflow-hidden p-0">
                <div className="flex items-center justify-between border-b border-ink/8 bg-paper px-4 py-2">
                  <span className="eyebrow">Case {i + 1}</span>
                  <span className="flex gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-rust/50" />
                    <span className="h-2 w-2 rounded-full bg-gold/60" />
                    <span className="h-2 w-2 rounded-full bg-quest/60" />
                  </span>
                </div>
                <div className="space-y-3 p-4 font-mono text-sm">
                  <div>
                    <p className="eyebrow mb-1">Input</p>
                    <pre className="overflow-x-auto whitespace-pre-wrap text-arena-text rounded-lg bg-arena p-3 leading-relaxed">
                      {tc.input.trimEnd()}
                    </pre>
                  </div>
                  <div>
                    <p className="eyebrow mb-1">Expected</p>
                    <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-quest/25 bg-quest/8 p-3 leading-relaxed text-quest">
                      {tc.expected_output}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="eyebrow">Starter code</p>
            <div className="flex gap-1.5">
              {LANGS.map((l) => (
                <button
                  key={l.key}
                  onClick={() => setLang(l.key)}
                  className={`rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors duration-150 ${
                    lang === l.key
                      ? 'bg-ink text-white shadow-card'
                      : 'bg-white text-ink-soft ring-1 ring-ink/12 hover:text-ink'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>
          <pre className="mt-3 overflow-x-auto rounded-xl border border-arena-line bg-arena p-5 font-mono text-sm leading-relaxed text-arena-text">
            {problem.starter_code[lang]}
          </pre>
        </section>

        <div className="mt-10 pb-4">
          <button
            onClick={() => navigate(`/problems/${problem.slug}/solve`)}
            className="btn btn-quest w-full py-4 text-base"
          >
            <Play size={18} />
            Enter the arena
          </button>
        </div>
      </main>
    </div>
  )
}
