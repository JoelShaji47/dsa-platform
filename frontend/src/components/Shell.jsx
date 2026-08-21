import { Compass, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Brand({ dark = false }) {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <span
        className={`flex h-8 w-8 items-center justify-center rounded-lg ${
          dark ? 'bg-gold text-arena' : 'bg-ink text-gold'
        }`}
      >
        <Compass size={18} strokeWidth={2.25} />
      </span>
      <span
        className={`font-display text-[1.05rem] font-bold uppercase tracking-[0.12em] ${
          dark ? 'text-arena-text' : 'text-ink'
        }`}
      >
        Code<span className="text-gold">Quest</span>
      </span>
    </Link>
  )
}

function NavLink({ to, active, children }) {
  return (
    <Link
      to={to}
      className={`relative flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors duration-150 ${
        active ? 'text-ink' : 'text-ink-soft hover:text-ink'
      }`}
    >
      <span
        className={`absolute -left-0.5 h-1.5 w-1.5 rotate-45 transition-opacity duration-150 ${
          active ? 'bg-gold opacity-100' : 'opacity-0'
        }`}
      />
      {children}
    </Link>
  )
}

export function TopBar({ active, children }) {
  const { logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-20 border-b border-ink/8 bg-paper/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-6">
        <Brand />
        <nav className="flex items-center gap-1">
          <NavLink to="/" active={active === 'dashboard'}>
            Campaign
          </NavLink>
          <NavLink to="/problems" active={active === 'problems'}>
            Problems
          </NavLink>
        </nav>
        <div className="ml-auto flex items-center gap-3">{children}</div>
        <button
          onClick={() => {
            logout()
            navigate('/login')
          }}
          className="btn border border-ink/12 px-3 py-1.5 text-sm text-ink-soft hover:border-rust hover:text-rust"
        >
          <LogOut size={15} />
          Log out
        </button>
      </div>
    </header>
  )
}

export function UserChip({ username }) {
  return (
    <span className="hidden items-center gap-1.5 rounded-full border border-ink/10 bg-white px-3 py-1 text-sm font-medium text-ink shadow-card sm:flex">
      <span className="h-1.5 w-1.5 rounded-full bg-quest" />
      {username}
    </span>
  )
}

const DIFFICULTY_CHIP = {
  EASY: 'border-quest/40 bg-quest/10 text-quest',
  MEDIUM: 'border-gold/50 bg-gold/10 text-gold-deep',
  HARD: 'border-rust/40 bg-rust/10 text-rust',
}

export function DifficultyChip({ difficulty }) {
  return (
    <span className={`stamp-chip ${DIFFICULTY_CHIP[difficulty] ?? DIFFICULTY_CHIP.MEDIUM}`}>
      {difficulty.charAt(0) + difficulty.slice(1).toLowerCase()}
    </span>
  )
}

export function SealCheck({ title }) {
  return (
    <span
      title={title ?? 'Solved'}
      className="flex h-7 w-7 items-center justify-center rounded-full border-[1.5px] border-quest bg-quest/10 text-quest"
    >
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="3">
        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  )
}
