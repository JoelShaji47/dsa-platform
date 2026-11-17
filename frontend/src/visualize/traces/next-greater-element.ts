import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface NextGreaterInput {
  values: number[];
}

export function parseNextGreater(raw: string): NextGreaterInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one number");
  if (values.length > 12) throw new Error("Keep it to 12 numbers");
  return { values };
}

export function generateNextGreater({ values }: NextGreaterInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const answer = new Array<number>(values.length).fill(-1);
  const stack: number[] = [];

  const stackSnap = (active: number[] = []) =>
    snapStack(
      stack.map((index) => `${index}:${values[index]}`),
      { active, label: "indices waiting" }
    );
  const answerSnap = (active: number[] = []) =>
    snap(answer, { active, label: "answers" });

  steps.push(
    step(0, "Start", "A decreasing stack of indices waits for the next larger value.", 0, snap(values), {}, { stack: stackSnap(), arrayAlt: answerSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    steps.push(
      step(
        steps.length,
        "Visit",
        `Value ${values[i]} can answer every waiting index with a smaller value.`,
        1,
        snap(values, { active: [i], pointers: { i } }),
        { value: values[i] },
        { stack: stackSnap(stack.length ? [stack.length - 1] : []), arrayAlt: answerSnap() }
      )
    );

    while (stack.length > 0 && values[stack[stack.length - 1]] < values[i]) {
      const index = stack.pop()!;
      answer[index] = values[i];
      steps.push(
        step(
          steps.length,
          "Answer",
          `${values[i]} is the next greater value for index ${index} (${values[index]}).`,
          2,
          snap(values, { active: [index, i], settled: answer.map((value, k) => (value !== -1 ? k : -1)).filter((k) => k >= 0), pointers: { i } }),
          { index, value: values[i] },
          { stack: stackSnap(), arrayAlt: answerSnap([index]) }
        )
      );
    }

    stack.push(i);
    steps.push(
      step(
        steps.length,
        "Wait",
        `Index ${i} (${values[i]}) still needs a greater value; push it.`,
        3,
        snap(values, { active: [i], pointers: { i } }),
        { index: i },
        { stack: stackSnap([stack.length - 1]), arrayAlt: answerSnap() }
      )
    );
  }

  const result = answer.join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `The next greater values are ${result}; remaining -1 values have no greater element to the right.`,
      5,
      snap(values, { settled: values.map((_, index) => index) }),
      { remaining: stack.length },
      { stack: stackSnap(), arrayAlt: answerSnap(answer.map((_, index) => index)), done: true, result }
    )
  );

  return steps;
}

export const nextGreaterElementEntry: VisualizerEntry = {
  slug: "next-greater-element",
  title: "Next Greater Element",
  inputHint: "n, then n numbers",
  defaultInput: "4\n4 5 2 25",
  presets: [
    { label: "example", value: "4\n4 5 2 25" },
    { label: "decreasing", value: "4\n13 7 6 12" },
    { label: "single", value: "1\n3" },
  ],
  pseudocode: [
    "answer = [-1] * n; stack = []",
    "for i, value in enumerate(nums):",
    "  while stack top has a smaller value:",
    "    answer[top] = value; pop",
    "  push i",
    "return answer",
  ],
  parse: parseNextGreater,
  generate: (input) => generateNextGreater(input as NextGreaterInput),
};
