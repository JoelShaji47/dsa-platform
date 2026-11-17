import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { countedNumbers } from "./input-utils";

export interface AsteroidCollisionInput {
  asteroids: number[];
}

export function parseAsteroidCollision(raw: string): AsteroidCollisionInput {
  const { values } = countedNumbers(raw);
  if (values.length === 0) throw new Error("Use at least one asteroid");
  if (values.length > 12) throw new Error("Keep it to 12 asteroids");
  if (values.some((value) => value === 0)) throw new Error("Asteroid sizes cannot be zero");
  return { asteroids: values };
}

export function generateAsteroidCollision({ asteroids }: AsteroidCollisionInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const stack: number[] = [];

  const stackSnap = (active: number[] = []) =>
    snapStack(stack, { active, label: "survivors" });

  steps.push(
    step(0, "Start", "Positive asteroids move right, negative ones move left; only opposing neighbors collide.", 0, snap(asteroids), {}, { stack: stackSnap() })
  );

  for (let i = 0; i < asteroids.length; i += 1) {
    const asteroid = asteroids[i];
    let alive = true;

    if (asteroid > 0) {
      stack.push(asteroid);
      steps.push(
        step(
          steps.length,
          "Move right",
          `${asteroid} moves right; nothing can collide until a left-mover appears.`,
          2,
          snap(asteroids, { active: [i], pointers: { i } }),
          { asteroid },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
      continue;
    }

    while (alive && stack.length > 0 && stack[stack.length - 1] > 0) {
      const top = stack[stack.length - 1];
      if (top < -asteroid) {
        stack.pop();
        steps.push(
          step(
            steps.length,
            "Destroy right",
            `${asteroid} destroys ${top} and keeps moving left.`,
            3,
            snap(asteroids, { active: [i], settled: [], pointers: { i } }),
            { asteroid, destroyed: top },
            { stack: stackSnap(stack.length ? [stack.length - 1] : []) }
          )
        );
      } else if (top === -asteroid) {
        stack.pop();
        alive = false;
        steps.push(
          step(
            steps.length,
            "Both explode",
            `${asteroid} and ${top} are equal; both are destroyed.`,
            3,
            snap(asteroids, { active: [i], pointers: { i } }),
            { asteroid, destroyed: top },
            { stack: stackSnap() }
          )
        );
      } else {
        alive = false;
        steps.push(
          step(
            steps.length,
            "Destroy left",
            `${top} is larger and destroys ${asteroid}.`,
            3,
            snap(asteroids, { active: [i], pointers: { i } }),
            { asteroid, destroyed: top },
            { stack: stackSnap([stack.length - 1]) }
          )
        );
      }
    }

    if (alive) {
      stack.push(asteroid);
      steps.push(
        step(
          steps.length,
          "Move left",
          `${asteroid} survives and joins the stack.`,
          4,
          snap(asteroids, { active: [i], pointers: { i } }),
          { asteroid },
          { stack: stackSnap([stack.length - 1]) }
        )
      );
    }
  }

  const result = stack.join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      stack.length ? `The surviving asteroids are ${result}.` : "Every asteroid was destroyed.",
      5,
      snap(asteroids, { settled: asteroids.map((_, index) => index) }),
      { survivors: stack.length },
      { stack: stackSnap(stack.map((_, index) => index)), done: true, result }
    )
  );

  return steps;
}

export const asteroidCollisionEntry: VisualizerEntry = {
  slug: "asteroid-collision",
  title: "Asteroid Collision",
  inputHint: "n, then n signed asteroid sizes",
  defaultInput: "3\n5 10 -5",
  presets: [
    { label: "example", value: "3\n5 10 -5" },
    { label: "annihilation", value: "2\n8 -8" },
    { label: "chain", value: "3\n10 2 -5" },
  ],
  pseudocode: [
    "stack = []",
    "for asteroid in asteroids:",
    "  while asteroid moves left and stack top moves right:",
    "    resolve the collision",
    "  push the survivor",
    "return stack",
  ],
  parse: parseAsteroidCollision,
  generate: (input) => generateAsteroidCollision(input as AsteroidCollisionInput),
};
