"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowUpDown,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ListFilter,
  Search,
  SearchX,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { SealCheck, TopBar, UserChip } from "@/components/shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Difficulty, ProblemListItem } from "@/lib/types";

const TOPICS = [
  "ARRAY",
  "STRING",
  "LINKED_LIST",
  "STACK",
  "QUEUE",
  "TREE",
  "GRAPH",
  "DP",
];

const DIFFICULTIES: Difficulty[] = ["EASY", "MEDIUM", "HARD"];

const DIFFICULTY_RANK: Record<Difficulty, number> = {
  EASY: 0,
  MEDIUM: 1,
  HARD: 2,
};

const DIFFICULTY_BADGE: Record<Difficulty, string> = {
  EASY: "border-quest/40 bg-quest/10 text-quest hover:bg-quest/20",
  MEDIUM: "border-gold/50 bg-gold/10 text-gold-deep hover:bg-gold/20",
  HARD: "border-rust/40 bg-rust/10 text-rust hover:bg-rust/20",
};

type StatusFilter = "all" | "solved" | "todo";
type SourceFilter = "all" | "neetcode" | "tuf";
type SortKey = "title" | "difficulty";
type SortDir = "asc" | "desc";

const PAGE_SIZE = 25;

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(t);
  }, [value, delayMs]);
  return debounced;
}

