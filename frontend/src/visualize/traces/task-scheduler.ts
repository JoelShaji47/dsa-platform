import { snap, snapQueue, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface TaskSchedulerInput {
  tasks: string;
  cooldown: number;
}

export function parseTaskScheduler(raw: string): TaskSchedulerInput {
  const match = raw.match(/^(.*),\s*(-?\d+)\s*$/);
  if (!match) throw new Error("Use the form AAABBB, 2");
  const tasks = (match[1].match(/[A-Za-z]/g) ?? []).map((c) => c.toUpperCase()).join("");
  const cooldown = Number(match[2]);
  if (tasks.length < 1) throw new Error("Add at least one task letter, e.g. AAABBB, 2");
  if (tasks.length > 8) throw new Error("Keep it to 8 tasks so the trace stays readable");
  if (!Number.isInteger(cooldown) || cooldown < 0 || cooldown > 4) {
    throw new Error("Cooldown must be an integer from 0 to 4");
  }
  return { tasks, cooldown };
}

export function generateTaskScheduler({ tasks, cooldown }: TaskSchedulerInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const counts = new Map<string, number>();
  for (const task of tasks) counts.set(task, (counts.get(task) ?? 0) + 1);
  const letters = [...counts.keys()].sort();
  const cooldownQueue: { task: string; ready: number }[] = [];

  const countSnap = (activeTask?: string) => {
    const active = activeTask == null ? [] : [letters.indexOf(activeTask)];
    const settled = letters
      .map((task, index) => ((counts.get(task) ?? 0) === 0 ? index : -1))
      .filter((index) => index >= 0);
    return snap(
      letters.map((task) => `${task}:${counts.get(task) ?? 0}`),
      { active, settled }
    );
  };
  const queueSnap = (active: number[] = []) =>
    snapQueue(
      cooldownQueue.map((entry) => `${entry.task}→${entry.ready}`),
      { active, label: "cooldown queue (ready time)" }
    );
  const available = () =>
    [...counts.entries()]
      .filter(([task, count]) => count > 0 && !cooldownQueue.some((entry) => entry.task === task))
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

  let time = 0;
  steps.push(
    step(
      0,
      "Start",
      `Schedule ${tasks.length} tasks with a ${cooldown}-slot cooldown. The queue holds tasks waiting to become available again.`,
      0,
      countSnap(),
      { time, cooldown },
      { queue: queueSnap() }
    )
  );

  while (letters.some((task) => (counts.get(task) ?? 0) > 0) || cooldownQueue.length > 0) {
    const released = cooldownQueue.filter((entry) => entry.ready <= time);
    if (released.length > 0) {
      for (const entry of released) {
        const index = cooldownQueue.indexOf(entry);
        if (index >= 0) cooldownQueue.splice(index, 1);
      }
      steps.push(
        step(
          steps.length,
          "Release",
          `${released.map((entry) => entry.task).join(", ")} cooled down at time ${time} — back in the available pool.`,
          3,
          countSnap(),
          { time, released: released.map((entry) => entry.task).join(", ") },
          { queue: queueSnap() }
        )
      );
    }

    const avail = available();
    if (avail.length > 0) {
      const [task] = avail[0];
      const before = counts.get(task) ?? 0;
      counts.set(task, before - 1);
      const queued = before - 1 > 0;
      const ready = time + cooldown + 1;
      if (queued) cooldownQueue.push({ task, ready });
      steps.push(
        step(
          steps.length,
          `Pick ${task}`,
          `Pick the most frequent available task (${task}). ${before} → ${before - 1} remaining.`,
          5,
          countSnap(task),
          { time, task, remaining: before - 1 },
          { queue: queueSnap() }
        )
      );
      if (queued) {
        steps.push(
          step(
            steps.length,
            "Cooldown",
            `${task} still has ${before - 1} copy/copies — it cannot run again until time ${ready}.`,
            6,
            countSnap(task),
            { time, task, ready },
            { queue: queueSnap([cooldownQueue.length - 1]) }
          )
        );
      }
    } else {
      steps.push(
        step(
          steps.length,
          "Idle",
          `Nothing is available at time ${time} — the CPU idles for one interval.`,
          7,
          countSnap(),
          { time },
          { queue: queueSnap() }
        )
      );
    }
    time += 1;
  }

  steps.push(
    step(
      steps.length,
      "Done",
      `All tasks finished. Minimum intervals: ${time}.`,
      9,
      countSnap(),
      { time },
      { queue: queueSnap(), result: String(time), done: true }
    )
  );
  return steps;
}

export const taskSchedulerEntry: VisualizerEntry = {
  slug: "task-scheduler",
  title: "Task Scheduler",
  inputHint: "AAABBB, 2",
  defaultInput: "AAABBB, 2",
  presets: [
    { label: "Classic", value: "AAABBB, 2" },
    { label: "Tight", value: "AAAB, 2" },
    { label: "No cooldown", value: "A, 0" },
  ],
  pseudocode: [
    "count = Counter(tasks)",
    "time = 0; cooldown = deque()",
    "while any(count) or cooldown:",
    "    release tasks with ready <= time",
    "    available = tasks with count > 0 and not cooling",
    "    pick the most frequent available task; count -= 1",
    "    if count > 0: cooldown.append((task, time + n + 1))",
    "    else if no available task: idle",
    "    time += 1",
    "return time",
  ],
  parse: (raw: string) => parseTaskScheduler(raw),
  generate: (input: unknown) => generateTaskScheduler(input as TaskSchedulerInput),
};
