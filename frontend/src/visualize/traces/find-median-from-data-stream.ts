import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface MedianStreamInput {
  values: number[];
}

export function parseMedianStream(raw: string): MedianStreamInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n, then n numbers");
  const n = Number(lines[0]);
  const values = integersFrom(lines.slice(1).join(" "));
  if (!Number.isInteger(n) || n < 1) throw new Error("n must be a positive integer");
  if (values.length !== n) throw new Error(`Expected ${n} numbers`);
  if (n > 12) throw new Error("Keep it to 12 numbers");
  return { values };
}

function insert(sorted: number[], value: number): number {
  let index = 0;
  while (index < sorted.length && sorted[index] < value) index += 1;
  sorted.splice(index, 0, value);
  return index;
}

function format(value: number): string {
  return value.toFixed(1);
}

export function generateMedianStream({ values }: MedianStreamInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const low: number[] = [];
  const high: number[] = [];
  const medians: string[] = [];

  const lowSnap = (active: number[] = []) =>
    snap(low, { active, settled: low.map((_, index) => index), label: "lower half (max at end)" });
  const highSnap = (active: number[] = []) =>
    snap(high, { active, settled: high.map((_, index) => index), label: "upper half (min at start)" });
  const medianSnap = () => snap(medians, { label: "medians" });

  steps.push(
    step(0, "Start", "Keep the lower and upper halves balanced; the median comes from their boundary.", 0, lowSnap(), {}, { arrayAlt: highSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    const value = values[i];
    if (low.length === 0 || value <= low[low.length - 1]) {
      const index = insert(low, value);
      steps.push(
        step(
          steps.length,
          "Insert low",
          `${value} belongs in the lower half.`,
          1,
          lowSnap([index]),
          { value, low: low.length, high: high.length },
          { arrayAlt: highSnap() }
        )
      );
    } else {
      const index = insert(high, value);
      steps.push(
        step(
          steps.length,
          "Insert high",
          `${value} belongs in the upper half.`,
          2,
          lowSnap(),
          { value, low: low.length, high: high.length },
          { arrayAlt: highSnap([index]) }
        )
      );
    }

    if (low.length > high.length + 1) {
      const moved = low.pop()!;
      const index = insert(high, moved);
      steps.push(
        step(
          steps.length,
          "Rebalance",
          `Move ${moved} from the lower half to the upper half.`,
          3,
          lowSnap(),
          { moved, low: low.length, high: high.length },
          { arrayAlt: highSnap([index]) }
        )
      );
    } else if (high.length > low.length) {
      const moved = high.shift()!;
      const index = insert(low, moved);
      steps.push(
        step(
          steps.length,
          "Rebalance",
          `Move ${moved} from the upper half to the lower half.`,
          3,
          lowSnap([index]),
          { moved, low: low.length, high: high.length },
          { arrayAlt: highSnap() }
        )
      );
    }

    const median =
      low.length > high.length ? low[low.length - 1] : (low[low.length - 1] + high[0]) / 2;
    medians.push(format(median));
    steps.push(
      step(
        steps.length,
        "Median",
        `The median after adding ${value} is ${format(median)}.`,
        5,
        lowSnap([low.length - 1]),
        { value, median: format(median) },
        { arrayAlt: highSnap([0]) }
      )
    );
  }

  const result = medians.join("\n");
  steps.push(
    step(
      steps.length,
      "Done",
      `The running medians are ${medians.join(", ")}.`,
      6,
      lowSnap(),
      { count: medians.length },
      { arrayAlt: highSnap(), done: true, result }
    )
  );

  return steps;
}

export const medianStreamEntry: VisualizerEntry = {
  slug: "find-median-from-data-stream",
  title: "Find Median from Data Stream",
  inputHint: "n, then n numbers",
  defaultInput: "5\n1 2 3 4 5",
  presets: [
    { label: "example", value: "5\n1 2 3 4 5" },
    { label: "mixed", value: "3\n2 1 3" },
    { label: "duplicates", value: "4\n1 1 2 2" },
  ],
  pseudocode: [
    "low = max-heap, high = min-heap",
    "add value to the appropriate half",
    "rebalance so low.size - high.size is 0 or 1",
    "median = low.top or average(low.top, high.top)",
  ],
  parse: parseMedianStream,
  generate: (input) => generateMedianStream(input as MedianStreamInput),
};
