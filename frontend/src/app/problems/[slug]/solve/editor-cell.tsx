"use client";

import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { oneDark } from "@codemirror/theme-one-dark";
import type { Language, ProblemDetail, RunMode } from "@/lib/types";

const EXTS: Record<Language, () => unknown> = { python, cpp, java };

export default function EditorCell({
  lang,
  mode,
  problem,
  code,
  runCount,
  onCode,
  onModeChange,
}: {
  lang: Language;
  mode: RunMode;
  problem: ProblemDetail;
  code: string;
  runCount: number;
  onCode: (v: string) => void;
  onModeChange: (m: RunMode) => void;
}) {
  return (
    <section className="flex h-full min-h-0 min-w-0 flex-col">
      <div className="flex shrink-0 items-center gap-2 border-b border-white/10 bg-[#1e1e30] px-4 py-1.5">
        <span className="font-mono text-[11px] text-gray-500">
          In [{runCount + 1}]
        </span>
        <span className="font-mono text-[11px] text-gray-600">{lang}</span>
        <span className="ml-auto flex gap-0.5 rounded-md border border-white/10 bg-[#252540] p-0.5">
          {(["main", "function"] as RunMode[]).map((m) => {
            const available =
              m === "main" || problem.function_modes?.includes(lang);
            const active = mode === m;
            return (
              <button
                key={m}
                onClick={() => available && onModeChange(m)}
                disabled={!available}
                title={
                  available
                    ? m === "main"
                      ? "Full program with input parsing"
                      : "Write solve() only — driver hidden (LeetCode style)"
                    : "Function mode isn't authored for this problem yet"
                }
                className={`rounded px-2 py-0.5 font-mono text-[11px] transition-colors ${
                  active
                    ? "bg-white/10 text-gray-100"
                    : available
                      ? "text-gray-500 hover:text-gray-300"
                      : "cursor-not-allowed text-gray-700"
                }`}
              >
                {m === "main" ? "Main" : "Function"}
              </button>
            );
          })}
        </span>
      </div>
      <div className="min-h-0 flex-1 overflow-hidden">
        <CodeMirror
          value={code}
          height="100%"
          style={{ fontSize: "14px", height: "100%" }}
          theme={oneDark}
          extensions={[(EXTS[lang]?.() ?? python()) as never]}
          onChange={(value: string) => onCode(value)}
          basicSetup={{ tabSize: 4 }}
        />
      </div>
    </section>
  );
}
