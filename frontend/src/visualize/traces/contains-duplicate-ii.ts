import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface ContainsDuplicateIIInput {
  values: number[];
  k: number;
}

export function parseContainsDuplicateII(raw: string): ContainsDuplicateIIInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: array, then k");
  const values = integersFrom(lines[0]);
  const k = Number(lines[1]);
  if (values.length > 14) throw new Error("Keep it to 14 numbers");
  if (!Number.isInteger(k) || k < 0) throw new Error("k must be a non-negative integer");
  return { values, k };
}

export function generateContainsDuplicateII({ values, k }: ContainsDuplicateIIInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const last = new Map<number, number>();

  const snapshot = (active: number[] = [], deps: number[] = []) =>
    snap(values, { active, deps, settled: [], pointers: { i: active[0] ?? 0 } });

  steps.push(
    step(0, "Start", `Check whether equal values appear within ${k} indices.`, 0, snapshot(), { k }, {})
  );

  for (let i = 0; i < values.length; i += 1) {
    const previous = last.get(values[i]);
    if (previous != null && i - previous <= k) {
      steps.push(
        step(
          steps.length,
          "Found",
          `${values[i]} appeared at index ${previous}; distance ${i - previous} <= ${k}.`,
          3,
          snapshot([i], [previous]),
          { i, previous, distance: i - previous },
          { done: true, result: "true" }
        )
      );
      return steps;
    }

    last.set(values[i], i);
    steps.push(
      step(
        steps.length,
        previous == null ? "Remember" : "Too far",
        previous == null
          ? `Record ${values[i]} at index ${i}.`
          : `${values[i]} was last at ${previous}, but the distance ${i - previous} exceeds ${k}.`,
        2,
        snapshot([i], previous == null ? [] : [previous]),
        { i, previous: previous ?? "none" },
        {}
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `No equal pair is within distance ${k}.`,
      5,
      snapshot([], []),
      { k },
      { done: true, result: "false" }
    )
  );

  return steps;
}

export const containsDuplicateIIEntry: VisualizerEntry = {
  slug: "contains-duplicate-ii",
  title: "Contains Duplicate II",
  inputHint: "array, then k",
  defaultInput: "[1,2,3,1]\n3",
  presets: [
    { label: "example", value: "[1,2,3,1]\n3" },
    { label: "too far", value: "[1,2,3,1,2,3]\n2" },
    { label: "adjacent", value: "[1,0,1,1]\n1" },
  ],
  pseudocode: [
    "last = empty map",
    "for i, value in nums:",
    "  if last[value] exists and i - last[value] <= k: return true",
    "  last[value] = i",
    "return false",
  ],
  parse: parseContainsDuplicateII,
  generate: (input) => generateContainsDuplicateII(input as ContainsDuplicateIIInput),
};
