"use client";

import { useState } from "react";
import { Brain, Loader2, Send, Trash2, X } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { AssistantHistoryItem } from "@/lib/types";

export interface CoachMessage {
  role: "user" | "assistant";
  content: string;
}

const CHIPS = [
  "Nudge me in the right direction",
  "Why does my code fail?",
  "What's the time complexity I should aim for?",
  "What should I try next?",
];

export default function AssistantPanel({
  messages,
  loading,
  provider,
  includeCode,
  contextNote,
  onToggleInclude,
  onSend,
  onClear,
  onClose,
}: {
  messages: CoachMessage[];
  loading: boolean;
  provider: string | null;
  includeCode: boolean;
  contextNote: string;
  onToggleInclude: () => void;
  onSend: (text: string) => void;
  onClear: () => void;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState("");

  const send = (text: string) => {
    const clean = text.trim();
    if (!clean || loading) return;
    setDraft("");
    onSend(clean);
  };

  return (
    <aside className="flex h-full w-full flex-col border-l border-white/10 bg-[#1e1e30]">
      <header className="flex shrink-0 items-center gap-2 border-b border-white/10 px-4 py-2.5">
        <Brain size={15} className="text-violet-300" />
        <span className="text-sm font-semibold text-gray-100">Coach</span>
        {provider && (
          <span className="rounded border border-white/10 px-1.5 py-0.5 font-mono text-[10px] text-gray-500">
            {provider}
          </span>
        )}
        <span className="ml-auto flex items-center gap-1">
          <button
            onClick={onClear}
            title="Clear chat"
            className="rounded-md p-1.5 text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-300"
          >
            <Trash2 size={13} />
          </button>
          <button
            onClick={onClose}
            title="Close coach"
            className="rounded-md p-1.5 text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-300"
          >
            <X size={14} />
          </button>
        </span>
      </header>

      <p className="shrink-0 border-b border-white/5 px-4 py-1.5 font-mono text-[10px] text-gray-600">
        {contextNote}
      </p>

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="rounded-lg border border-violet-500/20 bg-violet-500/5 p-3 text-[13px] leading-relaxed text-gray-400">
            <p className="mb-1 flex items-center gap-1.5 font-medium text-violet-200">
              <Brain size={13} />
              Socratic coach — nudges, never answers
            </p>
            Your current code and last result are attached automatically. Ask
            for a nudge, not the solution.
          </div>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div
              key={i}
              className="ml-8 rounded-lg bg-violet-600/20 px-3 py-2 text-[13px] text-gray-100"
            >
              {m.content}
            </div>
          ) : (
            <div
              key={i}
              className="mr-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2"
            >
              <article className="prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400">
                <Markdown remarkPlugins={[remarkGfm]}>{m.content}</Markdown>
              </article>
            </div>
          )
        )}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Loader2 size={13} className="animate-spin" />
            Coach is thinking…
          </div>
        )}
      </div>

      <div className="shrink-0 border-t border-white/10 p-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {CHIPS.map((c) => (
            <button
              key={c}
              onClick={() => send(c)}
              disabled={loading}
              className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[11px] text-gray-400 transition-colors hover:border-violet-400/40 hover:text-violet-200 disabled:opacity-50"
            >
              {c}
            </button>
          ))}
        </div>
        <label className="mb-2 flex cursor-pointer items-center gap-2 text-[11px] text-gray-500">
          <input
            type="checkbox"
            checked={includeCode}
            onChange={onToggleInclude}
            className="h-3.5 w-3.5 accent-violet-500"
          />
          Include my current code
        </label>
        <div className="flex gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(draft);
              }
            }}
            placeholder="Ask for a nudge…"
            className="min-w-0 flex-1 rounded-lg border border-white/10 bg-[#16162a] px-3 py-2 text-[13px] text-gray-100 placeholder:text-gray-600 focus:border-violet-400/50 focus:outline-none"
          />
          <button
            onClick={() => send(draft)}
            disabled={loading || !draft.trim()}
            className="flex items-center gap-1.5 rounded-lg bg-violet-600 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-violet-500 disabled:opacity-50"
          >
            <Send size={13} />
          </button>
        </div>
      </div>
    </aside>
  );
}

export type { AssistantHistoryItem };
