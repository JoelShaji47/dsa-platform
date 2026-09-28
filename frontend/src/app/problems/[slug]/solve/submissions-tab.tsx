"use client";

import { useState } from "react";
import { Clock, History, Loader2 } from "lucide-react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { oneDark } from "@codemirror/theme-one-dark";
import type { SubmissionHistoryItem } from "@/lib/types";
import { STATUS_STYLES } from "./status-utils";

export default function SubmissionsTab({
  submissions,
  loading,
}: {
  submissions: SubmissionHistoryItem[];
  loading: boolean;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-ink-faint">
        <Loader2 size={16} className="mr-2 animate-spin" />
        Loading submissions...
      </div>
    );
  }
  if (!submissions.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <History size={32} className="mb-3 text-ink-faint/50" />
        <p className="text-sm text-ink-soft">No submissions yet</p>
        <p className="mt-1 text-xs text-ink-faint">
          Submit your code to see results here
        </p>
      </div>
    );
  }

  const langMap: Record<string, () => unknown> = { python, cpp, java };

  return (
    <div className="space-y-1.5">
      {submissions.map((s) => {
        const style = STATUS_STYLES[s.status] || {
          chip: "text-ink-faint",
          icon: null,
          label: s.status,
        };
        const passed = s.status === "ACCEPTED";
        const totalPassed = s.judge_summary
          ? s.judge_summary.filter((t) => t.passed).length
          : null;
        const totalTests = s.judge_summary ? s.judge_summary.length : null;
        const isExpanded = expanded === s.submission_id;
        return (
          <div
            key={s.submission_id}
            className={`overflow-hidden rounded-lg border transition-colors ${
              passed
                ? "border-quest/40 bg-quest/5"
                : "border-ink/10 bg-white"
            }`}
          >
            <button
              onClick={() => setExpanded(isExpanded ? null : s.submission_id)}
              className="flex w-full items-center gap-3 px-3 py-2.5 text-left transition-colors hover:bg-ink/[0.03]"
            >
              <span
                className={`text-xs font-medium ${passed ? "text-quest" : "text-rust"}`}
              >
                {style.label}
              </span>
              <span className="rounded-md bg-paper-deep px-2 py-0.5 font-mono text-[11px] text-ink-soft">
                {s.language}
              </span>
              {totalPassed !== null && (
                <span className="text-[11px] text-ink-faint">
                  {totalPassed}/{totalTests}
                </span>
              )}
              <span className="ml-auto flex items-center gap-3">
                <span className="flex items-center gap-1 text-[11px] text-ink-faint">
                  <Clock size={11} />
                  {s.runtime_ms != null ? `${s.runtime_ms.toFixed(0)} ms` : "—"}
                </span>
                <span className="text-[11px] text-ink-faint">
                  {s.memory_kb != null
                    ? `${(s.memory_kb / 1024).toFixed(2)} MB`
                    : "—"}
                </span>
                <span className="text-[11px] text-ink-faint">
                  {new Date(s.submitted_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </span>
            </button>
            {isExpanded && (
              <div className="border-t border-ink/10 bg-arena">
                <div className="p-3">
                  <CodeMirror
                    value={s.code}
                    height="auto"
                    style={{
                      fontSize: "13px",
                      maxHeight: "350px",
                      overflow: "auto",
                    }}
                    theme={oneDark}
                    extensions={[(langMap[s.language] ?? python)() as never]}
                    readOnly
                    basicSetup={{
                      highlightActiveLine: false,
                      highlightActiveLineGutter: false,
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
