import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface KthLargestStreamInput {
  k: number;
  initial: number[];
  additions: number[];
}

export function parseKthLargestStream(raw: string): KthLargestStreamInput {
  const lines = inputLines(raw);
  if (lines.length < 4) throw new Error("Use: k n, n numbers, m, then m additions");
  const header = integersFrom(lines[0]);
  if (header.length !== 2) throw new Error("The first line must be: k n");
  const [k, n] = header;
  const initial = integersFrom(lines[1]);
  const m = Number(lines[2]);
  const additions = integersFrom(lines.slice(3).join(" "));
  if (initial.length !== n) throw new Error(`Expected ${n} initial numbers`);
  if (!Number.isInteger(m) || additions.length !== m) throw new Error("Addition count does not match");
  if (k < 1 || n < k - 1) throw new Error("The stream must have at least k - 1 initial values");
  if (n + m > 16) throw new Error("Keep the total stream to 16 values");
  return { k, initial, additions };
}

export function generateKthLargestStream({ k, initial, additions }: KthLargestStreamInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const heap: number[] = [];
  const outputs: number[] = [];

  const heapSnap = (active: number[] = []) =>
    snap(heap, { active, settled: heap.map((_, index) => index), label: `min-heap (k=${k})` });
  const outputSnap = () => snap(outputs, { label: "outputs" });

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
    step(0, "Start", `Maintain the ${k} largest values in a min-heap; the root is the kth largest.`, 0, heapSnap(), { k }, { arrayAlt: outputSnap() })
  );

  for (let i = 0; i < initial.length; i += 1) {
    const touched = push(initial[i]);
    if (heap.length > k) popRoot();
    steps.push(
      step(
        steps.length,
        "Initialize",
        `Insert ${initial[i]} and keep only the top ${k}.`,
        2,
        heapSnap(touched),
        { value: initial[i], size: heap.length },
        { arrayAlt: outputSnap() }
      )
    );
  }

  for (let i = 0; i < additions.length; i += 1) {
    const value = additions[i];
    const touched = push(value);
    if (heap.length > k) popRoot();
    outputs.push(heap[0]);
    steps.push(
      step(
        steps.length,
        "Add",
        `Add ${value}; the ${k}th largest is ${heap[0]}.`,
        4,
        heapSnap(touched),
        { value, kth: heap[0] },
        { arrayAlt: outputSnap() }
      )
    );
  }

  const result = outputs.join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `After each addition the kth largest values are ${result}.`,
      5,
      heapSnap(heap.map((_, index) => index)),
      { k },
      { arrayAlt: outputSnap(), done: true, result }
    )
  );

  return steps;
}

export const kthLargestStreamEntry: VisualizerEntry = {
  slug: "kth-largest-element-in-a-stream",
  title: "Kth Largest Element in a Stream",
  inputHint: "k n, n initial values, m, then m additions",
  defaultInput: "3 4\n4 5 8 2\n3\n3\n5\n10",
  presets: [
    { label: "example", value: "3 4\n4 5 8 2\n3\n3\n5\n10" },
    { label: "k=1", value: "1 1\n5\n2\n2\n3" },
    { label: "k=n", value: "3 3\n1 2 3\n2\n4\n5" },
  ],
  pseudocode: [
    "heap = min-heap of the largest k values",
    "for value in initial stream:",
    "  push value; if size > k: pop the minimum",
    "for value in additions:",
    "  push value; if size > k: pop the minimum",
    "  record heap[0]",
  ],
  parse: parseKthLargestStream,
  generate: (input) => generateKthLargestStream(input as KthLargestStreamInput),
};
