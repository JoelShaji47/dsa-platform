import {
  listFromValues,
  snap,
  snapList,
  step,
  type BaseStep,
  type LinkedListNode,
  type LinkedListSnapshot,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface RemoveNthInput {
  values: number[];
  n: number;
}

export function parseRemoveNth(raw: string): RemoveNthInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: list, then n");
  const values = integersFrom(lines[0]);
  const n = Number(lines[1]);
  if (values.length === 0) throw new Error("The list cannot be empty");
  if (values.length > 12) throw new Error("Keep it to 12 nodes");
  if (!Number.isInteger(n) || n < 1 || n > values.length) {
    throw new Error("n must be between 1 and the list length");
  }
  return { values, n };
}

export function generateRemoveNth({ values, n }: RemoveNthInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes: LinkedListNode[] = listFromValues(values);
  let head: number | null = nodes.length > 0 ? 0 : null;
  let fast: number | null = 0;
  let slow: number | null = 0;
  let prev: number | null = null;

  const snapshot = (
    active: number[] = [],
    settled: number[] = [],
    pointers: LinkedListSnapshot["pointers"] = {}
  ): LinkedListSnapshot => snapList(nodes, { head, active, settled, pointers });
  const arraySnap = (active: number[] = []) =>
    snap(values, {
      active,
      settled: Array.from({ length: active.length ? active[0] : 0 }, (_, index) => index),
      pointers: {},
      label: "values",
    });

  steps.push(
    step(0, "Start", `Move fast ${n} nodes ahead, then walk both pointers together.`, 0, arraySnap(), { n }, { linkedList: snapshot([], [], { slow: 0, fast: 0 }) })
  );

  for (let count = 0; count < n; count += 1) {
    if (fast != null) fast = nodes[fast].next;
    steps.push(
      step(
        steps.length,
        "Advance fast",
        `Move fast one node (${count + 1}/${n}).`,
        2,
        arraySnap(),
        { n, fast: fast ?? "null" },
        { linkedList: snapshot([], [], { slow: 0, fast: fast ?? undefined }) }
      )
    );
  }

  while (fast != null && slow != null) {
    prev = slow;
    slow = nodes[slow].next;
    fast = nodes[fast].next;
    steps.push(
      step(
        steps.length,
        "Move both",
        "Advance slow and fast until fast falls off the end.",
        3,
        arraySnap(),
        { slow: slow ?? "null", fast: fast ?? "null" },
        {
          linkedList: snapshot(
            [slow ?? prev ?? 0],
            prev == null ? [] : [prev],
            { slow: slow ?? undefined, fast: fast ?? undefined, prev: prev ?? undefined }
          ),
        }
      )
    );
  }

  if (slow == null) {
    steps.push(
      step(steps.length, "Missing", "No node to remove.", 4, arraySnap(), { n }, { linkedList: snapshot() })
    );
    return steps;
  }

  const removedIndex = slow;
  const removed = nodes[removedIndex];
  if (prev == null) {
    head = removed.next;
  } else {
    nodes[prev].next = removed.next;
  }

  steps.push(
    step(
      steps.length,
      "Remove",
      `Remove ${removed.value}, the ${n}${n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th"} node from the end.`,
      4,
      arraySnap([removedIndex]),
      { removed: removed.value },
      {
        linkedList: snapshot([], removed.next == null ? [prev ?? removedIndex] : [prev ?? removedIndex], {
          prev: prev ?? undefined,
        }),
      }
    )
  );

  const result = values.filter((_, index) => index !== removedIndex);
  steps.push(
    step(
      steps.length,
      "Done",
      `The list is now ${result.join(" ")}.`,
      5,
      arraySnap(),
      { n },
      {
        linkedList: snapshot([], nodes.map((_, index) => index)),
        done: true,
        result: result.join(" "),
      }
    )
  );

  return steps;
}

export const removeNthNodeEntry: VisualizerEntry = {
  slug: "remove-nth-node-from-end-of-list",
  title: "Remove Nth Node From End of List",
  inputHint: "list, then n",
  defaultInput: "1 2 3 4 5\n2",
  presets: [
    { label: "example", value: "1 2 3 4 5\n2" },
    { label: "head", value: "1 2\n2" },
    { label: "single", value: "7\n1" },
  ],
  pseudocode: [
    "fast = head",
    "advance fast n times",
    "slow = head, prev = null",
    "while fast: prev = slow; slow = slow.next; fast = fast.next",
    "remove slow (or update head if prev is null)",
    "return head",
  ],
  parse: parseRemoveNth,
  generate: (input) => generateRemoveNth(input as RemoveNthInput),
};
