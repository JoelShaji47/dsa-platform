"use client";

import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";
import { LANGS } from "./status-styles";
import type { Language } from "@/lib/types";

export function LanguagePicker({
  value,
  onChange,
}: {
  value: Language;
  onChange: (next: Language) => void;
}) {
  return (
    <div className="flex gap-0.5 rounded-lg border border-white/10 bg-[#252540] p-0.5">
      {LANGS.map((l) => (
        <button
          key={l.key}
          onClick={() => onChange(l.key)}
          className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
            value === l.key
              ? "bg-white/10 text-gray-100"
              : "text-gray-500 hover:text-gray-300"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}

export function CodeEditor({
  value,
  language,
  onChange,
  readOnly = false,
  height = "100%",
}: {
  value: string;
  language: Language;
  onChange?: (next: string) => void;
  readOnly?: boolean;
  height?: string;
}) {
  const active = LANGS.find((l) => l.key === language);
  return (
    <CodeMirror
      value={value}
      height={height}
      style={{ fontSize: "15px", height }}
      theme={oneDark}
      extensions={[(active?.ext() ?? python()) as never]}
      onChange={readOnly ? undefined : (next: string) => onChange?.(next)}
      readOnly={readOnly}
      basicSetup={{ tabSize: 4 }}
    />
  );
}
