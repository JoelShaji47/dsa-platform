import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export type MinStackOp = { kind: "push"; x: number } | { kind: "pop" | "top" | "getMin" };

export interface MinStackInput {
  ops: MinStackOp[];
}

export function parseMinStack(raw: string): MinStackInput {
  const parts = raw.split(/[,;]+/).map((s) => s.trim()).filter(Boolean);
  if (parts.length === 0) throw new Error("Enter ops like: push 3, push 5, getMin, pop");
  if (parts.length > 12) throw new Error("Keep it to 12 ops so the trace stays readable");
  const ops: MinStackOp[] = parts.map((p) => {
    const m = p.match(/^push\s+(-?\d+)$/i);
    if (m) return { kind: "push", x: Number(m[1]) };
    const k = p.toLowerCase();
    if (k === "pop") return { kind: "pop" };
    if (k === "top") return { kind: "top" };
    if (k === "getmin") return { kind: "getMin" };
    throw new Error(`Bad op '${p}' — use push N, pop, top, getMin`);
  });
  return { ops };
}

export function generateMinStack({ ops }: MinStackInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const main: number[] = [];
  const mins: number[] = [];
  const snap2 = (activeMain: number[] = [], activeMin: number[] = []) => ({
    stack: snapStack(main, { active: activeMain, label: "stack" }),
    stackAlt: snapStack(mins, { active: activeMin, label: "min-stack" }),
  });
  steps.push(
    step(0, "Start", "Two stacks: main holds everything, min-stack's top is always the current minimum.", 0, snap([]), {}, snap2())
  );
  for (const op of ops) {
    if (op.kind === "push") {
      main.push(op.x);
      const newMin = mins.length === 0 || op.x <= mins[mins.length - 1];
      if (newMin) mins.push(op.x);
      steps.push(
        step(
          steps.length, `push ${op.x}`,
          newMin ? `${op.x} is a new minimum (or tied) — push to both stacks.` : `${op.x} is above the current min ${mins[mins.length - 1]} — main stack only.`,
          0, snap([]), { x: op.x }, snap2([main.length - 1], newMin ? [mins.length - 1] : [])
        )
      );
      continue;
    }
    if (op.kind === "pop") {
      if (main.length === 0) {
        steps.push(step(steps.length, "pop", "Stack is empty — nothing to pop.", 1, snap([]), {}, { ...snap2(), done: true }));
        return steps;
      }
      const out = main.pop()!;
      const droppedMin = mins.length > 0 && out === mins[mins.length - 1];
      if (droppedMin) mins.pop();
      steps.push(
        step(
          steps.length, "pop",
          droppedMin ? `Popped ${out} — it was the minimum, so pop min-stack too.` : `Popped ${out} — minimum stays ${mins.length ? mins[mins.length - 1] : "—"}.`,
          1, snap([]), { popped: out }, snap2()
        )
      );
      continue;
    }
    if (op.kind === "top") {
      const t = main.length ? main[main.length - 1] : null;
      steps.push(
        step(steps.length, "top", t == null ? "Stack is empty." : `Top of main stack is ${t}.`, 2, snap([]), t == null ? {} : { top: t }, snap2(t == null ? [] : [main.length - 1]))
      );
      continue;
    }
    const m = mins.length ? mins[mins.length - 1] : null;
    steps.push(
      step(steps.length, "getMin", m == null ? "Stack is empty." : `Top of min-stack is ${m} — O(1), no scan.`, 3, snap([]), m == null ? {} : { min: m }, snap2([], m == null ? [] : [mins.length - 1]))
    );
  }
  const m = mins.length ? mins[mins.length - 1] : "—";
  steps.push(
    step(steps.length, "Done", `Final minimum is ${m}. Min-stack keeps every minimum ever pushed, so pops restore older ones.`, 3, snap([]), {}, { ...snap2(), result: String(m), done: true })
  );
  return steps;
}

export const minStackEntry: VisualizerEntry = {
  slug: "min-stack",
  title: "Min Stack",
  inputHint: "push 3, push 5, getMin, push 2, getMin, pop, getMin",
  defaultInput: "push 3, push 5, getMin, push 2, getMin, pop, getMin",
  presets: [
    { label: "Basic", value: "push 3, push 5, getMin, push 2, getMin, pop, getMin" },
    { label: "Duplicates", value: "push 2, push 2, getMin, pop, getMin" },
    { label: "Descending", value: "push 5, push 3, push 1, getMin, pop, getMin" },
  ],
  pseudocode: [
    "push(x): stack.push(x); if min empty or x <= min.top: min.push(x)",
    "pop(): if stack.pop() == min.top: min.pop()",
    "top(): return stack.top",
    "getMin(): return min.top",
  ],
  parse: (raw: string) => parseMinStack(raw),
  generate: (input: unknown) => generateMinStack(input as MinStackInput),
};
