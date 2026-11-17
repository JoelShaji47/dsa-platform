import {
  snap,
  snapGrid,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface EditDistanceInput {
  word1: string;
  word2: string;
}

export function parseEditDistance(raw: string): EditDistanceInput {
  const lines = raw.replace(/\r/g, "").split("\n");
  if (lines.length < 2) throw new Error("Use one string per line");
  const word1 = lines[0].trim();
  const word2 = lines[1].trim();
  if (word1.length > 6 || word2.length > 6) {
    throw new Error("Keep both strings to 6 characters so the trace stays readable");
  }
  return { word1, word2 };
}

export function generateEditDistance({ word1, word2 }: EditDistanceInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const rows = word1.length;
  const cols = word2.length;
  const dp = Array.from({ length: rows + 1 }, () =>
    Array.from({ length: cols + 1 }, () => 0)
  );
  const computed = Array.from({ length: rows + 1 }, () =>
    Array.from({ length: cols + 1 }, () => false)
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
    dp.map((row, rowIndex) =>
      row.map((value, colIndex) => (computed[rowIndex][colIndex] ? value : ""))
    );

  const rowLabels = ["", ...word1.split("")];
  const colLabels = ["", ...word2.split("")];

  const gridSnapshot = (
    active: [number, number][] = [],
    deps: [number, number][] = []
  ) =>
    snapGrid(display(), {
      active,
      deps,
      settled: settledCells(),
      showIndices: true,
      rowLabels,
      colLabels,
      label: "dp",
    });

  steps.push(
    step(
      0,
      "Start",
      `Convert "${word1}" into "${word2}" using insert, delete, or replace.`,
      0,
      snap([]),
      { word1, word2 },
      { grid: gridSnapshot([[0, 0]]) }
    )
  );

  dp[0][0] = 0;
  computed[0][0] = true;
  steps.push(
    step(
      steps.length,
      "Origin",
      "Converting an empty prefix to an empty prefix costs 0.",
      1,
      snap([]),
      { cost: 0 },
      { grid: gridSnapshot([[0, 0]]) }
    )
  );

  for (let row = 1; row <= rows; row += 1) {
    dp[row][0] = row;
    computed[row][0] = true;
    steps.push(
      step(
        steps.length,
        "Delete",
        `Converting "${word1.slice(0, row)}" to an empty string needs ${row} delete${row === 1 ? "" : "s"}.`,
        1,
        snap([]),
        { row, cost: row },
        { grid: gridSnapshot([[row, 0]], [[row - 1, 0]]) }
      )
    );
  }

  for (let col = 1; col <= cols; col += 1) {
    dp[0][col] = col;
    computed[0][col] = true;
    steps.push(
      step(
        steps.length,
        "Insert",
        `Converting an empty string to "${word2.slice(0, col)}" needs ${col} insert${col === 1 ? "" : "s"}.`,
        2,
        snap([]),
        { col, cost: col },
        { grid: gridSnapshot([[0, col]], [[0, col - 1]]) }
      )
    );
  }

  for (let row = 1; row <= rows; row += 1) {
    for (let col = 1; col <= cols; col += 1) {
      const a = word1[row - 1];
      const b = word2[col - 1];
      const same = a === b;

      steps.push(
        step(
          steps.length,
          "Compare",
          `Compare '${a}' with '${b}'.`,
          5,
          snap([]),
          { a, b, same: same ? "yes" : "no" },
          {
            grid: gridSnapshot(
              [[row, col]],
              [[row - 1, col - 1], [row - 1, col], [row, col - 1]]
            ),
          }
        )
      );

      if (same) {
        dp[row][col] = dp[row - 1][col - 1];
        computed[row][col] = true;
        steps.push(
          step(
            steps.length,
            "Match",
            `Characters match, so copy the diagonal value ${dp[row][col]}.`,
            6,
            snap([]),
            { row, col, cost: dp[row][col] },
            { grid: gridSnapshot([[row, col]], [[row - 1, col - 1]]) }
          )
        );
      } else {
        const replace = dp[row - 1][col - 1];
        const remove = dp[row - 1][col];
        const insert = dp[row][col - 1];
        dp[row][col] = 1 + Math.min(replace, remove, insert);
        computed[row][col] = true;
        steps.push(
          step(
            steps.length,
            "Choose",
            `1 + min(replace ${replace}, delete ${remove}, insert ${insert}) = ${dp[row][col]}.`,
            8,
            snap([]),
            { row, col, replace, remove, insert },
            {
              grid: gridSnapshot(
                [[row, col]],
                [[row - 1, col - 1], [row - 1, col], [row, col - 1]]
              ),
            }
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
      `The minimum edit distance is ${result}.`,
      9,
      snap([]),
      { distance: result },
      { grid: gridSnapshot(), result: String(result), done: true }
    )
  );

  return steps;
}

export const editDistanceEntry: VisualizerEntry = {
  slug: "edit-distance",
  title: "Edit Distance",
  inputHint: "horse / ros",
  defaultInput: "horse\nros",
  presets: [
    { label: "Horse / Ros", value: "horse\nros" },
    { label: "Cat / Cut", value: "cat\ncut" },
    { label: "Same", value: "abc\nabc" },
    { label: "Empty", value: "\n" },
  ],
  pseudocode: [
    "dp = [[0] * (n + 1) for _ in range(m + 1)]",
    "for i in range(m + 1): dp[i][0] = i",
    "for j in range(n + 1): dp[0][j] = j",
    "for i in range(1, m + 1):",
    "    for j in range(1, n + 1):",
    "        if word1[i-1] == word2[j-1]:",
    "            dp[i][j] = dp[i-1][j-1]",
    "        else:",
    "            dp[i][j] = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])",
    "return dp[m][n]",
  ],
  parse: (raw: string) => parseEditDistance(raw),
  generate: (input: unknown) => generateEditDistance(input as EditDistanceInput),
};
