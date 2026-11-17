import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface TrappingRainWaterInput {
  heights: number[];
}

export function parseTrappingRainWater(raw: string): TrappingRainWaterInput {
  const { values } = countedNumbers(raw);
  if (values.length < 1) throw new Error("Use at least one height");
  if (values.length > 14) throw new Error("Keep it to 14 heights");
  if (values.some((value) => value < 0)) throw new Error("Heights must be non-negative");
  return { heights: values };
}

export function generateTrappingRainWater({ heights }: TrappingRainWaterInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let left = 0;
  let right = heights.length - 1;
  let leftMax = 0;
  let rightMax = 0;
  let water = 0;
  const settled: number[] = [];

  steps.push(
    step(
      0,
      "Start",
      "Two pointers track the tallest wall seen from each side; the shorter side decides the trapped water.",
      0,
      snap(heights, { pointers: { left, right } }),
      { leftMax, rightMax, water },
      {}
    )
  );

  while (left < right) {
    if (heights[left] <= heights[right]) {
      if (heights[left] >= leftMax) {
        leftMax = heights[left];
        steps.push(
          step(
            steps.length,
            "New left max",
            `Height ${heights[left]} raises the left wall to ${leftMax}.`,
            2,
            snap(heights, {
              active: [left],
              settled: [...settled],
              pointers: { left, right },
            }),
            { leftMax, rightMax, water },
            {}
          )
        );
      } else {
        const added = leftMax - heights[left];
        water += added;
        settled.push(left);
        steps.push(
          step(
            steps.length,
            "Trap",
            `Cell ${left} traps ${added} unit${added === 1 ? "" : "s"} against the left wall.`,
            3,
            snap(heights, {
              active: [left],
              deps: [leftMax === heights[left] ? left : left - 1],
              settled: [...settled],
              pointers: { left, right },
            }),
            { leftMax, rightMax, water },
            {}
          )
        );
      }
      left += 1;
    } else {
      if (heights[right] >= rightMax) {
        rightMax = heights[right];
        steps.push(
          step(
            steps.length,
            "New right max",
            `Height ${heights[right]} raises the right wall to ${rightMax}.`,
            2,
            snap(heights, {
              active: [right],
              settled: [...settled],
              pointers: { left, right },
            }),
            { leftMax, rightMax, water },
            {}
          )
        );
      } else {
        const added = rightMax - heights[right];
        water += added;
        settled.push(right);
        steps.push(
          step(
            steps.length,
            "Trap",
            `Cell ${right} traps ${added} unit${added === 1 ? "" : "s"} against the right wall.`,
            3,
            snap(heights, {
              active: [right],
              deps: [rightMax === heights[right] ? right : right + 1],
              settled: [...settled],
              pointers: { left, right },
            }),
            { leftMax, rightMax, water },
            {}
          )
        );
      }
      right -= 1;
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The total trapped water is ${water}.`,
      5,
      snap(heights, {
        settled: heights.map((_, index) => index),
        pointers: {},
      }),
      { water },
      { done: true, result: String(water) }
    )
  );

  return steps;
}

export const trappingRainWaterEntry: VisualizerEntry = {
  slug: "trapping-rain-water",
  title: "Trapping Rain Water",
  inputHint: "n, then n heights",
  defaultInput: "12\n0 1 0 2 1 0 1 3 2 1 2 1",
  presets: [
    { label: "example", value: "12\n0 1 0 2 1 0 1 3 2 1 2 1" },
    { label: "valley", value: "5\n3 0 2 0 4" },
    { label: "no water", value: "4\n1 2 3 4" },
  ],
  pseudocode: [
    "left = 0, right = n - 1, leftMax = rightMax = water = 0",
    "while left < right:",
    "  if height[left] <= height[right]:",
    "    update leftMax or add leftMax - height[left]",
    "  else: update rightMax or add rightMax - height[right]",
    "return water",
  ],
  parse: parseTrappingRainWater,
  generate: (input) => generateTrappingRainWater(input as TrappingRainWaterInput),
};
