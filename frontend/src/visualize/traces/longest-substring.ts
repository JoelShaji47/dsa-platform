import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface LongestSubstringInput {
  chars: string[];
}

export function parseLongestSubstring(raw: string): LongestSubstringInput {
  const cleaned = raw.replace(/["'\s,]/g, "");
  if (cleaned.length < 2) throw new Error("Enter a string like abcabcbb");
  if (cleaned.length > 12) throw new Error("Keep it to 12 characters so the trace stays readable");
  return { chars: [...cleaned] };
}

export function generateLongestSubstring({ chars }: LongestSubstringInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const last = new Map<string, number>();
  let left = 0;
  let best = 0;
  steps.push(
    step(0, "Start", `Grow the window [left, right]; when a repeat enters, jump left past its last sighting.`, 0, snap(chars), { left, best })
  );
  for (let right = 0; right < chars.length; right++) {
    const ch = chars[right];
    const prev = last.get(ch);
    if (prev != null && prev >= left) {
      left = prev + 1;
      steps.push(
        step(
          steps.length, "Shrink", `'${ch}' was last seen at ${prev} — move left to ${left}.`,
          2, snap(chars, { active: [right], pointers: { left, right } }), { left, right, ch }
        )
      );
    } else {
      steps.push(
        step(
          steps.length, "Expand", `'${ch}' is new to the window — stretch right to ${right}.`,
          1, snap(chars, { active: [right], pointers: { left, right } }), { left, right, ch }
        )
      );
    }
    last.set(ch, right);
    const len = right - left + 1;
    if (len > best) {
      best = len;
      steps.push(
        step(
          steps.length, "New best", `Window '${chars.slice(left, right + 1).join("")}' has length ${best} — best so far.`,
          4, snap(chars, { active: chars.map((_, k) => k).slice(left, right + 1), settled: chars.map((_, k) => k).slice(left, right + 1), pointers: { left, right } }), { left, right, best }
        )
      );
    }
  }
  steps.push(
    step(steps.length, "Done", `Longest substring without repeats has length ${best}.`, 4, snap(chars, { settled: chars.map((_, k) => k) }), { best }, { result: String(best), done: true })
  );
  return steps;
}

export const longestSubstringEntry: VisualizerEntry = {
  slug: "longest-substring-without-repeating-characters",
  title: "Longest Substring Without Repeating Characters",
  inputHint: "abcabcbb",
  defaultInput: "abcabcbb",
  presets: [
    { label: "Classic", value: "abcabcbb" },
    { label: "All same", value: "bbbbb" },
    { label: "Mixed", value: "pwwkew" },
  ],
  pseudocode: [
    "last = {}; left = 0; best = 0",
    "for right, ch in enumerate(s):",
    "    if ch seen inside window: left = last[ch] + 1",
    "    last[ch] = right",
    "    best = max(best, right - left + 1)",
  ],
  parse: (raw: string) => parseLongestSubstring(raw),
  generate: (input: unknown) => generateLongestSubstring(input as LongestSubstringInput),
};
