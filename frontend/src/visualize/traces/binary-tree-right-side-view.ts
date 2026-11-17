import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface RightSideViewInput {
  tree: ParsedTree;
}

export function parseRightSideView(raw: string): RightSideViewInput {
  return { tree: parseLevelOrderTree(raw, { maxNodes: 15 }) };
}

export function generateRightSideView({ tree }: RightSideViewInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const levels: number[][] = [];
  let queue: number[] = tree.root == null ? [] : [tree.root];

  while (queue.length > 0) {
    levels.push([...queue]);
    const next: number[] = [];
    for (const id of queue) {
      if (nodes[id].left != null) next.push(nodes[id].left!);
      if (nodes[id].right != null) next.push(nodes[id].right!);
    }
    queue = next;
  }

  const result: number[] = [];
  const settled = new Set<number>();

  const snapshot = (active: number[] = []) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: {},
      label: "tree",
    });

  steps.push(
    step(0, "Start", "Traverse level by level; the rightmost node of each level is visible.", 0, snap([]), { levels: levels.length }, { tree: snapshot(tree.root == null ? [] : [tree.root]) })
  );

  levels.forEach((level, index) => {
    const visible = level[level.length - 1];
    result.push(nodes[visible].value as number);
    level.forEach((id) => settled.add(id));
    steps.push(
      step(
        steps.length,
        `Level ${index}`,
        `The rightmost node on level ${index} is ${nodes[visible].value}.`,
        2,
        snap(result, { active: [result.length - 1], settled: result.slice(0, -1).map((_, i) => i), label: "visible values" }),
        { level: index, visible: nodes[visible].value },
        { tree: snapshot(level) }
      )
    );
  });

  const output = result.join(" ");
  steps.push(
    step(
      steps.length,
      "Done",
      `The right side view is ${output}.`,
      3,
      snap(result, { settled: result.map((_, index) => index), label: "visible values" }),
      { levels: levels.length },
      { tree: snapshot(), done: true, result: output }
    )
  );

  return steps;
}

export const rightSideViewEntry: VisualizerEntry = {
  slug: "binary-tree-right-side-view",
  title: "Binary Tree Right Side View",
  inputHint: "level-order tree, e.g. [1, 2, 3, null, 5, null, 4]",
  defaultInput: "1 2 3 null 5 null 4",
  presets: [
    { label: "example", value: "1 2 3 null 5 null 4" },
    { label: "right chain", value: "1 null 3" },
    { label: "single", value: "1" },
  ],
  pseudocode: [
    "queue = [root]",
    "while queue:",
    "  level = all nodes in queue",
    "  record the last node's value",
    "  enqueue children of the level",
  ],
  parse: parseRightSideView,
  generate: (input) => generateRightSideView(input as RightSideViewInput),
};
