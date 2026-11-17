import {
  snap,
  snapList,
  step,
  type BaseStep,
  type LinkedListNode,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface MergeKListsInput {
  lists: number[][];
}

interface HeapItem {
  value: number;
  list: number;
  position: number;
}

export function parseMergeKLists(raw: string): MergeKListsInput {
  const lines = inputLines(raw);
  if (lines.length < 1) throw new Error("Use: k, then a length/list pair per list");
  const k = Number(lines[0]);
  if (!Number.isInteger(k) || k < 1) throw new Error("k must be a positive integer");
  const lists: number[][] = [];
  let cursor = 1;
  for (let i = 0; i < k; i += 1) {
    if (cursor >= lines.length) throw new Error(`Missing length for list ${i + 1}`);
    const length = Number(lines[cursor]);
    cursor += 1;
    if (!Number.isInteger(length) || length < 0) throw new Error(`Invalid length for list ${i + 1}`);
    if (length === 0) {
      lists.push([]);
      continue;
    }
    if (cursor >= lines.length) throw new Error(`Missing values for list ${i + 1}`);
    const values = integersFrom(lines[cursor]);
    cursor += 1;
    if (values.length !== length) throw new Error(`List ${i + 1} has the wrong number of values`);
    lists.push([...values].sort((a, b) => a - b));
  }
  if (lists.reduce((total, list) => total + list.length, 0) > 14) {
    throw new Error("Keep the total number of nodes to 14");
  }
  return { lists };
}

function heapLabels(heap: HeapItem[]): string[] {
  return heap.map((item) => `${item.value}@L${item.list + 1}`);
}

export function generateMergeKLists({ lists }: MergeKListsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const merged: LinkedListNode[] = [];
  let lastNode: number | null = null;
  const positions = lists.map(() => 0);
  const heap: HeapItem[] = [];

  const push = (item: HeapItem) => {
    heap.push(item);
    let index = heap.length - 1;
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (heap[parent].value <= heap[index].value) break;
      [heap[parent], heap[index]] = [heap[index], heap[parent]];
      index = parent;
    }
  };

  const pop = (): HeapItem => {
    const root = heap[0];
    const last = heap.pop()!;
    if (heap.length > 0) {
      heap[0] = last;
      let index = 0;
      while (true) {
        const left = index * 2 + 1;
        const right = left + 1;
        let smallest = index;
        if (left < heap.length && heap[left].value < heap[smallest].value) smallest = left;
        if (right < heap.length && heap[right].value < heap[smallest].value) smallest = right;
        if (smallest === index) break;
        [heap[index], heap[smallest]] = [heap[smallest], heap[index]];
        index = smallest;
      }
    }
    return root;
  };

  const mergedSnap = (active: number[] = []) =>
    snapList(merged, {
      active,
      settled: merged.map((_, index) => index).filter((index) => !active.includes(index)),
      label: "merged",
    });
  const headsSnap = (active: number[] = []) =>
    snap(
      lists.map((list, index) => list[positions[index]] ?? "—"),
      { active, label: "current heads" }
    );
  const heapSnap = () => snap(heapLabels(heap), { label: "min-heap" });

  steps.push(
    step(
      0,
      "Start",
      `Merge ${lists.length} sorted lists by repeatedly taking the smallest head.`,
      0,
      headsSnap(),
      { k: lists.length },
      { linkedList: mergedSnap(), arrayAlt: heapSnap() }
    )
  );

  lists.forEach((list, index) => {
    if (list.length > 0) push({ value: list[0], list: index, position: 0 });
  });

  steps.push(
    step(
      steps.length,
      "Seed heap",
      "Insert the first node from every non-empty list.",
      1,
      headsSnap(),
      { heap: heap.length },
      { linkedList: mergedSnap(), arrayAlt: heapSnap() }
    )
  );

  while (heap.length > 0) {
    const item = pop();
    const id = merged.length;
    merged.push({ id, value: item.value, next: null });
    if (lastNode != null) merged[lastNode].next = id;
    lastNode = id;
    positions[item.list] += 1;

    steps.push(
      step(
        steps.length,
        "Take min",
        `Take ${item.value} from list ${item.list + 1} and append it to the merged list.`,
        3,
        headsSnap([item.list]),
        { value: item.value, list: item.list + 1 },
        { linkedList: mergedSnap([id]), arrayAlt: heapSnap() }
      )
    );

    const nextPosition = positions[item.list];
    if (nextPosition < lists[item.list].length) {
      push({
        value: lists[item.list][nextPosition],
        list: item.list,
        position: nextPosition,
      });
      steps.push(
        step(
          steps.length,
          "Refill",
          `Push the next value from list ${item.list + 1} into the heap.`,
          4,
          headsSnap([item.list]),
          { value: lists[item.list][nextPosition], list: item.list + 1 },
          { linkedList: mergedSnap([id]), arrayAlt: heapSnap() }
        )
      );
    }
  }

  const result = merged.map((node) => node.value).join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `The merged list is ${result}.`,
      5,
      headsSnap(),
      { nodes: merged.length },
      {
        linkedList: mergedSnap(merged.map((_, index) => index)),
        arrayAlt: heapSnap(),
        done: true,
        result,
      }
    )
  );

  return steps;
}

export const mergeKSortedListsEntry: VisualizerEntry = {
  slug: "merge-k-sorted-lists",
  title: "Merge k Sorted Lists",
  inputHint: "k, then a length and values for each list",
  defaultInput: "3\n2\n1 4\n3\n2 5 3\n2\n6 0",
  presets: [
    { label: "example", value: "3\n2\n1 4\n3\n2 5 3\n2\n6 0" },
    { label: "one list", value: "1\n3\n1 2 3" },
    { label: "empty", value: "2\n0\n2\n1 2" },
  ],
  pseudocode: [
    "heap = first node of each list",
    "while heap is not empty:",
    "  pop the smallest node and append it",
    "  push the next node from that same list",
    "return the merged list",
  ],
  parse: parseMergeKLists,
  generate: (input) => generateMergeKLists(input as MergeKListsInput),
};
