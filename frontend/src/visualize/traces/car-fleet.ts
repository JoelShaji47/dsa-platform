import { snap, snapStack, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface CarFleetInput {
  target: number;
  positions: number[];
  speeds: number[];
}

export function parseCarFleet(raw: string): CarFleetInput {
  const lines = inputLines(raw);
  if (lines.length < 4) throw new Error("Use: target, n, positions, speeds");
  const target = Number(lines[0]);
  const n = Number(lines[1]);
  const positions = integersFrom(lines[2]);
  const speeds = integersFrom(lines[3]);
  if (!Number.isInteger(n) || n < 1) throw new Error("n must be a positive integer");
  if (positions.length !== n || speeds.length !== n) throw new Error("Provide n positions and n speeds");
  if (n > 12) throw new Error("Keep it to 12 cars");
  if (target <= 0 || positions.some((position) => position < 0) || speeds.some((speed) => speed <= 0)) {
    throw new Error("Use non-negative positions, positive speeds, and a positive target");
  }
  return { target, positions, speeds };
}

function formatTime(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

export function generateCarFleet({ target, positions, speeds }: CarFleetInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const cars = positions
    .map((position, index) => ({ position, speed: speeds[index] }))
    .sort((a, b) => b.position - a.position);
  const sortedPositions = cars.map((car) => car.position);
  const sortedSpeeds = cars.map((car) => car.speed);
  const fleetTimes: number[] = [];

  const arraySnap = (active: number[] = [], settled: number[] = []) =>
    snap(sortedPositions, { active, settled, pointers: {}, label: "positions (front first)" });
  const speedSnap = () => snap(sortedSpeeds, { label: "speeds" });
  const stackSnap = (active: number[] = []) =>
    snapStack(fleetTimes.map(formatTime), { active, label: "fleet arrival times" });

  steps.push(
    step(
      0,
      "Sort",
      "Process cars from closest to the target to farthest; a faster car behind can join the fleet ahead.",
      0,
      arraySnap(),
      { target, cars: cars.length },
      { arrayAlt: speedSnap(), stack: stackSnap() }
    )
  );

  cars.forEach((car, index) => {
    const time = (target - car.position) / car.speed;
    const ahead = fleetTimes[fleetTimes.length - 1];
    if (ahead == null || time > ahead) {
      fleetTimes.push(time);
      steps.push(
        step(
          steps.length,
          "New fleet",
          `Car at ${car.position} reaches the target at ${formatTime(time)}, after the fleet ahead, so it forms a new fleet.`,
          3,
          arraySnap([index], Array.from({ length: index }, (_, i) => i)),
          { position: car.position, time: formatTime(time), fleets: fleetTimes.length },
          { arrayAlt: speedSnap(), stack: stackSnap([fleetTimes.length - 1]) }
        )
      );
    } else {
      steps.push(
        step(
          steps.length,
          "Join fleet",
          `Car at ${car.position} would arrive at ${formatTime(time)}, but it catches the fleet ahead (${formatTime(ahead)}).`,
          2,
          arraySnap([index], Array.from({ length: index }, (_, i) => i)),
          { position: car.position, time: formatTime(time), fleets: fleetTimes.length },
          { arrayAlt: speedSnap(), stack: stackSnap([fleetTimes.length - 1]) }
        )
      );
    }
  });

  steps.push(
    step(
      steps.length,
      "Done",
      `The cars form ${fleetTimes.length} fleet${fleetTimes.length === 1 ? "" : "s"}.`,
      5,
      arraySnap([], sortedPositions.map((_, index) => index)),
      { fleets: fleetTimes.length },
      {
        arrayAlt: speedSnap(),
        stack: stackSnap(fleetTimes.map((_, index) => index)),
        done: true,
        result: String(fleetTimes.length),
      }
    )
  );

  return steps;
}

export const carFleetEntry: VisualizerEntry = {
  slug: "car-fleet",
  title: "Car Fleet",
  inputHint: "target, n, positions, speeds",
  defaultInput: "10\n4\n8 3 7 6\n4 4 4 4",
  presets: [
    { label: "example", value: "10\n4\n8 3 7 6\n4 4 4 4" },
    { label: "no catch", value: "10\n5\n3 4 5 6 7\n3 4 5 6 7" },
    { label: "all catch", value: "12\n3\n10 8 0\n2 4 1" },
  ],
  pseudocode: [
    "sort cars by position descending",
    "for each car:",
    "  time = (target - position) / speed",
    "  if time > last fleet time: new fleet",
    "  else: join the fleet ahead",
    "return number of fleets",
  ],
  parse: parseCarFleet,
  generate: (input) => generateCarFleet(input as CarFleetInput),
};
