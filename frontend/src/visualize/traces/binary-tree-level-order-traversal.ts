import {
  snap,
  snapQueue,
  snapTree,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface LevelOrderInput {
  tree: ParsedTree;
}

export function parseLevelOrder(raw: string): LevelOrderInput {
  return { tree: parseLevelOrderTree(raw, { allowEmpty: true }) };
}

export function generateLevelOrder({ tree }: LevelOrderInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  const levels: (number | string)[][] = [];

  const snapshot = (active: number[]) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      label: "tree",
    });

  const queueSnapshot = (queue: number[]) =>
    snapQueue(
      queue.map((id) => nodes[id]?.value ?? "null"),
      { active: queue.length > 0 ? [0] : [], label: "queue" }
    );

  if (tree.root == null) {
    steps.push(
      step(0, "Empty", "An empty tree has no levels.", 0, snap([]), {}, {
        tree: snapshot([]),
        queue: queueSnapshot([]),
        result: "[]",
        done: true,
      })
    );
    return steps;
  }

  const queue: number[] = [tree.root];
  steps.push(
    step(
      0,
      "Start",
      "BFS: process the current level left-to-right, enqueueing the next level as we go.",
      1,
      snap([]),
      { size: queue.length },
      { tree: snapshot([tree.root]), queue: queueSnapshot(queue) }
    )
  );

  while (queue.length > 0) {
    const levelSize = queue.length;
    const levelIds: number[] = [];
    const levelValues: (number | string)[] = [];

    steps.push(
      step(
        steps.length,
        "Level",
        `Process exactly ${levelSize} node${levelSize === 1 ? "" : "s"} at level ${levels.length}.`,
        3,
        snap([]),
        { level: levels.length, size: levelSize },
        { tree: snapshot([...queue]), queue: queueSnapshot(queue) }
      )
    );

    for (let i = 0; i < levelSize; i += 1) {
      const id = queue.shift()!;
      const node = nodes[id];
      if (!node) continue;
      settled.add(id);
      levelIds.push(id);
      levelValues.push(node.value);
      if (node.left != null) queue.push(node.left);
      if (node.right != null) queue.push(node.right);

      steps.push(
        step(
          steps.length,
          "Visit",
          `Pop ${node.value}; add it to this level and enqueue its children.`,
          6,
          snap([]),
          { value: node.value, remaining: queue.length },
          { tree: snapshot([id]), queue: queueSnapshot(queue) }
        )
      );
    }

    levels.push(levelValues);
    steps.push(
      step(
        steps.length,
        "Level done",
        `Level ${levels.length - 1}: [${levelValues.join(", ")}].`,
        9,
        snap([]),
        { level: levels.length - 1 },
        { tree: snapshot(levelIds), queue: queueSnapshot(queue) }
      )
    );
  }

  const result = `[${levels.map((level) => `[${level.join(", ")}]`).join(", ")}]`;
  steps.push(
    step(
      steps.length,
      "Done",
      "Every level has been collected in left-to-right order.",
      10,
      snap([]),
      { levels: levels.length },
      { tree: snapshot([]), queue: queueSnapshot([]), result, done: true }
    )
  );

  return steps;
}

export const levelOrderEntry: VisualizerEntry = {
  slug: "binary-tree-level-order-traversal",
  title: "Binary Tree Level Order Traversal",
  inputHint: "[3, 9, 20, null, null, 15, 7]",
  defaultInput: "[3, 9, 20, null, null, 15, 7]",
  presets: [
    { label: "Balanced", value: "[3, 9, 20, null, null, 15, 7]" },
    { label: "Single", value: "[1]" },
    { label: "Empty", value: "[]" },
  ],
  pseudocode: [
    "if not root: return []",
    "queue = deque([root])",
    "while queue:",
    "    level = []",
    "    for _ in range(len(queue)):",
    "        node = queue.popleft()",
    "        level.append(node.val)",
    "        if node.left: queue.append(node.left)",
    "        if node.right: queue.append(node.right)",
    "    result.append(level)",
    "return result",
  ],
  parse: (raw: string) => parseLevelOrder(raw),
  generate: (input: unknown) => generateLevelOrder(input as LevelOrderInput),
};
