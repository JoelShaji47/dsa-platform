import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface BinarySearchInput {
  nums: number[];
  target: number;
}

export function parseBinarySearch(raw: string): BinarySearchInput {
  const cleaned = raw.replace(/target/i, ",").trim();
  const bracket = cleaned.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [-1, 0, 3, 5, 9, 12], 9");
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 1 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error("Need a sorted array, e.g. [-1, 0, 3, 5, 9, 12], 9");
  }
  for (let k = 1; k < nums.length; k++) {
    if (nums[k] < nums[k - 1]) throw new Error("Array must be sorted ascending for binary search");
  }
  if (nums.length > 16) throw new Error("Keep it to 16 numbers so the trace stays readable");
  const rest = cleaned.slice(bracket[0].length).replace(/^,/, "").trim();
  if (!rest) throw new Error("Add a target after the array, e.g. [...], 9");
  const target = Number(rest);
  if (!Number.isFinite(target)) throw new Error("Add a target after the array, e.g. [...], 9");
  return { nums, target };
}

export function generateBinarySearch({ nums, target }: BinarySearchInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let lo = 0;
  let hi = nums.length - 1;
  steps.push(
    step(0, "Start", `Search for ${target} in a sorted array. Window is the whole array: low=0, high=${hi}.`, 0,
      snap(nums, { pointers: { low: lo, high: hi } }), { low: lo, high: hi, target })
  );
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    const outside = (k: number) => k < lo || k > hi;
    steps.push(
      step(steps.length, "Probe mid", `mid = (${lo} + ${hi}) ÷ 2 = ${mid}. nums[${mid}] = ${nums[mid]}.`, 1,
        snap(nums, {
          active: [mid],
          eliminated: nums.map((_, k) => k).filter(outside),
          pointers: { low: lo, mid, high: hi },
        }), { low: lo, mid, high: hi })
    );
    if (nums[mid] === target) {
      steps.push(
        step(steps.length, "Found", `nums[${mid}] = ${target}. Return ${mid}.`, 2,
          snap(nums, {
            active: [mid], settled: [mid],
            eliminated: nums.map((_, k) => k).filter(outside),
            pointers: { low: lo, mid, high: hi },
          }), { mid }, { result: `${mid}`, done: true })
      );
      return steps;
    }
    if (nums[mid] < target) {
      steps.push(
        step(steps.length, "Go right", `${nums[mid]} < ${target}, so everything at or left of ${mid} is out. low becomes ${mid + 1}.`, 3,
          snap(nums, {
            active: [mid],
            eliminated: nums.map((_, k) => k).filter((k) => outside(k) || k <= mid),
            pointers: { low: lo, mid, high: hi },
          }), { low: mid + 1, high: hi })
      );
      lo = mid + 1;
    } else {
      steps.push(
        step(steps.length, "Go left", `${nums[mid]} > ${target}, so everything at or right of ${mid} is out. high becomes ${mid - 1}.`, 4,
          snap(nums, {
            active: [mid],
            eliminated: nums.map((_, k) => k).filter((k) => outside(k) || k >= mid),
            pointers: { low: lo, mid, high: hi },
          }), { low: lo, high: mid - 1 })
      );
      hi = mid - 1;
    }
  }
  steps.push(
    step(steps.length, "Not found", `Window is empty (low > high) — ${target} is not in the array. Return -1.`, 5,
      snap(nums, { eliminated: nums.map((_, k) => k) }), { target }, { result: "-1", done: true })
  );
  return steps;
}

export const binarySearchEntry: VisualizerEntry = {
  slug: "binary-search",
  title: "Binary Search",
  inputHint: "[-1, 0, 3, 5, 9, 12], 9",
  defaultInput: "[-1, 0, 3, 5, 9, 12], 9",
  presets: [
    { label: "Found", value: "[-1, 0, 3, 5, 9, 12], 9" },
    { label: "Missing", value: "[-1, 0, 3, 5, 9, 12], 2" },
    { label: "First element", value: "[1, 2, 3, 4, 5], 1" },
  ],
  pseudocode: [
    "low = 0, high = n - 1",
    "while low <= high: mid = (low + high) // 2",
    "    if nums[mid] == target: return mid",
    "    elif nums[mid] < target: low = mid + 1",
    "    else: high = mid - 1",
    "return -1",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseBinarySearch(raw),
  generate: (input: unknown) => generateBinarySearch(input as BinarySearchInput),
};
