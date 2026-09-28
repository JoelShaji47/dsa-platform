"use client";

import { useState } from "react";
import { Brain, Loader2, Send, Trash2, X } from "lucide-react";
import { useTheme } from "@/context/theme-context";
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
  const dark = useTheme() === "dark";
  const th = (d: string, l: string) => (dark ? d : l);

  const send = (text: string) => {
    const clean = text.trim();
    if (!clean || loading) return;
    setDraft("");
    onSend(clean);
  };

  return (
    <aside className={th("flex h-full w-full flex-col bg-[#1e1e30]", "flex h-full w-full flex-col bg-card")}>
      <header className={th("flex shrink-0 items-center gap-2 border-b border-white/10 px-4 py-2.5", "flex shrink-0 items-center gap-2 border-b border-ink/10 bg-white px-4 py-2.5")}>
        <Brain size={15} className="text-violet-500" />
        <span className={th("text-sm font-semibold text-gray-100", "text-sm font-semibold text-ink")}>Coach</span>
        {provider && (
          <span className={th("rounded border border-white/10 px-1.5 py-0.5 font-mono text-[10px] text-gray-500", "rounded border border-ink/10 bg-paper-deep px-1.5 py-0.5 font-mono text-[10px] text-ink-faint")}>
            {provider}
          </span>
        )}
        <span className="ml-auto flex items-center gap-1">
          <button
            onClick={onClear}
            title="Clear chat"
            className={th("rounded-md p-1.5 text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-300", "rounded-md p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink")}
          >
            <Trash2 size={13} />
          </button>
          <button
            onClick={onClose}
            title="Close coach"
            className={th("rounded-md p-1.5 text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-300", "rounded-md p-1.5 text-ink-faint transition-colors hover:bg-ink/5 hover:text-ink")}
          >
            <X size={14} />
          </button>
        </span>
      </header>

      <p className={th("shrink-0 border-b border-white/5 px-4 py-1.5 font-mono text-[10px] text-gray-600", "shrink-0 border-b border-ink/10 px-4 py-1.5 font-mono text-[10px] text-ink-faint")}>
        {contextNote}
      </p>

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className={th("rounded-lg border border-violet-500/20 bg-violet-500/5 p-3 text-[13px] leading-relaxed text-gray-400", "rounded-lg border border-violet-500/30 bg-violet-500/10 p-3 text-[13px] leading-relaxed text-ink-soft")}>
            <p className={th("mb-1 flex items-center gap-1.5 font-medium text-violet-200", "mb-1 flex items-center gap-1.5 font-medium text-violet-700")}>
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
              className={th("ml-8 rounded-lg bg-violet-600/20 px-3 py-2 text-[13px] text-gray-100", "ml-8 rounded-lg bg-violet-600/15 px-3 py-2 text-[13px] text-ink")}
            >
              {m.content}
            </div>
          ) : (
            <div
              key={i}
              className={th("mr-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2", "mr-2 rounded-lg border border-ink/10 bg-paper px-3 py-2")}
            >
              <article className={th("prose prose-invert prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-emerald-400", "prose prose-sm max-w-none text-[13px] leading-relaxed prose-code:text-quest")}>
                <Markdown remarkPlugins={[remarkGfm]}>{m.content}</Markdown>
              </article>
            </div>
          )
        )}
        {loading && (
          <div className={th("flex items-center gap-2 text-xs text-gray-500", "flex items-center gap-2 text-xs text-ink-faint")}>
            <Loader2 size={13} className="animate-spin" />
            Coach is thinking…
          </div>
        )}
      </div>

      <div className={th("shrink-0 border-t border-white/10 p-3", "shrink-0 border-t border-ink/10 bg-white p-3")}>
        <div className="mb-2 flex flex-wrap gap-1.5">
          {CHIPS.map((c) => (
            <button
              key={c}
              onClick={() => send(c)}
              disabled={loading}
              className={th("rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[11px] text-gray-400 transition-colors hover:border-violet-400/40 hover:text-violet-200 disabled:opacity-50", "rounded-full border border-ink/10 bg-paper px-2.5 py-1 text-[11px] text-ink-soft transition-colors hover:border-violet-400/50 hover:text-violet-700 disabled:opacity-50")}
            >
              {c}
            </button>
          ))}
        </div>
        <label className={th("mb-2 flex cursor-pointer items-center gap-2 text-[11px] text-gray-500", "mb-2 flex cursor-pointer items-center gap-2 text-[11px] text-ink-faint")}>
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
            className={th("min-w-0 flex-1 rounded-lg border border-white/10 bg-[#16162a] px-3 py-2 text-[13px] text-gray-100 placeholder:text-gray-600 focus:border-violet-400/50 focus:outline-none", "field !rounded-lg !py-2 text-[13px]")}
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
