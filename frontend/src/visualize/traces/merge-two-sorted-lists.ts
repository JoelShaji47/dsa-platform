import {
  listFromValues,
  snap,
  snapList,
  step,
  type BaseStep,
  type ListPointerName,
  type VisualizerEntry,
} from "../trace-types";

export interface MergeTwoListsInput {
  a: number[];
  b: number[];
}

export function parseMergeTwoLists(raw: string): MergeTwoListsInput {
  const brackets = raw.match(/\[[^\]]*\]/g);
  if (!brackets || brackets.length !== 2) {
    throw new Error("Use the form [1, 2, 4], [1, 3, 4]");
  }
  const parseList = (part: string) =>
    part
      .replace(/[\[\]]/g, "")
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0)
      .map(Number);
  const a = parseList(brackets[0]);
  const b = parseList(brackets[1]);
  if ([...a, ...b].some((n) => !Number.isFinite(n))) {
    throw new Error("Both lists must contain numbers");
  }
  if (a.length + b.length > 12) {
    throw new Error("Keep the two lists to 12 nodes total so the trace stays readable");
  }
  for (const list of [a, b]) {
    for (let i = 1; i < list.length; i++) {
      if (list[i] < list[i - 1]) {
        throw new Error("Both lists must be sorted ascending");
      }
    }
  }
  return { a, b };
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

export function generateMergeTwoLists({ a, b }: MergeTwoListsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodesA = listFromValues(a);
  const nodesB = listFromValues(b);
  let ia: number | null = a.length > 0 ? 0 : null;
  let ib: number | null = b.length > 0 ? 0 : null;
  const merged: number[] = [];

  const listSnap = (activeA: number[] = [], activeB: number[] = []) => ({
    linkedList: snapList(nodesA, {
      head: ia,
      active: activeA,
      pointers: ptr({ a: ia }),
      label: "list A",
    }),
    linkedListAlt: snapList(nodesB, {
      head: ib,
      active: activeB,
      pointers: ptr({ b: ib }),
      label: "list B",
    }),
  });
  const mergedSnap = () => {
    const active = merged.length > 0 ? [merged.length - 1] : [];
    return snap(merged, { active, settled: merged.map((_, index) => index) });
  };

  steps.push(
    step(
      0,
      "Start",
      a.length === 0 || b.length === 0
        ? "One list is empty, so the other list is already the answer."
        : "Compare the two heads and repeatedly take the smaller node.",
      0,
      snap([]),
      { a: ia ?? "null", b: ib ?? "null" },
      { ...listSnap() }
    )
  );

  while (ia != null && ib != null) {
    const va = Number(nodesA[ia].value);
    const vb = Number(nodesB[ib].value);
    steps.push(
      step(
        steps.length,
        "Compare",
        `A has ${va}, B has ${vb} — take the smaller one.`,
        1,
        mergedSnap(),
        { a: va, b: vb },
        { ...listSnap([ia], [ib]) }
      )
    );

    if (va <= vb) {
      merged.push(va);
      ia = nodesA[ia].next;
      steps.push(
        step(
          steps.length,
          `Take ${va}`,
          `${va} <= ${vb}, so append A's node to the merged list.`,
          2,
          mergedSnap(),
          { taken: va, from: "A" },
          { ...listSnap(ia != null ? [ia] : [], ib != null ? [ib] : []) }
        )
      );
    } else {
      merged.push(vb);
      ib = nodesB[ib].next;
      steps.push(
        step(
          steps.length,
          `Take ${vb}`,
          `${vb} < ${va}, so append B's node to the merged list.`,
          3,
          mergedSnap(),
          { taken: vb, from: "B" },
          { ...listSnap(ia != null ? [ia] : [], ib != null ? [ib] : []) }
        )
      );
    }
  }

  const remaining: number[] = [];
  let id = ia;
  while (id != null) {
    remaining.push(Number(nodesA[id].value));
    id = nodesA[id].next;
  }
  id = ib;
  while (id != null) {
    remaining.push(Number(nodesB[id].value));
    id = nodesB[id].next;
  }
  if (remaining.length > 0) {
    merged.push(...remaining);
    steps.push(
      step(
        steps.length,
        "Attach remainder",
        `One list is exhausted — attach the rest: [${remaining.join(", ")}].`,
        5,
        mergedSnap(),
        { rest: remaining.join(", ") },
        { ...listSnap(ia != null ? [ia] : [], ib != null ? [ib] : []) }
      )
    );
    ia = null;
    ib = null;
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `Merged ${merged.length} node(s). Result: [${merged.join(", ")}].`,
      6,
      snap(merged, { settled: merged.map((_, index) => index) }),
      { merged: merged.join(", ") },
      {
        ...listSnap(),
        result: `[${merged.join(", ")}]`,
        done: true,
      }
    )
  );
  return steps;
}

export const mergeTwoListsEntry: VisualizerEntry = {
  slug: "merge-two-sorted-lists",
  title: "Merge Two Sorted Lists",
  inputHint: "[1, 2, 4], [1, 3, 4]",
  defaultInput: "[1, 2, 4], [1, 3, 4]",
  presets: [
    { label: "Classic", value: "[1, 2, 4], [1, 3, 4]" },
    { label: "One empty", value: "[], [1, 2, 3]" },
    { label: "Interleaved", value: "[1, 5, 9], [2, 3, 10]" },
  ],
  pseudocode: [
    "dummy = new ListNode(); tail = dummy",
    "while a and b:",
    "    if a.val <= b.val: tail.next = a; a = a.next",
    "    else: tail.next = b; b = b.next",
    "    tail = tail.next",
    "tail.next = a or b",
    "return dummy.next",
  ],
  parse: (raw: string) => parseMergeTwoLists(raw),
  generate: (input: unknown) => generateMergeTwoLists(input as MergeTwoListsInput),
};
