"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowLeft, Clock, Loader2, Sparkles, TriangleAlert } from "lucide-react";

import { useTheme } from "@/context/theme-context";
import type { AnalyzeOut } from "@/lib/types";

export default function AnalysisView({
  analysis,
  loading,
  error,
  onClose,
}: {
  analysis: AnalyzeOut | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
}) {
  const dark = useTheme() === "dark";
  const th = (d: string, l: string) => (dark ? d : l);

  return (
    <div
      className={th(
        "min-h-full overflow-y-auto bg-[#16162a]",
        "min-h-full overflow-y-auto bg-card"
      )}
    >
      <div className="mx-auto max-w-3xl px-6 py-8">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p
              className={th(
                "flex items-center gap-2 text-lg font-semibold text-white",
                "flex items-center gap-2 text-lg font-semibold text-ink"
              )}
            >
              <Sparkles size={18} className="text-emerald-400" />
              Code Analysis
            </p>
            <p
              className={th(
                "mt-1 text-xs text-gray-400",
                "mt-1 text-xs text-ink-soft"
              )}
            >
              Nice work — every test case passed. Here&apos;s what you built.
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className={th(
              "flex shrink-0 items-center gap-1.5 rounded-lg border border-white/15 px-3 py-1.5 text-xs font-medium text-gray-200 transition-colors hover:bg-white/10 disabled:opacity-50",
              "flex shrink-0 items-center gap-1.5 rounded-lg border border-ink/15 px-3 py-1.5 text-xs font-medium text-ink transition-colors hover:bg-ink/5 disabled:opacity-50"
            )}
          >
            {loading ? (
              <Loader2 size={13} className="animate-spin" />
            ) : (
              <ArrowLeft size={13} />
            )}
            Back to Code
          </button>
        </div>

        {error && (
          <div
            className={th(
              "mb-5 flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300",
              "mb-5 flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-600"
            )}
          >
            <TriangleAlert size={15} className="mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div
            className={th(
              "flex items-center gap-2 rounded-lg border border-white/10 px-4 py-8 text-sm text-gray-400",
              "flex items-center gap-2 rounded-lg border border-ink/10 px-4 py-8 text-sm text-ink-soft"
            )}
          >
            <Loader2 size={15} className="animate-spin text-emerald-400" />
            Reading your solution...
          </div>
        )}

        {!loading && !error && !analysis && (
          <p className={th("text-sm text-gray-500", "text-sm text-ink-faint")}>
            No analysis yet.
          </p>
        )}

        {!loading && analysis && (
          <>
            <div className="mb-6 grid gap-3 sm:grid-cols-2">
              {[
                {
                  label: "Time",
                  value: analysis.time_complexity,
                  why: analysis.time_why,
                  accent: "text-amber-400",
                },
                {
                  label: "Space",
                  value: analysis.space_complexity,
                  why: analysis.space_why,
                  accent: "text-sky-400",
                },
              ].map((tile) => (
                <div
                  key={tile.label}
                  className={th(
                    "rounded-xl border border-white/10 bg-white/[0.03] px-5 py-4",
                    "rounded-xl border border-ink/10 bg-ink/[0.02] px-5 py-4"
                  )}
                >
                  <p
                    className={th(
                      "flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider text-gray-500",
                      "flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider text-ink-faint"
                    )}
                  >
                    <Clock size={11} />
                    {tile.label} complexity
                  </p>
                  <p
                    className={`mt-1.5 font-mono text-2xl font-semibold ${tile.accent}`}
                  >
                    {tile.value}
                  </p>
                  {tile.why && (
                    <p
                      className={th(
                        "mt-2 text-[13px] leading-relaxed text-gray-300",
                        "mt-2 text-[13px] leading-relaxed text-ink-soft"
                      )}
                    >
                      {tile.why}
                    </p>
                  )}
                </div>
              ))}
            </div>

            <p
              className={th(
                "mb-2 text-[11px] font-medium uppercase tracking-wider text-gray-500",
                "mb-2 text-[11px] font-medium uppercase tracking-wider text-ink-faint"
              )}
            >
              How your solution works
            </p>
            <article
              className={th(
                "prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-strong:text-emerald-300 prose-code:text-emerald-400",
                "prose prose-sm max-w-none text-[13px] leading-relaxed prose-strong:text-quest prose-code:text-quest"
              )}
            >
              <Markdown remarkPlugins={[remarkGfm]}>{analysis.explanation}</Markdown>
            </article>
          </>
        )}
      </div>
    </div>
  );
}