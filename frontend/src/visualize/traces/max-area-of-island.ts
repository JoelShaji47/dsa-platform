import { snap, snapGrid, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseIntGrid } from "./input-utils";

export interface MaxAreaIslandInput {
  rows: number;
  cols: number;
  grid: number[][];
}

const DIRECTIONS: [number, number][] = [
  [1, 0],
  [-1, 0],
  [0, 1],
  [0, -1],
];

export function parseMaxAreaIsland(raw: string): MaxAreaIslandInput {
  const parsed = parseIntGrid(raw, 6, 6);
  if (parsed.grid.some((row) => row.some((cell) => cell !== 0 && cell !== 1))) {
    throw new Error("Use only 0 and 1");
  }
  return parsed;
}

export function generateMaxAreaIsland({ rows, cols, grid }: MaxAreaIslandInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const visited = new Set<string>();
  const settled: [number, number][] = [];
  const queue: [number, number][] = [];
  let best = 0;

  const key = (row: number, col: number) => `${row},${col}`;
  const queueSnap = () =>
    snapQueue(queue.map(([row, col]) => `${row},${col}`), {
      active: queue.length > 0 ? [0] : [],
      label: "queue",
    });
  const gridSnap = (active: [number, number][] = [], deps: [number, number][] = []) =>
    snapGrid(grid, { active, deps, settled: [...settled], label: "grid" });

  steps.push(
    step(0, "Start", "Scan for unvisited land and BFS each island to measure its area.", 0, snap([]), { best }, { grid: gridSnap() })
  );

  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      if (grid[row][col] !== 1 || visited.has(key(row, col))) continue;

      let area = 0;
      visited.add(key(row, col));
      settled.push([row, col]);
      queue.push([row, col]);
      steps.push(
        step(
          steps.length,
          "Island",
          `Start a new island at (${row}, ${col}).`,
          1,
          snap([]),
          { cell: `${row},${col}`, area, best },
          { grid: gridSnap([[row, col]]), queue: queueSnap() }
        )
      );

      while (queue.length > 0) {
        const [r, c] = queue.shift()!;
        area += 1;
        best = Math.max(best, area);
        steps.push(
          step(
            steps.length,
            "Expand",
            `Visit (${r}, ${c}); the island area is ${area}.`,
            3,
            snap([]),
            { cell: `${r},${c}`, area, best },
            { grid: gridSnap([[r, c]]), queue: queueSnap() }
          )
        );

        for (const [dr, dc] of DIRECTIONS) {
          const nr = r + dr;
          const nc = c + dc;
          if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
          if (grid[nr][nc] !== 1 || visited.has(key(nr, nc))) continue;
          visited.add(key(nr, nc));
          settled.push([nr, nc]);
          queue.push([nr, nc]);
          steps.push(
            step(
              steps.length,
              "Enqueue",
              `(${nr}, ${nc}) is connected land; add it to the queue.`,
              4,
              snap([]),
              { cell: `${nr},${nc}`, area, best },
              { grid: gridSnap([[nr, nc]], [[r, c]]), queue: queueSnap() }
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
      `The largest island has area ${best}.`,
      5,
      snap([]),
      { best },
      { grid: gridSnap(), queue: queueSnap(), done: true, result: String(best) }
    )
  );

  return steps;
}

export const maxAreaIslandEntry: VisualizerEntry = {
  slug: "max-area-of-island",
  title: "Max Area of Island",
  inputHint: "R C, then R rows of 0/1",
  defaultInput: "4 5\n0 0 1 0 0\n0 0 1 1 0\n0 0 0 1 0\n0 0 0 0 0",
  presets: [
    { label: "example", value: "4 5\n0 0 1 0 0\n0 0 1 1 0\n0 0 0 1 0\n0 0 0 0 0" },
    { label: "ring", value: "3 3\n1 1 1\n1 0 1\n1 1 1" },
    { label: "water", value: "2 2\n0 0\n0 0" },
  ],
  pseudocode: [
    "best = 0",
    "for each unvisited land cell:",
    "  BFS the island, counting cells",
    "  best = max(best, area)",
    "return best",
  ],
  parse: parseMaxAreaIsland,
  generate: (input) => generateMaxAreaIsland(input as MaxAreaIslandInput),
};
