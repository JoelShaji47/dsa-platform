import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface CarPoolingInput {
  trips: [number, number, number][];
  capacity: number;
}

interface Event {
  position: number;
  delta: number;
  label: string;
}

export function parseCarPooling(raw: string): CarPoolingInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: n, n trip lines, then capacity");
  const n = Number(lines[0]);
  if (!Number.isInteger(n) || n < 0) throw new Error("n must be a non-negative integer");
  if (lines.length !== n + 2) throw new Error(`Expected ${n} trip lines and a capacity`);
  const trips: [number, number, number][] = [];
  for (let i = 0; i < n; i += 1) {
    const values = integersFrom(lines[i + 1]);
    if (values.length !== 3) throw new Error(`Trip ${i + 1} must contain passengers start end`);
    const [passengers, start, end] = values;
    if (passengers < 0 || start < 0 || end <= start) throw new Error("Use valid trip ranges");
    trips.push([passengers, start, end]);
  }
  const capacity = Number(lines[n + 1]);
  if (!Number.isInteger(capacity) || capacity < 0) throw new Error("Capacity must be non-negative");
  return { trips, capacity };
}

export function generateCarPooling({ trips, capacity }: CarPoolingInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const events: Event[] = [];
  for (const [passengers, start, end] of trips) {
    events.push({ position: start, delta: passengers, label: `+${passengers}@${start}` });
    events.push({ position: end, delta: -passengers, label: `-${passengers}@${end}` });
  }
  events.sort((a, b) => a.position - b.position || a.delta - b.delta);

  const eventSnap = (active: number[] = [], settled: number[] = []) =>
    snap(events.map((event) => event.label), { active, settled, label: "events (position order)" });
  const deltaSnap = (active: number[] = []) =>
    snap(events.map((event) => event.delta), { active, label: "passenger delta" });

  let onboard = 0;
  let feasible = true;

  steps.push(
    step(0, "Sort", "Process pickups and drop-offs in position order; drop-offs come first at the same stop.", 0, eventSnap(), { capacity, onboard }, { arrayAlt: deltaSnap() })
  );

  for (let i = 0; i < events.length; i += 1) {
    const event = events[i];
    onboard += event.delta;
    if (onboard > capacity) feasible = false;
    steps.push(
      step(
        steps.length,
        event.delta > 0 ? "Pick up" : "Drop off",
        `${event.label} changes the passenger count to ${onboard}${onboard > capacity ? `, which exceeds capacity ${capacity}` : ""}.`,
        2,
        eventSnap([i], Array.from({ length: i }, (_, index) => index)),
        { position: event.position, onboard, capacity, feasible: feasible ? "true" : "false" },
        { arrayAlt: deltaSnap([i]) }
      )
    );
  }

  steps.push(
    step(
      steps.length,
      "Done",
      feasible ? `Every segment stays within capacity ${capacity}.` : `The load exceeds capacity ${capacity} at some point.`,
      3,
      eventSnap([], events.map((_, index) => index)),
      { feasible: feasible ? "true" : "false" },
      { arrayAlt: deltaSnap(), done: true, result: feasible ? "true" : "false" }
    )
  );

  return steps;
}

export const carPoolingEntry: VisualizerEntry = {
  slug: "car-pooling",
  title: "Car Pooling",
  inputHint: "n, then n lines of passengers start end, then capacity",
  defaultInput: "2\n2 1 5\n3 3 7\n4",
  presets: [
    { label: "over capacity", value: "2\n2 1 5\n3 3 7\n4" },
    { label: "fits", value: "2\n2 1 5\n3 3 7\n5" },
    { label: "no trips", value: "0\n0" },
  ],
  pseudocode: [
    "events = pickups (+passengers) and drop-offs (-passengers)",
    "sort events by position, drop-offs first on ties",
    "running = 0",
    "for each event: running += delta",
    "  if running > capacity: return false",
    "return true",
  ],
  parse: parseCarPooling,
  generate: (input) => generateCarPooling(input as CarPoolingInput),
};
