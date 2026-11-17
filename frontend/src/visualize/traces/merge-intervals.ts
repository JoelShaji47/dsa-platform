import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseIntervals } from "./input-utils";

export interface MergeIntervalsInput {
  intervals: [number, number][];
}

export function parseMergeIntervals(raw: string): MergeIntervalsInput {
  const intervals = parseIntervals(raw);
  if (intervals.length > 10) throw new Error("Keep it to 10 intervals");
  return { intervals };
}

function labels(intervals: [number, number][]): string[] {
  return intervals.map(([start, end]) => `${start}-${end}`);
}

export function generateMergeIntervals({ intervals }: MergeIntervalsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const sorted = intervals
    .map((interval) => [...interval] as [number, number])
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const merged: [number, number][] = [];
  const settled: number[] = [];

  steps.push(
    step(
      0,
      "Sort",
      "Sort intervals by start so overlapping intervals sit next to each other.",
      0,
      snap(labels(sorted), { active: [], settled: [], pointers: {} }),
      { intervals: intervals.length },
      {}
    )
  );

  for (let i = 0; i < sorted.length; i += 1) {
    const current = sorted[i];
    const last = merged[merged.length - 1];
    if (!last || current[0] > last[1]) {
      merged.push([...current]);
      settled.push(i);
      steps.push(
        step(
          steps.length,
          "Keep",
          `Interval ${current[0]}-${current[1]} does not overlap; start a new merged interval.`,
          2,
          snap(labels(sorted), { active: [i], settled: [...settled], pointers: {} }),
          { merged: merged.length },
          {}
        )
      );
    } else {
      const before = `${last[0]}-${last[1]}`;
      last[1] = Math.max(last[1], current[1]);
      settled.push(i);
      steps.push(
        step(
          steps.length,
          "Merge",
          `${current[0]}-${current[1]} overlaps ${before}; extend it to ${last[0]}-${last[1]}.`,
          3,
          snap(labels(sorted), { active: [i], settled: [...settled], pointers: {} }),
          { merged: merged.length },
          {}
        )
      );
    }
  }

  const result = merged.map(([start, end]) => `${start} ${end}`).join("\n");
  steps.push(
    step(
      steps.length,
      "Done",
      `The merged intervals are ${merged.map(([a, b]) => `[${a}, ${b}]`).join(", ")}.`,
      5,
      snap(
        labels(sorted),
        {
          settled: sorted.map((_, index) => index),
          pointers: {},
        }
      ),
      { merged: merged.length },
      { done: true, result }
    )
  );

  return steps;
}

export const mergeIntervalsEntry: VisualizerEntry = {
  slug: "merge-intervals",
  title: "Merge Intervals",
  inputHint: "n, then n lines of start end",
  defaultInput: "4\n1 3\n2 6\n8 10\n15 18",
  presets: [
    { label: "example", value: "4\n1 3\n2 6\n8 10\n15 18" },
    { label: "touching", value: "3\n1 2\n2 3\n3 4" },
    { label: "nested", value: "3\n1 10\n2 3\n4 5" },
  ],
  pseudocode: [
    "sort intervals by start",
    "merged = []",
    "for each interval:",
    "  if merged is empty or interval.start > last.end:",
    "    append interval",
    "  else: last.end = max(last.end, interval.end)",
    "return merged",
  ],
  parse: parseMergeIntervals,
  generate: (input) => generateMergeIntervals(input as MergeIntervalsInput),
};
