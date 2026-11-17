import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface KthLargestArrayInput {
  k: number;
  values: number[];
}

export function parseKthLargestArray(raw: string): KthLargestArrayInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n k, then n numbers");
  const header = integersFrom(lines[0]);
  if (header.length !== 2) throw new Error("The first line must be: n k");
  const [n, k] = header;
  const values = integersFrom(lines.slice(1).join(" "));
  if (values.length !== n) throw new Error(`Expected ${n} numbers`);
  if (k < 1 || k > n) throw new Error("k must be between 1 and n");
  if (n > 14) throw new Error("Keep it to 14 numbers");
  return { k, values };
}

export function generateKthLargestArray({ k, values }: KthLargestArrayInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const heap: number[] = [];

  const valuesSnap = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {}, label: "values" });
  const heapSnap = (active: number[] = []) =>
    snap(heap, { active, settled: heap.map((_, index) => index), label: `top-${k} min-heap` });

  const push = (value: number): number[] => {
    heap.push(value);
    let index = heap.length - 1;
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (heap[parent] <= heap[index]) break;
      [heap[parent], heap[index]] = [heap[index], heap[parent]];
      index = parent;
    }
    return [index];
  };

  const popRoot = (): number[] => {
    const last = heap.pop()!;
    if (heap.length === 0) return [];
    heap[0] = last;
    let index = 0;
    while (true) {
      const left = index * 2 + 1;
      const right = left + 1;
      let smallest = index;
      if (left < heap.length && heap[left] < heap[smallest]) smallest = left;
      if (right < heap.length && heap[right] < heap[smallest]) smallest = right;
      if (smallest === index) break;
      [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
      index = smallest;
    }
    return [index];
  };

  steps.push(
    step(0, "Start", `Keep a min-heap of the ${k} largest values; its root is the answer.`, 0, valuesSnap(), { k }, { arrayAlt: heapSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    const touched = push(values[i]);
    steps.push(
      step(
        steps.length,
        "Push",
        `Insert ${values[i]} into the heap.`,
        2,
        valuesSnap([i], Array.from({ length: i }, (_, index) => index)),
        { value: values[i], size: heap.length },
        { arrayAlt: heapSnap(touched) }
      )
    );

    if (heap.length > k) {
      const removed = heap[0];
      const touchedPop = popRoot();
      steps.push(
        step(
          steps.length,
          "Trim",
          `The heap has ${k + 1} values; remove the smallest (${removed}).`,
          3,
          valuesSnap([i], Array.from({ length: i }, (_, index) => index)),
          { removed, size: heap.length },
          { arrayAlt: heapSnap(touchedPop) }
        )
      );
    }
  }

  const result = heap[0];
  steps.push(
    step(
      steps.length,
      "Done",
      `The ${k}th largest value is ${result}.`,
      5,
      valuesSnap([], values.map((_, index) => index)),
      { kth: result },
      { arrayAlt: heapSnap(heap.map((_, index) => index)), done: true, result: String(result) }
    )
  );

  return steps;
}

export const kthLargestArrayEntry: VisualizerEntry = {
  slug: "kth-largest-element-in-an-array",
  title: "Kth Largest Element in an Array",
  inputHint: "n k, then n numbers",
  defaultInput: "6 2\n3 2 1 5 6 4",
  presets: [
    { label: "example", value: "6 2\n3 2 1 5 6 4" },
    { label: "single", value: "1 1\n1" },
    { label: "duplicates", value: "5 2\n3 3 1 2 4" },
  ],
  pseudocode: [
    "heap = empty min-heap",
    "for value in nums:",
    "  push value",
    "  if heap size > k: pop the minimum",
    "return heap root",
  ],
  parse: parseKthLargestArray,
  generate: (input) => generateKthLargestArray(input as KthLargestArrayInput),
};
