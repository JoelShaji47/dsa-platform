"use client";

import {
  Award,
  CheckCircle2,
  EyeOff,
  Lightbulb,
  Loader2,
  Sparkles,
  XCircle,
  Zap,
} from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type {
  ProblemDetail,
  ReviewOut,
  RunResultOut,
  SubmissionResultOut,
  SubmissionStatus,
  VisibleTestResult,
} from "@/lib/types";
import { useTheme } from "@/context/theme-context";
import { STATUS_STYLES, statusKeyLabel } from "./status-utils";

function TestChip({ passed, index }: { passed: boolean; index: number }) {
  return (
    <span
      title={`Test ${index + 1}: ${passed ? "passed" : "failed"}`}
      className={`flex h-7 w-7 items-center justify-center rounded-md border font-mono text-xs font-bold ${
        passed
          ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
          : "border-red-500/50 bg-red-500/15 text-red-400"
      }`}
    >
      {index + 1}
    </span>
  );
}

export default function ConsolePanel({
  problem,
  error,
  runResult,
  submitResult,
  consoleTab,
  setConsoleTab,
  review,
  reviewLoading,
  fetchReview,
}: {
  problem: ProblemDetail;
  error: string | null;
  runResult: RunResultOut | null;
  submitResult: SubmissionResultOut | null;
  consoleTab: string;
  setConsoleTab: (t: string) => void;
  review: ReviewOut | null;
  reviewLoading: boolean;
  fetchReview: () => void;
}) {
  const dark = useTheme() === "dark";
  // th() picks the dark class or the light class — keeps every surface themed.
  const th = (d: string, l: string) => (dark ? d : l);
  const shown = submitResult || runResult;
  const shownStatus: SubmissionStatus | undefined = shown?.status;
  const compileError =
    shown &&
    (shownStatus === "COMPILATION_ERROR" || shownStatus === "RUNTIME_ERROR")
      ? (shown as RunResultOut).test_results?.find((t) => t.actual_output)
          ?.actual_output
      : null;
  const hasOutputTab = error || compileError;

  return (
    <div className={th("min-h-full bg-[#16162a]", "min-h-full bg-card")}>
      {error && (
        <div className="border-b border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Tabs — Testcase is always available (LeetCode-style); Result needs a run */}
      <div className={th("flex border-b border-white/10", "flex border-b border-ink/10")}>
        <button
          onClick={() => shown && setConsoleTab("result")}
          disabled={!shown}
          className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
            consoleTab === "result"
              ? "border-emerald-400 text-emerald-400"
              : "border-transparent ${th('text-gray-500 hover:text-gray-300', 'text-ink-faint hover:text-ink')}"
          } disabled:opacity-40`}
        >
          Result
        </button>
        <button
          onClick={() => setConsoleTab("testcase")}
          className={`border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
            consoleTab === "testcase"
              ? "border-emerald-400 text-emerald-400"
              : "border-transparent ${th('text-gray-500 hover:text-gray-300', 'text-ink-faint hover:text-ink')}"
          }`}
        >
          Testcase
        </button>
        {hasOutputTab && (
          <button
            onClick={() => setConsoleTab("output")}
            className={`flex items-center gap-1.5 border-b-2 px-4 py-2 text-xs font-medium transition-colors ${
              consoleTab === "output"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent ${th('text-gray-500 hover:text-gray-300', 'text-ink-faint hover:text-ink')}"
            }`}
          >
            {compileError ? (
              <>
                <XCircle size={12} className="text-red-400" />
                Compile Error
              </>
            ) : (
              "Output"
            )}
          </button>
        )}
      </div>

      {shown && consoleTab === "result" && (
        <div className="p-4">
          <p className={th("mb-3 font-mono text-[11px] text-gray-500", "mb-3 font-mono text-[11px] text-ink-faint")}>
            {runResult
              ? `Run · ${runResult.test_results.length} visible case${runResult.test_results.length === 1 ? "" : "s"}`
              : `Submit · all ${(submitResult?.test_results.length ?? 0)} cases (${problem.hidden_test_count} hidden)`}
          </p>
          {submitResult && submitResult.xp_awarded > 0 && (
            <div className="mb-3 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-300">
              <p className="flex items-center gap-2">
                <Zap size={14} />
                +{submitResult.xp_awarded} XP earned
                {submitResult.current_streak > 1 && (
                  <span className="ml-auto text-xs text-yellow-400/70">
                    Streak · {submitResult.current_streak}d
                  </span>
                )}
              </p>
              {submitResult.xp_breakdown && (
                <p className="mt-1 font-mono text-[11px] text-yellow-400/70">
                  base {submitResult.xp_breakdown.base}
                  {submitResult.xp_breakdown.streak_mult > 1 &&
                    ` · streak ×${submitResult.xp_breakdown.streak_mult}`}
                  {submitResult.xp_breakdown.clean_mult > 1 && " · clean ×1.25"}
                  {submitResult.xp_breakdown.weak_mult > 1 && " · comeback ×1.25"}
                </p>
              )}
            </div>
          )}
          {submitResult && submitResult.xp_forfeited && (
            <div className={th("mb-3 flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-400", "mb-3 flex items-center gap-2 rounded-lg border border-ink/10 bg-ink/[0.03] px-3 py-2 text-xs text-ink-soft")}>
              <Lightbulb size={13} className="text-yellow-400/70" />
              First-solve XP forfeited — hints were used.
            </div>
          )}
          {submitResult && submitResult.new_badges?.length > 0 && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm font-medium text-yellow-300">
              <Award size={14} />
              Badge unlocked: {submitResult.new_badges.join(", ")}
            </div>
          )}

          {submitResult && (
            <div className="mb-3">
              <p className={th("mb-2 text-xs text-gray-500", "mb-2 text-xs text-ink-faint")}>
                Tests · {submitResult.test_results.filter((t) => t.passed).length}/
                {submitResult.test_results.length} passed
              </p>
              <div className="flex flex-wrap gap-1.5">
                {submitResult.test_results.map((t) => (
                  <TestChip key={t.index} index={t.index} passed={t.passed} />
                ))}
              </div>
            </div>
          )}

          {submitResult &&
            submitResult.test_results
              .filter((t) => !t.passed && !t.hidden)
              .map((t) => (
                <div
                  key={t.index}
                  className="mt-2 rounded-lg border border-red-500/30 bg-red-500/5 p-3"
                >
                  <p className={th("flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400", "flex items-center gap-1.5 font-mono text-xs font-medium text-ink-soft")}>
                    <XCircle size={12} className="text-red-400" />
                    Case {t.index + 1}
                    {t.status_key && <span>· {statusKeyLabel(t.status_key)}</span>}
                  </p>
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Input
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-gray-300", "overflow-x-auto whitespace-pre-wrap rounded-md bg-ink/[0.04] p-2 font-mono text-[12px] text-ink-soft")}>
                        {(t.input || "").trimEnd()}
                      </pre>
                    </div>
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Expected
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400", "overflow-x-auto whitespace-pre-wrap rounded-md bg-quest/10 p-2 font-mono text-[12px] text-quest")}>
                        {t.expected_output}
                      </pre>
                    </div>
                    <div className="sm:col-span-2">
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Your output
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300", "overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-rust/10 p-2 font-mono text-[12px] text-rust")}>
                        {t.actual_output || "(no output)"}
                      </pre>
                    </div>
                  </div>
                </div>
              ))}

          {submitResult &&
            submitResult.test_results
              .filter((t) => !t.passed && t.hidden)
              .map((t) => (
                <div
                  key={t.index}
                  className="mt-2 flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3"
                >
                  <EyeOff size={13} className="shrink-0 text-yellow-400/80" />
                  <p className={th("font-mono text-xs text-gray-400", "font-mono text-xs text-ink-soft")}>
                    Hidden test #{t.index + 1} failed
                    {t.status_key && (
                      <span className="text-yellow-300/90">
                        {" "}· {statusKeyLabel(t.status_key)}
                      </span>
                    )}
                    <span className={th("text-gray-600", "text-ink-faint")}> (input is secret)</span>
                  </p>
                </div>
              ))}

          <div className={th("mb-3 font-mono text-xs text-gray-500", "mb-3 font-mono text-xs text-ink-faint")}>
            {shown.runtime_ms.toFixed(0)} ms · {(shown.memory_kb / 1024).toFixed(1)} MB
          </div>

          {submitResult && submitResult.status !== "ACCEPTED" && (
            <div className="mt-3">
              {review ? (
                <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3">
                  <p className="flex items-center gap-2 text-sm font-semibold text-yellow-300">
                    <Sparkles size={14} />
                    AI review
                    <span className="rounded border border-yellow-500/30 px-1.5 py-0.5 text-[10px] font-normal text-yellow-400/80">
                      {review.bug_type}
                    </span>
                  </p>
                  <p className={th("mt-2 text-sm font-medium text-gray-200", "mt-2 text-sm font-medium text-ink")}>
                    {review.verdict}
                  </p>
                  <article className={th("prose prose-invert prose-sm mt-2 max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400", "prose prose-sm mt-2 max-w-none text-[13px] leading-relaxed prose-code:text-quest")}>
                    <Markdown remarkPlugins={[remarkGfm]}>{review.explanation}</Markdown>
                  </article>
                  <p className={th("mt-3 mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mt-3 mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                    How to fix
                  </p>
                  <article className={th("prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400", "prose prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-quest")}>
                    <Markdown remarkPlugins={[remarkGfm]}>{review.fix_hint}</Markdown>
                  </article>
                </div>
              ) : (
                <button
                  onClick={fetchReview}
                  disabled={reviewLoading}
                  className="flex items-center gap-1.5 rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs font-medium text-yellow-300 hover:bg-yellow-500/20 disabled:opacity-50"
                >
                  {reviewLoading ? (
                    <Loader2 size={13} className="animate-spin" />
                  ) : (
                    <Sparkles size={13} />
                  )}
                  Get AI review
                </button>
              )}
            </div>
          )}

          {runResult &&
            runResult.test_results.map((t: VisibleTestResult) => (
              <div
                key={t.index}
                className={`mt-2 rounded-lg border p-3 ${
                  t.passed
                    ? "border-emerald-500/30 bg-emerald-500/5"
                    : "border-red-500/30 bg-red-500/5"
                }`}
              >
                <p className={th("flex items-center gap-1.5 font-mono text-xs font-medium text-gray-400", "flex items-center gap-1.5 font-mono text-xs font-medium text-ink-soft")}>
                  {t.passed ? (
                    <CheckCircle2 size={12} className="text-emerald-400" />
                  ) : (
                    <XCircle size={12} className="text-red-400" />
                  )}
                  Case {t.index + 1}
                  {!t.passed && shownStatus && (
                    <span>· {STATUS_STYLES[shownStatus]?.label}</span>
                  )}
                </p>
                {!t.passed && t.input != null && (
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Input
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-gray-300", "overflow-x-auto whitespace-pre-wrap rounded-md bg-ink/[0.04] p-2 font-mono text-[12px] text-ink-soft")}>
                        {(t.input || "").trimEnd()}
                      </pre>
                    </div>
                    <div>
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Expected
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md bg-[#1a1a2e] p-2 font-mono text-[12px] text-emerald-400", "overflow-x-auto whitespace-pre-wrap rounded-md bg-quest/10 p-2 font-mono text-[12px] text-quest")}>
                        {t.expected_output}
                      </pre>
                    </div>
                    <div className="sm:col-span-2">
                      <p className={th("mb-1 text-[11px] font-medium uppercase tracking-wider text-gray-500", "mb-1 text-[11px] font-medium uppercase tracking-wider text-ink-faint")}>
                        Your output
                      </p>
                      <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-[#1a1a2e] p-2 font-mono text-[12px] text-red-300", "overflow-x-auto whitespace-pre-wrap rounded-md border border-red-500/30 bg-rust/10 p-2 font-mono text-[12px] text-rust")}>
                        {t.actual_output || "(no output)"}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ))}
        </div>
      )}

      {consoleTab === "testcase" && (
        <div className="p-4">
          <p className={th("mb-2 text-xs text-gray-500", "mb-2 text-xs text-ink-faint")}>
            {runResult
              ? "Test case inputs (read-only)"
              : "Visible test cases (read-only)"}
          </p>
          {(runResult
            ? runResult.test_results
            : problem.test_cases.map((c, i) => ({ index: i, input: c.input }))
          ).map((t) => (
            <div
              key={t.index}
              className={th("mb-2 rounded-lg border border-white/10 bg-[#1a1a2e] p-3", "mb-2 rounded-lg border border-ink/10 bg-card p-3")}
            >
              <p className={th("mb-1 font-mono text-xs text-gray-500", "mb-1 font-mono text-xs text-ink-faint")}>
                Case {t.index + 1}
              </p>
              <pre className={th("overflow-x-auto whitespace-pre-wrap font-mono text-[12px] text-gray-300", "overflow-x-auto whitespace-pre-wrap font-mono text-[12px] text-ink-soft")}>
                {((t as { input?: string }).input || "").trimEnd()}
              </pre>
            </div>
          ))}
        </div>
      )}

      {consoleTab === "output" && (
        <div className="p-4">
          {compileError ? (
            <div>
              <div className="mb-3 flex items-center gap-2">
                <XCircle size={14} className="text-red-400" />
                <span className="text-sm font-medium text-red-300">
                  {shownStatus === "COMPILATION_ERROR"
                    ? "Compilation Error"
                    : "Runtime Error"}
                </span>
              </div>
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[12px] leading-relaxed text-red-200">
                {compileError}
              </pre>
            </div>
          ) : error ? (
            <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/5 p-4 font-mono text-[12px] leading-relaxed text-red-200">
              {error}
            </pre>
          ) : shown ? (
            <div>
              <p className={th("mb-2 text-xs text-gray-500", "mb-2 text-xs text-ink-faint")}>Standard output</p>
              <pre className={th("overflow-x-auto whitespace-pre-wrap rounded-lg border border-white/10 bg-[#1a1a2e] p-4 font-mono text-[12px] leading-relaxed text-gray-300", "overflow-x-auto whitespace-pre-wrap rounded-lg border border-ink/10 bg-ink/[0.03] p-4 font-mono text-[12px] leading-relaxed text-ink-soft")}>
                {(shown as RunResultOut).test_results
                  ?.filter((t) => t.actual_output != null)
                  .map((t) => `Case ${t.index + 1}:\n${t.actual_output}`)
                  .join("\n\n") || "(no output)"}
              </pre>
            </div>
          ) : null}
        </div>
      )}

      {!shown && !error && consoleTab !== "testcase" && (
        <div className="flex flex-col items-center justify-center gap-1 py-8 text-center">
          <p className={th("text-sm text-gray-500", "text-sm text-ink-soft")}>
            Run or submit your code to see results here.
          </p>
          <p className={th("font-mono text-[11px] text-gray-600", "font-mono text-[11px] text-ink-faint")}>
            Run checks {problem.test_cases.length} visible case
            {problem.test_cases.length === 1 ? "" : "s"} · Submit checks all{" "}
            {problem.test_cases.length + problem.hidden_test_count} (
            {problem.hidden_test_count} hidden)
          </p>
        </div>
      )}
    </div>
  );
}
