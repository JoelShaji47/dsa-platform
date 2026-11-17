import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface KClosestInput {
  k: number;
  points: [number, number][];
}

export function parseKClosest(raw: string): KClosestInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n k, then n point lines");
  const header = integersFrom(lines[0]);
  if (header.length !== 2) throw new Error("The first line must be: n k");
  const [n, k] = header;
  if (!Number.isInteger(n) || n < 1) throw new Error("n must be a positive integer");
  if (k < 1 || k > n) throw new Error("k must be between 1 and n");
  if (lines.length !== n + 1) throw new Error(`Expected ${n} point lines`);
  const points: [number, number][] = [];
  for (let i = 0; i < n; i += 1) {
    const values = integersFrom(lines[i + 1]);
    if (values.length !== 2) throw new Error(`Point ${i + 1} must contain x y`);
    points.push([values[0], values[1]]);
  }
  if (n > 12) throw new Error("Keep it to 12 points");
  return { k, points };
}

export function generateKClosest({ k, points }: KClosestInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const labels = points.map(([x, y]) => `${x},${y}`);
  const distances = points.map(([x, y]) => x * x + y * y);
  const order = points.map((_, index) => index).sort((a, b) => distances[a] - distances[b]);

  const pointSnap = (active: number[] = [], settled: number[] = []) =>
    snap(labels, { active, settled, pointers: {}, label: "points (x,y)" });
  const distanceSnap = (active: number[] = []) =>
    snap(distances, { active, label: "squared distance" });

  steps.push(
    step(0, "Start", `Choose the ${k} points with the smallest squared distance from the origin.`, 0, pointSnap(), { k }, { arrayAlt: distanceSnap() })
  );

  for (let rank = 0; rank < order.length; rank += 1) {
    const index = order[rank];
    steps.push(
      step(
        steps.length,
        rank < k ? "Select" : "Skip",
        `Point (${labels[index]}) has distance ${distances[index]}; ${rank < k ? "it is among the closest" : "it falls outside the top k"}.`,
        2,
        pointSnap([index], order.slice(0, Math.min(rank, k))),
        { point: labels[index], distance: distances[index], selected: Math.min(rank + 1, k) },
        { arrayAlt: distanceSnap([index]) }
      )
    );
  }

  const selected = order.slice(0, k).map((index) => labels[index]);
  const result = order
    .slice(0, k)
    .map((index) => points[index].join(" "))
    .join("\n");
  steps.push(
    step(
      steps.length,
      "Done",
      `The closest points are ${selected.join("; ")}.`,
      3,
      pointSnap([], order.slice(0, k)),
      { k },
      { arrayAlt: distanceSnap(order.slice(0, k)), done: true, result }
    )
  );

  return steps;
}

export const kClosestPointsEntry: VisualizerEntry = {
  slug: "k-closest-points-to-origin",
  title: "K Closest Points to Origin",
  inputHint: "n k, then n lines of x y",
  defaultInput: "3 2\n1 3\n-2 2\n2 -2",
  presets: [
    { label: "example", value: "3 2\n1 3\n-2 2\n2 -2" },
    { label: "two", value: "2 1\n0 1\n0 -1" },
    { label: "all", value: "3 3\n1 0\n0 1\n1 1" },
  ],
  pseudocode: [
    "compute squared distance for each point",
    "sort points by distance",
    "take the first k points",
    "return them",
  ],
  parse: parseKClosest,
  generate: (input) => generateKClosest(input as KClosestInput),
};
