import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface HouseRobberInput {
  values: number[];
}

export function parseHouseRobber(raw: string): HouseRobberInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one house");
  if (values.length > 14) throw new Error("Keep it to 14 houses");
  if (values.some((value) => value < 0)) throw new Error("House values must be non-negative");
  return { values };
}

export function generateHouseRobber({ values }: HouseRobberInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dp: number[] = [];
  let previous = 0;
  let current = 0;

  const valuesSnap = (active: number[] = [], settled: number[] = []) =>
    snap(values, { active, settled, pointers: {}, label: "houses" });
  const dpSnap = (active: number[] = []) =>
    snap(dp, { active, settled: dp.map((_, index) => index), label: "best up to house i" });

  steps.push(
    step(0, "Start", "At each house choose: skip it, or rob it plus the best total from two houses back.", 0, valuesSnap(), { previous, current }, { arrayAlt: dpSnap() })
  );

  for (let i = 0; i < values.length; i += 1) {
    const skip = current;
    const take = previous + values[i];
    const best = Math.max(skip, take);
    dp.push(best);
    previous = current;
    current = best;

    steps.push(
      step(
        steps.length,
        "Choose",
        `House ${i} (${values[i]}): skip gives ${skip}, rob gives ${take}; best is ${best}.`,
        2,
        valuesSnap([i], Array.from({ length: i }, (_, index) => index)),
        { skip, take, best },
        { arrayAlt: dpSnap([i]) }
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `The maximum amount that can be robbed is ${current}.`,
      3,
      valuesSnap([], values.map((_, index) => index)),
      { max: current },
      { arrayAlt: dpSnap(dp.map((_, index) => index)), done: true, result: String(current) }
    )
  );

  return steps;
}

export const houseRobberEntry: VisualizerEntry = {
  slug: "house-robber",
  title: "House Robber",
  inputHint: "n, then n house values",
  defaultInput: "4\n1 2 3 1",
  presets: [
    { label: "example", value: "4\n1 2 3 1" },
    { label: "five houses", value: "5\n2 7 9 3 1" },
    { label: "single", value: "1\n5" },
  ],
  pseudocode: [
    "previous = current = 0",
    "for value in houses:",
    "  skip = current",
    "  take = previous + value",
    "  previous, current = current, max(skip, take)",
    "return current",
  ],
  parse: parseHouseRobber,
  generate: (input) => generateHouseRobber(input as HouseRobberInput),
};
