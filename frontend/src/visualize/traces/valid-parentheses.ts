import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface ValidParenthesesInput {
  chars: string[];
}

const OPEN = new Set(["(", "[", "{"]);
const MATCH: Record<string, string> = { ")": "(", "]": "[", "}": "{" };

export function parseValidParentheses(raw: string): ValidParenthesesInput {
  const cleaned = raw.replace(/["'\s,]/g, "");
  if (cleaned.length < 2) throw new Error("Enter brackets like ()[]{}");
  if (cleaned.length > 12) throw new Error("Keep it to 12 brackets so the trace stays readable");
  const chars = [...cleaned];
  if (chars.some((c) => !OPEN.has(c) && !(c in MATCH))) {
    throw new Error("Only ( ) [ ] { } characters, e.g. ()[]{}");
  }
  return { chars };
}

export function generateValidParentheses({ chars }: ValidParenthesesInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const stack: string[] = [];
  steps.push(
    step(0, "Start", `Scan ${chars.length} brackets. Openers get pushed; closers must match the top.`, 0, snap(chars), {}, { stack: snapStack([], { label: "stack" }) })
  );
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i];
    if (OPEN.has(ch)) {
      stack.push(ch);
      steps.push(
        step(
          steps.length, "Push", `'${ch}' is an opener — push it.`,
          2, snap(chars, { active: [i], pointers: { i } }), { i, ch },
          { stack: snapStack(stack, { active: [stack.length - 1], label: "stack" }) }
        )
      );
      continue;
    }
    const want = MATCH[ch];
    steps.push(
      step(
        steps.length, "Check", `'${ch}' is a closer — it needs '${want}' on top.`,
        3, snap(chars, { active: [i], pointers: { i } }), { i, ch },
        { stack: snapStack(stack, { active: stack.length ? [stack.length - 1] : [], label: "stack" }) }
      )
    );
    const top = stack.pop();
    if (top !== want) {
      steps.push(
        step(
          steps.length, "Mismatch", top == null ? `Stack is empty but '${ch}' needs a match — invalid.` : `Top is '${top}', not '${want}' — invalid.`,
          3, snap(chars, { active: [i], pointers: { i } }), { i, ch },
          { stack: snapStack(stack, { label: "stack" }), result: "false", done: true }
        )
      );
      return steps;
    }
    steps.push(
      step(
        steps.length, "Pop", `Top '${top}' matches '${ch}' — pop it.`,
        3, snap(chars, { settled: [i], pointers: { i } }), { i, ch },
        { stack: snapStack(stack, { label: "stack" }) }
      )
    );
  }
  const valid = stack.length === 0;
  steps.push(
    step(
      steps.length, valid ? "Valid" : "Leftover", valid ? "Every bracket matched and the stack is empty — valid." : `${stack.length} opener(s) never closed — invalid.`,
      4, snap(chars, { settled: chars.map((_, k) => k) }), {},
      { stack: snapStack(stack, { label: "stack" }), result: String(valid), done: true }
    )
  );
  return steps;
}

export const validParenthesesEntry: VisualizerEntry = {
  slug: "valid-parentheses",
  title: "Valid Parentheses",
  inputHint: "()[]{}",
  defaultInput: "()[]{}",
  presets: [
    { label: "Mixed", value: "()[]{}" },
    { label: "Nested", value: "{[()]}" },
    { label: "Mismatch", value: "([)]" },
  ],
  pseudocode: [
    "stack = []",
    "for ch in s:",
    "    if ch is opener: stack.push(ch)",
    "    elif stack empty or stack.pop() != match(ch): return False",
    "return stack is empty",
  ],
  parse: (raw: string) => parseValidParentheses(raw),
  generate: (input: unknown) => generateValidParentheses(input as ValidParenthesesInput),
};
