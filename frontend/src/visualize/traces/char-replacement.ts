import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface CharReplacementInput {
  chars: string[];
  k: number;
}

export function parseCharReplacement(raw: string): CharReplacementInput {
  const parts = raw.split(",").map((s) => s.trim());
  if (parts.length !== 2) throw new Error("Use the form AABABBA, 1");
  const chars = [...parts[0].replace(/["'\s]/g, "")];
  if (chars.length < 2) throw new Error("Enter a string like AABABBA, 1");
  if (chars.length > 12) throw new Error("Keep it to 12 characters so the trace stays readable");
  const k = Number(parts[1]);
  if (!Number.isInteger(k) || k < 0) throw new Error("k must be a non-negative integer, e.g. AABABBA, 1");
  return { chars, k };
}

export function generateCharReplacement({ chars, k }: CharReplacementInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const freq = new Map<string, number>();
  let left = 0;
  let best = 0;
  let maxf = 0;
  steps.push(
    step(0, "Start", `Window stays valid while (length − most-common count) ≤ ${k} replacements.`, 0, snap(chars), { k, left, best })
  );
  for (let right = 0; right < chars.length; right++) {
    const ch = chars[right];
    freq.set(ch, (freq.get(ch) ?? 0) + 1);
    maxf = Math.max(maxf, freq.get(ch)!);
    steps.push(
      step(
        steps.length, "Expand", `Add '${ch}' at ${right} — most common in window appears ${maxf} time(s).`,
        1, snap(chars, { active: [right], pointers: { left, right } }), { left, right, maxf }
      )
    );
    let need = right - left + 1 - maxf;
    while (need > k) {
      const out = chars[left];
      freq.set(out, freq.get(out)! - 1);
      left++;
      need = right - left + 1 - maxf;
      steps.push(
        step(
          steps.length, "Shrink", `Needs ${right - left + 1 + 1 - maxf} replacements but only ${k} allowed — drop '${out}', left → ${left}.`,
          2, snap(chars, { active: [right], pointers: { left, right } }), { left, right, maxf }
        )
      );
    }
    const len = right - left + 1;
    if (len > best) {
      best = len;
      steps.push(
        step(
          steps.length, "New best", `Window '${chars.slice(left, right + 1).join("")}' needs ${len - maxf} replacement(s) — length ${best}, best so far.`,
          3, snap(chars, { active: chars.map((_, idx) => idx).slice(left, right + 1), settled: chars.map((_, idx) => idx).slice(left, right + 1), pointers: { left, right } }), { left, right, best }
        )
      );
    }
  }
  steps.push(
    step(steps.length, "Done", `Longest replaceable run with k=${k} has length ${best}.`, 3, snap(chars, { settled: chars.map((_, idx) => idx) }), { best }, { result: String(best), done: true })
  );
  return steps;
}

export const charReplacementEntry: VisualizerEntry = {
  slug: "longest-repeating-character-replacement",
  title: "Longest Repeating Character Replacement",
  inputHint: "AABABBA, 1",
  defaultInput: "AABABBA, 1",
  presets: [
    { label: "Classic", value: "AABABBA, 1" },
    { label: "k = 2", value: "ABAB, 2" },
    { label: "No moves", value: "AAAA, 0" },
  ],
  pseudocode: [
    "freq = {}; left = 0; best = 0; maxf = 0",
    "for right, ch in enumerate(s):",
    "    freq[ch] += 1; maxf = max(maxf, freq[ch])",
    "    while (right-left+1) - maxf > k: drop s[left]; left += 1",
    "    best = max(best, right - left + 1)",
  ],
  parse: (raw: string) => parseCharReplacement(raw),
  generate: (input: unknown) => generateCharReplacement(input as CharReplacementInput),
};
