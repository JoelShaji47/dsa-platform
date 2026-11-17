import { snap, snapGrid, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseIntGrid } from "./input-utils";

export interface RottingOrangesInput {
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

export function parseRottingOranges(raw: string): RottingOrangesInput {
  const parsed = parseIntGrid(raw, 6, 6);
  if (parsed.grid.some((row) => row.some((cell) => cell < 0 || cell > 2))) {
    throw new Error("Use 0 (empty), 1 (fresh), or 2 (rotten)");
  }
  return parsed;
}

export function generateRottingOranges({ rows, cols, grid }: RottingOrangesInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const values = grid.map((row) => [...row]);
  const queue: [number, number][] = [];
  const settled: [number, number][] = [];
  let fresh = 0;

  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      if (values[row][col] === 2) queue.push([row, col]);
      if (values[row][col] === 1) fresh += 1;
    }
  }

  const queueSnap = () =>
    snapQueue(queue.map(([row, col]) => `${row},${col}`), {
      active: queue.length > 0 ? [0] : [],
      label: "rotten frontier",
    });
  const gridSnap = (active: [number, number][] = [], deps: [number, number][] = []) =>
    snapGrid(values, { active, deps, settled: [...settled], label: "grid" });

  steps.push(
    step(
      0,
      "Start",
      `Multi-source BFS from every rotten orange; ${fresh} fresh orange${fresh === 1 ? "" : "s"} remain.`,
      0,
      snap([]),
      { fresh, minutes: 0 },
      { grid: gridSnap(), queue: queueSnap() }
    )
  );

  let minutes = 0;
  while (queue.length > 0 && fresh > 0) {
    const size = queue.length;
    minutes += 1;
    for (let i = 0; i < size; i += 1) {
      const [row, col] = queue.shift()!;
      for (const [dr, dc] of DIRECTIONS) {
        const nr = row + dr;
        const nc = col + dc;
        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
        if (values[nr][nc] !== 1) continue;
        values[nr][nc] = 2;
        fresh -= 1;
        settled.push([row, col]);
        queue.push([nr, nc]);
        steps.push(
          step(
            steps.length,
            "Rot",
            `Minute ${minutes}: (${nr}, ${nc}) becomes rotten; ${fresh} fresh left.`,
            3,
            snap([]),
            { cell: `${nr},${nc}`, minutes, fresh },
            { grid: gridSnap([[nr, nc]], [[row, col]]), queue: queueSnap() }
          )
        );
      }
    }
    steps.push(
      step(
        steps.length,
        "Minute",
        `Finished minute ${minutes}; ${fresh} fresh orange${fresh === 1 ? "" : "s"} remain.`,
        4,
        snap([]),
        { minutes, fresh },
        { grid: gridSnap(), queue: queueSnap() }
      )
    );
  }

  const result = fresh === 0 ? minutes : -1;
  steps.push(
    step(
      steps.length,
      "Done",
      fresh === 0 ? `Every orange rots in ${minutes} minute${minutes === 1 ? "" : "s"}.` : `${fresh} orange${fresh === 1 ? "" : "s"} never rot.`,
      5,
      snap([]),
      { minutes, fresh, result },
      { grid: gridSnap(), queue: queueSnap(), done: true, result: String(result) }
    )
  );

  return steps;
}

export const rottingOrangesEntry: VisualizerEntry = {
  slug: "rotting-oranges",
  title: "Rotting Oranges",
  inputHint: "R C, then R rows of 0/1/2",
  defaultInput: "3 3\n2 1 1\n1 1 0\n0 1 1",
  presets: [
    { label: "example", value: "3 3\n2 1 1\n1 1 0\n0 1 1" },
    { label: "single", value: "1 1\n2" },
    { label: "trapped", value: "3 3\n2 0 0\n0 1 0\n0 0 2" },
  ],
  pseudocode: [
    "queue = all rotten oranges; minutes = 0",
    "while queue and fresh > 0:",
    "  process one BFS layer",
    "  rot adjacent fresh oranges",
    "  minutes += 1",
    "return minutes if no fresh remain, else -1",
  ],
  parse: parseRottingOranges,
  generate: (input) => generateRottingOranges(input as RottingOrangesInput),
};
