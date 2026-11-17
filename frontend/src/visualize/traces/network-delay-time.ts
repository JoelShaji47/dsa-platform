import {
  snap,
  snapGraph,
  step,
  type BaseStep,
  type GraphEdgeSnapshot,
  type GraphNodeSnapshot,
  type VisualizerEntry,
} from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";

export interface NetworkDelayInput {
  vertices: number;
  source: number;
  edges: [number, number, number][];
}

export function parseNetworkDelay(raw: string): NetworkDelayInput {
  const lines = inputLines(raw);
  if (lines.length < 1) throw new Error("Use: V E K, then E lines of u v w");
  const header = integersFrom(lines[0]);
  const [vertices, edgeCount, source] = header;
  if (header.length !== 3 || !Number.isInteger(vertices) || !Number.isInteger(edgeCount)) {
    throw new Error("The first line must be: V E K");
  }
  if (vertices < 1 || vertices > 10 || edgeCount < 0) throw new Error("Use 1..10 nodes and a valid edge count");
  if (source < 1 || source > vertices) throw new Error("The source must be a valid node");
  if (lines.length < edgeCount + 1) throw new Error("Some edge lines are missing");
  const edges: [number, number, number][] = [];
  for (const line of lines.slice(1, edgeCount + 1)) {
    const triple = integersFrom(line);
    const [u, v, w] = triple;
    if (triple.length !== 3 || u < 1 || u > vertices || v < 1 || v > vertices || w < 0) {
      throw new Error("Each edge needs valid u v w values");
    }
    edges.push([u, v, w]);
  }
  return { vertices, source, edges };
}

export function generateNetworkDelay({ vertices, source, edges }: NetworkDelayInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes: GraphNodeSnapshot[] = Array.from({ length: vertices }, (_, index) => ({
    id: index + 1,
    label: String(index + 1),
  }));
  const graphEdges: GraphEdgeSnapshot[] = edges.map(([u, v, w]) => ({
    from: u,
    to: v,
    directed: true,
    label: String(w),
  }));
  const adjacency = new Map<number, [number, number][]>();
  for (let id = 1; id <= vertices; id += 1) adjacency.set(id, []);
  for (const [u, v, w] of edges) adjacency.get(u)!.push([v, w]);

  const distances = new Map<number, number>();
  for (let id = 1; id <= vertices; id += 1) distances.set(id, Infinity);
  distances.set(source, 0);
  const settled: number[] = [];

  const graphSnap = (active: number[] = [], curr: number | null = null) =>
    snapGraph(nodes, graphEdges, {
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries(
        [...distances.entries()].map(([id, value]) => [id, value === Infinity ? "∞" : `d=${value}`])
      ),
      label: "weighted graph",
    });

  steps.push(
    step(0, "Start", `Dijkstra from node ${source}; all other distances start at infinity.`, 0, snap([]), { source }, { graph: graphSnap([source], source) })
  );

  for (let round = 0; round < vertices; round += 1) {
    let curr: number | null = null;
    let best = Infinity;
    for (let id = 1; id <= vertices; id += 1) {
      if (settled.includes(id)) continue;
      const value = distances.get(id) ?? Infinity;
      if (value < best) {
        best = value;
        curr = id;
      }
    }

    if (curr == null || best === Infinity) {
      steps.push(
        step(
          steps.length,
          "Unreachable",
          "The nearest unsettled node is unreachable; stop early.",
          2,
          snap([]),
          { round: round + 1 },
          { graph: graphSnap([], null) }
        )
      );
      break;
    }

    settled.push(curr);
    steps.push(
      step(
        steps.length,
        "Settle",
        `Node ${curr} has the smallest tentative distance (${best}); finalize it.`,
        2,
        snap([]),
        { node: curr, distance: best },
        { graph: graphSnap([curr], curr) }
      )
    );

    for (const [next, weight] of adjacency.get(curr) ?? []) {
      if (settled.includes(next)) continue;
      const candidate = best + weight;
      const known = distances.get(next) ?? Infinity;
      if (candidate < known) {
        distances.set(next, candidate);
        steps.push(
          step(
            steps.length,
            "Relax",
            `Path to ${next} via ${curr} costs ${candidate}, improving ${known === Infinity ? "∞" : known}.`,
            4,
            snap([]),
            { from: curr, to: next, candidate },
            { graph: graphSnap([curr, next], curr) }
          )
        );
      }
    }
  }

  const values = [...distances.values()];
  const reachable = values.every((value) => value !== Infinity);
  const result = reachable ? Math.max(...values) : -1;
  steps.push(
    step(
      steps.length,
      "Done",
      reachable ? `Every node is reached; the maximum delay is ${result}.` : "Some nodes are unreachable.",
      5,
      snap(values.map((value) => (value === Infinity ? "∞" : value)), { label: "distances by node" }),
      { result },
      { graph: graphSnap(), done: true, result: String(result) }
    )
  );

  return steps;
}

export const networkDelayEntry: VisualizerEntry = {
  slug: "network-delay-time",
  title: "Network Delay Time",
  inputHint: "V E K, then E lines of u v w",
  defaultInput: "4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 2",
  presets: [
    { label: "example", value: "4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 2" },
    { label: "chain", value: "3 2 1\n1 2 1\n2 3 1" },
    { label: "unreachable", value: "2 0 1" },
  ],
  pseudocode: [
    "dist = [∞] * (V + 1); dist[K] = 0",
    "repeat V times:",
    "  pick the unsettled node with the smallest dist",
    "  settle it",
    "  relax each outgoing edge",
    "return max(dist) or -1 if any node is unreachable",
  ],
  parse: parseNetworkDelay,
  generate: (input) => generateNetworkDelay(input as NetworkDelayInput),
};
