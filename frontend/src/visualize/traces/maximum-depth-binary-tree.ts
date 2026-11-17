import {
  snap,
  snapTree,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface MaximumDepthInput {
  tree: ParsedTree;
}

export function parseMaximumDepth(raw: string): MaximumDepthInput {
  return { tree: parseLevelOrderTree(raw, { allowEmpty: true }) };
}

export function generateMaximumDepth({ tree }: MaximumDepthInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  const depths = new Map<number, number>();

  const annotations = (): Record<number, string> =>
    Object.fromEntries([...depths.entries()].map(([id, depth]) => [id, `d=${depth}`]));

  const snapshot = (active: number[], curr: number | null) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: annotations(),
      label: "tree",
    });

  steps.push(
    step(
      0,
      "Start",
      tree.root == null
        ? "The tree is empty, so its depth is 0."
        : "Walk the tree bottom-up. Each node's depth is 1 plus the deeper of its two subtrees.",
      0,
      snap([]),
      { nodes: nodes.length },
      { tree: snapshot(tree.root == null ? [] : [tree.root], tree.root) }
    )
  );

  const visit = (id: number | null): number => {
    if (id == null) return 0;
    const node = nodes[id];
    if (!node) return 0;

    steps.push(
      step(
        steps.length,
        "Visit",
        `At node ${node.value}, recurse into its left and right children.`,
        2,
        snap([]),
        { node: node.value },
        { tree: snapshot([id], id) }
      )
    );

    const left = visit(node.left);
    const right = visit(node.right);
    const depth = 1 + Math.max(left, right);
    depths.set(id, depth);
    settled.add(id);

    steps.push(
      step(
        steps.length,
        "Depth",
        `Node ${node.value}: 1 + max(${left}, ${right}) = ${depth}.`,
        4,
        snap([]),
        { node: node.value, left, right, depth },
        { tree: snapshot([id], id) }
      )
    );
    return depth;
  };

  const depth = visit(tree.root);
  steps.push(
    step(
      steps.length,
      "Done",
      `The deepest path visits ${depth} node${depth === 1 ? "" : "s"}.`,
      4,
      snap([]),
      { depth },
      { tree: snapshot([], null), result: String(depth), done: true }
    )
  );

  return steps;
}

export const maximumDepthEntry: VisualizerEntry = {
  slug: "maximum-depth-binary-tree",
  title: "Maximum Depth of Binary Tree",
  inputHint: "[3, 9, 20, null, null, 15, 7]",
  defaultInput: "[3, 9, 20, null, null, 15, 7]",
  presets: [
    { label: "Balanced", value: "[3, 9, 20, null, null, 15, 7]" },
    { label: "Skewed", value: "[1, 2, null, 3, null, 4]" },
    { label: "Single", value: "[1]" },
    { label: "Empty", value: "[]" },
  ],
  pseudocode: [
    "def depth(node):",
    "    if not node: return 0",
    "    left = depth(node.left)",
    "    right = depth(node.right)",
    "    return 1 + max(left, right)",
  ],
  parse: (raw: string) => parseMaximumDepth(raw),
  generate: (input: unknown) => generateMaximumDepth(input as MaximumDepthInput),
};
