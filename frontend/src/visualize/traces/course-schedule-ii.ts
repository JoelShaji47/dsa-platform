import {
  snap,
  snapGraph,
  snapQueue,
  step,
  type BaseStep,
  type GraphEdgeSnapshot,
  type GraphNodeSnapshot,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface CourseScheduleIIInput {
  vertices: number;
  edges: [number, number][];
}

export function parseCourseScheduleII(raw: string): CourseScheduleIIInput {
  const lines = inputLines(raw);
  if (lines.length < 1) throw new Error("Use: V E, then E lines of a b");
  const header = integersFrom(lines[0]);
  const [vertices, edgeCount] = header;
  if (header.length !== 2 || !Number.isInteger(vertices) || !Number.isInteger(edgeCount)) {
    throw new Error("The first line must be: V E");
  }
  if (vertices < 1 || vertices > 8 || edgeCount < 0) throw new Error("Use 1..8 courses and a valid edge count");
  if (lines.length < edgeCount + 1) throw new Error("Some prerequisite lines are missing");
  const edges: [number, number][] = [];
  for (const line of lines.slice(1, edgeCount + 1)) {
    const pair = integersFrom(line);
    const [a, b] = pair;
    if (pair.length !== 2 || a < 0 || a >= vertices || b < 0 || b >= vertices) {
      throw new Error(`Courses must be numbered 0..${vertices - 1}`);
    }
    edges.push([a, b]);
  }
  return { vertices, edges };
}

export function generateCourseScheduleII({ vertices, edges }: CourseScheduleIIInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes: GraphNodeSnapshot[] = Array.from({ length: vertices }, (_, id) => ({
    id,
    label: String(id),
  }));
  const graphEdges: GraphEdgeSnapshot[] = edges.map(([a, b]) => ({
    from: b,
    to: a,
    directed: true,
  }));
  const adjacency: number[][] = Array.from({ length: vertices }, () => []);
  const indegree = new Array<number>(vertices).fill(0);
  for (const [a, b] of edges) {
    adjacency[b].push(a);
    indegree[a] += 1;
  }

  const queue: number[] = [];
  for (let i = 0; i < vertices; i += 1) if (indegree[i] === 0) queue.push(i);

  const order: number[] = [];
  const graphSnap = (active: number[] = [], curr: number | null = null) =>
    snapGraph(nodes, graphEdges, {
      active,
      settled: [...order],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries(vertices ? indegree.map((value, id) => [id, `in=${value}`]) : []),
      label: "prerequisites",
    });
  const queueSnap = () =>
    snapQueue(queue.map(String), { active: queue.length ? [0] : [], label: "ready courses" });
  const orderSnap = (active: number[] = []) => snap(order, { active, label: "order" });

  steps.push(
    step(0, "Start", "Kahn's algorithm: repeatedly take a course with no remaining prerequisites.", 0, orderSnap(), { ready: queue.length }, { graph: graphSnap(), queue: queueSnap() })
  );

  while (queue.length > 0) {
    const course = queue.shift()!;
    order.push(course);
    steps.push(
      step(
        steps.length,
        "Take",
        `Take course ${course}.`,
        3,
        orderSnap([order.length - 1]),
        { course, taken: order.length },
        { graph: graphSnap([course], course), queue: queueSnap() }
      )
    );

    for (const next of adjacency[course]) {
      indegree[next] -= 1;
      if (indegree[next] === 0) queue.push(next);
      steps.push(
        step(
          steps.length,
          "Unlock",
          `Remove ${course} -> ${next}; course ${next} now has indegree ${indegree[next]}${indegree[next] === 0 ? " and is ready" : ""}.`,
          5,
          orderSnap(),
          { from: course, to: next, indegree: indegree[next] },
          { graph: graphSnap([course, next], course), queue: queueSnap() }
        )
      );
    }
  }

  const possible = order.length === vertices;
  const result = possible ? order.join(" ") : "";
  steps.push(
    step(
      steps.length,
      possible ? "Done" : "Cycle",
      possible ? `A valid course order is ${result}.` : "Not all courses can be completed because of a cycle.",
      6,
      orderSnap(),
      { taken: order.length, total: vertices },
      { graph: graphSnap(), queue: queueSnap(), done: true, result }
    )
  );

  return steps;
}

export const courseScheduleIIEntry: VisualizerEntry = {
  slug: "course-schedule-ii",
  title: "Course Schedule II",
  inputHint: "V E, then E lines of course prerequisite",
  defaultInput: "4 3\n1 0\n2 1\n3 2",
  presets: [
    { label: "chain", value: "4 3\n1 0\n2 1\n3 2" },
    { label: "cycle", value: "2 2\n1 0\n0 1" },
    { label: "no edges", value: "4 0" },
  ],
  pseudocode: [
    "build adjacency and indegrees",
    "queue = courses with indegree 0",
    "while queue:",
    "  course = dequeue; append to order",
    "  decrement indegree of dependents",
    "return order if it contains every course, else []",
  ],
  parse: parseCourseScheduleII,
  generate: (input) => generateCourseScheduleII(input as CourseScheduleIIInput),
};
