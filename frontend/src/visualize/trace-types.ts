/** Shared trace model for the step-by-step visualizer.
 *
 * Traces are generated first (pure functions over an input), then played back
 * by the player. Snapshots are immutable so Previous/Next/Reset are exact.
 */

export type PointerName =
  | "low"
  | "mid"
  | "high"
  | "left"
  | "right"
  | "slow"
  | "fast"
  | "i"
  | "j"
  | "k"
  | "parent"
  | "child";

export interface ArraySnapshot {
  /** Numbers for array problems, single chars for string problems. */
  values: (number | string)[];
  /** Indices part of the current comparison/operation. */
  active: number[];
  /** Indices already settled (sorted region, placed element, …). */
  settled: number[];
  /** Indices eliminated from consideration (binary search). */
  eliminated: number[];
  /** Source indices used by the current computation (DP recurrences). */
  deps?: number[];
  pointers: Partial<Record<PointerName, number>>;
  /** Caption rendered under the array, e.g. "max-heap" / "words". */
  label?: string;
}

/** Vertical stack snapshot. Index 0 is the bottom; top is values.at(-1). */
export interface StackSnapshot {
  values: (number | string)[];
  /** Positions (from bottom) touched by the current op — usually the top. */
  active: number[];
  /** Positions already resolved/consumed. */
  settled: number[];
  /** Caption rendered under the stack, e.g. "stack" / "min-stack". */
  label?: string;
}

/** Horizontal queue/deque snapshot. Index 0 is the front. */
export interface QueueSnapshot {
  values: (number | string)[];
  /** Index of the front element (0 for an empty queue). */
  front: number;
  /** Index of the back element (-1 for an empty queue). */
  back: number;
  /** Positions touched by the current op — usually the front/back. */
  active: number[];
  /** Positions already consumed/resolved. */
  settled: number[];
  /** Caption rendered under the queue, e.g. "deque (indices)". */
  label?: string;
}

export type ListPointerName =
  | "head"
  | "tail"
  | "prev"
  | "curr"
  | "next"
  | "slow"
  | "fast"
  | "a"
  | "b"
  | "p"
  | "q";

export interface LinkedListNode {
  id: number;
  value: number | string;
  next: number | null;
  /** Random-pointer target for copy-list-with-random-pointer traces. */
  random?: number | null;
}

/** Linked-list snapshot. The renderer walks `head` through `next` links. */
export interface LinkedListSnapshot {
  nodes: LinkedListNode[];
  head: number | null;
  /** Node ids touched by the current op. */
  active: number[];
  /** Node ids already reversed/merged/resolved. */
  settled: number[];
  pointers: Partial<Record<ListPointerName, number>>;
  /** Caption rendered under the list, e.g. "reversed" / "remaining". */
  label?: string;
  /** Node id the tail links back to when the list contains a cycle. */
  cycleTo?: number | null;
}

export type TreePointerName = "curr" | "prev" | "left" | "right" | "p" | "q";

export interface TreeNodeSnapshot {
  id: number;
  value: number | string;
  left: number | null;
  right: number | null;
}

/** Binary-tree snapshot. The renderer lays nodes out by depth and in-order position. */
export interface TreeSnapshot {
  nodes: TreeNodeSnapshot[];
  root: number | null;
  /** Node ids touched by the current op. */
  active: number[];
  /** Node ids already processed/resolved. */
  settled: number[];
  pointers: Partial<Record<TreePointerName, number>>;
  /** Extra per-node captions, e.g. { 3: "d=2" } for computed depths. */
  annotations?: Record<number, string>;
  /** Caption rendered under the tree, e.g. "tree". */
  label?: string;
}

export type GraphPointerName = "curr" | "prev" | "next" | "node";

export interface GraphNodeSnapshot {
  id: number | string;
  label: string;
}

export interface GraphEdgeSnapshot {
  from: number | string;
  to: number | string;
  directed?: boolean;
  /** Weight or short caption rendered on the edge, e.g. "4" / "hot→dot". */
  label?: string;
}

/** Abstract graph snapshot. Nodes are placed on a circle; edges may be directed. */
export interface GraphSnapshot {
  nodes: GraphNodeSnapshot[];
  edges: GraphEdgeSnapshot[];
  /** Node ids touched by the current op. */
  active: (number | string)[];
  /** Node ids already visited/resolved. */
  settled: (number | string)[];
  pointers: Partial<Record<GraphPointerName, number | string>>;
  /** Extra per-node captions, e.g. { 3: "d=7" } for Dijkstra distances. */
  annotations?: Record<string, string>;
  /** Caption rendered under the graph, e.g. "original" / "clone". */
  label?: string;
}

/** Rectangular grid/matrix snapshot used by grid graphs and 2-D DP tables. */
export interface GridSnapshot {
  rows: number;
  cols: number;
  values: (number | string)[][];
  /** Cells touched by the current op. */
  active: [number, number][];
  /** Cells used to compute the current cell. */
  deps: [number, number][];
  /** Cells already processed/resolved. */
  settled: [number, number][];
  /** Render row/column headers (useful for DP tables). */
  showIndices?: boolean;
  /** Optional header labels; falls back to numeric indices. */
  rowLabels?: string[];
  colLabels?: string[];
  /** Caption rendered under the grid, e.g. "image" / "dp". */
  label?: string;
}

