"use client";

import { BookOpen, Play } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { HintMetaOut, ProblemDetail } from "@/lib/types";
import { HintsSection } from "./hints-section";
import TestCasesBlock from "./test-cases-block";

export default function DescriptionPanel({
  problem,
  hintMeta,
  revealedHints,
  armedHint,
  loadingHint,
  onHintClick,
}: {
  problem: ProblemDetail;
  hintMeta: HintMetaOut | null;
  revealedHints: Record<number, string>;
  armedHint: number | null;
  loadingHint: number | null;
  onHintClick: (level: number) => void;
}) {
  const statement = problem.description.replace(/^#\s+.+\r?\n+/, "");
  return (
    <div className="atlas-bg min-h-full px-5 py-5 sm:px-7">
      <p className="eyebrow">
        {problem.topic} · {problem.pattern_key ?? "practice"}
      </p>
      <h2 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
        {problem.title}
      </h2>

      <article className="prose mt-4 max-w-none text-[14px] leading-relaxed text-ink-soft prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-ink/[0.06] prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[13px] prose-code:text-quest prose-code:before:content-none prose-code:after:content-none prose-pre:bg-arena prose-pre:text-arena-text">
        <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
      </article>

      {(problem.editorial_url || problem.video_url) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {problem.editorial_url && (
            <a
              href={problem.editorial_url}
              target="_blank"
              rel="noreferrer"
              className="panel panel-hover flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ink-soft"
            >
              <BookOpen size={13} />
              Editorial
            </a>
          )}
          {problem.video_url && (
            <a
              href={problem.video_url}
              target="_blank"
              rel="noreferrer"
              className="panel panel-hover flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ink-soft"
            >
              <Play size={13} />
              Video
            </a>
          )}
        </div>
      )}

      <TestCasesBlock cases={problem.test_cases} />
      <HintsSection
        hintMeta={hintMeta}
        revealedHints={revealedHints}
        armedHint={armedHint}
        loadingHint={loadingHint}
        onHintClick={onHintClick}
      />
    </div>
  );
}
