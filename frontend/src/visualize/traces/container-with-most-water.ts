import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface ContainerInput {
  height: number[];
}

export function parseContainer(raw: string): ContainerInput {
  const bracket = raw.trim().match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [1, 8, 6, 2, 5, 4, 8, 3, 7]");
  const height = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (height.length < 2 || height.some((n) => !Number.isFinite(n) || n < 0)) {
    throw new Error("Need at least 2 non-negative heights, e.g. [1, 8, 6, 2, 5, 4, 8, 3, 7]");
  }
  if (height.length > 12) throw new Error("Keep it to 12 bars so the trace stays readable");
  return { height };
}

export function generateContainer({ height }: ContainerInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let left = 0;
  let right = height.length - 1;
  let best = 0;
  steps.push(
    step(0, "Start", "Widest container first. Each step keeps the taller wall and moves the shorter one in.", 0,
      snap(height, { pointers: { left, right } }), { left, right, best })
  );
  while (left < right) {
    const h = Math.min(height[left], height[right]);
    const area = h * (right - left);
    steps.push(
      step(steps.length, "Measure", `min(${height[left]}, ${height[right]}) × width ${right - left} = ${area}. Best so far: ${best}.`, 1,
        snap(height, { active: [left, right], pointers: { left, right } }), { left, right, area, best })
    );
    if (area > best) {
      best = area;
      steps.push(
        step(steps.length, "New best", `New record: ${best}. The pair (${left}, ${right}) is the best so far.`, 2,
          snap(height, { active: [left, right], settled: [left, right], pointers: { left, right } }), { best })
      );
    }
    if (height[left] < height[right]) {
      left++;
      steps.push(
        step(steps.length, "Move left", `Left wall (${height[left - 1]}) is shorter — moving it in can only help. left → ${left}.`, 3,
          snap(height, { pointers: { left, right } }), { left, right, best })
      );
    } else {
      right--;
      steps.push(
        step(steps.length, "Move right", `Right wall (${height[right + 1]}) is shorter or equal — moving it in can only help. right → ${right}.`, 3,
          snap(height, { pointers: { left, right } }), { left, right, best })
      );
    }
  }
  steps.push(
    step(steps.length, "Done", `Walls met. Maximum water: ${best}.`, 4,
      snap(height, {}), { best }, { result: `${best}`, done: true })
  );
  return steps;
}

export const containerEntry: VisualizerEntry = {
  slug: "container-with-most-water",
  title: "Container With Most Water",
  inputHint: "[1, 8, 6, 2, 5, 4, 8, 3, 7]",
  defaultInput: "[1, 8, 6, 2, 5, 4, 8, 3, 7]",
  presets: [
    { label: "Classic (49)", value: "[1, 8, 6, 2, 5, 4, 8, 3, 7]" },
    { label: "Two bars", value: "[1, 1]" },
    { label: "Descending", value: "[5, 4, 3, 2, 1]" },
  ],
  pseudocode: [
    "left = 0, right = n - 1, best = 0",
    "while left < right: area = min(h[left], h[right]) * (right - left)",
    "    best = max(best, area)",
    "    move the shorter wall inward",
    "return best",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseContainer(raw),
  generate: (input: unknown) => generateContainer(input as ContainerInput),
};
