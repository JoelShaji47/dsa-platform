import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";

export interface GroupAnagramsInput {
  words: string[];
}

export function parseGroupAnagrams(raw: string): GroupAnagramsInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n, then n words");
  const count = Number(lines[0]);
  if (!Number.isInteger(count) || count < 1) throw new Error("The first line must be a count");
  const words = lines
    .slice(1)
    .flatMap((line) => line.split(/\s+/))
    .filter(Boolean);
  if (words.length !== count) throw new Error(`Expected ${count} words, received ${words.length}`);
  if (words.some((word) => !/^[a-z]+$/.test(word))) throw new Error("Use lowercase words only");
  if (words.length === 0) throw new Error("Use at least one word");
  if (words.length > 10) throw new Error("Keep it to 10 words");
  if (words.some((word) => word.length > 8)) throw new Error("Keep each word to 8 letters");
  return { words };
}

function signature(word: string): string {
  return [...word].sort().join("");
}

export function generateGroupAnagrams({ words }: GroupAnagramsInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const groups = new Map<string, string[]>();

  const wordsSnap = (active: number[] = [], settled: number[] = []) =>
    snap(words, { active, settled, pointers: {}, label: "words" });
  const groupsSnap = () =>
    snap(
      [...groups.entries()].map(([key, values]) => `${key}: ${values.join(" ")}`),
      { label: "groups" }
    );

  steps.push(
    step(0, "Start", "Two words belong together when their sorted letters match.", 0, wordsSnap(), {}, { arrayAlt: groupsSnap() })
  );

  for (let i = 0; i < words.length; i += 1) {
    const key = signature(words[i]);
    const group = groups.get(key) ?? [];
    group.push(words[i]);
    groups.set(key, group);
    steps.push(
      step(
        steps.length,
        "Group",
        `"${words[i]}" sorts to "${key}", so it joins that group.`,
        2,
        wordsSnap([i], Array.from({ length: i }, (_, index) => index)),
        { word: words[i], key },
        { arrayAlt: groupsSnap() }
      )
    );
  }

  const resultGroups = [...groups.values()]
    .map((group) => [...group].sort())
    .sort((a, b) => a[0].localeCompare(b[0]));
  const result = resultGroups.map((group) => group.join(" ")).join("\n");

  steps.push(
    step(
      steps.length,
      "Done",
      `Found ${resultGroups.length} anagram group${resultGroups.length === 1 ? "" : "s"}.`,
      3,
      wordsSnap([], words.map((_, index) => index)),
      { groups: resultGroups.length },
      { arrayAlt: groupsSnap(), done: true, result }
    )
  );

  return steps;
}

export const groupAnagramsEntry: VisualizerEntry = {
  slug: "group-anagrams",
  title: "Group Anagrams",
  inputHint: "n, then n words",
  defaultInput: "6\neat tea tan ate nat bat",
  presets: [
    { label: "example", value: "6\neat tea tan ate nat bat" },
    { label: "none", value: "3\nabc def ghi" },
    { label: "all", value: "3\nabc bca cab" },
  ],
  pseudocode: [
    "groups = empty map",
    "for each word:",
    "  key = sorted letters of word",
    "  append word to groups[key]",
    "return groups",
  ],
  parse: parseGroupAnagrams,
  generate: (input) => generateGroupAnagrams(input as GroupAnagramsInput),
};
