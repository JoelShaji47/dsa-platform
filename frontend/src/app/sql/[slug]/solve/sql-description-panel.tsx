"use client";

import { useMemo } from "react";
import { BookOpen, Play } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTheme } from "@/context/theme-context";
import type { HintMetaOut, ProblemDetail } from "@/lib/types";
import { HintsSection } from "../../../problems/[slug]/solve/hints-section";

interface ColumnDef {
  name: string;
  type: string;
}

interface TableInfo {
  name: string;
  columns: ColumnDef[];
  rows: string[][];
}

function parseSqlInput(input: string): TableInfo[] {
  const tables: Map<string, TableInfo> = new Map();

  // Split into statements
  const stmts = input.split(";").map((s) => s.trim()).filter(Boolean);

  for (const stmt of stmts) {
    const createMatch = stmt.match(
      /CREATE\s+TABLE\s+(\w+)\s*\(([\s\S]+)\)/i
    );
    if (createMatch) {
      const tableName = createMatch[1];
      const cols = createMatch[2]
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean)
        .map((col) => {
          const parts = col.split(/\s+/);
          const name = parts[0].replace(/["`]/g, "");
          const type = parts
            .slice(1)
            .join(" ")
            .replace(
              /\s*(PRIMARY\s+KEY|NOT\s+NULL|UNIQUE|DEFAULT\s+\S+|CHECK\s*\([^)]+\))\s*/gi,
              ""
            )
            .trim();
          return { name, type };
        });
      tables.set(tableName, {
        name: tableName,
        columns: cols,
        rows: [],
      });
      continue;
    }

    const insertMatch = stmt.match(
      /INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*([\s\S]+)/i
    );
    if (insertMatch) {
      const tableName = insertMatch[1];
      const colNames = insertMatch[2].split(",").map((c) => c.trim());
      const rows: string[][] = [];
      const rowRegex = /\(([^)]+)\)/g;
      let m: RegExpExecArray | null;
      while ((m = rowRegex.exec(insertMatch[3])) !== null) {
        rows.push(
          m[1].split(",").map((c) => c.trim().replace(/^'|'$/g, ""))
        );
      }
      const existing = tables.get(tableName);
      if (existing) {
        existing.rows.push(...rows);
      } else {
        tables.set(tableName, {
          name: tableName,
          columns: colNames.map((n) => ({ name: n, type: "" })),
          rows,
        });
      }
    }
  }

  return Array.from(tables.values());
}

function parseExpectedRows(output: string): string[][] {
  if (!output.trim()) return [];
  const lines = output.trim().split("\n").filter(Boolean);
  if (lines.length === 0) return [];
  return lines.map((l) => l.split("|").map((c) => c.trim()));
}

