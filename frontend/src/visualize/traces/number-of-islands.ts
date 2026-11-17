import {
  snap,
  snapGrid,
  snapQueue,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface NumberOfIslandsInput {
  rows: number;
  cols: number;
  grid: string[][];
}

const DIRECTIONS: [number, number][] = [
  [1, 0],
  [-1, 0],
  [0, 1],
  [0, -1],
];

function key(row: number, col: number): string {
  return `${row},${col}`;
}

export function parseNumberOfIslands(raw: string): NumberOfIslandsInput {
  const lines = raw
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  if (lines.length < 2) throw new Error("Use: R C, then R rows of 0/1");

  const [rows, cols] = lines[0].split(/[\s,]+/).map(Number);
  if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 1 || cols < 1) {
    throw new Error("Grid dimensions must be positive integers");
  }
  if (rows > 6 || cols > 6) {
    throw new Error("Keep the grid to 6x6 so the trace stays readable");
  }
  if (lines.length < rows + 1) throw new Error("The grid is missing rows");

  const grid = lines.slice(1, rows + 1).map((line) => {
    const cells = /^[01]+$/.test(line) ? line.split("") : line.split(/[\s,]+/);
    if (cells.length !== cols || cells.some((cell) => cell !== "0" && cell !== "1")) {
      throw new Error(`Each row needs exactly ${cols} cells, each 0 or 1`);
    }
    return cells;
  });

  return { rows, cols, grid };
}

export function generateNumberOfIslands(input: NumberOfIslandsInput): BaseStep[] {
  const { rows, cols, grid } = input;
  const steps: BaseStep[] = [];
  const values = grid.map((row) => [...row]);
  const visited = new Set<string>();
  const settled: [number, number][] = [];
  const queue: [number, number][] = [];
  let islands = 0;

  const queueSnapshot = () =>
    snapQueue(
      queue.map(([row, col]) => `${row},${col}`),
      { active: queue.length > 0 ? [0] : [], label: "queue" }
    );

  const gridSnapshot = (
    active: [number, number][] = [],
    deps: [number, number][] = []
  ) =>
    snapGrid(values, {
      active,
      deps,
      settled: [...settled],
      showIndices: false,
      label: "grid",
    });

  steps.push(
    step(
      0,
      "Start",
      "Scan every cell. Each unvisited 1 starts a new island and a BFS over its connected land.",
      0,
      snap([]),
      { islands: 0 },
      { grid: gridSnapshot() }
    )
  );

  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      if (values[row][col] !== "1" || visited.has(key(row, col))) continue;

      islands += 1;
      visited.add(key(row, col));
      settled.push([row, col]);
      queue.push([row, col]);

      steps.push(
        step(
          steps.length,
          "Island",
          `(${row}, ${col}) is unvisited land; island ${islands} starts here.`,
          3,
          snap([]),
          { islands, cell: `${row},${col}` },
          { grid: gridSnapshot([[row, col]]), queue: queueSnapshot() }
        )
      );

      while (queue.length > 0) {
        const [r, c] = queue.shift()!;
        steps.push(
          step(
            steps.length,
            "Pop",
            `Explore the four neighbors of (${r}, ${c}).`,
            8,
            snap([]),
            { islands, cell: `${r},${c}` },
            { grid: gridSnapshot([[r, c]]), queue: queueSnapshot() }
          )
        );

        for (const [dr, dc] of DIRECTIONS) {
          const nr = r + dr;
          const nc = c + dc;
          if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
          if (values[nr][nc] !== "1" || visited.has(key(nr, nc))) continue;

          visited.add(key(nr, nc));
          settled.push([nr, nc]);
          queue.push([nr, nc]);

          steps.push(
            step(
              steps.length,
              "Visit",
              `(${nr}, ${nc}) is connected land; mark it visited and enqueue it.`,
              12,
              snap([]),
              { islands, cell: `${nr},${nc}` },
              {
                grid: gridSnapshot([[nr, nc]], [[r, c]]),
                queue: queueSnapshot(),
              }
            )
          );
        }
      }
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `All land has been visited; the grid contains ${islands} island${islands === 1 ? "" : "s"}.`,
      14,
      snap([]),
      { islands },
      {
        grid: gridSnapshot(),
        queue: queueSnapshot(),
        result: String(islands),
        done: true,
      }
    )
  );

  return steps;
}

export const numberOfIslandsEntry: VisualizerEntry = {
  slug: "number-of-islands",
  title: "Number of Islands",
  inputHint: "4 5 / rows of 0 and 1",
  defaultInput: "4 5\n11110\n11010\n11000\n00000",
  presets: [
    { label: "One island", value: "4 5\n11110\n11010\n11000\n00000" },
    { label: "Three islands", value: "4 5\n11000\n11000\n00100\n00011" },
    { label: "Water", value: "2 3\n000\n000" },
  ],
  pseudocode: [
    "islands = 0",
    "for r in range(R):",
    "    for c in range(C):",
    "        if grid[r][c] == '1' and not visited:",
    "            islands += 1",
    "            queue = deque([(r, c)])",
    "            visited.add((r, c))",
    "            while queue:",
    "                x, y = queue.popleft()",
    "                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):",
    "                    nx, ny = x + dx, y + dy",
    "                    if 0 <= nx < R and 0 <= ny < C and grid[nx][ny] == '1':",
    "                        if (nx, ny) not in visited:",
    "                            visited.add((nx, ny))",
    "                            queue.append((nx, ny))",
    "return islands",
  ],
  parse: (raw: string) => parseNumberOfIslands(raw),
  generate: (input: unknown) => generateNumberOfIslands(input as NumberOfIslandsInput),
};
