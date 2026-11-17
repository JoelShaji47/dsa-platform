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

export interface ReorderListInput {
  values: number[];
}

export function parseReorderList(raw: string): ReorderListInput {
  const lines = inputLines(raw);
  const values = integersFrom(lines[0] ?? "");
  if (values.length === 0) throw new Error("Enter at least one value");
  if (values.length > 12) throw new Error("Keep it to 12 nodes");
  return { values };
}

function walk(nodes: LinkedListNode[], head: number | null): number[] {
  const out: number[] = [];
  let node = head;
  const seen = new Set<number>();
  while (node != null && !seen.has(node)) {
    seen.add(node);
    out.push(node);
    node = nodes[node].next;
  }
  return out;
}

export function generateReorderList({ values }: ReorderListInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = listFromValues(values);
  let head: number | null = nodes.length > 0 ? 0 : null;

  const snapshot = (
    active: number[] = [],
    settled: number[] = [],
    pointers: LinkedListSnapshot["pointers"] = {}
  ) => snapList(nodes, { head, active, settled, pointers });

  steps.push(
    step(0, "Start", "Reorder the list as first, last, second, second-last, and so on.", 0, snap([]), { length: values.length }, { linkedList: snapshot() })
  );

  let slow = head;
  let fast = head;
  while (fast != null && nodes[fast].next != null && nodes[nodes[fast].next!].next != null) {
    slow = nodes[slow!].next;
    fast = nodes[nodes[fast].next!].next;
  }

  const splitAfter = slow!;
  let second = nodes[splitAfter].next;
  steps.push(
    step(
      steps.length,
      "Split",
      `Cut the list after the middle node; the second half starts at ${second == null ? "null" : nodes[second].value}.`,
      1,
      snap([]),
      { second: second == null ? "null" : nodes[second].value },
      { linkedList: snapshot([slow!], [], { slow: slow ?? undefined, fast: fast ?? undefined }) }
    )
  );

  if (second != null) {
    nodes[splitAfter].next = null;
    let prev: number | null = null;
    let curr: number | null = second;
    while (curr != null) {
      const next: number | null = nodes[curr].next;
      nodes[curr].next = prev;
      prev = curr;
      curr = next;
    }
    second = prev;
    steps.push(
      step(
        steps.length,
        "Reverse",
        "Reverse the detached second half so its last node comes first.",
        2,
        snap([]),
        { secondStart: second == null ? "null" : nodes[second].value },
        { linkedList: snapshot(second == null ? [] : [second], [], { prev: prev ?? undefined }) }
      )
    );
  }

  let first = head;
  while (second != null) {
    const firstNext = first == null ? null : nodes[first].next;
    const secondNext = nodes[second].next;
    if (first != null) nodes[first].next = second;
    nodes[second].next = firstNext;
    steps.push(
      step(
        steps.length,
        "Weave",
        `Link ${first == null ? "null" : nodes[first].value} to ${nodes[second].value}, then continue with the remaining halves.`,
        4,
        snap([]),
        { a: first ?? "null", b: second },
        {
          linkedList: snapshot(
            [first ?? second, second].filter((id): id is number => id != null)
          ),
        }
      )
    );
    first = firstNext;
    second = secondNext;
  }

  const order = walk(nodes, head);
  const result = order.map((id) => nodes[id].value).join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `The reordered list is ${result}.`,
      5,
      snap([]),
      { length: order.length },
      { linkedList: snapshot([], order), done: true, result }
    )
  );

  return steps;
}

export const reorderListEntry: VisualizerEntry = {
  slug: "reorder-list",
  title: "Reorder List",
  inputHint: "a single linked list",
  defaultInput: "1 2 3 4",
  presets: [
    { label: "even", value: "1 2 3 4" },
    { label: "odd", value: "1 2 3 4 5" },
    { label: "single", value: "1" },
  ],
  pseudocode: [
    "find the middle with slow/fast pointers",
    "reverse the second half",
    "weave nodes from the first and second halves",
    "return the reordered list",
  ],
  parse: parseReorderList,
  generate: (input) => generateReorderList(input as ReorderListInput),
};
