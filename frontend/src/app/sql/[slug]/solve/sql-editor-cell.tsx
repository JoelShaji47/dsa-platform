"use client";

import CodeMirror from "@uiw/react-codemirror";
import { sql } from "@codemirror/lang-sql";
import { oneDark } from "@codemirror/theme-one-dark";
import { useTheme } from "@/context/theme-context";

export default function SqlEditorCell({
  code,
  runCount,
  onCode,
}: {
  code: string;
  runCount: number;
  onCode: (v: string) => void;
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
        <span
          className={`font-mono text-[11px] ${dark ? "text-gray-600" : "text-ink-faint"}`}
        >
          sql
        </span>
      </div>
      <div className="min-h-0 flex-1 overflow-hidden">
        <CodeMirror
          value={code}
          height="100%"
          style={{ fontSize: "14px", height: "100%" }}
          theme={dark ? oneDark : "light"}
          extensions={[sql() as never]}
          onChange={(value: string) => onCode(value)}
          basicSetup={{ tabSize: 4 }}
        />
      </div>
    </section>
  );
}
