import {
  snap,
  snapTree,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface ValidateBstInput {
  tree: ParsedTree;
}

export function parseValidateBst(raw: string): ValidateBstInput {
  return { tree: parseLevelOrderTree(raw, { allowEmpty: true }) };
}

export function generateValidateBst({ tree }: ValidateBstInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();

  const snapshot = (active: number[], curr: number | null) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      label: "tree",
    });

  steps.push(
    step(
      0,
      "Start",
      tree.root == null
        ? "An empty tree is a valid BST."
        : "Carry an allowed (low, high) range down the tree. A valid node must stay strictly inside it.",
      0,
      snap([]),
      { nodes: nodes.length },
      { tree: snapshot(tree.root == null ? [] : [tree.root], tree.root) }
    )
  );

  interface Frame {
    id: number;
    low: number;
    high: number;
  }

  const stack: Frame[] = [];
  if (tree.root != null) stack.push({ id: tree.root, low: -Infinity, high: Infinity });

  while (stack.length > 0) {
    const { id, low, high } = stack.pop()!;
    const node = nodes[id];
    if (!node) continue;
    const value = Number(node.value);
    const lowLabel = Number.isFinite(low) ? String(low) : "-inf";
    const highLabel = Number.isFinite(high) ? String(high) : "+inf";

    steps.push(
      step(
        steps.length,
        "Check",
        `Node ${value} must satisfy ${lowLabel} < value < ${highLabel}.`,
        2,
        snap([]),
        { value, low: lowLabel, high: highLabel },
        { tree: snapshot([id], id) }
      )
    );

    if (value <= low || value >= high) {
      steps.push(
        step(
          steps.length,
          "Invalid",
          `${value} is outside (${lowLabel}, ${highLabel}). The tree is not a valid BST.`,
          2,
          snap([]),
          { value, low: lowLabel, high: highLabel },
          { tree: snapshot([id], id), result: "false", done: true }
        )
      );
      return steps;
    }

    settled.add(id);
    steps.push(
      step(
        steps.length,
        "Valid",
        `${value} fits the range. Recurse with tighter bounds for each child.`,
        3,
        snap([]),
        { value, low: lowLabel, high: highLabel },
        { tree: snapshot([id], id) }
      )
    );

    if (node.right != null) {
      stack.push({ id: node.right, low: value, high });
    }
    if (node.left != null) {
      stack.push({ id: node.left, low, high: value });
    }
  }

  steps.push(
    step(
      steps.length,
      "Valid BST",
      `Every node respected its range, so the tree is a valid BST.`,
      3,
      snap([]),
      { nodes: settled.size },
      { tree: snapshot([], null), result: "true", done: true }
    )
  );

  return steps;
}

export const validateBstEntry: VisualizerEntry = {
  slug: "validate-binary-search-tree",
  title: "Validate Binary Search Tree",
  inputHint: "[5, 1, 4, null, null, 3, 6]",
  defaultInput: "[5, 1, 4, null, null, 3, 6]",
  presets: [
    { label: "Invalid", value: "[5, 1, 4, null, null, 3, 6]" },
    { label: "Valid", value: "[2, 1, 3]" },
    { label: "Single", value: "[1]" },
    { label: "Empty", value: "[]" },
  ],
  pseudocode: [
    "def valid(node, low, high):",
    "    if not node: return True",
    "    if not low < node.val < high: return False",
    "    return valid(node.left, low, node.val) and valid(node.right, node.val, high)",
  ],
  parse: (raw: string) => parseValidateBst(raw),
  generate: (input: unknown) => generateValidateBst(input as ValidateBstInput),
};
