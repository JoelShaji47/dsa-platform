import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { CheckCircle2, Loader2, LogOut, Search } from 'lucide-react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

const TOPICS = ['ARRAY', 'STRING', 'LINKED_LIST', 'STACK', 'QUEUE', 'TREE', 'GRAPH', 'DP']
const DIFFICULTIES = ['EASY', 'MEDIUM', 'HARD']

const DIFFICULTY_STYLES = {
  EASY: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  HARD: 'bg-red-500/10 text-red-400 border-red-500/30',
}

export default function Problems() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [problems, setProblems] = useState([])
  const [loading, setLoading] = useState(true)
  const [topic, setTopic] = useState('')
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
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-xl font-bold text-white">
            DSA Platform
          </Link>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">Problems</span>
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
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        <h2 className="text-2xl font-bold text-white">Problem Library</h2>

        <div className="mt-6 flex flex-col gap-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setTopic('')}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                topic === ''
                  ? 'border-indigo-500 bg-indigo-500/20 text-indigo-300'
                  : 'border-slate-700 text-slate-400 hover:border-slate-500'
              }`}
            >
              All topics
            </button>
            {TOPICS.map((t) => (
              <button
                key={t}
                onClick={() => setTopic(t)}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                  topic === t
                    ? 'border-indigo-500 bg-indigo-500/20 text-indigo-300'
                    : 'border-slate-700 text-slate-400 hover:border-slate-500'
                }`}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[220px]">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by title..."
                className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2 pl-9 pr-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="">All difficulties</option>
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>
                  {d.charAt(0) + d.slice(1).toLowerCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800">
          {loading ? (
            <div className="flex items-center justify-center gap-2 bg-slate-900 py-16 text-slate-400">
              <Loader2 size={20} className="animate-spin" />
              Loading problems...
            </div>
          ) : problems.length === 0 ? (
            <div className="bg-slate-900 py-16 text-center text-slate-400">
              No problems match your filters.
            </div>
          ) : (
            <table className="w-full bg-slate-900 text-left text-sm">
              <tbody className="divide-y divide-slate-800">
                {problems.map((p) => (
                  <tr key={p.id} className="transition hover:bg-slate-800/60">
                    <td className="w-10 pl-4">
                      {p.solved && <CheckCircle2 size={18} className="text-emerald-400" />}
                    </td>
                    <td className="py-3.5 pr-4">
                      <Link to={`/problems/${p.slug}`} className="font-medium text-white hover:text-indigo-300">
                        {p.title}
                      </Link>
                    </td>
                    <td className="w-28 pr-4">
                      <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${DIFFICULTY_STYLES[p.difficulty]}`}>
                        {p.difficulty.charAt(0) + p.difficulty.slice(1).toLowerCase()}
                      </span>
                    </td>
                    <td className="w-32 pr-4 text-xs text-slate-500">{p.topic.replace('_', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}
