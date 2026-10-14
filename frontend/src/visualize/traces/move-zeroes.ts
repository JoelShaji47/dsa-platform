import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface MoveZeroesInput {
  nums: number[];
}

export function parseMoveZeroes(raw: string): MoveZeroesInput {
  const bracket = raw.trim().match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [0, 1, 0, 3, 12]");
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 1 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error("Need at least 1 number, e.g. [0, 1, 0, 3, 12]");
  }
  if (nums.length > 12) throw new Error("Keep it to 12 numbers so the trace stays readable");
  return { nums };
}

export function generateMoveZeroes({ nums }: MoveZeroesInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const a = [...nums];
  let j = 0; // next slot for a non-zero
  steps.push(
    step(0, "Start", "Keep relative order and push every non-zero forward. j marks where the next non-zero goes.", 0,
      snap(a, { pointers: { i: 0, j } }), { i: 0, j })
  );
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== 0) {
      if (i !== j) {
        steps.push(
          step(steps.length, "Swap", `nums[${i}] = ${a[i]} is non-zero — swap it into slot ${j}.`, 1,
            snap(a, { active: [i, j], pointers: { i, j } }), { i, j })
        );
        [a[i], a[j]] = [a[j], a[i]];
      } else {
        steps.push(
          step(steps.length, "Keep", `nums[${i}] = ${a[i]} is already in place (i == j).`, 1,
            snap(a, { active: [i], pointers: { i, j } }), { i, j })
        );
      }
      j++;
      steps.push(
        step(steps.length, "Advance j", `Slot ${j - 1} is settled. j moves to ${j}.`, 2,
          snap(a, { settled: a.map((_, k) => k).filter((k) => k < j), pointers: { i, j } }), { i, j })
      );
    } else {
      steps.push(
        step(steps.length, "Skip zero", `nums[${i}] is zero — leave it, i moves on.`, 3,
          snap(a, { active: [i], settled: a.map((_, k) => k).filter((k) => k < j), pointers: { i, j } }), { i, j })
      );
    }
  }
  steps.push(
    step(steps.length, "Done", `All non-zeroes are front-loaded in order: [${a.join(", ")}].`, 4,
      snap(a, { settled: a.map((_, k) => k) }), {}, { result: `[${a.join(", ")}]`, done: true })
  );
  return steps;
}

export const moveZeroesEntry: VisualizerEntry = {
  slug: "move-zeroes",
  title: "Move Zeroes",
  inputHint: "[0, 1, 0, 3, 12]",
  defaultInput: "[0, 1, 0, 3, 12]",
  presets: [
    { label: "Mixed", value: "[0, 1, 0, 3, 12]" },
    { label: "All zeros", value: "[0, 0, 0]" },
    { label: "No zeros", value: "[1, 2, 3]" },
  ],
  pseudocode: [
    "j = 0  // next slot for a non-zero",
    "for i in range(n): if nums[i] != 0: swap(nums[i], nums[j]); j += 1",
    "// (swap shown for clarity; same-slot writes are no-ops)",
    "zeros collect at the end",
    "relative order preserved",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseMoveZeroes(raw),
  generate: (input: unknown) => generateMoveZeroes(input as MoveZeroesInput),
};
