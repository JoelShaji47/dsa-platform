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

export interface CopyRandomInput {
  values: number[];
  random: number[];
}

export function parseCopyRandom(raw: string): CopyRandomInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: values, then random indices");
  const values = integersFrom(lines[0]);
  const random = integersFrom(lines[1]);
  if (values.length === 0) throw new Error("The list cannot be empty");
  if (values.length > 10) throw new Error("Keep it to 10 nodes");
  if (random.length !== values.length) throw new Error("Provide one random index per node");
  if (random.some((index) => index < -1 || index >= values.length)) {
    throw new Error("Random indices must be -1 or a valid node index");
  }
  return { values, random };
}

export function generateCopyRandom({ values, random }: CopyRandomInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const original: LinkedListNode[] = listFromValues(values).map((node, index) => ({
    ...node,
    random: random[index] === -1 ? null : random[index],
  }));
  const clone: LinkedListNode[] = listFromValues(values).map((node) => ({ ...node, random: null }));

  const originalSnap = (active: number[] = [], settled: number[] = []): LinkedListSnapshot =>
    snapList(original, { active, settled, label: "original" });
  const cloneSnap = (active: number[] = [], settled: number[] = []): LinkedListSnapshot =>
    snapList(clone, { active, settled, label: "copy" });

  steps.push(
    step(0, "Start", "Create a deep copy; the copy must not share nodes with the original.", 0, snap([]), {}, {
      linkedList: originalSnap(),
      linkedListAlt: cloneSnap(),
    })
  );

  for (let i = 0; i < values.length; i += 1) {
    steps.push(
      step(
        steps.length,
        "Copy node",
        `Create a copy of node ${values[i]} with the same value.`,
        1,
        snap([]),
        { index: i, value: values[i] },
        {
          linkedList: originalSnap([i], Array.from({ length: i }, (_, index) => index)),
          linkedListAlt: cloneSnap([i], Array.from({ length: i }, (_, index) => index)),
        }
      )
    );
  }

  for (let i = 0; i < clone.length; i += 1) {
    if (i + 1 < clone.length) clone[i].next = i + 1;
    else clone[i].next = null;
    clone[i].random = random[i] === -1 ? null : random[i];
    steps.push(
      step(
        steps.length,
        "Wire links",
        random[i] === -1
          ? `Copy node ${values[i]} has a null random pointer.`
          : `Copy node ${values[i]} points its random pointer at node ${values[random[i]]}.`,
        2,
        snap([]),
        { index: i, random: random[i] === -1 ? "null" : values[random[i]] },
        {
          linkedList: originalSnap([i], original.map((_, index) => index)),
          linkedListAlt: cloneSnap([i], Array.from({ length: i }, (_, index) => index)),
        }
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The copied list has the same values and random links: ${values.join(" ")}.`,
      3,
      snap([]),
      { cloned: values.length },
      {
        linkedList: originalSnap([], original.map((_, index) => index)),
        linkedListAlt: cloneSnap([], clone.map((_, index) => index)),
        done: true,
        result: values.join(" "),
      }
    )
  );

  return steps;
}

export const copyRandomPointerEntry: VisualizerEntry = {
  slug: "copy-list-with-random-pointer",
  title: "Copy List with Random Pointer",
  inputHint: "values, then one random index per node (-1 for null)",
  defaultInput: "7 13 11 10 1\n1 2 3 -1 0",
  presets: [
    { label: "example", value: "7 13 11 10 1\n1 2 3 -1 0" },
    { label: "two nodes", value: "1 2\n1 -1" },
    { label: "all null", value: "1 2 3\n-1 -1 -1" },
  ],
  pseudocode: [
    "create a copy node for every original node",
    "link copied nodes with next",
    "copy each random pointer using the same index",
    "return the copied head",
  ],
  parse: parseCopyRandom,
  generate: (input) => generateCopyRandom(input as CopyRandomInput),
};
