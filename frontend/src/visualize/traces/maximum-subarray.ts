import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface MaximumSubarrayInput {
  values: number[];
}

export function parseMaximumSubarray(raw: string): MaximumSubarrayInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one number");
  if (values.length > 14) throw new Error("Keep it to 14 numbers");
  return { values };
}

export function generateMaximumSubarray({ values }: MaximumSubarrayInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let best = values[0];
  let current = values[0];
  let bestStart = 0;
  let bestEnd = 0;
  let start = 0;

  const snapshot = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {} });

  steps.push(
    step(
      0,
      "Start",
      "Kadane's algorithm keeps the best subarray ending at the current index.",
      0,
      snapshot([0]),
      { current, best },
      {}
    )
  );

  for (let i = 1; i < values.length; i += 1) {
    if (current + values[i] < values[i]) {
      current = values[i];
      start = i;
    } else {
      current += values[i];
    }

    if (current > best) {
      best = current;
      bestStart = start;
      bestEnd = i;
    }

    const settled = Array.from({ length: i + 1 }, (_, index) => index);
    steps.push(
      step(
        steps.length,
        current === values[i] ? "Restart" : "Extend",
        `At index ${i}, the best sum ending here is ${current}; overall best is ${best}.`,
        2,
        snapshot([i], settled),
        { i, current, best, window: `${bestStart}..${bestEnd}` },
        {}
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The maximum subarray sum is ${best}.`,
      4,
      snap(
        values,
        {
          settled: Array.from({ length: values.length }, (_, index) => index),
          pointers: {},
        }
      ),
      { best },
      { done: true, result: String(best) }
    )
  );

  return steps;
}

export const maximumSubarrayEntry: VisualizerEntry = {
  slug: "maximum-subarray",
  title: "Maximum Subarray",
  inputHint: "n, then the array, e.g. 9 / -2 1 -3 4 -1 2 1 -5 4",
  defaultInput: "9\n-2 1 -3 4 -1 2 1 -5 4",
  presets: [
    { label: "example", value: "9\n-2 1 -3 4 -1 2 1 -5 4" },
    { label: "all negative", value: "3\n-3 -1 -2" },
    { label: "single", value: "1\n5" },
  ],
  pseudocode: [
    "current = best = nums[0]",
    "for i from 1 to n - 1:",
    "  current = max(nums[i], current + nums[i])",
    "  best = max(best, current)",
    "return best",
  ],
  parse: parseMaximumSubarray,
  generate: (input) => generateMaximumSubarray(input as MaximumSubarrayInput),
};
