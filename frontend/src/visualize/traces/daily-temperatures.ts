import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface DailyTemperaturesInput {
  temps: number[];
}

export function parseDailyTemperatures(raw: string): DailyTemperaturesInput {
  const cleaned = raw.replace(/[\[\]]/g, " ").trim();
  const temps = cleaned.split(/[\s,]+/).filter(Boolean).map(Number);
  if (temps.length < 2 || temps.some((n) => !Number.isFinite(n))) {
    throw new Error("Enter temperatures like [73, 74, 75, 71, 69, 72, 76, 73]");
  }
  if (temps.length > 12) throw new Error("Keep it to 12 days so the trace stays readable");
  return { temps };
}

export function generateDailyTemperatures({ temps }: DailyTemperaturesInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const ans = new Array<number>(temps.length).fill(0);
  const stack: number[] = [];
  const snap2 = (activeStack: number[] = []) => ({
    stack: snapStack(stack, { active: activeStack, label: "waiting (indices)" }),
  });
  steps.push(
    step(0, "Start", "Keep a stack of indices still waiting for a warmer day. It stays decreasing.", 0, snap(temps), {}, snap2())
  );
  for (let i = 0; i < temps.length; i++) {
    steps.push(
      step(
        steps.length, `Day ${i}`, `Temperature ${temps[i]}. Resolve every waiting day colder than it.`,
        2, snap(temps, { active: [i], pointers: { i } }), { i, t: temps[i] }, snap2(stack.length ? [stack.length - 1] : [])
      )
    );
    while (stack.length > 0 && temps[i] > temps[stack[stack.length - 1]]) {
      const j = stack.pop()!;
      ans[j] = i - j;
      steps.push(
        step(
          steps.length, `Resolve ${j}`, `Day ${j} (${temps[j]}°) waited ${i - j} day(s) for ${temps[i]}° — pop it.`,
          3, snap(temps, { active: [j, i], settled: ans.map((a, k) => (a > 0 ? k : -1)).filter((k) => k >= 0), pointers: { i } }), { j, wait: ans[j] }, snap2()
        )
      );
    }
    stack.push(i);
    steps.push(
      step(
        steps.length, `Wait ${i}`, `No warmer day yet for ${temps[i]}° — push index ${i} and move on.`,
        4, snap(temps, { active: [i], pointers: { i } }), { i }, snap2([stack.length - 1])
      )
    );
  }
  steps.push(
    step(steps.length, "Done", `Days left in the stack never see warmth — they stay 0. Answer: [${ans}].`, 4, snap(temps, { settled: temps.map((_, k) => k) }), {}, { ...snap2(), result: `[${ans}]`, done: true })
  );
  return steps;
}

export const dailyTemperaturesEntry: VisualizerEntry = {
  slug: "daily-temperatures",
  title: "Daily Temperatures",
  inputHint: "[73, 74, 75, 71, 69, 72, 76, 73]",
  defaultInput: "[73, 74, 75, 71, 69, 72, 76, 73]",
  presets: [
    { label: "Classic", value: "[73, 74, 75, 71, 69, 72, 76, 73]" },
    { label: "Rising", value: "[30, 40, 50, 60]" },
    { label: "Falling", value: "[60, 50, 40, 30]" },
  ],
  pseudocode: [
    "ans = [0] * n; stack = []",
    "for i, t in enumerate(temps):",
    "    while stack and t > temps[stack.top]:",
    "        j = stack.pop(); ans[j] = i - j",
    "    stack.push(i)",
  ],
  parse: (raw: string) => parseDailyTemperatures(raw),
  generate: (input: unknown) => generateDailyTemperatures(input as DailyTemperaturesInput),
};
