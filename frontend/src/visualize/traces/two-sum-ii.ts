import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface TwoSumIIInput {
  nums: number[];
  target: number;
}

function parsePair(raw: string, example: string, maxLen: number): TwoSumIIInput {
  const cleaned = raw.replace(/target/i, ",").trim();
  const bracket = cleaned.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error(`Use the form ${example}`);
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 2 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error(`Need at least 2 numbers, e.g. ${example}`);
  }
  if (nums.length > maxLen) throw new Error(`Keep it to ${maxLen} numbers so the trace stays readable`);
  const rest = cleaned.slice(bracket[0].length).replace(/^,/, "").trim();
  if (!rest) throw new Error(`Add a target after the array, e.g. ${example}`);
  const target = Number(rest);
  if (!Number.isFinite(target)) throw new Error(`Add a target after the array, e.g. ${example}`);
  return { nums, target };
}

export function parseTwoSumII(raw: string): TwoSumIIInput {
  return parsePair(raw, "[2, 7, 11, 15], 9", 12);
}

export function generateTwoSumII({ nums, target }: TwoSumIIInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let left = 0;
  let right = nums.length - 1;
  steps.push(
    step(0, "Start", `Array is sorted, so squeeze from both ends toward ${target}. left=0, right=${right}.`, 0,
      snap(nums, { pointers: { left, right } }), { left, right, target })
  );
  while (left < right) {
    const s = nums[left] + nums[right];
    steps.push(
      step(steps.length, "Compare", `${nums[left]} + ${nums[right]} = ${s}. Target is ${target}.`, 1,
        snap(nums, { active: [left, right], pointers: { left, right } }), { left, right, sum: s })
    );
    if (s === target) {
      steps.push(
        step(steps.length, "Found", `Match — answers are 1-indexed, so return [${left + 1}, ${right + 1}].`, 2,
          snap(nums, { active: [left, right], settled: [left, right], pointers: { left, right } }),
          { left: left + 1, right: right + 1 }, { result: `[${left + 1}, ${right + 1}]`, done: true })
      );
      return steps;
    }
    if (s < target) {
      left++;
      steps.push(
        step(steps.length, "Move left", `${s} < ${target} — need a bigger sum, so left moves to ${left}.`, 3,
          snap(nums, { pointers: { left, right } }), { left, right })
      );
    } else {
      right--;
      steps.push(
        step(steps.length, "Move right", `${s} > ${target} — need a smaller sum, so right moves to ${right}.`, 4,
          snap(nums, { pointers: { left, right } }), { left, right })
      );
    }
  }
  steps.push(
    step(steps.length, "No pair", `Pointers met with no match for ${target}.`, 4,
      snap(nums, { pointers: { left, right } }), { target }, { done: true })
  );
  return steps;
}

export const twoSumIIEntry: VisualizerEntry = {
  slug: "two-sum-ii-input-array-is-sorted",
  title: "Two Sum II",
  inputHint: "[2, 7, 11, 15], 9",
  defaultInput: "[2, 7, 11, 15], 9",
  presets: [
    { label: "Basic", value: "[2, 7, 11, 15], 9" },
    { label: "Ends", value: "[1, 2, 3, 4, 5], 9" },
    { label: "No pair", value: "[1, 2, 3], 7" },
  ],
  pseudocode: [
    "left = 0, right = n - 1",
    "while left < right: s = nums[left] + nums[right]",
    "    if s == target: return [left+1, right+1]",
    "    elif s < target: left += 1",
    "    else: right -= 1",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseTwoSumII(raw),
  generate: (input: unknown) => generateTwoSumII(input as TwoSumIIInput),
};