export default function ProblemsClient() {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [problems, setProblems] = useState<ProblemListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(false);

  const [topic, setTopic] = useState(searchParams.get("topic") ?? "all");
  const [difficulty, setDifficulty] = useState(searchParams.get("difficulty") ?? "all");
  const [source, setSource] = useState<SourceFilter>(
    (searchParams.get("source") as SourceFilter) || "all"
  );
  const [search, setSearch] = useState(searchParams.get("search") ?? "");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [sortKey, setSortKey] = useState<SortKey>("title");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(0);

  const debouncedSearch = useDebouncedValue(search, 300);

  // Keep the URL in sync so filters survive navigation / back-button.
  useEffect(() => {
    const params = new URLSearchParams();
    if (topic !== "all") params.set("topic", topic);
    if (difficulty !== "all") params.set("difficulty", difficulty);
    if (source !== "all") params.set("source", source);
    if (debouncedSearch) params.set("search", debouncedSearch);
    const qs = params.toString();
    router.replace(qs ? `/problems?${qs}` : "/problems", { scroll: false });
  }, [topic, difficulty, source, debouncedSearch, router]);

  // Filter changes re-arm the loading state from the event handlers below;
  // the fetch effect itself only writes results (async continuations).
  // Client-side sort/status changes only reset the page (safePage clamps).
  const beginFetch = useCallback(() => {
    setLoading(true);
    setFetchError(false);
    setPage(0);
  }, []);
  const resetPage = useCallback(() => {
    setPage(0);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const params: Record<string, string> = {};
    if (topic !== "all") params.topic = topic;
    if (difficulty !== "all") params.difficulty = difficulty;
    if (source !== "all") params.source = source;
    if (debouncedSearch) params.search = debouncedSearch;
    client
      .get<ProblemListItem[]>("/problems", { params })
      .then((res) => {
        if (!cancelled) setProblems(res.data);
      })
      .catch(() => {
        if (!cancelled) {
          setProblems([]);
          setFetchError(true);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [topic, difficulty, source, debouncedSearch]);

  const visible = useMemo(() => {
    const filtered =
      status === "all"
        ? problems
        : problems.filter((p) => (status === "solved" ? p.solved : !p.solved));
    const sorted = [...filtered].sort((a, b) => {
      const cmp =
        sortKey === "title"
          ? a.title.localeCompare(b.title)
          : DIFFICULTY_RANK[a.difficulty] - DIFFICULTY_RANK[b.difficulty];
      return sortDir === "asc" ? cmp : -cmp;
    });
    return sorted;
  }, [problems, status, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount - 1);
  const pageRows = visible.slice(
    safePage * PAGE_SIZE,
    safePage * PAGE_SIZE + PAGE_SIZE
  );

  const solvedCount = problems.filter((p) => p.solved).length;
  const filtersActive =
    topic !== "all" ||
    difficulty !== "all" ||
    source !== "all" ||
    debouncedSearch !== "" ||
    status !== "all";

  const clearFilters = () => {
    beginFetch();
    setTopic("all");
    setDifficulty("all");
    setSource("all");
    setSearch("");
    setStatus("all");
  };

  const toggleSort = (key: SortKey) => {
    resetPage();
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen">
        <TopBar active="problems">
          {user && <UserChip username={user.username} />}
        </TopBar>

        <main className="mx-auto max-w-6xl px-6 py-10">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="eyebrow">Problem library</p>
              <h1 className="mt-1 font-display text-4xl font-bold tracking-tight text-ink">
                Choose your next challenge
              </h1>
            </div>
            {!loading && !fetchError && problems.length > 0 && (
              <Badge
                variant="secondary"
                className="gap-1.5 px-3 py-1.5 text-sm font-semibold"
              >
                <CheckCircle2 size={15} className="text-quest" />
                {solvedCount}/{problems.length} solved
              </Badge>
            )}
          </div>

          {/* ── Toolbar ─────────────────────────────────────────── */}
          <div className="panel mt-7 flex flex-col gap-3 p-4 lg:flex-row lg:items-center">
            <div className="relative min-w-[220px] flex-1">
              <Search
                size={17}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
              />
              <Input
                value={search}
                onChange={(e) => {
                  beginFetch();
                  setSearch(e.target.value);
                }}
                placeholder="Search by title…"
                className="bg-white pl-10"
              />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Select
                value={topic}
                onValueChange={(v) => {
                  beginFetch();
                  setTopic(v);
                }}
              >
                <SelectTrigger className="w-[160px] bg-white">
                  <SelectValue placeholder="All topics" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All topics</SelectItem>
                  {TOPICS.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t.replace("_", " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={difficulty}
                onValueChange={(v) => {
                  beginFetch();
                  setDifficulty(v);
                }}
              >
                <SelectTrigger className="w-[140px] bg-white">
                  <SelectValue placeholder="Difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All levels</SelectItem>
                  {DIFFICULTIES.map((d) => (
                    <SelectItem key={d} value={d}>
                      {d.charAt(0) + d.slice(1).toLowerCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={status}
                onValueChange={(v) => {
                  resetPage();
                  setStatus(v as StatusFilter);
                }}
              >
                <SelectTrigger className="w-[130px] bg-white">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="todo">To do</SelectItem>
                  <SelectItem value="solved">Solved</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={source}
                onValueChange={(v) => {
                  beginFetch();
                  setSource(v as SourceFilter);
                }}
              >
                <SelectTrigger className="w-[150px] bg-white">
                  <SelectValue placeholder="Source" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All sources</SelectItem>
                  <SelectItem value="neetcode">NeetCode</SelectItem>
                  <SelectItem value="tuf">TakeUForward</SelectItem>
                </SelectContent>
              </Select>
              {filtersActive && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <ListFilter size={14} />
                  Clear
                </Button>
              )}
            </div>
          </div>

          {/* ── Table ───────────────────────────────────────────── */}
          <div className="panel mt-4 overflow-hidden">
            {loading ? (
              <div className="space-y-3 p-5">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <Skeleton className="h-7 w-7 rounded-full" />
                    <Skeleton className="h-5 flex-1" />
                    <Skeleton className="h-6 w-20" />
                  </div>
                ))}
              </div>
            ) : fetchError ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <p className="text-[0.95rem] text-ink-soft">
                  Couldn&apos;t load problems. The server might be down.
                </p>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  Try again
                </Button>
              </div>
            ) : visible.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <SearchX size={28} className="text-ink-faint" />
                <p className="text-[0.95rem] text-ink-faint">
                  No problems match these filters. Loosen them and look again.
                </p>
                {filtersActive && (
                  <Button variant="outline" size="sm" onClick={clearFilters}>
                    Clear filters
                  </Button>
                )}
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="w-12">Status</TableHead>
                      <TableHead className="w-14">#</TableHead>
                      <TableHead>
                        <button
                          onClick={() => toggleSort("title")}
                          className="inline-flex items-center gap-1 hover:text-ink"
                        >
                          Title
                          <ArrowUpDown
                            size={13}
                            className={cn(sortKey === "title" && "text-gold-deep")}
                          />
                        </button>
                      </TableHead>
                      <TableHead>Topic</TableHead>
                      <TableHead>
                        <button
                          onClick={() => toggleSort("difficulty")}
                          className="inline-flex items-center gap-1 hover:text-ink"
                        >
                          Difficulty
                          <ArrowUpDown
                            size={13}
                            className={cn(
                              sortKey === "difficulty" && "text-gold-deep"
                            )}
                          />
                        </button>
                      </TableHead>
                      <TableHead className="w-24 text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pageRows.map((p, i) => (
                      <TableRow key={p.id}>
                        <TableCell>
                          {p.solved ? (
                            <SealCheck title={`Solved: ${p.title}`} />
                          ) : (
                            <span className="block h-7 w-7 rounded-full border-[1.5px] border-dashed border-ink/20" />
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-xs text-ink-faint">
                          {safePage * PAGE_SIZE + i + 1}
                        </TableCell>
                        <TableCell>
                          <Link
                            href={`/problems/${p.slug}/solve`}
                            className="font-semibold text-ink hover:text-gold-deep hover:underline"
                          >
                            {p.title}
                          </Link>
                          {p.sources.includes("tuf") && (
                            <Badge
                              variant="outline"
                              className="ml-2 border-gold/50 bg-gold/10 align-middle text-[10px] text-gold-deep"
                            >
                              TUF
                            </Badge>
                          )}
                          {p.sources.includes("neetcode") &&
                            p.sources.includes("tuf") && (
                              <Badge
                                variant="outline"
                                className="ml-1 border-ink/20 bg-ink/5 align-middle text-[10px] text-ink-soft"
                              >
                                NC
                              </Badge>
                            )}
                        </TableCell>
                        <TableCell className="eyebrow">
                          {p.topic.replace("_", " ")}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={cn(DIFFICULTY_BADGE[p.difficulty])}
                          >
                            {p.difficulty.charAt(0) +
                              p.difficulty.slice(1).toLowerCase()}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm" asChild>
                            <Link href={`/problems/${p.slug}/solve`}>
                              Solve
                              <ChevronRight size={14} />
                            </Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {pageCount > 1 && (
                  <div className="flex items-center justify-between border-t border-ink/8 px-5 py-3">
                    <p className="font-mono text-xs text-ink-faint">
                      Page {safePage + 1} of {pageCount} · {visible.length}{" "}
                      problems
                    </p>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={safePage === 0}
                        onClick={() => setPage(safePage - 1)}
                      >
                        <ChevronLeft size={14} />
                        Prev
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={safePage >= pageCount - 1}
                        onClick={() => setPage(safePage + 1)}
                      >
                        Next
                        <ChevronRight size={14} />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
