import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Loader2, Search } from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import { TopBar, UserChip, DifficultyChip, SealCheck } from '../components/Shell'

const TOPICS = ['ARRAY', 'STRING', 'LINKED_LIST', 'STACK', 'QUEUE', 'TREE', 'GRAPH', 'DP']
const DIFFICULTIES = ['EASY', 'MEDIUM', 'HARD']

export default function Problems() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [problems, setProblems] = useState([])
  const [loading, setLoading] = useState(true)
  const [topic, setTopic] = useState(searchParams.get('topic') ?? '')
  const [difficulty, setDifficulty] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    const params = {}
    if (topic) params.topic = topic
    if (difficulty) params.difficulty = difficulty
    if (search) params.search = search
    client
      .get('/problems', { params })
      .then((res) => {
        if (!cancelled) setProblems(res.data)
      })
      .catch(() => {
        if (!cancelled) setProblems([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [topic, difficulty, search])

  return (
    <div className="min-h-screen">
      <TopBar active="problems">
        <UserChip username={user.username} />
      </TopBar>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="eyebrow">Problem library</p>
        <h1 className="mt-1 font-display text-4xl font-bold tracking-tight text-ink">
          Choose your next challenge
        </h1>

        <div className="mt-7 flex flex-col gap-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setTopic('')}
              className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors duration-150 ${
                topic === ''
                  ? 'border-ink bg-ink text-white shadow-card'
                  : 'border-ink/15 bg-white text-ink-soft hover:border-ink/35 hover:text-ink'
              }`}
            >
              All topics
            </button>
            {TOPICS.map((t) => (
              <button
                key={t}
                onClick={() => setTopic(t)}
                className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors duration-150 ${
                  topic === t
                    ? 'border-ink bg-ink text-white shadow-card'
                    : 'border-ink/15 bg-white text-ink-soft hover:border-ink/35 hover:text-ink'
                }`}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[240px] flex-1">
              <Search size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by title…"
                className="field pl-10"
              />
            </div>
            <div className="flex gap-1.5">
              <button
                onClick={() => setDifficulty('')}
                className={`stamp-chip ${difficulty === '' ? 'border-ink bg-ink text-white' : 'border-ink/15 bg-white text-ink-soft'}`}
              >
                All
              </button>
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  onClick={() => setDifficulty(d)}
                  aria-pressed={difficulty === d}
                  className={`stamp-chip transition-opacity ${
                    difficulty === ''
                      ? 'border-ink/15 bg-white text-ink-soft opacity-80 hover:opacity-100'
                      : difficulty === d
                        ? 'border-gold-deep bg-gold/15 text-gold-deep ring-2 ring-gold/40'
                        : 'border-ink/15 bg-white text-ink-faint opacity-70 hover:opacity-100'
                  }`}
                >
                  {d.charAt(0) + d.slice(1).toLowerCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="panel mt-7 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center gap-2 py-16 text-ink-soft">
              <Loader2 size={20} className="animate-spin" />
              Loading problems…
            </div>
          ) : problems.length === 0 ? (
            <div className="py-16 text-center text-[0.95rem] text-ink-faint">
              No problems match these filters. Loosen them and look again.
            </div>
          ) : (
            <ul className="divide-y divide-ink/6">
              {problems.map((p) => (
                <li key={p.id}>
                  <Link
                    to={`/problems/${p.slug}`}
                    className="group flex items-center gap-4 px-5 py-4 transition-colors duration-150 hover:bg-paper"
                  >
                    {p.solved ? (
                      <SealCheck title={`Solved: ${p.title}`} />
                    ) : (
                      <span className="h-7 w-7 shrink-0 rounded-full border-[1.5px] border-dashed border-ink/20" />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-[1.05rem] font-semibold text-ink group-hover:text-gold-deep">
                        {p.title}
                      </p>
                      <p className="eyebrow mt-0.5">{p.topic.replace('_', ' ')}</p>
                    </div>
                    <DifficultyChip difficulty={p.difficulty} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
