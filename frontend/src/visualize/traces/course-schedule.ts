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

export interface CourseScheduleInput {
  vertices: number;
  edges: [number, number][];
}

export function parseCourseSchedule(raw: string): CourseScheduleInput {
  const lines = raw
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  if (lines.length < 1) throw new Error("Use: V E, then E lines of a b");

  const [vertices, edgeCount] = lines[0].split(/[\s,]+/).map(Number);
  if (
    !Number.isInteger(vertices) ||
    !Number.isInteger(edgeCount) ||
    vertices < 1 ||
    edgeCount < 0
  ) {
    throw new Error("V and E must be positive integers (E may be 0)");
  }
  if (vertices > 8) {
    throw new Error("Keep it to 8 courses so the graph stays readable");
  }
  if (lines.length < edgeCount + 1) throw new Error("Some prerequisite lines are missing");

  const seen = new Set<string>();
  const edges: [number, number][] = [];
  for (const line of lines.slice(1, edgeCount + 1)) {
    const [a, b] = line.split(/[\s,]+/).map(Number);
    if (
      !Number.isInteger(a) ||
      !Number.isInteger(b) ||
      a < 0 ||
      a >= vertices ||
      b < 0 ||
      b >= vertices
    ) {
      throw new Error(`Courses must be numbered 0..${vertices - 1}`);
    }
    const key = `${a},${b}`;
    if (seen.has(key)) throw new Error("Duplicate prerequisite pair");
    seen.add(key);
    edges.push([a, b]);
  }

  return { vertices, edges };
}

export function generateCourseSchedule(input: CourseScheduleInput): BaseStep[] {
  const { vertices, edges } = input;
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
  const indegree = Array.from({ length: vertices }, () => 0);

  for (const [a, b] of edges) {
    adjacency[b].push(a);
    indegree[a] += 1;
  }

  const settled: number[] = [];
  const queue: number[] = [];
  for (let i = 0; i < vertices; i += 1) {
    if (indegree[i] === 0) queue.push(i);
  }

  const graphSnapshot = (
    active: number[] = [],
    curr: number | null = null,
    next: number | null = null
  ) =>
    snapGraph(nodes, graphEdges, {
      active,
      settled: [...settled],
      pointers: {
        ...(curr == null ? {} : { curr }),
        ...(next == null ? {} : { next }),
      },
      label: "prerequisites",
    });

  const queueSnapshot = () =>
    snapQueue(queue.map(String), {
      active: queue.length > 0 ? [0] : [],
      label: "queue",
    });

  const orderSnapshot = () => snap([...settled]);

  const indegrees = () => indegree.map((value, id) => `${id}:${value}`).join("  ");

  steps.push(
    step(
      0,
      "Start",
      queue.length === 0
        ? "No course has indegree 0, so a cycle exists and no course can be taken first."
        : `Kahn's algorithm: start with the ${queue.length} course${queue.length === 1 ? "" : "s"} that have no prerequisites.`,
      5,
      snap([]),
      { taken: 0, queue: queue.length, indegree: indegrees() },
      { graph: graphSnapshot([], null, null), queue: queueSnapshot(), array: orderSnapshot() }
    )
  );

  while (queue.length > 0) {
    const u = queue.shift()!;
    settled.push(u);

    steps.push(
      step(
        steps.length,
        "Take",
        `Course ${u} has indegree 0; take it and remove its outgoing prerequisites.`,
        8,
        snap([]),
        { course: u, taken: settled.length, indegree: indegrees() },
        { graph: graphSnapshot([u], u, null), queue: queueSnapshot(), array: orderSnapshot() }
      )
    );

    for (const v of adjacency[u]) {
      indegree[v] -= 1;
      if (indegree[v] === 0) queue.push(v);

      steps.push(
        step(
          steps.length,
          "Unlock",
          `Remove ${u} -> ${v}. Course ${v} now has indegree ${indegree[v]}${indegree[v] === 0 ? " and joins the queue" : ""}.`,
          11,
          snap([]),
          { from: u, to: v, indegree: indegrees() },
          {
            graph: graphSnapshot([u, v], u, v),
            queue: queueSnapshot(),
            array: orderSnapshot(),
          }
        )
      );
    }
  }

  const possible = settled.length === vertices;
  steps.push(
    step(
      steps.length,
      possible ? "Possible" : "Cycle",
      possible
        ? `All ${vertices} courses were taken, so the prerequisites are finishable.`
        : `Only ${settled.length} of ${vertices} courses were taken; the remaining courses form a cycle.`,
      11,
      snap([]),
      { taken: settled.length, total: vertices },
      {
        graph: graphSnapshot(),
        queue: queueSnapshot(),
        array: orderSnapshot(),
        result: possible ? "true" : "false",
        done: true,
      }
    )
  );

  return steps;
}

export const courseScheduleEntry: VisualizerEntry = {
  slug: "course-schedule",
  title: "Course Schedule",
  inputHint: "4 3 / a b",
  defaultInput: "4 3\n1 0\n2 1\n3 2",
  presets: [
    { label: "Chain", value: "4 3\n1 0\n2 1\n3 2" },
    { label: "Cycle", value: "2 2\n1 0\n0 1" },
    { label: "No edges", value: "4 0" },
    { label: "Diamond", value: "4 4\n1 0\n2 0\n3 1\n3 2" },
  ],
  pseudocode: [
    "indegree = [0] * V",
    "adj = [[] for _ in range(V)]",
    "for a, b in edges:",
    "    adj[b].append(a)",
    "    indegree[a] += 1",
    "queue = deque(i for i in range(V) if indegree[i] == 0)",
    "taken = 0",
    "while queue:",
    "    u = queue.popleft(); taken += 1",
    "    for v in adj[u]:",
    "        indegree[v] -= 1",
    "        if indegree[v] == 0: queue.append(v)",
    "return taken == V",
  ],
  parse: (raw: string) => parseCourseSchedule(raw),
  generate: (input: unknown) => generateCourseSchedule(input as CourseScheduleInput),
};
