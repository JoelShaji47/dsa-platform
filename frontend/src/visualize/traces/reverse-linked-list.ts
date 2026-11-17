import {
  listFromValues,
  snap,
  snapList,
  step,
  type BaseStep,
  type ListPointerName,
  type VisualizerEntry,
} from "../trace-types";

export interface ReverseLinkedListInput {
  values: number[];
}

export function parseReverseLinkedList(raw: string): ReverseLinkedListInput {
  const bracket = raw.match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [1, 2, 3, 4, 5]");
  const values = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (values.some((n) => !Number.isFinite(n))) {
    throw new Error("Use numbers, e.g. [1, 2, 3, 4, 5]");
  }
  if (values.length > 12) throw new Error("Keep it to 12 nodes so the trace stays readable");
  return { values };
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

export function generateReverseLinkedList({ values }: ReverseLinkedListInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = listFromValues(values);
  const chainIds = (head: number | null) => {
    const ids: number[] = [];
    const seen = new Set<number>();
    let id = head;
    while (id != null && !seen.has(id)) {
      ids.push(id);
      seen.add(id);
      id = nodes[id].next;
    }
    return ids;
  };
  const snapBoth = (
    prevHead: number | null,
    currHead: number | null,
    prevPointers: Partial<Record<ListPointerName, number>>,
    currPointers: Partial<Record<ListPointerName, number>>,
    active: number[] = []
  ) => ({
    linkedList: snapList(nodes, {
      head: prevHead,
      active,
      settled: chainIds(prevHead),
      pointers: prevPointers,
      label: "reversed",
    }),
    linkedListAlt: snapList(nodes, {
      head: currHead,
      active,
      pointers: currPointers,
      label: "remaining",
    }),
  });

  let prev: number | null = null;
  let curr: number | null = values.length > 0 ? 0 : null;

  steps.push(
    step(
      0,
      "Start",
      values.length === 0
        ? "The list is empty — there is nothing to reverse."
        : "Walk the list once. The reversed chain grows on the left while the remaining chain shrinks on the right.",
      0,
      snap([]),
      { prev: "null", curr: curr ?? "null" },
      {
        ...snapBoth(null, curr, {}, ptr({ curr }), curr != null ? [curr] : []),
      }
    )
  );

  while (curr != null) {
    const nextId = nodes[curr].next;
    steps.push(
      step(
        steps.length,
        "Save next",
        `Save the rest of the list after node ${curr} so it is not lost when the link flips.`,
        2,
        snap([]),
        { prev: prev ?? "null", curr, next: nextId ?? "null" },
        {
          ...snapBoth(
            prev,
            curr,
            ptr({ prev }),
            ptr({ curr, next: nextId }),
            [curr]
          ),
        }
      )
    );

    nodes[curr].next = prev;
    steps.push(
      step(
        steps.length,
        "Reverse link",
        `Point node ${curr} back to ${prev ?? "null"}.`,
        3,
        snap([]),
        { prev: prev ?? "null", curr, next: nextId ?? "null" },
        {
          ...snapBoth(
            curr,
            nextId,
            ptr({ curr, prev }),
            ptr({ next: nextId }),
            [curr]
          ),
        }
      )
    );

    prev = curr;
    curr = nextId;
    steps.push(
      step(
        steps.length,
        "Advance",
        `Move prev to ${prev} and curr to ${curr ?? "null"}.`,
        4,
        snap([]),
        { prev, curr: curr ?? "null" },
        {
          ...snapBoth(
            prev,
            curr,
            ptr({ prev }),
            ptr({ curr, next: curr != null ? nodes[curr].next : null }),
            curr != null ? [curr] : []
          ),
        }
      )
    );
  }

  const resultValues = chainIds(prev).map((id) => nodes[id].value);
  steps.push(
    step(
      steps.length,
      "Done",
      `The list is fully reversed. Result: [${resultValues.join(", ")}].`,
      5,
      snap([]),
      { prev: prev ?? "null" },
      {
        ...snapBoth(prev, null, ptr({ prev }), {}, []),
        result: `[${resultValues.join(", ")}]`,
        done: true,
      }
    )
  );
  return steps;
}

export const reverseLinkedListEntry: VisualizerEntry = {
  slug: "reverse-linked-list",
  title: "Reverse Linked List",
  inputHint: "[1, 2, 3, 4, 5]",
  defaultInput: "[1, 2, 3, 4, 5]",
  presets: [
    { label: "Classic", value: "[1, 2, 3, 4, 5]" },
    { label: "Two nodes", value: "[1, 2]" },
    { label: "Single node", value: "[7]" },
  ],
  pseudocode: [
    "prev, curr = None, head",
    "while curr:",
    "    nxt = curr.next",
    "    curr.next = prev",
    "    prev, curr = curr, nxt",
    "return prev",
  ],
  parse: (raw: string) => parseReverseLinkedList(raw),
  generate: (input: unknown) => generateReverseLinkedList(input as ReverseLinkedListInput),
};
