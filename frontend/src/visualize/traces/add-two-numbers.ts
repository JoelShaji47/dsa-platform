import {
  snap,
  snapList,
  step,
  type BaseStep,
  type LinkedListNode,
  type LinkedListSnapshot,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface AddTwoNumbersInput {
  first: number[];
  second: number[];
}

export function parseAddTwoNumbers(raw: string): AddTwoNumbersInput {
  const lines = inputLines(raw);
  if (lines.length < 4) throw new Error("Use: n, list1, m, list2");
  const n = Number(lines[0]);
  const first = integersFrom(lines[1]);
  const m = Number(lines[2]);
  const second = integersFrom(lines[3]);
  if (!Number.isInteger(n) || !Number.isInteger(m) || n < 1 || m < 1) {
    throw new Error("Each list needs a positive length");
  }
  if (first.length !== n || second.length !== m) throw new Error("List lengths do not match");
  if (first.length > 6 || second.length > 6) throw new Error("Keep each list to 6 digits");
  if (first.some((digit) => digit < 0 || digit > 9) || second.some((digit) => digit < 0 || digit > 9)) {
    throw new Error("Digits must be 0..9");
  }
  return { first, second };
}

function nodesFor(values: number[]): LinkedListNode[] {
  return values.map((value, index) => ({
    id: index,
    value,
    next: index + 1 < values.length ? index + 1 : null,
  }));
}

export function generateAddTwoNumbers({ first, second }: AddTwoNumbersInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const a = nodesFor(first);
  const b = nodesFor(second);
  const result: number[] = [];
  let i = 0;
  let j = 0;
  let carry = 0;

  const snapA = (active: number[] = [], settled: number[] = []): LinkedListSnapshot =>
    snapList(a, { active, settled, pointers: { curr: i < a.length ? i : undefined }, label: "l1" });
  const snapB = (active: number[] = [], settled: number[] = []): LinkedListSnapshot =>
    snapList(b, { active, settled, pointers: { curr: j < b.length ? j : undefined }, label: "l2" });
  const resultSnap = (active: number[] = []) =>
    snap(result, {
      active,
      settled: result.map((_, index) => index),
      pointers: {},
      label: "result digits",
    });

  steps.push(
    step(0, "Start", "Add the lists digit by digit, carrying into the next column.", 0, resultSnap(), { carry }, { linkedList: snapA(), linkedListAlt: snapB() })
  );

  while (i < first.length || j < second.length || carry > 0) {
    const left = i < first.length ? first[i] : 0;
    const right = j < second.length ? second[j] : 0;
    const total = left + right + carry;
    const digit = total % 10;
    carry = Math.floor(total / 10);
    result.push(digit);

    steps.push(
      step(
        steps.length,
        "Add",
        `${left} + ${right} + carry ${carry === 0 ? 0 : "→"} gives digit ${digit}${carry ? `, carry ${carry}` : ""}.`,
        2,
        resultSnap([result.length - 1]),
        { left, right, digit, carry },
        {
          linkedList: snapA(i < first.length ? [i] : [], Array.from({ length: i }, (_, index) => index)),
          linkedListAlt: snapB(j < second.length ? [j] : [], Array.from({ length: j }, (_, index) => index)),
        }
      )
    );
    i += 1;
    j += 1;
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The sum is ${result.join("")} stored in reverse order as ${result.join(" ")}.`,
      5,
      resultSnap(result.map((_, index) => index)),
      { carry },
      {
        linkedList: snapA([], a.map((_, index) => index)),
        linkedListAlt: snapB([], b.map((_, index) => index)),
        done: true,
        result: result.join(" "),
      }
    )
  );

  return steps;
}

export const addTwoNumbersEntry: VisualizerEntry = {
  slug: "add-two-numbers",
  title: "Add Two Numbers",
  inputHint: "n, list1, m, list2 (digits are stored in reverse order)",
  defaultInput: "3\n2 4 3\n3\n5 6 4",
  presets: [
    { label: "example", value: "3\n2 4 3\n3\n5 6 4" },
    { label: "carry", value: "1\n9\n1\n9" },
    { label: "zero", value: "1\n0\n1\n0" },
  ],
  pseudocode: [
    "i = j = carry = 0",
    "while either list has digits or carry:",
    "  total = digit1 + digit2 + carry",
    "  append total % 10",
    "  carry = total // 10",
    "return reversed result digits",
  ],
  parse: parseAddTwoNumbers,
  generate: (input) => generateAddTwoNumbers(input as AddTwoNumbersInput),
};
