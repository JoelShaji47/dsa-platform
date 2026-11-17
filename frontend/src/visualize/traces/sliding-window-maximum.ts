import { snap, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface SlidingWindowMaximumInput {
  nums: number[];
  k: number;
}

export function parseSlidingWindowMaximum(raw: string): SlidingWindowMaximumInput {
  const bracket = raw.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [1, 3, -1, -3, 5, 3, 6, 7], 3");
  const nums = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (nums.length < 1 || nums.some((n) => !Number.isFinite(n))) {
    throw new Error("Need a non-empty numeric array, e.g. [1, 3, -1, -3, 5, 3, 6, 7], 3");
  }
  if (nums.length > 12) throw new Error("Keep it to 12 numbers so the trace stays readable");
  const close = raw.indexOf("]", raw.indexOf("["));
  const rest = raw.slice(close + 1).replace(/^,/, "").trim();
  if (!rest) throw new Error("Add a window size after the array, e.g. [...], 3");
  const k = Number(rest);
  if (!Number.isInteger(k) || k < 1 || k > nums.length) {
    throw new Error("Window size k must be an integer between 1 and the array length");
  }
  return { nums, k };
}

export function generateSlidingWindowMaximum({ nums, k }: SlidingWindowMaximumInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const deq: number[] = [];
  const out: number[] = [];
  const window = (i: number) => {
    const start = Math.max(0, i - k + 1);
    return Array.from({ length: i - start + 1 }, (_, offset) => start + offset);
  };
  const queueSnap = (active: number[] = []) =>
    snapQueue(deq, { active, label: "deque (indices)" });

  steps.push(
    step(
      0,
      "Start",
      `Slide a window of size ${k}. The deque keeps indices whose values decrease from front to back.`,
      0,
      snap(nums),
      { k },
      { queue: queueSnap() }
    )
  );

  for (let i = 0; i < nums.length; i++) {
    const expired: number[] = [];
    while (deq.length > 0 && deq[0] <= i - k) expired.push(deq.shift()!);
    if (expired.length > 0) {
      steps.push(
        step(
          steps.length,
          "Expire front",
          `Index ${expired.join(", ")} left the window — drop it from the front.`,
          2,
          snap(nums, { active: window(i), pointers: { i } }),
          { i, removed: expired.join(", ") },
          { queue: queueSnap(deq.length > 0 ? [0] : []) }
        )
      );
    }

    const popped: number[] = [];
    while (deq.length > 0 && nums[deq[deq.length - 1]] <= nums[i]) {
      popped.push(deq.pop()!);
    }
    if (popped.length > 0) {
      steps.push(
        step(
          steps.length,
          "Pop back",
          `nums[${i}] = ${nums[i]} is at least as large as the back — those indices can never be a maximum again.`,
          3,
          snap(nums, { active: window(i), pointers: { i } }),
          { i, removed: popped.join(", ") },
          { queue: queueSnap(deq.length > 0 ? [deq.length - 1] : []) }
        )
      );
    }

    deq.push(i);
    steps.push(
      step(
        steps.length,
        "Push",
        `Push index ${i} (${nums[i]}) at the back.`,
        4,
        snap(nums, { active: window(i), pointers: { i } }),
        { i, deque: deq.join(", ") },
        { queue: queueSnap([deq.length - 1]) }
      )
    );

    if (i >= k - 1) {
      const max = nums[deq[0]];
      out.push(max);
      steps.push(
        step(
          steps.length,
          "Record max",
          `Window ${window(i).join("–")} is full. The front index ${deq[0]} holds the maximum: ${max}.`,
          5,
          snap(nums, {
            active: window(i),
            settled: Array.from({ length: i - k + 1 }, (_, offset) => offset),
            pointers: { i },
          }),
          { i, max, out: out.join(", ") },
          { queue: queueSnap([0]) }
        )
      );
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `Every window's maximum is recorded. Result: [${out.join(", ")}].`,
      6,
      snap(nums, { settled: nums.map((_, k) => k) }),
      { out: out.join(", ") },
      { queue: queueSnap(), result: `[${out.join(", ")}]`, done: true }
    )
  );
  return steps;
}

export const slidingWindowMaximumEntry: VisualizerEntry = {
  slug: "sliding-window-maximum",
  title: "Sliding Window Maximum",
  inputHint: "[1, 3, -1, -3, 5, 3, 6, 7], 3",
  defaultInput: "[1, 3, -1, -3, 5, 3, 6, 7], 3",
  presets: [
    { label: "Classic", value: "[1, 3, -1, -3, 5, 3, 6, 7], 3" },
    { label: "k = 1", value: "[9, 7, 5], 1" },
    { label: "Falling", value: "[7, 6, 5, 4], 2" },
  ],
  pseudocode: [
    "deque = []  # indices, values decreasing",
    "for i, x in enumerate(nums):",
    "    while deque and deque[0] <= i - k: deque.popleft()",
    "    while deque and nums[deque[-1]] <= x: deque.pop()",
    "    deque.append(i)",
    "    if i >= k - 1: ans.append(nums[deque[0]])",
    "return ans",
  ],
  parse: (raw: string) => parseSlidingWindowMaximum(raw),
  generate: (input: unknown) => generateSlidingWindowMaximum(input as SlidingWindowMaximumInput),
};
