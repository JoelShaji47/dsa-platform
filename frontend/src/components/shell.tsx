"use client";

import { Compass, LogOut, ChevronDown } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useRef, useEffect, type ReactNode } from "react";
import { useAuth } from "@/context/auth-context";
import { ThemeToggle } from "@/context/theme-context";
import { cn } from "@/lib/utils";
import type { Difficulty } from "@/lib/types";

export function Brand({ dark = false }: { dark?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span
        className={cn(
          "flex h-8 w-8 items-center justify-center rounded-lg",
          dark ? "bg-gold text-arena" : "bg-ink text-gold"
        )}
      >
        <Compass size={18} strokeWidth={2.25} />
      </span>
      <span
        className={cn(
          "font-display text-[1.05rem] font-bold uppercase tracking-[0.12em]",
          dark ? "text-arena-text" : "text-ink"
        )}
      >
        Code<span className="text-gold">Quest</span>
      </span>
    </Link>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: ReactNode;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "relative flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors duration-150",
        active ? "text-ink" : "text-ink-soft hover:text-ink"
      )}
    >
      <span
        className={cn(
          "absolute -left-0.5 h-1.5 w-1.5 rotate-45 transition-opacity duration-150",
          active ? "bg-gold opacity-100" : "opacity-0"
        )}
      />
      {children}
    </Link>
  );
}

function ProblemsDropdown({ active }: { active: boolean }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const isProblems = active || pathname.startsWith("/problems") || pathname.startsWith("/sql");

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          "relative flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors duration-150",
          isProblems ? "text-ink" : "text-ink-soft hover:text-ink"
        )}
      >
        <span
          className={cn(
            "absolute -left-0.5 h-1.5 w-1.5 rotate-45 transition-opacity duration-150",
            isProblems ? "bg-gold opacity-100" : "opacity-0"
          )}
        />
        Problems
        <ChevronDown
          size={14}
          className={cn("transition-transform duration-150", open && "rotate-180")}
        />
      </button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 min-w-[160px] rounded-lg border border-ink/10 bg-paper shadow-card">
          <Link
            href="/problems"
            onClick={() => setOpen(false)}
            className={cn(
              "flex items-center gap-2 rounded-t-lg px-4 py-2.5 text-sm font-medium transition-colors hover:bg-ink/5",
              pathname.startsWith("/problems")
                ? "bg-ink/5 text-ink"
                : "text-ink-soft"
            )}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-gold" />
            DSA Problems
          </Link>
          <Link
            href="/sql"
            onClick={() => setOpen(false)}
            className={cn(
              "flex items-center gap-2 rounded-b-lg px-4 py-2.5 text-sm font-medium transition-colors hover:bg-ink/5",
              pathname.startsWith("/sql")
                ? "bg-ink/5 text-ink"
                : "text-ink-soft"
            )}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-quest" />
            SQL Problems
          </Link>
        </div>
      )}
    </div>
  );
}

export function TopBar({
  active,
  children,
}: {
  active: "dashboard" | "roadmap" | "problems" | "leagues" | "test" | "profile";
  children?: ReactNode;
}) {
  const { logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const current =
    active ??
    (pathname.startsWith("/campaign")
      ? "dashboard"
      : pathname.startsWith("/roadmap")
        ? "roadmap"
        : pathname.startsWith("/leagues")
          ? "leagues"
          : pathname.startsWith("/test")
            ? "test"
            : "problems");

  return (
    <header className="sticky top-0 z-20 border-b border-ink/8 bg-paper/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-6">
        <Brand />
        <nav className="flex items-center gap-1">
          <NavLink href="/campaign" active={current === "dashboard"}>
            Campaign
          </NavLink>
          <NavLink href="/roadmap" active={current === "roadmap"}>
            Roadmap
          </NavLink>
          <ProblemsDropdown active={current === "problems"} />
          <NavLink href="/leagues" active={current === "leagues"}>
            Leagues
          </NavLink>
          <NavLink href="/test" active={current === "test"}>
            Test
          </NavLink>
        </nav>
        <div className="ml-auto flex items-center gap-3">{children}</div>
        <ThemeToggle />
        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="btn border border-ink/12 px-3 py-1.5 text-sm text-ink-soft hover:border-rust hover:text-rust"
        >
          <LogOut size={15} />
          Log out
        </button>
      </div>
    </header>
  );
}

export function UserChip({ username }: { username: string }) {
  return (
    <Link
      href="/profile"
      title="Your profile"
      className="hidden items-center gap-1.5 rounded-full border border-gold/50 bg-gold/15 px-3 py-1 text-sm font-medium text-ink shadow-card transition-colors hover:border-gold-deep hover:bg-gold/25 sm:flex"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-gold-deep" />
      {username}
    </Link>
  );
}

const DIFFICULTY_CHIP: Record<Difficulty, string> = {
  EASY: "border-quest/40 bg-quest/10 text-quest",
  MEDIUM: "border-gold/50 bg-gold/10 text-gold-deep",
  HARD: "border-rust/40 bg-rust/10 text-rust",
};

export function DifficultyChip({ difficulty }: { difficulty: Difficulty }) {
  return (
    <span className={cn("stamp-chip", DIFFICULTY_CHIP[difficulty])}>
      {difficulty.charAt(0) + difficulty.slice(1).toLowerCase()}
    </span>
  );
}

export function SealCheck({ title }: { title?: string }) {
  return (
    <span
      title={title ?? "Solved"}
      className="flex h-7 w-7 items-center justify-center rounded-full border-[1.5px] border-quest bg-quest/10 text-quest"
    >
      <svg
        viewBox="0 0 24 24"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
      >
        <path
          d="M5 13l4 4L19 7"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
