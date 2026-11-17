import type { TreeNodeSnapshot } from "../trace-types";

export interface ParsedTree {
  values: (number | null)[];
  nodes: TreeNodeSnapshot[];
  root: number | null;
}

const NULL_TOKENS = new Set(["null", "none", "nil", "#"]);

export function parseLevelOrderTree(
  raw: string,
  options: { allowEmpty?: boolean; maxNodes?: number } = {}
): ParsedTree {
  const { allowEmpty = false, maxNodes = 15 } = options;
  const bracket = raw.match(/\[([^\]]*)\]/);
  const body = (bracket ? bracket[1] : raw).trim();

  if (body === "") {
    if (allowEmpty) return { values: [], nodes: [], root: null };
    throw new Error("Use the form [3, 9, 20, null, null, 15, 7]");
  }

  const values = body.split(",").map((token) => {
    const cleaned = token.trim().toLowerCase();
    if (NULL_TOKENS.has(cleaned)) return null;
    const value = Number(token);
    if (!Number.isFinite(value)) {
      throw new Error("Use numbers and null, e.g. [3, 9, 20, null, 15]");
    }
    return value;
  });

  const rootValue = values[0];
  if (rootValue == null) throw new Error("The root cannot be null");

  const nodes: TreeNodeSnapshot[] = [];
  const root: TreeNodeSnapshot = { id: 0, value: rootValue, left: null, right: null };
  nodes.push(root);
  const queue: TreeNodeSnapshot[] = [root];
  let cursor = 1;

  while (cursor < values.length && queue.length > 0) {
    const parent = queue.shift()!;

    const leftValue = values[cursor++];
    if (leftValue != null) {
      const child: TreeNodeSnapshot = {
        id: nodes.length,
        value: leftValue,
        left: null,
        right: null,
      };
      nodes.push(child);
      parent.left = child.id;
      queue.push(child);
    }

    if (cursor >= values.length) break;
    const rightValue = values[cursor++];
    if (rightValue != null) {
      const child: TreeNodeSnapshot = {
        id: nodes.length,
        value: rightValue,
        left: null,
        right: null,
      };
      nodes.push(child);
      parent.right = child.id;
      queue.push(child);
    }
  }

  while (cursor < values.length) {
    if (values[cursor] != null) {
      throw new Error("Too many values for a level-order tree");
    }
    cursor += 1;
  }

  if (nodes.length > maxNodes) {
    throw new Error(`Keep it to ${maxNodes} nodes so the trace stays readable`);
  }

  return { values, nodes, root: 0 };
}

export function treeLevelOrder(
  nodes: TreeNodeSnapshot[],
  root: number | null
): (number | string | null)[] {
  const out: (number | string | null)[] = [];
  const queue: (number | null)[] = root == null ? [] : [root];

  while (queue.length > 0) {
    const id = queue.shift()!;
    if (id == null) {
      out.push(null);
      continue;
    }
    const node = nodes[id];
    if (!node) {
      out.push(null);
      continue;
    }
    out.push(node.value);
    queue.push(node.left, node.right);
  }

  while (out.length > 0 && out[out.length - 1] == null) out.pop();
  return out;
}

export function formatTreeValues(values: (number | string | null)[]): string {
  return `[${values.map((value) => (value == null ? "null" : value)).join(", ")}]`;
}
