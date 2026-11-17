import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface WordBreakInput {
  text: string;
  words: string[];
}

export function parseWordBreak(raw: string): WordBreakInput {
  const lines = inputLines(raw);
  if (lines.length < 3) throw new Error("Use: s, n, then n dictionary words");
  const text = lines[0];
  const n = Number(lines[1]);
  const words = lines
    .slice(2)
    .flatMap((line) => line.split(/\s+/))
    .filter(Boolean);
  if (!Number.isInteger(n) || words.length !== n) throw new Error("Dictionary count does not match");
  if (text.length > 18) throw new Error("Keep the string to 18 characters");
  if (n > 10) throw new Error("Keep the dictionary to 10 words");
  return { text, words };
}

export function generateWordBreak({ text, words }: WordBreakInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const n = text.length;
  const dp = new Array<boolean>(n + 1).fill(false);
  dp[0] = true;
  const chars = [...text];

  const textSnap = (active: number[] = [], settled: number[] = []) =>
    snap(chars, { active, settled, pointers: {}, label: "string" });
  const dpSnap = (active: number[] = []) =>
    snap(dp.map((value) => (value ? "T" : "F")), {
      active,
      settled: dp.map((value, index) => (value ? index : -1)).filter((index) => index >= 0),
      label: "dp prefix reachable",
    });

  steps.push(
    step(0, "Start", "dp[i] is true when text[0..i) can be split into dictionary words.", 0, textSnap(), { n }, { arrayAlt: dpSnap([0]) })
  );

  for (let start = 0; start <= n; start += 1) {
    if (!dp[start]) continue;
    steps.push(
      step(
        steps.length,
        "Reachable",
        `Prefix ending at ${start} is reachable; try every dictionary word from here.`,
        2,
        textSnap([], Array.from({ length: start }, (_, index) => index)),
        { start },
        { arrayAlt: dpSnap([start]) }
      )
    );

    for (const word of words) {
      if (!text.startsWith(word, start)) continue;
      const end = start + word.length;
      dp[end] = true;
      steps.push(
        step(
          steps.length,
          "Match word",
          `"${word}" matches ${start}..${end}; prefix ${end} becomes reachable.`,
          4,
          textSnap(Array.from({ length: word.length }, (_, index) => start + index)),
          { word, start, end },
          { arrayAlt: dpSnap([end]) }
        )
      );
    }
  }

  const result = dp[n];
  steps.push(
    step(
      steps.length,
      "Done",
      result ? "The whole string can be segmented." : "No segmentation covers the whole string.",
      5,
      textSnap([], chars.map((_, index) => index)),
      { result: result ? "true" : "false" },
      { arrayAlt: dpSnap(dp.map((_, index) => index)), done: true, result: result ? "true" : "false" }
    )
  );

  return steps;
}

export const wordBreakEntry: VisualizerEntry = {
  slug: "word-break",
  title: "Word Break",
  inputHint: "s, n, then n dictionary words",
  defaultInput: "applepenapple\n2\napple pen",
  presets: [
    { label: "example", value: "applepenapple\n2\napple pen" },
    { label: "no split", value: "catsandog\n5\ncats dog sand and cat" },
    { label: "repeated", value: "aaaaaaa\n2\naaaa aaa" },
  ],
  pseudocode: [
    "dp[0] = true",
    "for start in 0..n:",
    "  if not dp[start]: continue",
    "  for word in words:",
    "    if text[start:].startswith(word): dp[start + len(word)] = true",
    "return dp[n]",
  ],
  parse: parseWordBreak,
  generate: (input) => generateWordBreak(input as WordBreakInput),
};
