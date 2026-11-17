import {
  snap,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface ClimbingStairsInput {
  n: number;
}

export function parseClimbingStairs(raw: string): ClimbingStairsInput {
  const n = Number(raw.trim());
  if (!Number.isInteger(n) || n < 1) {
    throw new Error("Use a positive integer n");
  }
  if (n > 12) throw new Error("Keep n <= 12 so the trace stays readable");
  return { n };
}

export function generateClimbingStairs({ n }: ClimbingStairsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dp = Array.from({ length: n + 1 }, () => 0);
  const computed = new Set<number>();

  const display = () => dp.map((value, index) => (computed.has(index) ? value : ""));
  const settled = () => [...computed].sort((a, b) => a - b);

  steps.push(
    step(
      0,
      "Start",
      `Count the ways to climb ${n} step${n === 1 ? "" : "s"} using 1- or 2-step moves.`,
      0,
      snap(display()),
      { n },
      {}
    )
  );

  dp[0] = 1;
  computed.add(0);
  steps.push(
    step(
      steps.length,
      "Base 0",
      "There is exactly one way to stand still: take no steps.",
      1,
      snap(display(), { active: [0], settled: settled() }),
      { ways: dp[0] },
      {}
    )
  );

  if (n >= 1) {
    dp[1] = 1;
    computed.add(1);
    steps.push(
      step(
        steps.length,
        "Base 1",
        "There is one way to reach step 1: a single 1-step move.",
        2,
        snap(display(), { active: [1], settled: settled() }),
        { ways: dp[1] },
        {}
      )
    );
  }

  for (let i = 2; i <= n; i += 1) {
    steps.push(
      step(
        steps.length,
        "Compute",
        `To reach step ${i}, come from step ${i - 1} or step ${i - 2}.`,
        4,
        snap(display(), {
          active: [i],
          deps: [i - 1, i - 2],
          settled: settled(),
        }),
        { i, from1: dp[i - 1], from2: dp[i - 2] },
        {}
      )
    );

    dp[i] = dp[i - 1] + dp[i - 2];
    computed.add(i);
    steps.push(
      step(
        steps.length,
        "Store",
        `dp[${i}] = ${dp[i - 1]} + ${dp[i - 2]} = ${dp[i]}.`,
        4,
        snap(display(), {
          active: [i],
          deps: [i - 1, i - 2],
          settled: settled(),
        }),
        { i, ways: dp[i] },
        {}
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `There are ${dp[n]} distinct way${dp[n] === 1 ? "" : "s"} to reach step ${n}.`,
      5,
      snap(display(), { settled: settled() }),
      { ways: dp[n] },
      { result: String(dp[n]), done: true }
    )
  );

  return steps;
}

export const climbingStairsEntry: VisualizerEntry = {
  slug: "climbing-stairs",
  title: "Climbing Stairs",
  inputHint: "5",
  defaultInput: "5",
  presets: [
    { label: "Example", value: "5" },
    { label: "Small", value: "3" },
    { label: "One step", value: "1" },
    { label: "Ten", value: "10" },
  ],
  pseudocode: [
    "dp = [0] * (n + 1)",
    "dp[0] = 1",
    "dp[1] = 1",
    "for i in range(2, n + 1):",
    "    dp[i] = dp[i-1] + dp[i-2]",
    "return dp[n]",
  ],
  parse: (raw: string) => parseClimbingStairs(raw),
  generate: (input: unknown) => generateClimbingStairs(input as ClimbingStairsInput),
};
