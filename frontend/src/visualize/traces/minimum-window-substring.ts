import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface MinimumWindowInput {
  source: string;
  target: string;
}

export function parseMinimumWindow(raw: string): MinimumWindowInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use two lines: source then target");
  const [source, target] = lines;
  if (source.length > 16) throw new Error("Keep the source to 16 characters");
  if (target.length > 8) throw new Error("Keep the target to 8 characters");
  if (target.length === 0) throw new Error("The target cannot be empty");
  return { source, target };
}

export function generateMinimumWindow({ source, target }: MinimumWindowInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const chars = [...source];
  const need = new Map<string, number>();
  const window = new Map<string, number>();
  for (const char of target) need.set(char, (need.get(char) ?? 0) + 1);

  let left = 0;
  let right = 0;
  let formed = 0;
  let bestStart = 0;
  let bestLength = Infinity;
  const required = need.size;

  const snapshot = (active: number[] = [], settled: number[] = []) =>
    snap(chars, {
      active,
      settled,
      pointers: { left, right },
      label: `window ${source.slice(left, right + 1) || "∅"}`,
    });

  steps.push(
    step(
      0,
      "Start",
      `Find the shortest substring of "${source}" containing every character of "${target}".`,
      0,
      snapshot(),
      { need: target, formed: 0 },
      {}
    )
  );

  while (right < chars.length) {
    const char = chars[right];
    window.set(char, (window.get(char) ?? 0) + 1);
    if (need.has(char) && window.get(char) === need.get(char)) formed += 1;
    steps.push(
      step(
        steps.length,
        "Expand",
        `Add '${char}' at index ${right}; ${formed}/${required} target characters satisfied.`,
        2,
        snapshot([right], Array.from({ length: left }, (_, index) => index)),
        { left, right, formed, need: required },
        {}
      )
    );

    while (formed === required) {
      const length = right - left + 1;
      if (length < bestLength) {
        bestLength = length;
        bestStart = left;
        steps.push(
          step(
            steps.length,
            "Best",
            `The window "${source.slice(left, right + 1)}" is a new best at length ${length}.`,
            3,
            snapshot(Array.from({ length }, (_, index) => left + index)),
            { left, right, best: source.slice(bestStart, bestStart + bestLength) },
            {}
          )
        );
      }

      const leaving = chars[left];
      window.set(leaving, (window.get(leaving) ?? 0) - 1);
      if (need.has(leaving) && window.get(leaving)! < need.get(leaving)!) formed -= 1;
      steps.push(
        step(
          steps.length,
          "Shrink",
          `Remove '${leaving}' from the left; ${formed}/${required} requirements remain satisfied.`,
          4,
          snapshot([left], []),
          { left, right, formed, need: required },
          {}
        )
      );
      left += 1;
    }
    right += 1;
  }

  const result =
    bestLength === Infinity ? "" : source.slice(bestStart, bestStart + bestLength);
  steps.push(
    step(
      steps.length,
      "Done",
      result ? `The shortest covering substring is "${result}".` : "No window covers the target.",
      5,
      snapshot(
        bestLength === Infinity
          ? []
          : Array.from({ length: bestLength }, (_, index) => bestStart + index)
      ),
      { result: result || "none" },
      { done: true, result: result || "" }
    )
  );

  return steps;
}

export const minimumWindowSubstringEntry: VisualizerEntry = {
  slug: "minimum-window-substring",
  title: "Minimum Window Substring",
  inputHint: "two lines: source then target",
  defaultInput: "ADOBECODEBANC\nABC",
  presets: [
    { label: "example", value: "ADOBECODEBANC\nABC" },
    { label: "exact", value: "a\nb" },
    { label: "repeated", value: "aaflslflsldkals\naaa" },
  ],
  pseudocode: [
    "need = counts of target",
    "left = right = formed = 0",
    "expand right until all target characters are covered",
    "shrink left while the window remains valid",
    "track the shortest valid window",
  ],
  parse: parseMinimumWindow,
  generate: (input) => generateMinimumWindow(input as MinimumWindowInput),
};
