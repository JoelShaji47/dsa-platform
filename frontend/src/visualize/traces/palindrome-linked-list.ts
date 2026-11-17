import {
  listFromValues,
  snap,
  snapList,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface PalindromeListInput {
  values: number[];
}

export function parsePalindromeList(raw: string): PalindromeListInput {
  const lines = inputLines(raw);
  const values = integersFrom(lines[0] ?? "");
  if (values.length === 0) throw new Error("The list cannot be empty");
  if (values.length > 14) throw new Error("Keep it to 14 nodes");
  return { values };
}

export function generatePalindromeList({ values }: PalindromeListInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = listFromValues(values);
  const arraySnap = (active: number[] = [], deps: number[] = []) =>
    snap(values, {
      active,
      deps,
      settled: [],
      pointers: {},
      label: "values",
    });

  let slow = 0;
  let fast = 0;
  steps.push(
    step(
      0,
      "Start",
      "Find the midpoint, then compare values from both ends.",
      0,
      arraySnap([0, values.length - 1]),
      {},
      { linkedList: snapList(nodes, { active: [0], pointers: { slow: 0, fast: 0 } }) }
    )
  );

  while (nodes[fast].next != null && nodes[nodes[fast].next!].next != null) {
    slow = nodes[slow].next!;
    fast = nodes[nodes[fast].next!].next!;
    steps.push(
      step(
        steps.length,
        "Find middle",
        `Move slow to ${values[slow]} and fast to ${values[fast]}.`,
        1,
        arraySnap([slow, fast]),
        { slow: values[slow], fast: values[fast] },
        { linkedList: snapList(nodes, { active: [slow, fast], pointers: { slow, fast } }) }
      )
    );
  }

  let left = 0;
  let right = values.length - 1;
  let valid = true;
  const matched: number[] = [];

  while (left < right) {
    const same = values[left] === values[right];
    steps.push(
      step(
        steps.length,
        same ? "Match" : "Mismatch",
        same
          ? `${values[left]} equals ${values[right]}.`
          : `${values[left]} does not equal ${values[right]}.`,
        3,
        snap(values, {
          active: [left, right],
          deps: [slow],
          settled: [...matched],
          pointers: { left, right },
          label: "values",
        }),
        { left, right },
        { linkedList: snapList(nodes, { active: [left, right], settled: [...matched], pointers: { slow } }) }
      )
    );
    if (!same) {
      valid = false;
      break;
    }
    matched.push(left, right);
    left += 1;
    right -= 1;
  }

  steps.push(
    step(
      steps.length,
      "Done",
      valid ? "The linked list is a palindrome." : "The linked list is not a palindrome.",
      4,
      snap(values, {
        settled: values.map((_, index) => index),
        pointers: {},
        label: "values",
      }),
      { valid: valid ? "true" : "false" },
      {
        linkedList: snapList(nodes, {
          settled: values.map((_, index) => index),
          pointers: { slow },
        }),
        done: true,
        result: valid ? "true" : "false",
      }
    )
  );

  return steps;
}

export const palindromeLinkedListEntry: VisualizerEntry = {
  slug: "palindrome-linked-list",
  title: "Palindrome Linked List",
  inputHint: "a single linked list",
  defaultInput: "[1,2,2,1]",
  presets: [
    { label: "palindrome", value: "[1,2,2,1]" },
    { label: "odd", value: "[1,2,3,2,1]" },
    { label: "not palindrome", value: "[1,2]" },
  ],
  pseudocode: [
    "find the middle with slow/fast pointers",
    "compare values from both ends",
    "stop at the first mismatch",
    "return true if every pair matches",
  ],
  parse: parsePalindromeList,
  generate: (input) => generatePalindromeList(input as PalindromeListInput),
};
