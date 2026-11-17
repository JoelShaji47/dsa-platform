import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface BalancedTreeInput {
  tree: ParsedTree;
}

export function parseBalancedTree(raw: string): BalancedTreeInput {
  return { tree: parseLevelOrderTree(raw, { maxNodes: 15 }) };
}

export function generateBalancedTree({ tree }: BalancedTreeInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  const heights = new Map<number, number>();
  let balanced = true;

  const snapshot = (active: number[] = [], curr: number | null = null) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries([...heights.entries()].map(([id, height]) => [id, `h=${height}`])),
      label: "tree",
    });

  steps.push(
    step(
      0,
      "Start",
      "Compute each subtree's height from the bottom up; unbalanced subtrees report -1.",
      0,
      snap([]),
      { nodes: nodes.length },
      { tree: snapshot(tree.root == null ? [] : [tree.root], tree.root) }
    )
  );

  const heightOf = (id: number | null): number => {
    if (id == null) return 0;
    const node = nodes[id];
    if (!node) return 0;

    steps.push(
      step(
        steps.length,
        "Visit",
        `Measure the left and right subtrees of ${node.value}.`,
        2,
        snap([]),
        { node: node.value },
        { tree: snapshot([id], id) }
      )
    );

    const left = heightOf(node.left);
    const right = heightOf(node.right);
    let height = 0;
    if (left === -1 || right === -1 || Math.abs(left - right) > 1) {
      balanced = false;
      height = -1;
    } else {
      height = Math.max(left, right) + 1;
    }
    heights.set(id, height);
    settled.add(id);

    steps.push(
      step(
        steps.length,
        height === -1 ? "Unbalanced" : "Height",
        height === -1
          ? `Node ${node.value} has subtree heights ${left} and ${right}, so this subtree is unbalanced.`
          : `Node ${node.value} has height ${height} (left ${left}, right ${right}).`,
        3,
        snap([]),
        { node: node.value, left, right, height },
        { tree: snapshot([id], id) }
      )
    );

    return height;
  };

  heightOf(tree.root);

  steps.push(
    step(
      steps.length,
      "Done",
      balanced ? "Every subtree differs in height by at most one." : "At least one subtree is unbalanced.",
      5,
      snap([]),
      { balanced: balanced ? "true" : "false" },
      {
        tree: snapshot([], null),
        done: true,
        result: balanced ? "true" : "false",
      }
    )
  );

  return steps;
}

export const balancedTreeEntry: VisualizerEntry = {
  slug: "balanced-binary-tree",
  title: "Balanced Binary Tree",
  inputHint: "level-order tree, e.g. [3, 9, 20, null, null, 15, 7]",
  defaultInput: "3 9 20 null null 15 7",
  presets: [
    { label: "balanced", value: "3 9 20 null null 15 7" },
    { label: "unbalanced", value: "1 2 2 3 3 null null 4 4" },
    { label: "single", value: "1" },
  ],
  pseudocode: [
    "height(node):",
    "  if node is null: return 0",
    "  left = height(node.left); right = height(node.right)",
    "  if either is -1 or |left - right| > 1: return -1",
    "  return max(left, right) + 1",
  ],
  parse: parseBalancedTree,
  generate: (input) => generateBalancedTree(input as BalancedTreeInput),
};
