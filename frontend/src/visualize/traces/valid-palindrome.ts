import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface ValidPalindromeInput {
  text: string;
}

export function parseValidPalindrome(raw: string): ValidPalindromeInput {
  const lines = inputLines(raw);
  if (lines.length === 0) throw new Error("Enter a string");
  const text = lines.join(" ");
  const cleaned = text.replace(/[^a-z0-9]/gi, "").toLowerCase();
  if (cleaned.length === 0) throw new Error("The string needs at least one letter or digit");
  if (cleaned.length > 24) throw new Error("Keep it to 24 letters/digits");
  return { text };
}

export function generateValidPalindrome({ text }: ValidPalindromeInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const cleaned = [...text.replace(/[^a-z0-9]/gi, "").toLowerCase()];
  let left = 0;
  let right = cleaned.length - 1;
  let valid = true;

  const snapshot = (active: number[] = [], settled: number[] = []) =>
    snap(cleaned, {
      active,
      settled,
      pointers: { left, right },
      label: `cleaned: ${cleaned.join("")}`,
    });

  steps.push(
    step(
      0,
      "Clean",
      `Remove spaces and punctuation, then compare from both ends: "${cleaned.join("")}".`,
      0,
      snapshot([left, right]),
      { left, right },
      {}
    )
  );

  while (left < right) {
    const same = cleaned[left] === cleaned[right];
    steps.push(
      step(
        steps.length,
        same ? "Match" : "Mismatch",
        same
          ? `'${cleaned[left]}' matches '${cleaned[right]}'.`
          : `'${cleaned[left]}' does not match '${cleaned[right]}'.`,
        2,
        snapshot([left, right], Array.from({ length: left }, (_, index) => index)),
        { left, right },
        {}
      )
    );
    if (!same) {
      valid = false;
      break;
    }
    left += 1;
    right -= 1;
  }

  steps.push(
    step(
      steps.length,
      "Done",
      valid ? "The cleaned string reads the same in both directions." : "The string is not a palindrome.",
      3,
      snapshot([], cleaned.map((_, index) => index)),
      { valid: valid ? "true" : "false" },
      { done: true, result: valid ? "true" : "false" }
    )
  );

  return steps;
}

export const validPalindromeEntry: VisualizerEntry = {
  slug: "valid-palindrome",
  title: "Valid Palindrome",
  inputHint: "a single line of text",
  defaultInput: "A man, a plan, a canal: Panama",
  presets: [
    { label: "example", value: "A man, a plan, a canal: Panama" },
    { label: "not palindrome", value: "race a car" },
    { label: "single char", value: "a." },
  ],
  pseudocode: [
    "keep only letters and digits, lowercase them",
    "left = 0, right = n - 1",
    "while left < right:",
    "  if chars differ: return false",
    "  move both pointers inward",
    "return true",
  ],
  parse: parseValidPalindrome,
  generate: (input) => generateValidPalindrome(input as ValidPalindromeInput),
};
