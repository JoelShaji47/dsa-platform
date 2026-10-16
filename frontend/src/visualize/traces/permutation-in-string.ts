import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface PermutationInStringInput {
  pattern: string[];
  text: string[];
}

export function parsePermutationInString(raw: string): PermutationInStringInput {
  const parts = raw.split(",").map((s) => s.replace(/["'\s]/g, ""));
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new Error("Use the form ab, eidbaooo");
  }
  const [p, t] = parts;
  if (p.length > 6) throw new Error("Keep the pattern to 6 characters");
  if (t.length > 12) throw new Error("Keep the text to 12 characters so the trace stays readable");
  if (p.length > t.length) throw new Error("Pattern is longer than the text — no permutation fits");
  return { pattern: [...p], text: [...t] };
}

function counts(chars: string[]): Map<string, number> {
  const m = new Map<string, number>();
  for (const c of chars) m.set(c, (m.get(c) ?? 0) + 1);
  return m;
}

export function generatePermutationInString({ pattern, text }: PermutationInStringInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const need = counts(pattern);
  const k = pattern.length;
  let left = 0;
  steps.push(
    step(0, "Start", `Slide a window of size ${k} over '${text.join("")}' and compare letter counts to '${pattern.join("")}'.`, 0, snap(text), { k })
  );
  for (let right = 0; right < text.length; right++) {
    if (right - left + 1 > k) left++;
    const win = text.slice(left, right + 1);
    const winCounts = counts(win);
    const full = win.length === k;
    const match = full && [...need.entries()].every(([c, n]) => winCounts.get(c) === n);
    steps.push(
      step(
        steps.length, full ? (match ? "Match" : "Slide") : "Grow",
        full
          ? (match ? `Window '${win.join("")}' has the same counts — found it.` : `Window '${win.join("")}' doesn't match — slide on.`)
          : `Window '${win.join("")}' is still growing to size ${k}.`,
        full ? 3 : 1, snap(text, { active: text.map((_, idx) => idx).slice(left, right + 1), pointers: { left, right } }),
        { left, right, window: win.join("") },
        match ? { result: "true", done: true } : {}
      )
    );
    if (match) return steps;
  }
  steps.push(
    step(steps.length, "No match", `No window of size ${k} permutes '${pattern.join("")}'.`, 3, snap(text, { settled: text.map((_, idx) => idx) }), {}, { result: "false", done: true })
  );
  return steps;
}

export const permutationInStringEntry: VisualizerEntry = {
  slug: "permutation-in-string",
  title: "Permutation in String",
  inputHint: "ab, eidbaooo",
  defaultInput: "ab, eidbaooo",
  presets: [
    { label: "Found", value: "ab, eidbaooo" },
    { label: "Missing", value: "ab, eidboaoo" },
    { label: "Longer", value: "adc, dcda" },
  ],
  pseudocode: [
    "need = counts(s1); left = 0",
    "for right, ch in enumerate(s2):",
    "    add ch; if window > len(s1): drop s2[left]; left += 1",
    "    if window counts == need: return True",
    "return False",
  ],
  parse: (raw: string) => parsePermutationInString(raw),
  generate: (input: unknown) => generatePermutationInString(input as PermutationInStringInput),
};
