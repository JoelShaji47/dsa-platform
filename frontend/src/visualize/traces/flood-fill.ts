import {
  snap,
  snapGrid,
  snapQueue,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface FloodFillInput {
  rows: number;
  cols: number;
  image: number[][];
  sr: number;
  sc: number;
  newColor: number;
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

export function parseFloodFill(raw: string): FloodFillInput {
  const lines = raw
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  if (lines.length < 2) {
    throw new Error("Use: R C, then the grid, then sr sc newColor");
  }

  const [rows, cols] = lines[0].split(/[\s,]+/).map(Number);
  if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 1 || cols < 1) {
    throw new Error("Grid dimensions must be positive integers");
  }
  if (rows > 6 || cols > 6) {
    throw new Error("Keep the grid to 6x6 so the trace stays readable");
  }
  if (lines.length < rows + 2) {
    throw new Error("The grid is missing rows, or the start line is missing");
  }

  const image = lines.slice(1, rows + 1).map((line) => {
    const values = line.split(/[\s,]+/).map(Number);
    if (values.length !== cols || values.some((value) => !Number.isFinite(value))) {
      throw new Error(`Each grid row needs exactly ${cols} numbers`);
    }
    return values;
  });

  const [sr, sc, newColor] = lines[rows + 1].split(/[\s,]+/).map(Number);
  if (
    !Number.isInteger(sr) ||
    !Number.isInteger(sc) ||
    !Number.isFinite(newColor) ||
    sr < 0 ||
    sr >= rows ||
    sc < 0 ||
    sc >= cols
  ) {
    throw new Error("The start pixel must be inside the grid");
  }

  return { rows, cols, image, sr, sc, newColor };
}

export function generateFloodFill(input: FloodFillInput): BaseStep[] {
  const { rows, cols, sr, sc, newColor } = input;
  const steps: BaseStep[] = [];
  const image = input.image.map((row) => [...row]);
  const target = image[sr][sc];
  const settled: [number, number][] = [];
  const filled = new Set<string>();
  const queue: [number, number][] = [];

  const queueSnapshot = () =>
    snapQueue(
      queue.map(([row, col]) => `${row},${col}`),
      { active: queue.length > 0 ? [0] : [], label: "queue" }
    );

  const gridSnapshot = (
    active: [number, number][] = [],
    deps: [number, number][] = []
  ) =>
    snapGrid(image, {
      active,
      deps,
      settled: [...settled],
      showIndices: false,
      label: "image",
    });

  steps.push(
    step(
      0,
      "Start",
      `Start at (${sr}, ${sc}) with color ${target}. Recolor that connected region to ${newColor}.`,
      0,
      snap([]),
      { start: `${sr},${sc}`, color: target, newColor },
      { grid: gridSnapshot([[sr, sc]]) }
    )
  );

  if (target === newColor) {
    steps.push(
      step(
        steps.length,
        "No change",
        "The starting color already equals the new color, so the image is unchanged.",
        1,
        snap([]),
        { color: target },
        {
          grid: gridSnapshot([[sr, sc]]),
          result: image.map((row) => row.join(" ")).join(" / "),
          done: true,
        }
      )
    );
    return steps;
  }

  image[sr][sc] = newColor;
  filled.add(key(sr, sc));
  settled.push([sr, sc]);
  queue.push([sr, sc]);

  steps.push(
    step(
      steps.length,
      "Fill start",
      `Recolor the start pixel and enqueue it as the BFS seed.`,
      3,
      snap([]),
      { filled: filled.size, queue: queue.length },
      { grid: gridSnapshot([[sr, sc]]), queue: queueSnapshot() }
    )
  );

  while (queue.length > 0) {
    const [row, col] = queue.shift()!;
    steps.push(
      step(
        steps.length,
        "Pop",
        `Inspect the four neighbors of (${row}, ${col}).`,
        5,
        snap([]),
        { cell: `${row},${col}`, queue: queue.length },
        { grid: gridSnapshot([[row, col]]), queue: queueSnapshot() }
      )
    );

    for (const [dr, dc] of DIRECTIONS) {
      const nr = row + dr;
      const nc = col + dc;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
      if (image[nr][nc] !== target) continue;

      image[nr][nc] = newColor;
      filled.add(key(nr, nc));
      settled.push([nr, nc]);
      queue.push([nr, nc]);

      steps.push(
        step(
          steps.length,
          "Fill",
          `(${nr}, ${nc}) still has color ${target}; recolor it and enqueue it.`,
          10,
          snap([]),
          { cell: `${nr},${nc}`, filled: filled.size },
          {
            grid: gridSnapshot([[nr, nc]], [[row, col]]),
            queue: queueSnapshot(),
          }
        )
      );
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The connected region has been recolored to ${newColor}.`,
      11,
      snap([]),
      { filled: filled.size },
      {
        grid: gridSnapshot(),
        queue: queueSnapshot(),
        result: image.map((row) => row.join(" ")).join(" / "),
        done: true,
      }
    )
  );

  return steps;
}

export const floodFillEntry: VisualizerEntry = {
  slug: "flood-fill",
  title: "Flood Fill",
  inputHint: "3 3 / grid / 1 1 2",
  defaultInput: "3 3\n1 1 1\n1 1 0\n1 0 1\n1 1 2",
  presets: [
    { label: "Classic", value: "3 3\n1 1 1\n1 1 0\n1 0 1\n1 1 2" },
    { label: "Single", value: "1 1\n0\n0 0 2" },
    { label: "Same color", value: "2 2\n1 1\n1 1\n0 0 1" },
  ],
  pseudocode: [
    "target = image[sr][sc]",
    "if target == newColor: return image",
    "queue = deque([(sr, sc)])",
    "image[sr][sc] = newColor",
    "while queue:",
    "    r, c = queue.popleft()",
    "    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):",
    "        nr, nc = r + dr, c + dc",
    "        if 0 <= nr < R and 0 <= nc < C and image[nr][nc] == target:",
    "            image[nr][nc] = newColor",
    "            queue.append((nr, nc))",
    "return image",
  ],
  parse: (raw: string) => parseFloodFill(raw),
  generate: (input: unknown) => generateFloodFill(input as FloodFillInput),
};
