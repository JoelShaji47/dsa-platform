"use client";

import { useState } from "react";
import { Beaker, ChevronRight } from "lucide-react";
import type { TestCaseOut } from "@/lib/types";

export default function TestCasesBlock({ cases }: { cases: TestCaseOut[] }) {
  const [open, setOpen] = useState(true);
  if (!cases.length) return null;
  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-ink/10 bg-white">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm font-semibold text-ink"
      >
        <ChevronRight
          size={14}
          className={`text-ink-faint transition-transform ${open ? "rotate-90" : ""}`}
        />
        <Beaker size={14} className="text-quest" />
        Sample test cases
        <span className="ml-auto rounded-full bg-paper-deep px-2 py-0.5 font-mono text-[11px] font-medium text-ink-soft">
          {cases.length}
        </span>
      </button>
      {open && (
        <div className="space-y-2 border-t border-ink/10 bg-paper px-4 py-3">
          {cases.map((t, i) => (
            <div
              key={i}
              className="grid grid-cols-1 gap-2 rounded-lg border border-ink/10 bg-white p-3 sm:grid-cols-2"
            >
              <div className="sm:col-span-2">
                <p className="font-mono text-[11px] font-semibold uppercase tracking-wider text-ink-faint">
                  Case {i + 1}
                </p>
              </div>
              <div>
                <p className="mb-1 font-mono text-[11px] uppercase tracking-wider text-ink-faint">
                  Input
                </p>
                <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-arena px-2.5 py-2 font-mono text-[12px] leading-relaxed text-arena-text">
                  {t.input.trimEnd() || "(empty)"}
                </pre>
              </div>
              <div>
                <p className="mb-1 font-mono text-[11px] uppercase tracking-wider text-ink-faint">
                  Expected
                </p>
                <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-quest/10 px-2.5 py-2 font-mono text-[12px] leading-relaxed text-quest">
                  {t.expected_output.trimEnd() || "(empty)"}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
