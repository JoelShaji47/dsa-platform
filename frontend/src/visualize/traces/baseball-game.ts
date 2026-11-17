import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface BaseballGameInput {
  operations: string[];
}

export function parseBaseballGame(raw: string): BaseballGameInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n, then n operations");
  const n = Number(lines[0]);
  const operations = lines
    .slice(1)
    .flatMap((line) => line.split(/\s+/))
    .filter(Boolean);
  if (!Number.isInteger(n) || n < 1) throw new Error("n must be a positive integer");
  if (operations.length !== n) throw new Error(`Expected ${n} operations, received ${operations.length}`);
  if (n > 14) throw new Error("Keep it to 14 operations");
  for (const operation of operations) {
    if (operation !== "C" && operation !== "D" && operation !== "+" && !/^-?\d+$/.test(operation)) {
      throw new Error(`Unknown operation: ${operation}`);
    }
  }
  return { operations };
}

export function generateBaseballGame({ operations }: BaseballGameInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const stack: number[] = [];

  const opsSnap = (active: number[] = [], settled: number[] = []) =>
    snap(operations, { active, settled, pointers: {}, label: "operations" });
  const stackSnap = (active: number[] = []) => snapStack(stack, { active, label: "scores" });
  const score = () => stack.reduce((total, value) => total + value, 0);

  steps.push(
    step(0, "Start", "Process each operation and keep the valid round scores on a stack.", 0, opsSnap(), { score: 0 }, { stack: stackSnap() })
  );

  for (let i = 0; i < operations.length; i += 1) {
    const operation = operations[i];
    if (operation === "C") {
      const removed = stack.pop();
      steps.push(
        step(
          steps.length,
          "Cancel",
          `C removes the previous score ${removed ?? "—"}.`,
          2,
          opsSnap([i], Array.from({ length: i }, (_, index) => index)),
          { operation, score: score() },
          { stack: stackSnap() }
        )
      );
    } else if (operation === "D") {
      const value = stack[stack.length - 1] * 2;
      stack.push(value);
      steps.push(
        step(
          steps.length,
          "Double",
          `D adds double the previous score: ${value}.`,
          3,
          opsSnap([i], Array.from({ length: i }, (_, index) => index)),
          { operation, score: score() },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
    } else if (operation === "+") {
      const value = stack[stack.length - 1] + stack[stack.length - 2];
      stack.push(value);
      steps.push(
        step(
          steps.length,
          "Sum",
          `+ adds the sum of the previous two scores: ${value}.`,
          4,
          opsSnap([i], Array.from({ length: i }, (_, index) => index)),
          { operation, score: score() },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
    } else {
      const value = Number(operation);
      stack.push(value);
      steps.push(
        step(
          steps.length,
          "Push",
          `Record a new score of ${value}.`,
          1,
          opsSnap([i], Array.from({ length: i }, (_, index) => index)),
          { operation, score: score() },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
    }
  }

  const result = score();
  steps.push(
    step(
      steps.length,
      "Done",
      `The total score is ${result}.`,
      5,
      opsSnap([], operations.map((_, index) => index)),
      { score: result },
      { stack: stackSnap(stack.map((_, index) => index)), done: true, result: String(result) }
    )
  );

  return steps;
}

export const baseballGameEntry: VisualizerEntry = {
  slug: "baseball-game",
  title: "Baseball Game",
  inputHint: "n, then n operations (integer / C / D / +)",
  defaultInput: "5\n5\n2\nC\nD\n+",
  presets: [
    { label: "example", value: "5\n5\n2\nC\nD\n+" },
    { label: "mixed", value: "8\n5\n-2\n4\nC\nD\n9\n+\n+" },
    { label: "cancel all", value: "2\n1\nC" },
  ],
  pseudocode: [
    "scores = []",
    "for operation in operations:",
    "  integer: push value",
    "  C: pop",
    "  D: push 2 * top",
    "  +: push top + second top",
    "return sum(scores)",
  ],
  parse: parseBaseballGame,
  generate: (input) => generateBaseballGame(input as BaseballGameInput),
};
