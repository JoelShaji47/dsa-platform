import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface LisInput {
  values: number[];
}

export function parseLis(raw: string): LisInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one number");
  if (values.length > 14) throw new Error("Keep it to 14 numbers");
  return { values };
}

export function generateLis({ values }: LisInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dp = new Array<number>(values.length).fill(1);
  let best = values.length > 0 ? 1 : 0;

  const arraySnap = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {}, label: "sequence" });
  const dpSnap = (active: number[] = [], deps: number[] = []) =>
    snap(dp, { active, deps, settled: dp.map((_, index) => index), label: "LIS ending at i" });

  steps.push(
    step(0, "Start", "Each position starts with an LIS of length 1; extend from smaller earlier values.", 0, arraySnap(), { best }, { arrayAlt: dpSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    let length = 1;
    let from = -1;
    for (let j = 0; j < i; j += 1) {
      if (values[j] < values[i] && dp[j] + 1 > length) {
        length = dp[j] + 1;
        from = j;
      }
    }
    dp[i] = length;
    best = Math.max(best, length);
    steps.push(
      step(
        steps.length,
        from >= 0 ? "Extend" : "Restart",
        from >= 0
          ? `Extend the subsequence ending at ${values[from]} to include ${values[i]}; length ${length}.`
          : `${values[i]} does not extend any smaller value; keep length 1.`,
        2,
        arraySnap([i], Array.from({ length: i }, (_, index) => index)),
        { value: values[i], length, best },
        { arrayAlt: dpSnap([i], from >= 0 ? [from] : []) }
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The longest increasing subsequence has length ${best}.`,
      3,
      arraySnap([], values.map((_, index) => index)),
      { best },
      { arrayAlt: dpSnap(dp.map((_, index) => index)), done: true, result: String(best) }
    )
  );

  return steps;
}

export const lisEntry: VisualizerEntry = {
  slug: "longest-increasing-subsequence",
  title: "Longest Increasing Subsequence",
  inputHint: "n, then n numbers",
  defaultInput: "8\n10 9 2 5 3 7 101 18",
  presets: [
    { label: "example", value: "8\n10 9 2 5 3 7 101 18" },
    { label: "mixed", value: "6\n0 1 0 3 2 3" },
    { label: "single", value: "1\n7" },
  ],
  pseudocode: [
    "dp[i] = 1 for every i",
    "for i in range(n):",
    "  for j in range(i):",
    "    if nums[j] < nums[i]: dp[i] = max(dp[i], dp[j] + 1)",
    "return max(dp)",
  ],
  parse: parseLis,
  generate: (input) => generateLis(input as LisInput),
};
