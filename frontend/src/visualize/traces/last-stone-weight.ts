import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface LastStoneWeightInput {
  stones: number[];
}

export function parseLastStoneWeight(raw: string): LastStoneWeightInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one stone");
  if (values.length > 12) throw new Error("Keep it to 12 stones");
  if (values.some((value) => value <= 0)) throw new Error("Stone weights must be positive");
  return { stones: values };
}

export function generateLastStoneWeight({ stones }: LastStoneWeightInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let heap = [...stones].sort((a, b) => b - a);
  const history: number[] = [];

  const heapSnap = (active: number[] = [], settled: number[] = []) =>
    snap(heap, { active, settled, pointers: {}, label: "stones (max first)" });
  const historySnap = (active: number[] = []) => snap(history, { active, label: "smash results" });

  steps.push(
    step(0, "Start", "Repeatedly smash the two heaviest stones; the difference goes back into the pile.", 0, heapSnap(), { stones: heap.length }, { arrayAlt: historySnap() })
  );

  while (heap.length > 1) {
    const first = heap[0];
    const second = heap[1];
    heap = heap.slice(2);
    const difference = first - second;

    steps.push(
      step(
        steps.length,
        "Smash",
        `Smash ${first} and ${second}; ${first === second ? "both disappear" : `${difference} remains`}.`,
        2,
        heapSnap([], []),
        { first, second, difference },
        { arrayAlt: historySnap() }
      )
    );

    if (difference > 0) {
      heap.push(difference);
      heap.sort((a, b) => b - a);
      history.push(difference);
      steps.push(
        step(
          steps.length,
          "Keep remainder",
          `Return ${difference} to the pile.`,
          3,
          heapSnap([0], []),
          { difference, stones: heap.length },
          { arrayAlt: historySnap() }
        )
      );
    }
  }

  const result = heap[0] ?? 0;
  steps.push(
    step(
      steps.length,
      "Done",
      heap.length === 1 ? `The last stone weighs ${result}.` : "No stones remain.",
      4,
      heapSnap(heap.map((_, index) => index)),
      { result },
      { arrayAlt: historySnap(history.map((_, index) => index)), done: true, result: String(result) }
    )
  );

  return steps;
}

export const lastStoneWeightEntry: VisualizerEntry = {
  slug: "last-stone-weight",
  title: "Last Stone Weight",
  inputHint: "n, then n stone weights",
  defaultInput: "4\n2 7 4 1",
  presets: [
    { label: "example", value: "4\n2 7 4 1" },
    { label: "six stones", value: "6\n2 7 4 1 8 1" },
    { label: "last stone", value: "2\n10 4" },
  ],
  pseudocode: [
    "max-heap = stones",
    "while heap has at least two stones:",
    "  first = pop max; second = pop max",
    "  if first != second: push first - second",
    "return the remaining stone or 0",
  ],
  parse: parseLastStoneWeight,
  generate: (input) => generateLastStoneWeight(input as LastStoneWeightInput),
};
