import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface FruitIntoBasketsInput {
  fruits: number[];
}

export function parseFruitIntoBaskets(raw: string): FruitIntoBasketsInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one fruit");
  if (values.length > 14) throw new Error("Keep it to 14 fruits");
  return { fruits: values };
}

export function generateFruitIntoBaskets({ fruits }: FruitIntoBasketsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const counts = new Map<number, number>();
  let left = 0;
  let best = 0;
  let bestLeft = 0;
  let bestRight = -1;

  const window = () => Array.from({ length: Math.max(0, bestRight - bestLeft + 1) }, (_, index) => bestLeft + index);
  const snapshot = (active: number[] = []) =>
    snap(fruits, {
      active,
      settled: window(),
      pointers: { left, right: active.at(-1) ?? left },
    });

  steps.push(
    step(
      0,
      "Start",
      "Keep a window with at most two distinct fruit types; expand right, shrink left when a third appears.",
      0,
      snapshot([0]),
      { left, right: 0, best },
      {}
    )
  );

  for (let right = 0; right < fruits.length; right += 1) {
    counts.set(fruits[right], (counts.get(fruits[right]) ?? 0) + 1);
    steps.push(
      step(
        steps.length,
        "Add",
        `Add fruit type ${fruits[right]} at index ${right}; the window has ${counts.size} type${counts.size === 1 ? "" : "s"}.`,
        1,
        snapshot(Array.from({ length: right - left + 1 }, (_, index) => left + index)),
        { left, right, distinct: counts.size, best },
        {}
      )
    );

    while (counts.size > 2) {
      const leaving = fruits[left];
      counts.set(leaving, counts.get(leaving)! - 1);
      if (counts.get(leaving) === 0) counts.delete(leaving);
      steps.push(
        step(
          steps.length,
          "Shrink",
          `Three types are present; drop index ${left} (type ${leaving}).`,
          2,
          snapshot([left]),
          { left, right, distinct: counts.size, best },
          {}
        )
      );
      left += 1;
    }

    const length = right - left + 1;
    if (length > best) {
      best = length;
      bestLeft = left;
      bestRight = right;
      steps.push(
        step(
          steps.length,
          "Best",
          `The window now has ${best} fruit${best === 1 ? "" : "s"}.`,
          3,
          snapshot(Array.from({ length }, (_, index) => left + index)),
          { left, right, distinct: counts.size, best },
          {}
        )
      );
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The largest valid basket holds ${best} fruit${best === 1 ? "" : "s"}.`,
      5,
      snapshot(window()),
      { best },
      { done: true, result: String(best) }
    )
  );

  return steps;
}

export const fruitIntoBasketsEntry: VisualizerEntry = {
  slug: "fruit-into-baskets",
  title: "Fruit Into Baskets",
  inputHint: "n, then n fruit types",
  defaultInput: "3\n1 2 1",
  presets: [
    { label: "example", value: "3\n1 2 1" },
    { label: "long", value: "6\n1 2 3 2 2 2" },
    { label: "one type", value: "4\n5 5 5 5" },
  ],
  pseudocode: [
    "left = 0, counts = empty map, best = 0",
    "for right in 0..n-1:",
    "  add fruits[right]",
    "  while counts has more than 2 types: remove fruits[left], left++",
    "  best = max(best, right - left + 1)",
    "return best",
  ],
  parse: parseFruitIntoBaskets,
  generate: (input) => generateFruitIntoBaskets(input as FruitIntoBasketsInput),
};
