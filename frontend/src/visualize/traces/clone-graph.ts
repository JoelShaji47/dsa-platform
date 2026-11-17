import {
  snap,
  snapGraph,
  step,
  type BaseStep,
  type GraphEdgeSnapshot,
  type GraphNodeSnapshot,
  type VisualizerEntry,
} from "../trace-types";

export interface CloneGraphInput {
  vertices: number;
  adjacency: number[][];
}

export function parseCloneGraph(raw: string): CloneGraphInput {
  const lines = raw.replace(/\r/g, "").split("\n");
  const first = (lines[0] ?? "").trim();
  if (first === "") throw new Error("Use: n, then one line of neighbors per node");

  const vertices = Number(first);
  if (!Number.isInteger(vertices) || vertices < 0) {
    throw new Error("n must be a non-negative integer");
  }
  if (vertices > 6) {
    throw new Error("Keep it to 6 nodes so the graph stays readable");
  }
  if (lines.length < vertices + 1) {
    throw new Error("One neighbor line is required for each node");
  }

  const adjacency: number[][] = Array.from({ length: vertices + 1 }, () => []);
  for (let node = 1; node <= vertices; node += 1) {
    const line = (lines[node] ?? "").trim();
    const neighbors = line === "" ? [] : line.split(/[\s,]+/).map(Number);
    const seen = new Set<number>();
    for (const neighbor of neighbors) {
      if (
        !Number.isInteger(neighbor) ||
        neighbor < 1 ||
        neighbor > vertices ||
        neighbor === node
      ) {
        throw new Error(`Neighbors must be nodes 1..${vertices}, excluding self-loops`);
      }
      if (seen.has(neighbor)) throw new Error("Duplicate neighbor in a node's line");
      seen.add(neighbor);
    }
    adjacency[node] = neighbors;
  }

  return { vertices, adjacency };
}

export function generateCloneGraph(input: CloneGraphInput): BaseStep[] {
  const { vertices, adjacency } = input;
  const steps: BaseStep[] = [];
  const originalNodes: GraphNodeSnapshot[] = Array.from({ length: vertices }, (_, index) => ({
    id: index + 1,
    label: String(index + 1),
  }));
  const originalEdges: GraphEdgeSnapshot[] = [];
  const edgeSeen = new Set<string>();
  for (let node = 1; node <= vertices; node += 1) {
    for (const neighbor of adjacency[node] ?? []) {
      const low = Math.min(node, neighbor);
      const high = Math.max(node, neighbor);
      const key = `${low}|${high}`;
      if (edgeSeen.has(key)) continue;
      edgeSeen.add(key);
      originalEdges.push({ from: low, to: high });
    }
  }

  const cloneMap = new Map<number, string>();
  const cloneNodes: GraphNodeSnapshot[] = [];
  const cloneEdges: GraphEdgeSnapshot[] = [];
  const cloneEdgeKeys = new Set<string>();
  const settledOriginal = new Set<number>();
  const settledClone = new Set<string>();
  const order: number[] = [];

  const snapshots = (
    activeOriginal: number[],
    activeClone: string[],
    currOriginal: number | null,
    currClone: string | null
  ) => ({
    graph: snapGraph(originalNodes, originalEdges, {
      active: activeOriginal,
      settled: [...settledOriginal],
      pointers: currOriginal == null ? {} : { curr: currOriginal },
      label: "original",
    }),
    graphAlt: snapGraph(cloneNodes, cloneEdges, {
      active: activeClone,
      settled: [...settledClone],
      pointers: currClone == null ? {} : { curr: currClone },
      label: "clone",
    }),
    array: snap(order.map((node) => `${node}'`)),
  });

  steps.push(
    step(
      0,
      "Start",
      vertices === 0
        ? "The graph is empty, so the clone is empty too."
        : "Build the copy depth-first. The original graph stays on the left while the clone grows on the right.",
      0,
      snap([]),
      { nodes: vertices },
      { ...snapshots([], [], null, null) }
    )
  );

  if (vertices === 0) {
    steps.push(
      step(
        steps.length,
        "Done",
        "There are no nodes to copy.",
        6,
        snap([]),
        { nodes: 0 },
        { ...snapshots([], [], null, null), result: "empty graph", done: true }
      )
    );
    return steps;
  }

  const clone = (node: number): string => {
    const existing = cloneMap.get(node);
    if (existing) return existing;

    const cloneId = `c${node}`;
    cloneMap.set(node, cloneId);
    cloneNodes.push({ id: cloneId, label: `${node}'` });
    settledClone.add(cloneId);
    order.push(node);

    steps.push(
      step(
        steps.length,
        "Clone",
        `Create copy ${node}' for original node ${node}.`,
        2,
        snap([]),
        { node },
        { ...snapshots([node], [cloneId], node, cloneId) }
      )
    );

    for (const neighbor of adjacency[node] ?? []) {
      const neighborClone = clone(neighbor);
      const edgeKey = [cloneId, neighborClone].sort().join("|");
      if (cloneEdgeKeys.has(edgeKey)) continue;
      cloneEdgeKeys.add(edgeKey);
      cloneEdges.push({ from: cloneId, to: neighborClone });

      steps.push(
        step(
          steps.length,
          "Connect",
          `Copy the undirected edge ${node} - ${neighbor} into the clone graph.`,
          5,
          snap([]),
          { from: node, to: neighbor },
          {
            ...snapshots(
              [node, neighbor],
              [cloneId, neighborClone],
              node,
              cloneId
            ),
          }
        )
      );
    }

    settledOriginal.add(node);
    steps.push(
      step(
        steps.length,
        "Done",
        `Original node ${node} and clone ${node}' are fully linked.`,
        6,
        snap([]),
        { node },
        { ...snapshots([node], [cloneId], node, cloneId) }
      )
    );

    return cloneId;
  };

  clone(1);

  steps.push(
    step(
      steps.length,
      "Done",
      "Every reachable node has a copied value and copied neighbors.",
      6,
      snap([]),
      { cloned: order.length },
      {
        ...snapshots([], [], null, null),
        result: order.join(" "),
        done: true,
      }
    )
  );

  return steps;
}

export const cloneGraphEntry: VisualizerEntry = {
  slug: "clone-graph",
  title: "Clone Graph",
  inputHint: "4 / one line of neighbors per node",
  defaultInput: "4\n2 4\n1 3\n2 4\n1 3",
  presets: [
    { label: "Cycle", value: "4\n2 4\n1 3\n2 4\n1 3" },
    { label: "Single", value: "1\n" },
    { label: "Path", value: "3\n2\n1 3\n2" },
    { label: "Star", value: "4\n2 3 4\n1\n1\n1" },
  ],
  pseudocode: [
    "def clone(node):",
    "    if node in cloned: return cloned[node]",
    "    copy = Node(node.val)",
    "    cloned[node] = copy",
    "    for neighbor in node.neighbors:",
    "        copy.neighbors.append(clone(neighbor))",
    "    return copy",
  ],
  parse: (raw: string) => parseCloneGraph(raw),
  generate: (input: unknown) => generateCloneGraph(input as CloneGraphInput),
};
