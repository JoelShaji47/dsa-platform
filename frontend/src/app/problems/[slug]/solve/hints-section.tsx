"use client";

import { Lightbulb, Loader2 } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { HintLevelInfo, HintMetaOut } from "@/lib/types";

export function HintsSection({
  hintMeta,
  revealedHints,
  armedHint,
  loadingHint,
  onHintClick,
}: {
  hintMeta: HintMetaOut | null;
  revealedHints: Record<number, string>;
  armedHint: number | null;
  loadingHint: number | null;
  onHintClick: (level: number) => void;
}) {
  if (!hintMeta) return null;
  return (
    <div className="panel mt-4 p-4">
      <p className="flex items-center gap-2 text-sm font-semibold text-ink">
        <Lightbulb size={15} className="text-gold-deep" />
        Hints
        <span className="text-xs font-normal text-ink-faint">
          Viewing any hint forfeits first-solve XP
        </span>
      </p>
      <div className="mt-3 space-y-1.5">
        {hintMeta.levels.map((entry: HintLevelInfo) => (
          <div
            key={entry.level}
            className="overflow-hidden rounded-lg border border-ink/10"
          >
            <button
              onClick={() => onHintClick(entry.level)}
              disabled={loadingHint !== null}
              className={`flex w-full items-center gap-2 px-3 py-2.5 text-left text-sm transition-colors ${
                entry.revealed || armedHint === entry.level
                  ? "bg-gold/15 text-gold-deep"
                  : "text-ink-soft hover:bg-ink/[0.03] hover:text-ink"
              } disabled:opacity-50`}
            >
              {loadingHint === entry.level ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Lightbulb
                  size={14}
                  className={
                    entry.revealed || armedHint === entry.level
                      ? "text-gold-deep"
                      : ""
                  }
                />
              )}
              Level {entry.level}: {entry.label}
              {!entry.revealed && (
                <span className="ml-auto text-xs text-ink-faint">
                  {hintMeta.xp_forfeit_applies
                    ? armedHint === entry.level
                      ? "Click again — XP will be forfeited"
                      : "Reveal · costs XP"
                    : "Reveal"}
                </span>
              )}
            </button>
            {revealedHints[entry.level] && (
              <div className="border-t border-ink/10 bg-paper px-3 py-2.5">
                <article className="prose prose-sm max-w-none text-[13px] leading-relaxed">
                  <Markdown remarkPlugins={[remarkGfm]}>
                    {revealedHints[entry.level]}
                  </Markdown>
                </article>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
