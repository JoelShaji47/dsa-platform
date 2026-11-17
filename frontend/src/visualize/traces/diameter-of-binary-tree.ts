import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface DiameterTreeInput {
  tree: ParsedTree;
}

export function parseDiameterTree(raw: string): DiameterTreeInput {
  return { tree: parseLevelOrderTree(raw, { maxNodes: 15 }) };
}

export function generateDiameterTree({ tree }: DiameterTreeInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  const heights = new Map<number, number>();
  let best = 0;
  let bestNode: number | null = null;

  const snapshot = (active: number[] = [], curr: number | null = null) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries(
        [...heights.entries()].map(([id, height]) => [id, `h=${height}`])
      ),
      label: "tree",
    });

  steps.push(
    step(
      0,
      "Start",
      "For each node, the best path through it is left height + right height.",
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
        `Measure the left and right depths below ${node.value}.`,
        2,
        snap([]),
        { node: node.value },
        { tree: snapshot([id], id) }
      )
    );

    const left = heightOf(node.left);
    const right = heightOf(node.right);
    const candidate = left + right;
    if (candidate > best) {
      best = candidate;
      bestNode = id;
    }
    const height = Math.max(left, right) + 1;
    heights.set(id, height);
    settled.add(id);

    steps.push(
      step(
        steps.length,
        "Update diameter",
        `Through ${node.value}: ${left} + ${right} = ${candidate}; best is ${best}. Height is ${height}.`,
        3,
        snap([]),
        { node: node.value, candidate, best, height },
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
      `The diameter is ${best} edge${best === 1 ? "" : "s"}${bestNode == null ? "" : `, best seen at node ${nodes[bestNode].value}`}.`,
      5,
      snap([]),
      { diameter: best },
      {
        tree: snapshot([], null),
        done: true,
        result: String(best),
      }
    )
  );

  return steps;
}

export const diameterTreeEntry: VisualizerEntry = {
  slug: "diameter-of-binary-tree",
  title: "Diameter of Binary Tree",
  inputHint: "level-order tree, e.g. [1, 2, 3, 4, 5]",
  defaultInput: "1 2 3 4 5",
  presets: [
    { label: "example", value: "1 2 3 4 5" },
    { label: "path", value: "1 2" },
    { label: "single", value: "1" },
  ],
  pseudocode: [
    "diameter = 0",
    "height(node):",
    "  if node is null: return 0",
    "  left = height(node.left); right = height(node.right)",
    "  diameter = max(diameter, left + right)",
    "  return max(left, right) + 1",
  ],
  parse: parseDiameterTree,
  generate: (input) => generateDiameterTree(input as DiameterTreeInput),
};
