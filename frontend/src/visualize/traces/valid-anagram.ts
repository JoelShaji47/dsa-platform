import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface ValidAnagramInput {
  first: string;
  second: string;
}

export function parseValidAnagram(raw: string): ValidAnagramInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use two lines: s then t");
  const [first, second] = lines;
  if (first.length > 12 || second.length > 12) {
    throw new Error("Keep both strings to 12 characters");
  }
  return { first, second };
}

export function generateValidAnagram({ first, second }: ValidAnagramInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const a = [...first];
  const b = [...second];
  const counts = new Map<string, number>();

  const firstSnap = (active: number[] = [], settled: number[] = []) =>
    snap(a, { active, settled, pointers: {}, label: "s" });
  const secondSnap = (active: number[] = [], settled: number[] = []) =>
    snap(b, { active, settled, pointers: {}, label: "t" });

  steps.push(
    step(
      0,
      "Start",
      "Count characters in the first string, then cancel them against the second.",
      0,
      firstSnap(),
      { first: first.length, second: second.length },
      { arrayAlt: secondSnap() }
    )
  );

  for (let i = 0; i < a.length; i += 1) {
    counts.set(a[i], (counts.get(a[i]) ?? 0) + 1);
    steps.push(
      step(
        steps.length,
        "Count",
        `Add '${a[i]}' to the frequency map.`,
        1,
        firstSnap([i], Array.from({ length: i }, (_, index) => index)),
        { char: a[i], count: counts.get(a[i]) ?? 0 },
        { arrayAlt: secondSnap() }
      )
    );
  }

  let valid = a.length === b.length;
  const used: number[] = [];
  for (let i = 0; i < b.length; i += 1) {
    const remaining = counts.get(b[i]) ?? 0;
    if (remaining === 0) valid = false;
    else counts.set(b[i], remaining - 1);
    used.push(i);
    steps.push(
      step(
        steps.length,
        remaining === 0 ? "Missing" : "Cancel",
        remaining === 0
          ? `'${b[i]}' has no remaining match in s.`
          : `Cancel one '${b[i]}' from the frequency map.`,
        2,
        firstSnap([], Array.from({ length: a.length }, (_, index) => index)),
        { char: b[i], remaining: Math.max(0, remaining - 1) },
        { arrayAlt: secondSnap([i], [...used]) }
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      valid ? "Both strings contain the same characters with the same counts." : "The strings are not anagrams.",
      3,
      firstSnap([], a.map((_, index) => index)),
      { valid: valid ? "true" : "false" },
      {
        arrayAlt: secondSnap([], b.map((_, index) => index)),
        done: true,
        result: valid ? "true" : "false",
      }
    )
  );

  return steps;
}

export const validAnagramEntry: VisualizerEntry = {
  slug: "valid-anagram",
  title: "Valid Anagram",
  inputHint: "two lines: s then t",
  defaultInput: "anagram\nnagaram",
  presets: [
    { label: "example", value: "anagram\nnagaram" },
    { label: "not anagram", value: "rat\ncar" },
    { label: "single", value: "a\na" },
  ],
  pseudocode: [
    "count characters in s",
    "for each character in t:",
    "  if count is zero: return false",
    "  decrement count",
    "return every count is zero",
  ],
  parse: parseValidAnagram,
  generate: (input) => generateValidAnagram(input as ValidAnagramInput),
};
