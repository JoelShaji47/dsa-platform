"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Beaker,
  CheckCircle2,
  ChevronRight,
  EyeOff,
  Loader2,
  Play,
  Send,
  XCircle,
} from "lucide-react";
import CodeMirror from "@uiw/react-codemirror";
import { sql } from "@codemirror/lang-sql";
import { oneDark } from "@codemirror/theme-one-dark";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import client from "@/lib/api";
import { ThemeToggle, useTheme } from "@/context/theme-context";
import ProtectedRoute from "@/components/protected-route";
import { useAuth } from "@/context/auth-context";
import type {
  Difficulty,
  ProblemDetail,
  RunResultOut,
  SubmissionResultOut,
  VisibleTestResult,
} from "@/lib/types";

const DIFFICULTY_STYLE: Record<Difficulty, string> = {
  EASY: "text-quest",
  MEDIUM: "text-gold-deep",
  HARD: "text-rust",
};

function errDetail(err: unknown): string {
  if (typeof err === "object" && err !== null && "response" in err) {
    const r = (err as { response?: { data?: { detail?: string } } }).response;
    if (r?.data?.detail) return r.data.detail;
  }
  return "Something went wrong. Try again.";
}

/* ── SQL parsing helpers ────────────────────────────────────── */

interface ColumnDef {
  name: string;
  type: string;
}

interface TableInfo {
  name: string;
  columns: ColumnDef[];
  rows: string[][];
}

function parseSqlInput(input: string): TableInfo[] {
  const tables: Map<string, TableInfo> = new Map();

  // Split into statements
  const stmts = input.split(";").map((s) => s.trim()).filter(Boolean);

  for (const stmt of stmts) {
    const createMatch = stmt.match(
      /CREATE\s+TABLE\s+(\w+)\s*\(([\s\S]+)\)/i
    );
    if (createMatch) {
      const tableName = createMatch[1];
      const cols = createMatch[2]
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean)
        .map((col) => {
          const parts = col.split(/\s+/);
          const name = parts[0].replace(/["`]/g, "");
          const type = parts
            .slice(1)
            .join(" ")
            .replace(
              /\s*(PRIMARY\s+KEY|NOT\s+NULL|UNIQUE|DEFAULT\s+\S+|CHECK\s*\([^)]+\))\s*/gi,
              ""
            )
            .trim();
          return { name, type };
        });
      tables.set(tableName, {
        name: tableName,
        columns: cols,
        rows: [],
      });
      continue;
    }

    const insertMatch = stmt.match(
      /INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*([\s\S]+)/i
    );
    if (insertMatch) {
      const tableName = insertMatch[1];
      const colNames = insertMatch[2].split(",").map((c) => c.trim());
      const rows: string[][] = [];
      const rowRegex = /\(([^)]+)\)/g;
      let m: RegExpExecArray | null;
      while ((m = rowRegex.exec(insertMatch[3])) !== null) {
        rows.push(
          m[1].split(",").map((c) => c.trim().replace(/^'|'$/g, ""))
        );
      }
      const existing = tables.get(tableName);
      if (existing) {
        existing.rows.push(...rows);
      } else {
        tables.set(tableName, {
          name: tableName,
          columns: colNames.map((n) => ({ name: n, type: "" })),
          rows,
        });
      }
    }
  }

  return Array.from(tables.values());
}

function parseExpectedRows(output: string): string[][] {
  if (!output.trim()) return [];
  const lines = output.trim().split("\n").filter(Boolean);
  if (lines.length === 0) return [];
  return [
    lines[0].split("|").map((c) => c.trim()),
    ...lines.slice(1).map((l) => l.split("|").map((c) => c.trim())),
  ];
}

