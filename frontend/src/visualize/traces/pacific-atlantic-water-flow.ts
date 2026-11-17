import { snap, snapGrid, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseIntGrid } from "./input-utils";

export interface PacificAtlanticInput {
  rows: number;
  cols: number;
  heights: number[][];
}

const DIRECTIONS: [number, number][] = [
  [1, 0],
  [-1, 0],
  [0, 1],
  [0, -1],
];

export function parsePacificAtlantic(raw: string): PacificAtlanticInput {
  const parsed = parseIntGrid(raw, 6, 6);
  return { rows: parsed.rows, cols: parsed.cols, heights: parsed.grid };
}

export function generatePacificAtlantic({ rows, cols, heights }: PacificAtlanticInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const pacific = new Set<string>();
  const atlantic = new Set<string>();
  let queue: [number, number][] = [];
  let ocean = "Pacific";

  const key = (row: number, col: number) => `${row},${col}`;
  const gridSnap = (active: [number, number][] = [], deps: [number, number][] = []) => {
    const status = heights.map((row, r) =>
      row.map((_, c) => {
        const id = key(r, c);
        if (pacific.has(id) && atlantic.has(id)) return "PA";
        if (pacific.has(id)) return "P";
        if (atlantic.has(id)) return "A";
        return ".";
      })
    );
    return snapGrid(status, {
      active,
      deps,
      settled: [...pacific, ...atlantic].map((id) => id.split(",").map(Number) as [number, number]),
      label: `${ocean} reachability`,
    });
  };
  const queueSnap = () =>
    snapQueue(queue.map(([row, col]) => `${row},${col}`), {
      active: queue.length > 0 ? [0] : [],
      label: `${ocean} frontier`,
    });

  const heightsSnap = (active: [number, number][] = []) =>
    snapGrid(heights, { active, label: "heights" });

  steps.push(
    step(
      0,
      "Start",
      "Water flows from a cell to neighbors of equal or lower height. Search inward from each ocean.",
      0,
      snap([]),
      { rows, cols },
      { grid: heightsSnap() }
    )
  );

  const search = (set: Set<string>, label: string) => {
    ocean = label;
    const localQueue: [number, number][] = [];
    const seed = (row: number, col: number) => {
      const id = key(row, col);
      if (set.has(id)) return;
      set.add(id);
      localQueue.push([row, col]);
    };
    for (let col = 0; col < cols; col += 1) {
      if (label === "Pacific") seed(0, col);
      else seed(rows - 1, col);
    }
    for (let row = 0; row < rows; row += 1) {
      if (label === "Pacific") seed(row, 0);
      else seed(row, cols - 1);
    }

    queue = [...localQueue];
    steps.push(
      step(
        steps.length,
        `Seed ${label}`,
        `Add the ${label} border cells to the queue.`,
        1,
        snap([]),
        { ocean: label, queued: queue.length },
        { grid: gridSnap(), queue: queueSnap() }
      )
    );

    while (queue.length > 0) {
      const [row, col] = queue.shift()!;
      steps.push(
        step(
          steps.length,
          "Expand",
          `From (${row}, ${col}), climb to neighbors at least as high.`,
          2,
          snap([]),
          { ocean: label, cell: `${row},${col}` },
          { grid: gridSnap([[row, col]]), queue: queueSnap() }
        )
      );

      for (const [dr, dc] of DIRECTIONS) {
        const nr = row + dr;
        const nc = col + dc;
        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
        if (heights[nr][nc] < heights[row][col]) continue;
        const id = key(nr, nc);
        if (set.has(id)) continue;
        set.add(id);
        queue.push([nr, nc]);
        steps.push(
          step(
            steps.length,
            "Reach",
            `(${nr}, ${nc}) can drain to the ${label}.`,
            3,
            snap([]),
            { ocean: label, cell: `${nr},${nc}` },
            { grid: gridSnap([[nr, nc]], [[row, col]]), queue: queueSnap() }
          )
        );
      }
    }
  };

  search(pacific, "Pacific");
  search(atlantic, "Atlantic");

  const resultCells: [number, number][] = [];
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      if (pacific.has(key(row, col)) && atlantic.has(key(row, col))) {
        resultCells.push([row, col]);
      }
    }
  }

  ocean = "both";
  const result = resultCells.map(([row, col]) => `${row} ${col}`).join("\n");
  steps.push(
    step(
      steps.length,
      "Done",
      resultCells.length
        ? `Cells reaching both oceans: ${resultCells.map(([r, c]) => `(${r}, ${c})`).join(", ")}.`
        : "No cell reaches both oceans.",
      4,
      snap(resultCells.map(([row, col]) => `${row},${col}`), { label: "both oceans" }),
      { count: resultCells.length },
      { grid: gridSnap(resultCells), done: true, result }
    )
  );

  return steps;
}

export const pacificAtlanticEntry: VisualizerEntry = {
  slug: "pacific-atlantic-water-flow",
  title: "Pacific Atlantic Water Flow",
  inputHint: "R C, then R rows of heights",
  defaultInput: "5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4",
  presets: [
    { label: "example", value: "5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4" },
    { label: "single", value: "1 1\n1" },
    { label: "flat", value: "2 2\n1 1\n1 1" },
  ],
  pseudocode: [
    "pacific = cells reachable from top/left borders",
    "atlantic = cells reachable from bottom/right borders",
    "reverse DFS climbs to neighbors with height >= current",
    "return the intersection",
  ],
  parse: parsePacificAtlantic,
  generate: (input) => generatePacificAtlantic(input as PacificAtlanticInput),
};
