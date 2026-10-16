import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface EvalRpnInput {
  tokens: string[];
}

const OPS = new Set(["+", "-", "*", "/"]);

export function parseEvalRpn(raw: string): EvalRpnInput {
  const tokens = raw.replace(/,/g, " ").split(/\s+/).filter(Boolean);
  if (tokens.length < 3) throw new Error("Enter tokens like: 2 1 + 3 *");
  if (tokens.length > 20) throw new Error("Keep it to 20 tokens so the trace stays readable");
  if (tokens.some((t) => !OPS.has(t) && !/^-?\d+$/.test(t))) {
    throw new Error("Only integers and + - * /, e.g. 2 1 + 3 *");
  }
  return { tokens };
}

export function generateEvalRpn({ tokens }: EvalRpnInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const stack: number[] = [];
  steps.push(
    step(0, "Start", "Numbers get pushed; an operator pops two operands and pushes the result.", 0, snap(tokens), {}, { stack: snapStack([], { label: "stack" }) })
  );
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (!OPS.has(t)) {
      stack.push(Number(t));
      steps.push(
        step(
          steps.length, `Push ${t}`, `'${t}' is a number — push it.`,
          1, snap(tokens, { active: [i], pointers: { i } }), { i, token: t },
          { stack: snapStack(stack, { active: [stack.length - 1], label: "stack" }) }
        )
      );
      continue;
    }
    const b = stack.pop()!;
    const a = stack.pop()!;
    let r: number;
    if (t === "+") r = a + b;
    else if (t === "-") r = a - b;
    else if (t === "*") r = a * b;
    else r = Math.trunc(a / b);
    stack.push(r);
    steps.push(
      step(
        steps.length, `Apply ${t}`, `'${t}': pop ${a} and ${b}, push ${a} ${t} ${b} = ${r}${t === "/" ? " (truncated toward zero)" : ""}.`,
        2, snap(tokens, { active: [i], pointers: { i } }), { i, a, b, r },
        { stack: snapStack(stack, { active: [stack.length - 1], label: "stack" }) }
      )
    );
  }
  const result = stack[stack.length - 1];
  steps.push(
    step(steps.length, "Result", `One value left on the stack: ${result}.`, 3, snap(tokens, { settled: tokens.map((_, k) => k) }), { result }, { stack: snapStack(stack, { active: [stack.length - 1], label: "stack" }), result: String(result), done: true })
  );
  return steps;
}

export const evalRpnEntry: VisualizerEntry = {
  slug: "evaluate-reverse-polish-notation",
  title: "Evaluate Reverse Polish Notation",
  inputHint: "2 1 + 3 *",
  defaultInput: "2 1 + 3 *",
  presets: [
    { label: "Basic", value: "2 1 + 3 *" },
    { label: "Division", value: "4 13 5 / +" },
    { label: "Subtraction", value: "10 6 9 3 + -11 * / * 17 + 5 +" },
  ],
  pseudocode: [
    "stack = []",
    "for token in tokens:",
    "    if token is number: stack.push(token)",
    "    else: b, a = pop, pop; push(a op b)",
    "return stack.top",
  ],
  parse: (raw: string) => parseEvalRpn(raw),
  generate: (input: unknown) => generateEvalRpn(input as EvalRpnInput),
};
