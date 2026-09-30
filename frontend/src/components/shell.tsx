"use client";

import { Compass, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
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

export function TopBar({
  active,
  children,
}: {
  active: "dashboard" | "roadmap" | "problems" | "leagues" | "test";
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
          <NavLink href="/problems" active={current === "problems"}>
            Problems
          </NavLink>
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
    <span className="hidden items-center gap-1.5 rounded-full border border-gold/50 bg-gold/15 px-3 py-1 text-sm font-medium text-ink shadow-card sm:flex">
      <span className="h-1.5 w-1.5 rounded-full bg-gold-deep" />
      {username}
    </span>
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
