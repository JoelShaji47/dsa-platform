import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface PartitionSubsetInput {
  values: number[];
}

export function parsePartitionSubset(raw: string): PartitionSubsetInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one number");
  if (values.length > 12) throw new Error("Keep it to 12 numbers");
  if (values.some((value) => value <= 0)) throw new Error("Numbers must be positive");
  return { values };
}

export function generatePartitionSubset({ values }: PartitionSubsetInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const total = values.reduce((sum, value) => sum + value, 0);
  const target = total / 2;
  const possible = total % 2 === 0;

  const valuesSnap = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {}, label: "numbers" });

  steps.push(
    step(
      0,
      "Start",
      possible
        ? `Total is ${total}; look for a subset summing to ${target}.`
        : `Total is ${total} (odd), so an equal partition is impossible.`,
      0,
      valuesSnap(),
      { total, target: possible ? target : "odd" },
      {}
    )
  );

  if (!possible) {
    steps.push(
      step(
        steps.length,
        "Done",
        "An odd total cannot be split into two equal integer sums.",
        4,
        valuesSnap(),
        { result: "false" },
        { done: true, result: "false" }
      )
    );
    return steps;
  }

  const dp = new Array<boolean>(target + 1).fill(false);
  dp[0] = true;
  const dpSnap = (active: number[] = []) =>
    snap(dp.map((value) => (value ? "T" : "F")), {
      active,
      settled: dp.map((value, index) => (value ? index : -1)).filter((index) => index >= 0),
      label: `subset sums up to ${target}`,
    });

  steps.push(
    step(
      steps.length,
      "Base",
      "A sum of 0 is always reachable with the empty subset.",
      1,
      valuesSnap(),
      { target },
      { arrayAlt: dpSnap([0]) }
    )
  );

  for (let i = 0; i < values.length; i += 1) {
    const value = values[i];
    for (let sum = target; sum >= value; sum -= 1) {
      if (!dp[sum - value] || dp[sum]) continue;
      dp[sum] = true;
      steps.push(
        step(
          steps.length,
          "Reach sum",
          `Using ${value}, sum ${sum - value} makes sum ${sum} reachable.`,
          3,
          valuesSnap([i], Array.from({ length: i }, (_, index) => index)),
          { value, from: sum - value, to: sum },
          { arrayAlt: dpSnap([sum]) }
        )
      );
      if (sum === target) break;
    }
  }

  const result = dp[target];
  steps.push(
    step(
      steps.length,
      "Done",
      result ? `A subset summing to ${target} exists, so the array can be partitioned.` : `No subset sums to ${target}.`,
      4,
      valuesSnap([], values.map((_, index) => index)),
      { result: result ? "true" : "false" },
      { arrayAlt: dpSnap(dp.map((_, index) => index)), done: true, result: result ? "true" : "false" }
    )
  );

  return steps;
}

export const partitionSubsetEntry: VisualizerEntry = {
  slug: "partition-equal-subset-sum",
  title: "Partition Equal Subset Sum",
  inputHint: "n, then n positive numbers",
  defaultInput: "4\n1 5 11 5",
  presets: [
    { label: "example", value: "4\n1 5 11 5" },
    { label: "impossible", value: "3\n1 2 3" },
    { label: "pair", value: "2\n2 2" },
  ],
  pseudocode: [
    "total = sum(nums); if total is odd: return false",
    "target = total / 2",
    "dp[0] = true",
    "for value in nums:",
    "  for sum from target down to value:",
    "    dp[sum] = dp[sum] or dp[sum - value]",
    "return dp[target]",
  ],
  parse: parsePartitionSubset,
  generate: (input) => generatePartitionSubset(input as PartitionSubsetInput),
};