export interface BaseStep {
  index: number;
  /** Short label, e.g. "Compare", "Swap", "Move left". */
  op: string;
  /** One-sentence explanation of this step. */
  explanation: string;
  /** Pseudocode line this step maps to (index into the entry's pseudocode). */
  line: number;
  array: ArraySnapshot;
  /** Secondary array (two-string / two-heap comparisons). Rendered beside `array`. */
  arrayAlt?: ArraySnapshot;
  /** Primary stack (stack problems). Rendered when present. */
  stack?: StackSnapshot;
  /** Secondary stack (Min Stack's min-stack). Rendered beside `stack`. */
  stackAlt?: StackSnapshot;
  /** Primary queue/deque (queue problems). Rendered when present. */
  queue?: QueueSnapshot;
  /** Secondary queue (e.g. a second deque). Rendered beside `queue`. */
  queueAlt?: QueueSnapshot;
  /** Primary linked list. Rendered when present. */
  linkedList?: LinkedListSnapshot;
  /** Secondary linked list (two input lists). Rendered beside `linkedList`. */
  linkedListAlt?: LinkedListSnapshot;
  /** Binary tree (tree problems). Rendered when present. */
  tree?: TreeSnapshot;
  /** Secondary tree (e.g. the second input to Same Tree). Rendered beside `tree`. */
  treeAlt?: TreeSnapshot;
  /** Primary abstract graph (graph problems). Rendered when present. */
  graph?: GraphSnapshot;
  /** Secondary graph (e.g. the cloned copy). Rendered beside `graph`. */
  graphAlt?: GraphSnapshot;
  /** Grid/matrix (grid graphs and 2-D DP tables). Rendered when present. */
  grid?: GridSnapshot;
  /** Secondary grid (e.g. the two Pacific/Atlantic passes). Rendered beside `grid`. */
  gridAlt?: GridSnapshot;
  /** Named variable values shown beside the code, e.g. { target: 9 }. */
  vars: Record<string, string | number>;
  result?: string;
  done?: boolean;
}

export interface Trace<TInput = unknown> {
  steps: BaseStep[];
  input: TInput;
}

/** Registry-facing entry. Inputs cross this boundary as `unknown`; each trace
 * module owns the single narrowing cast for its own input shape. */
export interface VisualizerEntry {
  slug: string;
  title: string;
  /** Short input hint, e.g. "[2, 7, 11, 15], target 9". */
  inputHint: string;
  defaultInput: string;
  presets: { label: string; value: string }[];
  pseudocode: string[];
  parse: (raw: string) => unknown;
  generate: (input: unknown) => BaseStep[];
}

function emptyArray(values: (number | string)[]): ArraySnapshot {
  return {
    values: [...values],
    active: [],
    settled: [],
    eliminated: [],
    deps: [],
    pointers: {},
  };
}

export function snapStack(
  values: (number | string)[],
  partial: Partial<StackSnapshot> = {}
): StackSnapshot {
  return { values: [...values], active: [], settled: [], ...partial };
}

export function snapQueue(
  values: (number | string)[],
  partial: Partial<QueueSnapshot> = {}
): QueueSnapshot {
  return {
    values: [...values],
    front: 0,
    back: values.length - 1,
    active: [],
    settled: [],
    ...partial,
  };
}

export function listFromValues(values: (number | string)[]): LinkedListNode[] {
  return values.map((value, i) => ({
    id: i,
    value,
    next: i + 1 < values.length ? i + 1 : null,
  }));
}

export function snapList(
  nodes: LinkedListNode[],
  partial: Partial<LinkedListSnapshot> = {}
): LinkedListSnapshot {
  const copied = nodes.map((node) => ({ ...node }));
  return {
    nodes: copied,
    head: copied.length > 0 ? copied[0].id : null,
    active: [],
    settled: [],
    pointers: {},
    ...partial,
  };
}

export function snapTree(
  nodes: TreeNodeSnapshot[],
  partial: Partial<TreeSnapshot> = {}
): TreeSnapshot {
  const copied = nodes.map((node) => ({ ...node }));
  return {
    nodes: copied,
    root: copied.length > 0 ? copied[0].id : null,
    active: [],
    settled: [],
    pointers: {},
    ...partial,
  };
}

export function snapGraph(
  nodes: GraphNodeSnapshot[],
  edges: GraphEdgeSnapshot[],
  partial: Partial<GraphSnapshot> = {}
): GraphSnapshot {
  return {
    nodes: nodes.map((node) => ({ ...node })),
    edges: edges.map((edge) => ({ ...edge })),
    active: [],
    settled: [],
    pointers: {},
    ...partial,
  };
}

export function snapGrid(
  values: (number | string)[][],
  partial: Partial<GridSnapshot> = {}
): GridSnapshot {
  return {
    rows: values.length,
    cols: values[0]?.length ?? 0,
    values: values.map((row) => [...row]),
    active: [],
    deps: [],
    settled: [],
    ...partial,
  };
}

export function step(
  index: number,
  op: string,
  explanation: string,
  line: number,
  array: ArraySnapshot,
  vars: Record<string, string | number> = {},
  extra: Partial<BaseStep> = {}
): BaseStep {
  return { index, op, explanation, line, array, vars, ...extra };
}

export function snap(
  values: (number | string)[],
  partial: Partial<ArraySnapshot> = {}
): ArraySnapshot {
  return { ...emptyArray(values), ...partial };
}
