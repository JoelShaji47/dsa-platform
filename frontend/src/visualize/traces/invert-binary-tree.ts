import {
  snap,
  snapTree,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";
import {
  formatTreeValues,
  parseLevelOrderTree,
  treeLevelOrder,
  type ParsedTree,
} from "./tree-utils";

export interface InvertBinaryTreeInput {
  tree: ParsedTree;
}

export function parseInvertBinaryTree(raw: string): InvertBinaryTreeInput {
  return { tree: parseLevelOrderTree(raw, { allowEmpty: true }) };
}

export function generateInvertBinaryTree({ tree }: InvertBinaryTreeInput): BaseStep[] {
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

  const childLabel = (id: number | null): string =>
    id == null ? "null" : String(nodes[id]?.value ?? "null");

  steps.push(
    step(
      0,
      "Start",
      tree.root == null
        ? "The tree is empty, so there is nothing to invert."
        : "Swap every node's left and right child. The swap happens before recursing.",
      0,
      snap([]),
      { nodes: nodes.length },
      { tree: snapshot(tree.root == null ? [] : [tree.root], tree.root) }
    )
  );

  const invert = (id: number | null): void => {
    if (id == null) return;
    const node = nodes[id];
    if (!node) return;

    steps.push(
      step(
        steps.length,
        "Visit",
        `At node ${node.value}, swap its left and right children.`,
        2,
        snap([]),
        { node: node.value },
        { tree: snapshot([id], id) }
      )
    );

    const left = node.left;
    node.left = node.right;
    node.right = left;
    settled.add(id);

    steps.push(
      step(
        steps.length,
        "Swap",
        `Node ${node.value} now has left=${childLabel(node.left)} and right=${childLabel(node.right)}.`,
        2,
        snap([]),
        { node: node.value, left: childLabel(node.left), right: childLabel(node.right) },
        { tree: snapshot([id], id) }
      )
    );

    invert(node.left);
    invert(node.right);
  };

  invert(tree.root);

  const resultValues = treeLevelOrder(nodes, tree.root);
  steps.push(
    step(
      steps.length,
      "Done",
      "Every node's children have been swapped.",
      3,
      snap([]),
      { inverted: formatTreeValues(resultValues) },
      { tree: snapshot([], null), result: formatTreeValues(resultValues), done: true }
    )
  );

  return steps;
}

export const invertBinaryTreeEntry: VisualizerEntry = {
  slug: "invert-binary-tree",
  title: "Invert Binary Tree",
  inputHint: "[4, 2, 7, 1, 3, 6, 9]",
  defaultInput: "[4, 2, 7, 1, 3, 6, 9]",
  presets: [
    { label: "Balanced", value: "[4, 2, 7, 1, 3, 6, 9]" },
    { label: "Small", value: "[2, 1, 3]" },
    { label: "Single", value: "[1]" },
    { label: "Empty", value: "[]" },
  ],
  pseudocode: [
    "def invert(node):",
    "    if not node: return None",
    "    node.left, node.right = node.right, node.left",
    "    invert(node.left); invert(node.right)",
    "    return node",
  ],
  parse: (raw: string) => parseInvertBinaryTree(raw),
  generate: (input: unknown) => generateInvertBinaryTree(input as InvertBinaryTreeInput),
};
