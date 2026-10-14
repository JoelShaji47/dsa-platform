import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface ThreeSumInput {
  nums: number[];
}

export function parseThreeSum(raw: string): ThreeSumInput {
  const bracket = raw.trim().match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [-1, 0, 1, 2, -1, -4]");
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 3 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error("Need at least 3 numbers, e.g. [-1, 0, 1, 2, -1, -4]");
  }
  if (nums.length > 9) throw new Error("Keep it to 9 numbers so the trace stays readable");
  return { nums };
}

export function generateThreeSum({ nums }: ThreeSumInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const a = [...nums].sort((x, y) => x - y);
  const found: number[][] = [];
  steps.push(
    step(0, "Sort", `Sort first: [${a.join(", ")}]. Then fix one element and two-pointer the rest.`, 0,
      snap(a, {}), {})
  );
  for (let i = 0; i < a.length - 2; i++) {
    if (i > 0 && a[i] === a[i - 1]) {
      steps.push(
        step(steps.length, "Skip duplicate", `a[${i}] = ${a[i]} repeats a[${i - 1}] — same triplets would repeat. Skip.`, 1,
          snap(a, { active: [i] }), { i })
      );
      continue;
    }
    let left = i + 1;
    let right = a.length - 1;
    steps.push(
      step(steps.length, "Fix i", `Fix a[${i}] = ${a[i]}. Need a pair summing to ${-a[i]} in the rest.`, 1,
        snap(a, { active: [i], pointers: { i, left, right } }), { i, left, right, need: -a[i] })
    );
    while (left < right) {
      const s = a[i] + a[left] + a[right];
      steps.push(
        step(steps.length, "Compare", `${a[i]} + ${a[left]} + ${a[right]} = ${s}.`, 2,
          snap(a, { active: [i, left, right], pointers: { i, left, right } }), { sum: s })
      );
      if (s === 0) {
        found.push([a[i], a[left], a[right]]);
        steps.push(
          step(steps.length, "Triplet", `Triplet [${a[i]}, ${a[left]}, ${a[right]}] — record it and shrink both sides past duplicates.`, 3,
            snap(a, { active: [i, left, right], settled: [i, left, right], pointers: { i, left, right } }),
            { found: found.length }, { result: found.map((t) => `[${t.join(", ")}]`).join(" ") })
        );
        const lv = a[left];
        const rv = a[right];
        while (left < right && a[left] === lv) left++;
        while (left <= right && a[right] === rv) right--;
      } else if (s < 0) {
        left++;
        steps.push(
          step(steps.length, "Move left", `${s} < 0 — need bigger. left → ${left}.`, 4,
            snap(a, { active: [i], pointers: { i, left, right } }), { i, left, right })
        );
      } else {
        right--;
        steps.push(
          step(steps.length, "Move right", `${s} > 0 — need smaller. right → ${right}.`, 4,
            snap(a, { active: [i], pointers: { i, left, right } }), { i, left, right })
        );
      }
    }
  }
  steps.push(
    step(steps.length, "Done", found.length ? `${found.length} unique triplet${found.length > 1 ? "s" : ""} found.` : "No triplet sums to zero.",
      5, snap(a, {}), { found: found.length },
      { result: found.length ? found.map((t) => `[${t.join(", ")}]`).join(" ") : "[]", done: true })
  );
  return steps;
}

export const threeSumEntry: VisualizerEntry = {
  slug: "3sum",
  title: "3Sum",
  inputHint: "[-1, 0, 1, 2, -1, -4]",
  defaultInput: "[-1, 0, 1, 2, -1, -4]",
  presets: [
    { label: "Classic", value: "[-1, 0, 1, 2, -1, -4]" },
    { label: "Zeros", value: "[0, 0, 0]" },
    { label: "None", value: "[1, 2, 3]" },
  ],
  pseudocode: [
    "sort(nums)",
    "for i in range(n-2): skip duplicate a[i]",
    "    two-pointer (left, right) for sum == -a[i]",
    "    on hit: record, skip dup left/right values",
    "return triplets",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseThreeSum(raw),
  generate: (input: unknown) => generateThreeSum(input as ThreeSumInput),
};
