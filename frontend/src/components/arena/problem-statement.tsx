"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function ProblemStatement({ text }: { text: string }) {
  const statement = text.replace(/^#\s+.+\r?\n+/, "");
  return (
    <article className="prose prose-invert max-w-none text-base leading-relaxed prose-headings:text-gray-100 prose-p:text-gray-300 prose-strong:text-white prose-code:rounded prose-code:bg-white/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-emerald-400 prose-code:before:content-none prose-code:after:content-none prose-pre:rounded-xl prose-pre:bg-[#16162a] prose-pre:text-[#dce3f2]">
      <Markdown remarkPlugins={[remarkGfm]}>{statement}</Markdown>
    </article>
  );
}