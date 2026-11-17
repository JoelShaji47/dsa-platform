import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface HouseRobberIIInput {
  values: number[];
}

export function parseHouseRobberII(raw: string): HouseRobberIIInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one house");
  if (values.length > 14) throw new Error("Keep it to 14 houses");
  if (values.some((value) => value < 0)) throw new Error("House values must be non-negative");
  return { values };
}

export function generateHouseRobberII({ values }: HouseRobberIIInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let best = 0;

  const valuesSnap = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {}, label: "houses (circular)" });

  steps.push(
    step(
      0,
      "Start",
      "The first and last houses are adjacent, so solve two linear cases: exclude the first or exclude the last.",
      0,
      valuesSnap(),
      { houses: values.length },
      {}
    )
  );

  const solve = (start: number, end: number, label: string): number => {
    const segment = values.slice(start, end + 1);
    const dp: number[] = [];
    let previous = 0;
    let current = 0;

    steps.push(
      step(
        steps.length,
        `Case ${label}`,
        `Consider houses ${start}..${end}: ${segment.join(", ")}.`,
        1,
        valuesSnap(
          Array.from({ length: end - start + 1 }, (_, index) => start + index),
          []
        ),
        { case: label, previous, current },
        { arrayAlt: snap(dp, { label: `dp for ${label}` }) }
      )
    );

    for (let offset = 0; offset < segment.length; offset += 1) {
      const index = start + offset;
      const skip = current;
      const take = previous + segment[offset];
      const value = Math.max(skip, take);
      dp.push(value);
      previous = current;
      current = value;

      steps.push(
        step(
          steps.length,
          "Choose",
          `${label}: house ${index} (${segment[offset]}), skip ${skip}, rob ${take}, best ${value}.`,
          2,
          valuesSnap([index], Array.from({ length: offset }, (_, i) => start + i)),
          { case: label, skip, take, best: value },
          {
            arrayAlt: snap(dp, {
              active: [offset],
              settled: dp.map((_, i) => i),
              label: `dp for ${label}`,
            }),
          }
        )
      );
    }

    steps.push(
      step(
        steps.length,
        `Finish ${label}`,
        `${label} yields ${current}.`,
        3,
        valuesSnap(),
        { case: label, total: current },
        { arrayAlt: snap(dp, { settled: dp.map((_, i) => i), label: `dp for ${label}` }) }
      )
    );
    return current;
  };

  if (values.length === 1) {
    best = values[0];
  } else {
    const excludeLast = solve(0, values.length - 2, "exclude last");
    const excludeFirst = solve(1, values.length - 1, "exclude first");
    best = Math.max(excludeLast, excludeFirst);
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The best circular robbery takes ${best}.`,
      4,
      valuesSnap([], values.map((_, index) => index)),
      { best },
      { done: true, result: String(best) }
    )
  );

  return steps;
}

export const houseRobberIIEntry: VisualizerEntry = {
  slug: "house-robber-ii",
  title: "House Robber II",
  inputHint: "n, then n house values arranged in a circle",
  defaultInput: "3\n2 3 2",
  presets: [
    { label: "example", value: "3\n2 3 2" },
    { label: "four", value: "4\n1 2 3 1" },
    { label: "single", value: "1\n5" },
  ],
  pseudocode: [
    "if only one house: return its value",
    "a = rob houses 0..n-2",
    "b = rob houses 1..n-1",
    "return max(a, b)",
  ],
  parse: parseHouseRobberII,
  generate: (input) => generateHouseRobberII(input as HouseRobberIIInput),
};
