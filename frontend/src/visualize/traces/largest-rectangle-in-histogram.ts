import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface LargestRectangleInput {
  heights: number[];
}

export function parseLargestRectangle(raw: string): LargestRectangleInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one bar");
  if (values.length > 12) throw new Error("Keep it to 12 bars");
  if (values.some((value) => value < 0)) throw new Error("Heights must be non-negative");
  return { heights: values };
}

export function generateLargestRectangle({ heights }: LargestRectangleInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const stack: number[] = [];
  let best = 0;
  let bestRange: [number, number] = [0, -1];

  const stackSnap = (active: number[] = []) =>
    snapStack(
      stack.map((index) => `${index}:${heights[index]}`),
      { active, label: "increasing indices" }
    );

  steps.push(
    step(0, "Start", "Keep indices with increasing heights; a shorter bar closes taller rectangles.", 0, snap(heights), {}, { stack: stackSnap() })
  );

  for (let i = 0; i <= heights.length; i += 1) {
    const current = i === heights.length ? 0 : heights[i];
    while (stack.length > 0 && heights[stack[stack.length - 1]] > current) {
      const index = stack.pop()!;
      const height = heights[index];
      const left = stack.length === 0 ? 0 : stack[stack.length - 1] + 1;
      const width = i - left;
      const area = height * width;
      if (area > best) {
        best = area;
        bestRange = [left, i - 1];
      }
      steps.push(
        step(
          steps.length,
          "Close rectangle",
          `Bar ${index} (height ${height}) spans width ${width}, area ${area}.`,
          3,
          snap(heights, {
            active: Array.from({ length: width }, (_, offset) => left + offset),
            settled: [],
            pointers: { i: Math.min(i, heights.length - 1) },
          }),
          { index, height, width, area, best },
          { stack: stackSnap(stack.length ? [stack.length - 1] : []) }
        )
      );
    }

    if (i < heights.length) {
      stack.push(i);
      steps.push(
        step(
          steps.length,
          "Push",
          `Push bar ${i} (height ${current}); the stack heights stay increasing.`,
          4,
          snap(heights, { active: [i], pointers: { i } }),
          { index: i, height: current },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The largest rectangle has area ${best}.`,
      5,
      snap(heights, {
        settled: Array.from({ length: bestRange[1] - bestRange[0] + 1 }, (_, offset) => bestRange[0] + offset),
      }),
      { best },
      { stack: stackSnap(), done: true, result: String(best) }
    )
  );

  return steps;
}

export const largestRectangleEntry: VisualizerEntry = {
  slug: "largest-rectangle-in-histogram",
  title: "Largest Rectangle in Histogram",
  inputHint: "n, then n bar heights",
  defaultInput: "6\n2 1 5 6 2 3",
  presets: [
    { label: "example", value: "6\n2 1 5 6 2 3" },
    { label: "flat", value: "3\n2 2 2" },
    { label: "rising", value: "4\n1 2 3 4" },
  ],
  pseudocode: [
    "stack = []",
    "for i from 0 to n:",
    "  while stack top is taller than height[i]:",
    "    pop and compute area with the current width",
    "  push i",
    "return the best area",
  ],
  parse: parseLargestRectangle,
  generate: (input) => generateLargestRectangle(input as LargestRectangleInput),
};
