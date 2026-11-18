"use client";

import Editor from "@monaco-editor/react";
import { useTheme } from "@/context/theme-context";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Language, ProblemDetail, RunMode } from "@/lib/types";

const MONACO_LANG: Record<Language, string> = {
  python: "python",
  cpp: "cpp",
  java: "java",
};

const LANG_LABEL: Record<Language, string> = {
  python: "Python",
  cpp: "C++",
  java: "Java",
};

export default function EditorCell({
  lang,
  mode,
  problem,
  code,
  runCount,
  onCode,
  onModeChange,
  onLangChange,
}: {
  lang: Language;
  mode: RunMode;
  problem: ProblemDetail;
  code: string;
  runCount: number;
  onCode: (v: string) => void;
  onModeChange: (m: RunMode) => void;
  onLangChange: (l: Language) => void;
}) {
  const theme = useTheme();
  const dark = theme === "dark";
  return (
    <section className="flex h-full min-h-0 min-w-0 flex-col">
      <div
        className={`flex shrink-0 items-center gap-2 border-b px-4 py-1.5 ${
          dark ? "border-white/10 bg-[#1e1e30]" : "border-ink/10 bg-white"
        }`}
      >
        <span
          className={`font-mono text-[11px] ${dark ? "text-gray-500" : "text-ink-faint"}`}
        >
          In [{runCount + 1}]
        </span>
        <Select value={lang} onValueChange={(v) => onLangChange(v as Language)}>
          <SelectTrigger
            aria-label="Language"
            className={`h-7 w-[118px] gap-1 border-0 bg-transparent px-1.5 font-mono text-[11px] shadow-none focus:ring-0 ${
              dark ? "text-gray-300" : "text-ink-soft"
            }`}
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {(Object.keys(LANG_LABEL) as Language[]).map((l) => (
              <SelectItem key={l} value={l} className="font-mono text-xs">
                {LANG_LABEL[l]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span
          className={`ml-auto flex gap-0.5 rounded-md border p-0.5 ${
            dark ? "border-white/10 bg-[#252540]" : "border-ink/10 bg-paper-deep"
          }`}
        >
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
                    ? dark
                      ? "bg-white/10 text-gray-100"
                      : "bg-ink text-white"
                    : available
                      ? dark
                        ? "text-gray-500 hover:text-gray-300"
                        : "text-ink-faint hover:text-ink"
                      : dark
                        ? "cursor-not-allowed text-gray-700"
                        : "cursor-not-allowed text-ink-faint/40"
                }`}
              >
                {m === "main" ? "Main" : "Function"}
              </button>
            );
          })}
        </span>
      </div>
      <div className="min-h-0 flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={MONACO_LANG[lang]}
          value={code}
          theme={dark ? "vs-dark" : "vs"}
          onChange={(value) => onCode(value ?? "")}
          loading={
            <div
              className={`flex h-full items-center justify-center text-xs ${
                dark ? "text-gray-500" : "text-ink-faint"
              }`}
            >
              Loading editor…
            </div>
          }
          options={{
            fontSize: 14,
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontLigatures: true,
            minimap: { enabled: false },
            smoothScrolling: true,
            padding: { top: 12 },
            tabSize: 4,
            insertSpaces: true,
            scrollBeyondLastLine: false,
            renderLineHighlight: "all",
            automaticLayout: true,
            stickyScroll: { enabled: false },
            scrollbar: { verticalScrollbarSize: 8, horizontalScrollbarSize: 8 },
            overviewRulerLanes: 0,
            hideCursorInOverviewRuler: true,
            guides: { bracketPairs: true },
            bracketPairColorization: { enabled: true },
          }}
        />
      </div>
    </section>
  );
}
