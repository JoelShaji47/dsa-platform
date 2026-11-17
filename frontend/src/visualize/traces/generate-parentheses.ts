import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface GenerateParenthesesInput {
  pairs: number;
}

export function parseGenerateParentheses(raw: string): GenerateParenthesesInput {
  const lines = inputLines(raw);
  const pairs = integersFrom(lines[0] ?? "")[0];
  if (!Number.isInteger(pairs) || pairs < 1) throw new Error("n must be a positive integer");
  if (pairs > 4) throw new Error("Keep n to 4 so the output stays readable");
  return { pairs };
}

export function generateParentheses({ pairs }: GenerateParenthesesInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const path: string[] = [];
  const results: string[] = [];

  const pathSnap = (active: number[] = []) =>
    snapStack(path, { active, label: "current prefix" });
  const resultsSnap = (active: number[] = []) =>
    snap(results, { active, settled: results.map((_, index) => index), label: "valid strings" });

  steps.push(
    step(
      0,
      "Start",
      `Build every string with ${pairs} pairs, adding '(' only when we still have one available.`,
      0,
      resultsSnap(),
      { open: 0, close: 0, n: pairs },
      { stack: pathSnap() }
    )
  );

  const dfs = (open: number, close: number) => {
    if (path.length === pairs * 2) {
      results.push(path.join(""));
      steps.push(
        step(
          steps.length,
          "Record",
          `The prefix is balanced and complete: ${results[results.length - 1]}.`,
          4,
          resultsSnap([results.length - 1]),
          { open, close, complete: results.length },
          { stack: pathSnap(path.map((_, index) => index)) }
        )
      );
      return;
    }

    if (open < pairs) {
      path.push("(");
      steps.push(
        step(
          steps.length,
          "Open",
          `Add '(' (${open + 1}/${pairs} open so far).`,
          2,
          resultsSnap(),
          { open: open + 1, close, n: pairs },
          { stack: pathSnap([path.length - 1]) }
        )
      );
      dfs(open + 1, close);
      path.pop();
    }

    if (close < open) {
      path.push(")");
      steps.push(
        step(
          steps.length,
          "Close",
          `Add ')' (${close + 1} closed, ${open} open).`,
          3,
          resultsSnap(),
          { open, close: close + 1, n: pairs },
          { stack: pathSnap([path.length - 1]) }
        )
      );
      dfs(open, close + 1);
      path.pop();
    }
  };

  dfs(0, 0);
  const result = results.join("\n");
  steps.push(
    step(
      steps.length,
      "Done",
      `Generated ${results.length} well-formed combination${results.length === 1 ? "" : "s"}.`,
      5,
      resultsSnap(results.map((_, index) => index)),
      { total: results.length },
      { stack: pathSnap(), done: true, result }
    )
  );

  return steps;
}

export const generateParenthesesEntry: VisualizerEntry = {
  slug: "generate-parentheses",
  title: "Generate Parentheses",
  inputHint: "n (number of pairs)",
  defaultInput: "3",
  presets: [
    { label: "n=3", value: "3" },
    { label: "n=1", value: "1" },
    { label: "n=2", value: "2" },
  ],
  pseudocode: [
    "prefix = []",
    "dfs(open, close):",
    "  if len(prefix) == 2n: record prefix",
    "  if open < n: add '(' and recurse",
    "  if close < open: add ')' and recurse",
  ],
  parse: parseGenerateParentheses,
  generate: (input) => generateParentheses(input as GenerateParenthesesInput),
};
