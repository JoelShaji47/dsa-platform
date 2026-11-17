import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface TopKFrequentInput {
  k: number;
  values: number[];
}

interface Counted {
  value: number;
  count: number;
}

export function parseTopKFrequent(raw: string): TopKFrequentInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n k, then n numbers");
  const header = integersFrom(lines[0]);
  if (header.length !== 2) throw new Error("The first line must be: n k");
  const [n, k] = header;
  const values = integersFrom(lines.slice(1).join(" "));
  if (values.length !== n) throw new Error(`Expected ${n} numbers, received ${values.length}`);
  if (n < 1 || n > 14) throw new Error("Keep it to 14 numbers");
  if (k < 1 || k > new Set(values).size) {
    throw new Error("k must be between 1 and the number of distinct values");
  }
  return { k, values };
}

function heapLabels(heap: Counted[]): string[] {
  return heap.map((item) => `${item.value}×${item.count}`);
}

export function generateTopKFrequent({ k, values }: TopKFrequentInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const counts = new Map<number, number>();
  const heap: Counted[] = [];

  const original = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {} });
  const heapSnap = (active: number[] = [], settled: number[] = []) =>
    snap(heapLabels(heap), {
      active,
      settled,
      pointers: active.length > 0 ? { i: active[0] } : {},
      label: "min-heap by frequency",
    });

  const push = (item: Counted): number[] => {
    heap.push(item);
    let index = heap.length - 1;
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (heap[parent].count <= heap[index].count) break;
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
      if (left < heap.length && heap[left].count < heap[smallest].count) smallest = left;
      if (right < heap.length && heap[right].count < heap[smallest].count) smallest = right;
      if (smallest === index) break;
      [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
      index = smallest;
    }
    return [index];
  };

  steps.push(
    step(0, "Start", `Find the ${k} most frequent values.`, 0, original(), { k }, { arrayAlt: heapSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    const value = values[i];
    const next = (counts.get(value) ?? 0) + 1;
    counts.set(value, next);
    steps.push(
      step(
        steps.length,
        "Count",
        `Count ${value}: it now appears ${next} time${next === 1 ? "" : "s"}.`,
        1,
        original([i]),
        { value, count: next },
        { arrayAlt: heapSnap() }
      )
    );

    const existing = heap.findIndex((item) => item.value === value);
    if (existing >= 0) {
      heap[existing].count = next;
      let index = existing;
      while (index > 0) {
        const parent = Math.floor((index - 1) / 2);
        if (heap[parent].count <= heap[index].count) break;
        [heap[parent], heap[index]] = [heap[index], heap[parent]];
        index = parent;
      }
      steps.push(
        step(
          steps.length,
          "Update",
          `${value} is already in the heap; increase its frequency to ${next}.`,
          3,
          original([i]),
          { heap: heap.length },
          { arrayAlt: heapSnap([index]) }
        )
      );
      continue;
    }

    const touched = push({ value, count: next });
    steps.push(
      step(
        steps.length,
        "Push",
        `Add ${value}×${next} to the min-heap.`,
        3,
        original([i]),
        { heap: heap.length },
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
          `The heap has ${k + 1} entries; remove the least frequent, ${removed.value}×${removed.count}.`,
          4,
          original([i]),
          { heap: heap.length },
          { arrayAlt: heapSnap(touchedPop) }
        )
      );
    }
  }

  const result = [...heap]
    .map((item) => item.value)
    .sort((a, b) => a - b);
  steps.push(
    step(
      steps.length,
      "Done",
      `The top ${k} values are ${result.join(", ")}.`,
      5,
      original([], values.map((_, index) => index)),
      { k },
      { arrayAlt: heapSnap([], heap.map((_, index) => index)), done: true, result: result.join(" ") }
    )
  );

  return steps;
}

export const topKFrequentEntry: VisualizerEntry = {
  slug: "top-k-frequent-elements",
  title: "Top K Frequent Elements",
  inputHint: "n k, then n numbers",
  defaultInput: "6 2\n1 1 1 2 2 3",
  presets: [
    { label: "example", value: "6 2\n1 1 1 2 2 3" },
    { label: "all unique", value: "3 2\n4 7 9" },
    { label: "single", value: "1 1\n5" },
  ],
  pseudocode: [
    "count = frequency map",
    "heap = min-heap by frequency",
    "for each value:",
    "  push or update value in heap",
    "  if heap.size > k: pop least frequent",
    "return heap values",
  ],
  parse: parseTopKFrequent,
  generate: (input) => generateTopKFrequent(input as TopKFrequentInput),
};