function stripSchemaExample(desc: string): string {
  return desc
    .replace(/## Schema[\s\S]*?(?=##\s|$)/i, "")
    .replace(/## Example[\s\S]*?(?=##\s|$)/i, "")
    .replace(/## Output[\s\S]*?(?=##\s|$)/i, "")
    .replace(/^#\s+.+\r?\n+/, "");
}

/* ── Description panel ──────────────────────────────────────── */

function SqlDescription({
  problem,
  dark,
}: {
  problem: ProblemDetail;
  dark: boolean;
}) {
  const statement = stripSchemaExample(problem.description);

  const parsedCases = useMemo(
    () =>
      problem.test_cases.map((t) => ({
        tables: parseSqlInput(t.input),
        expected: parseExpectedRows(t.expected_output),
      })),
    [problem.test_cases]
  );

  const th = (d: string, l: string) => (dark ? d : l);

  return (
    <div
      className={`min-h-full px-5 py-5 sm:px-7 ${th("bg-[#0e1119]", "bg-paper")}`}
    >
      <div className="mx-auto w-full max-w-3xl">
        <p className="eyebrow">SQL · practice</p>
        <h2 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          {problem.title}
        </h2>

        <article
          className={
            dark
              ? "prose prose-invert mt-4 max-w-none text-[14px] leading-relaxed prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[13px] prose-code:text-emerald-300 prose-code:before:content-none prose-code:after:content-none"
              : "prose mt-4 max-w-none text-[14px] leading-relaxed text-ink-soft prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-ink/[0.06] prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[13px] prose-code:text-quest prose-code:before:content-none prose-code:after:content-none"
          }
        >
          <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
        </article>

        {parsedCases.map((c, i) => (
          <div key={i} className="mt-4 space-y-5">
            {c.tables.map((tbl) => (
              <div key={tbl.name} className="space-y-3">
                {/* Schema table */}
                {tbl.columns.length > 0 && tbl.columns[0].type && (
                  <div>
                    <p className="mb-1.5 text-sm font-semibold text-ink">
                      <code
                        className={`rounded px-1.5 py-0.5 font-mono text-[13px] ${th("bg-white/10 text-emerald-300", "bg-ink/[0.06] text-quest")}`}
                      >
                        {tbl.name}
                      </code>{" "}
                      Table
                    </p>
                    <div className="overflow-hidden rounded-lg border border-ink/10">
                      <table className="w-full text-sm">
                        <thead>
                          <tr
                            className={th(
                              "bg-white/5 border-b border-white/10",
                              "bg-ink/[0.03] border-b border-ink/10"
                            )}
                          >
                            <th className="px-4 py-2.5 text-left font-semibold text-ink">
                              Column Name
                            </th>
                            <th className="px-4 py-2.5 text-left font-semibold text-ink">
                              Type
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {tbl.columns.map((col, ci) => (
                            <tr
                              key={ci}
                              className={`border-b last:border-0 ${th("border-white/5", "border-ink/5")}`}
                            >
                              <td className="px-4 py-2 font-mono text-[13px] text-ink">
                                {col.name}
                              </td>
                              <td
                                className={`px-4 py-2 font-mono text-[13px] ${th("text-gray-400", "text-ink-soft")}`}
                              >
                                {col.type}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Data table */}
                {tbl.rows.length > 0 && (
                  <div>
                    <p className="mb-1.5 text-sm font-semibold text-ink">
                      <code
                        className={`rounded px-1.5 py-0.5 font-mono text-[13px] ${th("bg-white/10 text-emerald-300", "bg-ink/[0.06] text-quest")}`}
                      >
                        {tbl.name}
                      </code>{" "}
                      Example Input
                    </p>
                    <div className="overflow-hidden rounded-lg border border-ink/10">
                      <table className="w-full text-sm">
                        <thead>
                          <tr
                            className={th(
                              "bg-white/5 border-b border-white/10",
                              "bg-ink/[0.03] border-b border-ink/10"
                            )}
                          >
                            {tbl.columns.map((col, ci) => (
                              <th
                                key={ci}
                                className="px-4 py-2.5 text-left font-semibold text-ink"
                              >
                                {col.name}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {tbl.rows.map((row, ri) => (
                            <tr
                              key={ri}
                              className={`border-b last:border-0 ${th("border-white/5", "border-ink/5")}`}
                            >
                              {row.map((cell, ci) => (
                                <td
                                  key={ci}
                                  className={`px-4 py-2 font-mono text-[13px] ${th("text-gray-600", "text-ink-soft")}`}
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {c.expected.length > 0 ? (
              <div>
                <p className="mb-1.5 text-sm font-semibold text-ink">
                  Example Output
                </p>
                <div className="overflow-hidden rounded-lg border border-quest/20">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-quest/20 bg-quest/5">
                        {c.expected[0].map((col, ci) => (
                          <th
                            key={ci}
                            className="px-4 py-2.5 text-left font-semibold text-quest"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {c.expected.slice(1).map((row, ri) => (
                        <tr
                          key={ri}
                          className="border-b border-quest/10 last:border-0"
                        >
                          {row.map((cell, ci) => (
                            <td
                              key={ci}
                              className="px-4 py-2 font-mono text-[13px] text-quest"
                            >
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Console panel ──────────────────────────────────────────── */

function SqlConsole({
  error,
  runResult,
  submitResult,
  problem,
  dark,
}: {
  error: string | null;
  runResult: RunResultOut | null;
  submitResult: SubmissionResultOut | null;
  problem: ProblemDetail;
  dark: boolean;
}) {
  const th = (d: string, l: string) => (dark ? d : l);
  const shown = submitResult || runResult;
  const isRun = !!runResult && !submitResult;

  return (
    <div className={th("min-h-full bg-[#16162a]", "min-h-full bg-card")}>
      {error && (
        <div className="border-b border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {shown && (
        <div className="p-4">
          <p className={th("mb-3 font-mono text-[11px] text-gray-500", "mb-3 font-mono text-[11px] text-ink-faint")}>
            {isRun
              ? `Run · ${runResult.test_results.length} visible case${runResult.test_results.length === 1 ? "" : "s"}`
              : `Submit · all ${submitResult?.test_results.length ?? 0} cases`}
          </p>

          {submitResult && submitResult.xp_awarded > 0 && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-300">
              +{submitResult.xp_awarded} XP earned
            </div>
          )}

          {submitResult && submitResult.new_badges?.length > 0 && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm font-medium text-yellow-300">
              Badge unlocked: {submitResult.new_badges.join(", ")}
            </div>
          )}

          {submitResult && (
            <div className="mb-3">
              <p className={th("mb-2 text-xs text-gray-500", "mb-2 text-xs text-ink-faint")}>
                Tests · {submitResult.test_results.filter((t) => t.passed).length}/{submitResult.test_results.length} passed
              </p>
              <div className="flex flex-wrap gap-1.5">
                {submitResult.test_results.map((t) => (
                  <span
                    key={t.index}
                    title={`Test ${t.index + 1}: ${t.passed ? "passed" : "failed"}`}
                    className={`flex h-7 w-7 items-center justify-center rounded-md border font-mono text-xs font-bold ${
                      t.passed
                        ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
                        : "border-red-500/50 bg-red-500/15 text-red-400"
                    }`}
                  >
                    {t.index + 1}
                  </span>
                ))}
              </div>
            </div>
          )}

          {submitResult &&
            submitResult.test_results
              .filter((t) => !t.passed && !t.hidden)
              .map((t) => (
                <div key={t.index} className="mt-2 rounded-lg border border-red-500/30 bg-red-500/5 p-3">
                  <p className={th("flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400", "flex items-center gap-1.5 font-mono text-xs font-medium text-ink-soft")}>
                    <XCircle size={12} className="text-red-400" />
                    Case {t.index + 1}
                  </p>
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>Expected</p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400", "overflow-x-auto whitespace-pre-wrap rounded-md bg-quest/10 p-2 font-mono text-[12px] text-quest")}>{t.expected_output || ""}</pre>
                    </div>
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>Your output</p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300", "overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-rust/10 p-2 font-mono text-[12px] text-rust")}>{t.actual_output || "(no output)"}</pre>
                    </div>
                  </div>
                </div>
              ))}

          {submitResult &&
            submitResult.test_results
              .filter((t) => !t.passed && t.hidden)
              .map((t) => (
                <div key={t.index} className="mt-2 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3">
                  <EyeOff size={13} className="shrink-0 text-yellow-400/80" />
                  <p className={th("font-mono text-xs text-gray-400", "font-mono text-xs text-ink-soft")}>
                    Hidden test #{t.index + 1} failed
                    <span className={th("text-gray-600", "text-ink-faint")}> (input is secret)</span>
                  </p>
                </div>
              ))}

          {isRun &&
            runResult.test_results.map((t: VisibleTestResult) => (
              <div key={t.index} className={`mt-2 rounded-lg border p-3 ${t.passed ? "border-emerald-500/30 bg-emerald-500/5" : "border-red-500/30 bg-red-500/5"}`}>
                <p className={th("flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400", "flex items-center gap-1.5 font-mono text-xs font-medium text-ink-soft")}>
                  {t.passed ? <CheckCircle2 size={12} className="text-emerald-400" /> : <XCircle size={12} className="text-red-400" />}
                  Case {t.index + 1}
                </p>
                {!t.passed && (
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>Expected</p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400", "overflow-x-auto whitespace-pre-wrap rounded-md bg-quest/10 p-2 font-mono text-[12px] text-quest")}>{t.expected_output}</pre>
                    </div>
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>Your output</p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300", "overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-rust/10 p-2 font-mono text-[12px] text-rust")}>{t.actual_output || "(no output)"}</pre>
                    </div>
                  </div>
                )}
              </div>
            ))}

          <div className={th("mb-3 font-mono text-xs text-gray-500", "mb-3 font-mono text-xs text-ink-faint")}>
            {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
          </div>
        </div>
      )}

      {!shown && !error && (
        <div className="flex flex-col items-center justify-center gap-1 py-8 text-center">
          <p className={th("text-sm text-gray-500", "text-sm text-ink-soft")}>Run or submit your query to see results here.</p>
          <p className={th("font-mono text-[11px] text-gray-600", "font-mono text-[11px] text-ink-faint")}>
            Run checks {problem.test_cases.length} visible case{problem.test_cases.length === 1 ? "" : "s"} · Submit checks all{" "}
            {problem.test_cases.length + problem.hidden_test_count} ({problem.hidden_test_count} hidden)
          </p>
        </div>
      )}
    </div>
  );
}

/* ── Main page ──────────────────────────────────────────────── */

export default function SqlSolveClient() {
  const params = useParams();
  const { user } = useAuth();
  const dark = useTheme() === "dark";
  const th = (d: string, l: string) => (dark ? d : l);
  const slug = Array.isArray(params.slug)
    ? params.slug[0]
    : (params.slug as string);

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [pageStatus, setPageStatus] = useState("loading");
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<RunResultOut | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmissionResultOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    client
      .get<ProblemDetail>(`/sql/${slug}`)
      .then((res) => {
        if (cancelled) return;
        setProblem(res.data);
        setCode(res.data.starter_code?.sql ?? "");
        setPageStatus("ok");
      })
      .catch(() => {
        if (!cancelled) setPageStatus("error");
      });
    return () => { cancelled = true; };
  }, [slug]);

  const run = useCallback(async () => {
    setRunning(true);
    setError(null);
    setSubmitResult(null);
    try {
      const res = await client.post<RunResultOut>(`/sql/${slug}/run`, { language: "sql", source_code: code }, { timeout: 120000 });
      setRunResult(res.data);
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setRunning(false);
    }
  }, [slug, code]);

  const submit = useCallback(async () => {
    setSubmitting(true);
    setError(null);
    setRunResult(null);
    try {
      const res = await client.post<SubmissionResultOut>(`/sql/${slug}/submit`, { language: "sql", source_code: code }, { timeout: 120000 });
      setSubmitResult(res.data);
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setSubmitting(false);
    }
  }, [slug, code]);

  if (pageStatus === "loading") {
    return (
      <div className="atlas-bg flex h-screen items-center justify-center gap-2 text-ink-soft">
        <Loader2 size={20} className="animate-spin" />
        Loading...
      </div>
    );
  }

  if (pageStatus === "error" || !problem) {
    return (
      <div className="atlas-bg flex h-screen flex-col items-center justify-center gap-4">
        <p className="text-lg text-ink-soft">This SQL problem does not exist.</p>
        <Link href="/sql" className="font-semibold text-quest hover:underline">Back to SQL problems</Link>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className={`flex h-screen flex-col ${th("bg-[#0b0d12]", "bg-paper")}`}>
        {/* ── Top bar ──────────────────────────────────────────── */}
        <header className={`flex h-12 shrink-0 items-center justify-between border-b px-4 ${th("border-white/10 bg-[#0e1119]", "border-ink/10 bg-white")}`}>
          <div className="flex min-w-0 items-center gap-3">
            <Link href="/sql" className={`flex items-center gap-1.5 rounded-md px-2 py-1 text-sm transition-colors ${th("text-gray-400 hover:text-gray-200", "text-ink-soft hover:text-ink")}`}>
              <ArrowLeft size={15} />
              SQL Problems
            </Link>
            <span className={`h-4 w-px ${th("bg-white/10", "bg-ink/10")}`} />
            <h1 className={`truncate text-sm font-semibold ${th("text-gray-100", "text-ink")}`}>{problem.title}</h1>
            <span className={`text-xs font-medium ${DIFFICULTY_STYLE[problem.difficulty as Difficulty]}`}>
              {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
            </span>
            {problem.solved && (
              <span className="rounded-md border border-emerald-500/50 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">Solved</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button onClick={run} disabled={running || submitting} className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${th("border-white/10 bg-[#252540] text-gray-300 hover:border-white/20 hover:text-gray-100", "border-ink/15 bg-ink/[0.04] text-ink-soft hover:border-ink/25 hover:text-ink")}`}>
              {running ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} />}
              Run
            </button>
            <button onClick={submit} disabled={running || submitting} className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-500 disabled:opacity-50">
              {submitting ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
              Submit
            </button>
          </div>
        </header>

        {/* ── Main layout ──────────────────────────────────────── */}
        <div className="flex min-h-0 flex-1">
          {/* Left: description */}
          <div className={`w-[420px] shrink-0 overflow-y-auto border-r ${th("border-white/10", "border-ink/10")}`}>
            <SqlDescription problem={problem} dark={dark} />
          </div>

          {/* Right: editor + console */}
          <div className="flex min-w-0 flex-1 flex-col">
            {/* Code editor - light wrapper in light mode */}
            <div className={`min-h-0 flex-1 overflow-auto ${th("bg-[#1e1e2e]", "bg-white")}`}>
              <CodeMirror
                value={code}
                onChange={(val) => setCode(val)}
                extensions={[sql()]}
                theme={dark ? oneDark : undefined}
                height="100%"
                basicSetup={{
                  lineNumbers: true,
                  highlightActiveLine: true,
                  highlightSelectionMatches: true,
                  foldGutter: true,
                }}
              />
            </div>
            {/* Console */}
            <div className={`shrink-0 border-t ${th("border-white/10", "border-ink/10")}`}>
              <div className="max-h-[40vh] overflow-y-auto">
                <SqlConsole error={error} runResult={runResult} submitResult={submitResult} problem={problem} dark={dark} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
