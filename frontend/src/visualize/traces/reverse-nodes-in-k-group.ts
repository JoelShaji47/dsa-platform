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

export interface ReverseKGroupInput {
  values: number[];
  k: number;
}

export function parseReverseKGroup(raw: string): ReverseKGroupInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: list, then k");
  const values = integersFrom(lines[0]);
  const k = Number(lines[1]);
  if (values.length === 0) throw new Error("The list cannot be empty");
  if (values.length > 12) throw new Error("Keep it to 12 nodes");
  if (!Number.isInteger(k) || k < 1) throw new Error("k must be a positive integer");
  return { values, k };
}

function walk(nodes: LinkedListNode[], head: number | null): number[] {
  const order: number[] = [];
  const seen = new Set<number>();
  let node = head;
  while (node != null && !seen.has(node)) {
    seen.add(node);
    order.push(node);
    node = nodes[node].next;
  }
  return order;
}

export function generateReverseKGroup({ values, k }: ReverseKGroupInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = listFromValues(values);
  let head: number | null = nodes.length > 0 ? 0 : null;
  let curr: number | null = head;
  let previousGroupTail: number | null = null;

  const snapshot = (
    active: number[] = [],
    settled: number[] = [],
    pointers: LinkedListSnapshot["pointers"] = {}
  ) => snapList(nodes, { head, active, settled, pointers });

  steps.push(
    step(0, "Start", `Reverse the list in groups of ${k}; leave any leftover suffix in place.`, 0, snap([]), { k }, { linkedList: snapshot([], [], { curr: head ?? undefined }) })
  );

  while (curr != null) {
    let groupEnd: number | null = curr;
    for (let i = 1; i < k && groupEnd != null; i += 1) groupEnd = nodes[groupEnd].next;

    if (groupEnd == null) {
      steps.push(
        step(
          steps.length,
          "Leftover",
          `Fewer than ${k} nodes remain; keep them in the original order.`,
          1,
          snap([]),
          { curr: curr == null ? "null" : nodes[curr].value },
          { linkedList: snapshot(curr == null ? [] : [curr], []) }
        )
      );
      break;
    }

    const groupNext = nodes[groupEnd].next;
    let prev: number | null = groupNext;
    let node: number | null = curr;
    const groupIds: number[] = [];
    while (node != null && node !== groupNext) {
      groupIds.push(node);
      const next: number | null = nodes[node].next;
      nodes[node].next = prev;
      prev = node;
      node = next;
    }

    const newGroupHead = prev;
    if (previousGroupTail == null) head = newGroupHead;
    else nodes[previousGroupTail].next = newGroupHead;
    previousGroupTail = curr;
    curr = groupNext;

    steps.push(
      step(
        steps.length,
        "Reverse group",
        `Reverse nodes ${groupIds.map((id) => nodes[id].value).join(" → ")} into ${groupIds
          .slice()
          .reverse()
          .map((id) => nodes[id].value)
          .join(" → ")}.`,
        3,
        snap([]),
        { group: groupIds.length, k },
        {
          linkedList: snapshot(groupIds, [], {
            prev: prev ?? undefined,
            curr: curr ?? undefined,
          }),
        }
      )
    );
  }

  const order = walk(nodes, head);
  const result = order.map((id) => nodes[id].value).join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `The reordered list is ${result}.`,
      4,
      snap([]),
      { k },
      { linkedList: snapshot([], order), done: true, result }
    )
  );

  return steps;
}

export const reverseKGroupEntry: VisualizerEntry = {
  slug: "reverse-nodes-in-k-group",
  title: "Reverse Nodes in k-Group",
  inputHint: "list, then k",
  defaultInput: "1 2 3 4 5\n2",
  presets: [
    { label: "k=2", value: "1 2 3 4 5\n2" },
    { label: "k=3", value: "1 2 3 4 5\n3" },
    { label: "k=1", value: "1 2 3\n1" },
  ],
  pseudocode: [
    "curr = head",
    "while curr:",
    "  find the kth node; stop if fewer than k remain",
    "  reverse the next k links",
    "  connect the reversed group to the previous group",
    "return head",
  ],
  parse: parseReverseKGroup,
  generate: (input) => generateReverseKGroup(input as ReverseKGroupInput),
};
