import { useEffect, useState } from 'react'

export default function App() {
  const [health, setHealth] = useState('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth('backend offline'))
  }, [])

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center shadow-2xl">
        <h1 className="text-3xl font-bold text-white">DSA Platform</h1>
        <p className="mt-2 text-slate-400">
          AI-Powered Gamified DSA Learning
        </p>
        <p className="mt-6 inline-block rounded-full bg-emerald-500/10 px-4 py-1 text-sm text-emerald-400">
          backend: {health}
        </p>
      </div>
    </div>
  )
}
