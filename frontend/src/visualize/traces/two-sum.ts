import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface TwoSumInput {
  nums: number[];
  target: number;
}

export function parseTwoSum(raw: string): TwoSumInput {
  // "[2, 7, 11, 15], 9" or "[2,7,11,15], target 9"
  const cleaned = raw.replace(/target/i, ",").trim();
  const bracket = cleaned.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [2, 7, 11, 15], 9");
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 2 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error("Need at least 2 numbers, e.g. [2, 7, 11, 15], 9");
  }
  if (nums.length > 12) throw new Error("Keep it to 12 numbers so the trace stays readable");
  const rest = cleaned.slice(bracket[0].length).replace(/^,/, "").trim();
  if (!rest) throw new Error("Add a target after the array, e.g. [2, 7, 11, 15], 9");
  const target = Number(rest);
  if (!Number.isFinite(target)) throw new Error("Add a target after the array, e.g. [2, 7, 11, 15], 9");
  return { nums, target };
}

export function generateTwoSum({ nums, target }: TwoSumInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const seen = new Map<number, number>();
  steps.push(
    step(0, "Start", `Look for two numbers adding to ${target}. Scan left to right, remembering each value's index.`, 0, snap(nums), { target })
  );
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    steps.push(
      step(
        steps.length, "Check", `At i=${i} (value ${nums[i]}). Need ${need} to reach ${target}.`,
        1, snap(nums, { active: [i], pointers: { i } }), { i, need }
      )
    );
    if (seen.has(need)) {
      const j = seen.get(need)!;
      steps.push(
        step(
          steps.length, "Found", `${nums[j]} + ${nums[i]} = ${target}. Return [${j}, ${i}].`,
          2, snap(nums, { active: [j, i], settled: [j, i], pointers: { i, j } }),
          { i, j }, { result: `[${j}, ${i}]`, done: true }
        )
      );
      return steps;
    }
    steps.push(
      step(
        steps.length, "Remember", `No match yet — store ${nums[i]} at index ${i} and move on.`,
        3, snap(nums, { active: [i], settled: [...seen.values()], pointers: { i } }), { i }
      )
    );
    seen.set(nums[i], i);
  }
  steps.push(
    step(steps.length, "No pair", `Checked every element — no two sum to ${target}.`, 3, snap(nums, { settled: [...seen.values()] }), { target }, { done: true })
  );
  return steps;
}

export const twoSumEntry: VisualizerEntry = {
  slug: "two-sum",
  title: "Two Sum",
  inputHint: "[2, 7, 11, 15], 9",
  defaultInput: "[2, 7, 11, 15], 9",
  presets: [
    { label: "Basic", value: "[2, 7, 11, 15], 9" },
    { label: "Duplicates", value: "[3, 3], 6" },
    { label: "No pair", value: "[1, 2, 3], 7" },
  ],
  pseudocode: [
    "seen = {}",
    "for i, x in enumerate(nums):",
    "    if target - x in seen: return [seen[target-x], i]",
    "    seen[x] = i",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseTwoSum(raw),
  generate: (input: unknown) => generateTwoSum(input as TwoSumInput),
};
