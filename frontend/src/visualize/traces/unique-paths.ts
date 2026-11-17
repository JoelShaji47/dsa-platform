import {
  snap,
  snapGrid,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface UniquePathsInput {
  rows: number;
  cols: number;
}

export function parseUniquePaths(raw: string): UniquePathsInput {
  const values = raw
    .trim()
    .split(/[\s,]+/)
    .filter((token) => token.length > 0)
    .map(Number);
  if (values.length !== 2) throw new Error("Use two integers: m n");
  const [rows, cols] = values;
  if (
    !Number.isInteger(rows) ||
    !Number.isInteger(cols) ||
    rows < 1 ||
    cols < 1
  ) {
    throw new Error("m and n must be positive integers");
  }
  if (rows > 8 || cols > 8) {
    throw new Error("Keep the grid to 8x8 so the trace stays readable");
  }
  return { rows, cols };
}

export function generateUniquePaths({ rows, cols }: UniquePathsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dp = Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0));
  const computed = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => false)
  );

  const settledCells = (): [number, number][] => {
    const cells: [number, number][] = [];
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        if (computed[row][col]) cells.push([row, col]);
      }
    }
    return cells;
  };

  const display = () =>
    dp.map((row, rowIndex) =>
      row.map((value, colIndex) => (computed[rowIndex][colIndex] ? value : ""))
    );

  const gridSnapshot = (
    active: [number, number][] = [],
    deps: [number, number][] = []
  ) =>
    snapGrid(display(), {
      active,
      deps,
      settled: settledCells(),
      showIndices: true,
      label: "dp (paths)",
    });

  steps.push(
    step(
      0,
      "Start",
      `Fill a ${rows}x${cols} table. Each cell counts paths from the top-left corner.`,
      0,
      snap([]),
      { rows, cols },
      { grid: gridSnapshot([[0, 0]]) }
    )
  );

  for (let col = 0; col < cols; col += 1) {
    dp[0][col] = 1;
    computed[0][col] = true;
    const deps: [number, number][] = col > 0 ? [[0, col - 1]] : [];
    steps.push(
      step(
        steps.length,
        "Top row",
        col === 0
          ? "The start cell has exactly one path: stay put."
          : `Along the top row there is only one path: keep moving right.`,
        1,
        snap([]),
        { row: 0, col },
        { grid: gridSnapshot([[0, col]], deps) }
      )
    );
  }

  for (let row = 1; row < rows; row += 1) {
    dp[row][0] = 1;
    computed[row][0] = true;
    steps.push(
      step(
        steps.length,
        "Left column",
        "Along the left column there is only one path: keep moving down.",
        2,
        snap([]),
        { row, col: 0 },
        { grid: gridSnapshot([[row, 0]], [[row - 1, 0]]) }
      )
    );
  }

  for (let row = 1; row < rows; row += 1) {
    for (let col = 1; col < cols; col += 1) {
      steps.push(
        step(
          steps.length,
          "Compute",
          `Cell (${row}, ${col}) can be reached from above or from the left.`,
          5,
          snap([]),
          { row, col, above: dp[row - 1][col], left: dp[row][col - 1] },
          { grid: gridSnapshot([[row, col]], [[row - 1, col], [row, col - 1]]) }
        )
      );

      dp[row][col] = dp[row - 1][col] + dp[row][col - 1];
      computed[row][col] = true;
      steps.push(
        step(
          steps.length,
          "Store",
          `dp[${row}][${col}] = ${dp[row - 1][col]} + ${dp[row][col - 1]} = ${dp[row][col]}.`,
          5,
          snap([]),
          { row, col, paths: dp[row][col] },
          { grid: gridSnapshot([[row, col]], [[row - 1, col], [row, col - 1]]) }
        )
      );
    }
  }

  const result = dp[rows - 1][cols - 1];
  steps.push(
    step(
      steps.length,
      "Done",
      `The bottom-right cell contains ${result} unique path${result === 1 ? "" : "s"}.`,
      6,
      snap([]),
      { paths: result },
      { grid: gridSnapshot(), result: String(result), done: true }
    )
  );

  return steps;
}

export const uniquePathsEntry: VisualizerEntry = {
  slug: "unique-paths",
  title: "Unique Paths",
  inputHint: "3 7",
  defaultInput: "3 7",
  presets: [
    { label: "Example", value: "3 7" },
    { label: "Small", value: "3 2" },
    { label: "Single cell", value: "1 1" },
    { label: "Square", value: "5 5" },
  ],
  pseudocode: [
    "dp = [[0] * n for _ in range(m)]",
    "for j in range(n): dp[0][j] = 1",
    "for i in range(m): dp[i][0] = 1",
    "for i in range(1, m):",
    "    for j in range(1, n):",
    "        dp[i][j] = dp[i-1][j] + dp[i][j-1]",
    "return dp[m-1][n-1]",
  ],
  parse: (raw: string) => parseUniquePaths(raw),
  generate: (input: unknown) => generateUniquePaths(input as UniquePathsInput),
};
