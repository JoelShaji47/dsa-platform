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
import { inputLines } from "./input-utils";

export interface WordLadderInput {
  begin: string;
  end: string;
  words: string[];
}

export function parseWordLadder(raw: string): WordLadderInput {
  const lines = inputLines(raw);
  if (lines.length < 3) throw new Error("Use: begin end, n, then n words");
  const [begin, end] = lines[0].split(/\s+/);
  const n = Number(lines[1]);
  const words = lines.slice(2);
  if (!begin || !end) throw new Error("Provide both begin and end words");
  if (!Number.isInteger(n) || words.length !== n) throw new Error("Word count does not match");
  if (n > 10) throw new Error("Keep the dictionary to 10 words");
  if (words.some((word) => word.length !== begin.length)) {
    throw new Error("Every word must have the same length");
  }
  return { begin, end, words };
}

function differsByOne(a: string, b: string): boolean {
  let differences = 0;
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) differences += 1;
    if (differences > 1) return false;
  }
  return differences === 1;
}

export function generateWordLadder({ begin, end, words }: WordLadderInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dictionary = [begin, ...words.filter((word) => word !== begin)];
  const nodes: GraphNodeSnapshot[] = dictionary.map((word, id) => ({ id, label: word }));
  const edges: GraphEdgeSnapshot[] = [];
  for (let i = 0; i < dictionary.length; i += 1) {
    for (let j = i + 1; j < dictionary.length; j += 1) {
      if (differsByOne(dictionary[i], dictionary[j])) {
        edges.push({ from: i, to: j });
      }
    }
  }

  const adjacency = new Map<string, number[]>();
  dictionary.forEach((word, id) => adjacency.set(word, []));
  edges.forEach((edge) => {
    adjacency.get(dictionary[edge.from as number])!.push(edge.to as number);
    adjacency.get(dictionary[edge.to as number])!.push(edge.from as number);
  });

  const distance = new Map<number, number>();
  const visited = new Set<number>();
  const queue: number[] = [];
  const settled: number[] = [];
  const start = 0;
  const target = dictionary.indexOf(end);

  const graphSnap = (active: number[] = [], curr: number | null = null) =>
    snapGraph(nodes, edges, {
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries(
        [...distance.entries()].map(([id, value]) => [id, `d=${value}`])
      ),
      label: "word graph",
    });
  const queueSnap = (active: number[] = []) =>
    snapQueue(queue.map((id) => dictionary[id]), { active, label: "BFS queue" });

  steps.push(
    step(0, "Start", "Build a graph where words one letter apart are connected, then BFS from begin.", 0, snap([]), { start: begin, end }, { graph: graphSnap(), queue: queueSnap() })
  );

  if (target < 0) {
    steps.push(
      step(
        steps.length,
        "Missing",
        `${end} is not in the dictionary.`,
        1,
        snap([]),
        { end },
        { graph: graphSnap(), queue: queueSnap(), done: true, result: "0" }
      )
    );
    return steps;
  }

  distance.set(start, 1);
  visited.add(start);
  queue.push(start);
  steps.push(
    step(
      steps.length,
      "Enqueue start",
      `Start BFS at "${begin}" with distance 1.`,
      2,
      snap([]),
      { word: begin, distance: 1 },
      { graph: graphSnap([start], start), queue: queueSnap([0]) }
    )
  );

  while (queue.length > 0) {
    const id = queue.shift()!;
    settled.push(id);
    const word = dictionary[id];
    const dist = distance.get(id) ?? 0;
    steps.push(
      step(
        steps.length,
        "Visit",
        `Visit "${word}" at distance ${dist}.`,
        4,
        snap([]),
        { word, distance: dist },
        { graph: graphSnap([id], id), queue: queueSnap() }
      )
    );

    if (id === target) break;

    for (const next of adjacency.get(word) ?? []) {
      if (visited.has(next)) continue;
      visited.add(next);
      const nextDistance = dist + 1;
      distance.set(next, nextDistance);
      queue.push(next);
      steps.push(
        step(
          steps.length,
          "Expand",
          `"${dictionary[next]}" is one letter away; distance ${nextDistance}.`,
          5,
          snap([]),
          { word: dictionary[next], distance: nextDistance },
          { graph: graphSnap([next], id), queue: queueSnap(queue.length ? [0] : []) }
        )
      );
    }
  }

  const result = distance.get(target) ?? 0;
  steps.push(
    step(
      steps.length,
      "Done",
      result ? `The shortest transformation is ${result} words long.` : `No path from "${begin}" to "${end}".`,
      6,
      snap([]),
      { distance: result || "none" },
      { graph: graphSnap(), queue: queueSnap(), done: true, result: String(result) }
    )
  );

  return steps;
}

export const wordLadderEntry: VisualizerEntry = {
  slug: "word-ladder",
  title: "Word Ladder",
  inputHint: "begin end, n, then n dictionary words",
  defaultInput: "hit cog\n6\nhot\ndot\ndog\nlot\nlog\ncog",
  presets: [
    { label: "example", value: "hit cog\n6\nhot\ndot\ndog\nlot\nlog\ncog" },
    { label: "no path", value: "hit cog\n3\nhot\ndot\ndog" },
    { label: "direct", value: "hit hot\n1\nhot" },
  ],
  pseudocode: [
    "build edges between words differing by one letter",
    "queue = [(begin, 1)]; visited = {begin}",
    "while queue:",
    "  word, dist = queue.popleft()",
    "  if word == end: return dist",
    "  enqueue unvisited neighbors with dist + 1",
    "return 0",
  ],
  parse: parseWordLadder,
  generate: (input) => generateWordLadder(input as WordLadderInput),
};
