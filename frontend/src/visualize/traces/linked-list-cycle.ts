import {
  listFromValues,
  snap,
  snapList,
  step,
  type BaseStep,
  type ListPointerName,
  type VisualizerEntry,
} from "../trace-types";

export interface LinkedListCycleInput {
  values: number[];
  pos: number;
}

export function parseLinkedListCycle(raw: string): LinkedListCycleInput {
  const bracket = raw.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [3, 2, 0, -4], 1");
  const values = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (values.some((n) => !Number.isFinite(n))) {
    throw new Error("Use numbers, e.g. [3, 2, 0, -4], 1");
  }
  if (values.length > 12) throw new Error("Keep it to 12 nodes so the trace stays readable");
  const close = raw.indexOf("]", raw.indexOf("["));
  const rest = raw.slice(close + 1).replace(/^,/, "").trim();
  if (!rest) throw new Error("Add pos after the list, e.g. [3, 2, 0, -4], 1");
  const pos = rest.toLowerCase() === "null" ? -1 : Number(rest);
  if (!Number.isInteger(pos) || pos < -1 || (pos !== -1 && pos >= values.length)) {
    throw new Error("pos must be -1 (no cycle) or an index inside the list");
  }
  return { values, pos };
}

function ptr(
  entries: Partial<Record<ListPointerName, number | null | undefined>>
): Partial<Record<ListPointerName, number>> {
  const out: Partial<Record<ListPointerName, number>> = {};
  (Object.entries(entries) as [ListPointerName, number | null | undefined][]).forEach(
    ([name, id]) => {
      if (id != null) out[name] = id;
    }
  );
  return out;
}

export function generateLinkedListCycle({ values, pos }: LinkedListCycleInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = listFromValues(values);
  const cycleTo = pos >= 0 ? pos : null;
  const nextOf = (id: number | null): number | null => {
    if (id == null) return null;
    const tail = nodes[id].next;
    return tail == null ? cycleTo : tail;
  };
  let slow: number | null = values.length > 0 ? 0 : null;
  let fast: number | null = values.length > 0 ? 0 : null;

  const listSnap = (active: number[] = []) =>
    snapList(nodes, {
      head: values.length > 0 ? 0 : null,
      active,
      pointers: ptr({ slow, fast }),
      label: "list",
      cycleTo,
    });

  steps.push(
    step(
      0,
      "Start",
      cycleTo == null
        ? "No cycle: slow and fast both start at the head."
        : `The tail links back to index ${cycleTo}. Slow and fast both start at the head.`,
      0,
      snap([]),
      { slow: slow ?? "null", fast: fast ?? "null" },
      { linkedList: listSnap(slow != null ? [slow] : []) }
    )
  );

  while (fast != null && nextOf(fast) != null) {
    slow = nextOf(slow);
    fast = nextOf(nextOf(fast));
    const active = Array.from(
      new Set([slow, fast].filter((id): id is number => id != null))
    );
    steps.push(
      step(
        steps.length,
        "Move",
        `slow moves 1 step to ${slow ?? "null"}; fast moves 2 steps to ${fast ?? "null"}.`,
        3,
        snap([]),
        { slow: slow ?? "null", fast: fast ?? "null" },
        { linkedList: listSnap(active) }
      )
    );
    if (slow != null && slow === fast) {
      steps.push(
        step(
          steps.length,
          "Meet",
          `slow and fast meet at node ${slow} — a cycle exists.`,
          4,
          snap([]),
          { slow, fast },
          { linkedList: listSnap([slow]), result: "true", done: true }
        )
      );
      return steps;
    }
  }

  steps.push(
    step(
      steps.length,
      "No cycle",
      "fast reached the end of the list — there is no cycle.",
      5,
      snap([]),
      { slow: slow ?? "null", fast: fast ?? "null" },
      { linkedList: listSnap(), result: "false", done: true }
    )
  );
  return steps;
}

export const linkedListCycleEntry: VisualizerEntry = {
  slug: "linked-list-cycle",
  title: "Linked List Cycle",
  inputHint: "[3, 2, 0, -4], 1",
  defaultInput: "[3, 2, 0, -4], 1",
  presets: [
    { label: "Cycle", value: "[3, 2, 0, -4], 1" },
    { label: "No cycle", value: "[1, 2, 3], -1" },
    { label: "Self-loop", value: "[1, 2], 1" },
  ],
  pseudocode: [
    "slow = fast = head",
    "while fast and fast.next:",
    "    slow = slow.next",
    "    fast = fast.next.next",
    "    if slow == fast: return True",
    "return False",
  ],
  parse: (raw: string) => parseLinkedListCycle(raw),
  generate: (input: unknown) => generateLinkedListCycle(input as LinkedListCycleInput),
};
