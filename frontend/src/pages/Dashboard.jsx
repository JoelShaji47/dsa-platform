import { useNavigate } from 'react-router-dom'
import { Flame, LogOut, Zap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-bold text-white">DSA Platform</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">{user.username}</span>
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
      <main className="mx-auto max-w-5xl px-6 py-10">
        <h2 className="text-2xl font-bold text-white">
          Welcome back, {user.username}
        </h2>
        <p className="mt-1 text-slate-400">
          Your progress dashboard is coming in Phase 2
        </p>
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center gap-2 text-yellow-400">
              <Zap size={20} />
              <span className="text-sm font-medium">Total XP</span>
            </div>
            <p className="mt-3 text-4xl font-bold text-white">{user.xp}</p>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center gap-2 text-orange-400">
              <Flame size={20} />
              <span className="text-sm font-medium">Daily streak</span>
            </div>
            <p className="mt-3 text-4xl font-bold text-white">
              {user.current_streak} days
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-indigo-500/30 bg-indigo-500/10 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Ready to practice?</h3>
              <p className="mt-1 text-sm text-slate-400">
                Pick a problem and keep the streak alive.
              </p>
            </div>
            <button
              onClick={() => navigate('/problems')}
              className="rounded-xl bg-indigo-600 px-5 py-2.5 font-semibold text-white transition hover:bg-indigo-500"
            >
              Browse problems
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