function stripSchemaExample(desc: string): string {
  return desc
    .replace(/## Schema[\s\S]*?(?=##\s|$)/i, "")
    .replace(/## Example[\s\S]*?(?=##\s|$)/i, "")
    .replace(/## Output[\s\S]*?(?=##\s|$)/i, "")
    .replace(/^#\s+.+\r?\n+/, "");
}

export default function SqlDescriptionPanel({
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
  const statement = stripSchemaExample(problem.description);
  const dark = useTheme() === "dark";

  const parsedCases = useMemo(
    () =>
      problem.test_cases.map((t) => ({
        tables: parseSqlInput(t.input),
        expected: parseExpectedRows(t.expected_output),
      })),
    [problem.test_cases]
  );

  const th = (d: string, l: string) => (dark ? d : l);

  return (
    <div className="atlas-bg min-h-full px-5 py-5 sm:px-7">
      <div className="mx-auto w-full max-w-3xl">
        <p className="eyebrow">
          SQL · {problem.pattern_key ?? "practice"}
        </p>
        <h2 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          {problem.title}
        </h2>

        <article
          className={
            dark
              ? "prose prose-invert mt-4 max-w-none text-[14px] leading-relaxed prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[13px] prose-code:text-emerald-300 prose-code:before:content-none prose-code:after:content-none prose-pre:bg-arena prose-pre:text-arena-text"
              : "prose mt-4 max-w-none text-[14px] leading-relaxed text-ink-soft prose-headings:font-display prose-headings:text-ink prose-strong:text-ink prose-code:rounded prose-code:bg-ink/[0.06] prose-code:px-1.5 prose-code:py-0.5 prose-code:font-mono prose-code:text-[13px] prose-code:text-quest prose-code:before:content-none prose-code:after:content-none prose-pre:bg-arena prose-pre:text-arena-text"
          }
        >
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

        {parsedCases.map((c, i) => (
          <div key={i} className="mt-4 space-y-5">
            {c.tables.map((tbl) => (
              <div key={tbl.name} className="space-y-3">
                {tbl.columns.length > 0 && tbl.columns[0].type && (
                  <div>
                    <p className="mb-1.5 text-sm font-semibold text-ink">
                      <code
                        className={`rounded px-1.5 py-0.5 font-mono text-[13px] ${th("bg-white/10 text-emerald-300", "bg-ink/[0.06] text-quest")}`}
                      >
                        {tbl.name}
                      </code>{" "}
                      Table
                    </p>
                    <div className="overflow-hidden rounded-lg border border-ink/10">
                      <table className="w-full text-sm">
                        <thead>
                          <tr
                            className={th(
                              "bg-white/5 border-b border-white/10",
                              "bg-ink/[0.03] border-b border-ink/10"
                            )}
                          >
                            <th className="px-4 py-2.5 text-left font-semibold text-ink">
                              Column Name
                            </th>
                            <th className="px-4 py-2.5 text-left font-semibold text-ink">
                              Type
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {tbl.columns.map((col, ci) => (
                            <tr
                              key={ci}
                              className={`border-b last:border-0 ${th("border-white/5", "border-ink/5")}`}
                            >
                              <td className="px-4 py-2 font-mono text-[13px] text-ink">
                                {col.name}
                              </td>
                              <td
                                className={`px-4 py-2 font-mono text-[13px] ${th("text-gray-400", "text-ink-soft")}`}
                              >
                                {col.type}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {tbl.rows.length > 0 && (
                  <div>
                    <p className="mb-1.5 text-sm font-semibold text-ink">
                      <code
                        className={`rounded px-1.5 py-0.5 font-mono text-[13px] ${th("bg-white/10 text-emerald-300", "bg-ink/[0.06] text-quest")}`}
                      >
                        {tbl.name}
                      </code>{" "}
                      Example Input
                    </p>
                    <div className="overflow-hidden rounded-lg border border-ink/10">
                      <table className="w-full text-sm">
                        <thead>
                          <tr
                            className={th(
                              "bg-white/5 border-b border-white/10",
                              "bg-ink/[0.03] border-b border-ink/10"
                            )}
                          >
                            {tbl.columns.map((col, ci) => (
                              <th
                                key={ci}
                                className="px-4 py-2.5 text-left font-semibold text-ink"
                              >
                                {col.name}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {tbl.rows.map((row, ri) => (
                            <tr
                              key={ri}
                              className={`border-b last:border-0 ${th("border-white/5", "border-ink/5")}`}
                            >
                              {row.map((cell, ci) => (
                                <td
                                  key={ci}
                                  className={`px-4 py-2 font-mono text-[13px] ${th("text-gray-600", "text-ink-soft")}`}
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {c.expected.length > 0 ? (
              <div>
                <p className="mb-1.5 text-sm font-semibold text-ink">
                  Example Output
                </p>
                <div className="overflow-hidden rounded-lg border border-quest/20">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-quest/20 bg-quest/5">
                        {c.expected[0].map((col, ci) => (
                          <th
                            key={ci}
                            className="px-4 py-2.5 text-left font-semibold text-quest"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {c.expected.slice(1).map((row, ri) => (
                        <tr
                          key={ri}
                          className="border-b border-quest/10 last:border-0"
                        >
                          {row.map((cell, ci) => (
                            <td
                              key={ci}
                              className="px-4 py-2 font-mono text-[13px] text-quest"
                            >
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : null}
          </div>
        ))}

        <HintsSection
          hintMeta={hintMeta}
          revealedHints={revealedHints}
          armedHint={armedHint}
          loadingHint={loadingHint}
          onHintClick={onHintClick}
        />
      </div>
    </div>
  );
}
