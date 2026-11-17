import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines } from "./input-utils";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface SameTreeInput {
  first: ParsedTree;
  second: ParsedTree;
}

export function parseSameTree(raw: string): SameTreeInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use two lines: tree p, then tree q");
  return {
    first: parseLevelOrderTree(lines[0], { maxNodes: 15 }),
    second: parseLevelOrderTree(lines[1], { maxNodes: 15 }),
  };
}

export function generateSameTree({ first, second }: SameTreeInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let same = true;

  const snapshot = (activeA: number[] = [], activeB: number[] = []) => ({
    tree: snapTree(first.nodes, { root: first.root, active: activeA, label: "p" }),
    treeAlt: snapTree(second.nodes, { root: second.root, active: activeB, label: "q" }),
  });

  steps.push(
    step(
      0,
      "Start",
      "Compare both trees node by node: values, left children, and right children must match.",
      0,
      snap([]),
      {},
      snapshot(first.root == null ? [] : [first.root], second.root == null ? [] : [second.root])
    )
  );

  const compare = (a: number | null, b: number | null): boolean => {
    if (a == null && b == null) {
      steps.push(
        step(
          steps.length,
          "Both null",
          "Both branches end here.",
          1,
          snap([]),
          {},
          snapshot()
        )
      );
      return true;
    }

    if (a == null || b == null) {
      same = false;
      steps.push(
        step(
          steps.length,
          "Structure differs",
          "One tree has a node where the other has null.",
          2,
          snap([]),
          { p: a == null ? "null" : first.nodes[a].value, q: b == null ? "null" : second.nodes[b].value },
          snapshot(a == null ? [] : [a], b == null ? [] : [b])
        )
      );
      return false;
    }

    const nodeA = first.nodes[a];
    const nodeB = second.nodes[b];
    if (nodeA.value !== nodeB.value) {
      same = false;
      steps.push(
        step(
          steps.length,
          "Values differ",
          `${nodeA.value} does not equal ${nodeB.value}.`,
          2,
          snap([]),
          { p: nodeA.value, q: nodeB.value },
          snapshot([a], [b])
        )
      );
      return false;
    }

    steps.push(
      step(
        steps.length,
        "Match",
        `Both nodes are ${nodeA.value}; compare their children.`,
        2,
        snap([]),
        { p: nodeA.value, q: nodeB.value },
        snapshot([a], [b])
      )
    );

    return compare(nodeA.left, nodeB.left) && compare(nodeA.right, nodeB.right);
  };

  compare(first.root, second.root);

  steps.push(
    step(
      steps.length,
      "Done",
      same ? "The trees are identical in structure and values." : "The trees differ.",
      4,
      snap([]),
      { same: same ? "true" : "false" },
      { ...snapshot(), done: true, result: same ? "true" : "false" }
    )
  );

  return steps;
}

export const sameTreeEntry: VisualizerEntry = {
  slug: "same-tree",
  title: "Same Tree",
  inputHint: "two lines, one level-order tree per line",
  defaultInput: "1 2 3\n1 2 3",
  presets: [
    { label: "same", value: "1 2 3\n1 2 3" },
    { label: "different", value: "1 2\n1 null 2" },
    { label: "values differ", value: "1 2\n1 3" },
  ],
  pseudocode: [
    "if p and q are both null: return true",
    "if one is null: return false",
    "if p.value != q.value: return false",
    "return same(p.left, q.left) and same(p.right, q.right)",
  ],
  parse: parseSameTree,
  generate: (input) => generateSameTree(input as SameTreeInput),
};
