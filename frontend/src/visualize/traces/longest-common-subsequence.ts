import { snap, snapGrid, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface LcsInput {
  first: string;
  second: string;
}

export function parseLcs(raw: string): LcsInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use two lines: text1 then text2");
  const [first, second] = lines;
  if (first.length > 8 || second.length > 8) throw new Error("Keep both strings to 8 characters");
  return { first, second };
}

export function generateLcs({ first, second }: LcsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const rows = first.length;
  const cols = second.length;
  const dp = Array.from({ length: rows + 1 }, () => new Array<number>(cols + 1).fill(0));
  const computed = Array.from({ length: rows + 1 }, () =>
    new Array<boolean>(cols + 1).fill(false)
  );

  const settledCells = (): [number, number][] => {
    const cells: [number, number][] = [];
    for (let row = 0; row <= rows; row += 1) {
      for (let col = 0; col <= cols; col += 1) {
        if (computed[row][col]) cells.push([row, col]);
      }
    }
    return cells;
  };

  const display = () =>
    dp.map((row, r) => row.map((value, c) => (computed[r][c] ? value : "")));

  const gridSnap = (active: [number, number][] = [], deps: [number, number][] = []) =>
    snapGrid(display(), {
      active,
      deps,
      settled: settledCells(),
      showIndices: true,
      rowLabels: ["", ...first.split("")],
      colLabels: ["", ...second.split("")],
      label: "dp",
    });

  steps.push(
    step(0, "Start", `Find the longest subsequence shared by "${first}" and "${second}".`, 0, snap([]), { first, second }, { grid: gridSnap([[0, 0]]) })
  );

  for (let row = 0; row <= rows; row += 1) {
    dp[row][0] = 0;
    computed[row][0] = true;
  }
  for (let col = 0; col <= cols; col += 1) {
    dp[0][col] = 0;
    computed[0][col] = true;
  }
  steps.push(
    step(
      steps.length,
      "Base row/column",
      "An empty prefix shares a subsequence of length 0.",
      0,
      snap([]),
      { rows, cols },
      { grid: gridSnap([[0, 0]]) }
    )
  );

  for (let row = 1; row <= rows; row += 1) {
    for (let col = 1; col <= cols; col += 1) {
      const a = first[row - 1];
      const b = second[col - 1];
      if (a === b) {
        dp[row][col] = dp[row - 1][col - 1] + 1;
        computed[row][col] = true;
        steps.push(
          step(
            steps.length,
            "Match",
            `'${a}' matches '${b}'; extend the diagonal by 1 to ${dp[row][col]}.`,
            4,
            snap([]),
            { a, b, length: dp[row][col] },
            { grid: gridSnap([[row, col]], [[row - 1, col - 1]]) }
          )
        );
      } else {
        dp[row][col] = Math.max(dp[row - 1][col], dp[row][col - 1]);
        computed[row][col] = true;
        steps.push(
          step(
            steps.length,
            "Skip",
            `'${a}' != '${b}'; take the better of skipping either character (${dp[row][col]}).`,
            5,
            snap([]),
            { a, b, length: dp[row][col] },
            { grid: gridSnap([[row, col]], [[row - 1, col], [row, col - 1]]) }
          )
        );
      }
    }
  }

  const result = dp[rows][cols];
  steps.push(
    step(
      steps.length,
      "Done",
      `The longest common subsequence has length ${result}.`,
      6,
      snap([]),
      { length: result },
      { grid: gridSnap(), done: true, result: String(result) }
    )
  );

  return steps;
}

export const lcsEntry: VisualizerEntry = {
  slug: "longest-common-subsequence",
  title: "Longest Common Subsequence",
  inputHint: "two lines: text1 then text2",
  defaultInput: "abcde\nace",
  presets: [
    { label: "example", value: "abcde\nace" },
    { label: "same", value: "abc\nabc" },
    { label: "none", value: "abc\ndef" },
  ],
  pseudocode: [
    "dp = zeros(m+1, n+1)",
    "for i in 1..m:",
    "  for j in 1..n:",
    "    if text1[i-1] == text2[j-1]: dp[i][j] = dp[i-1][j-1] + 1",
    "    else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])",
    "return dp[m][n]",
  ],
  parse: parseLcs,
  generate: (input) => generateLcs(input as LcsInput),
};
