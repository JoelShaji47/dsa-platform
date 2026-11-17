import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface KthSmallestBSTInput {
  tree: ParsedTree;
  k: number;
}

export function parseKthSmallestBST(raw: string): KthSmallestBSTInput {
  const lines = inputLines(raw);
  if (lines.length < 2) throw new Error("Use: tree, then k");
  const tree = parseLevelOrderTree(lines[0], { maxNodes: 15 });
  const k = integersFrom(lines[1])[0];
  if (!Number.isInteger(k) || k < 1 || k > tree.nodes.length) {
    throw new Error("k must be between 1 and the number of nodes");
  }
  return { tree, k };
}

export function generateKthSmallestBST({ tree, k }: KthSmallestBSTInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  let count = 0;
  let answer: number | null = null;
  let done = false;

  const snapshot = (active: number[] = [], curr: number | null = null) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: curr == null ? {} : { curr },
      annotations: Object.fromEntries([...settled].map((id) => [id, `#${nodes[id].value}`])),
      label: "BST (in-order)",
    });

  steps.push(
    step(
      0,
      "Start",
      `In-order traversal visits BST values in sorted order; stop at the ${k}th node.`,
      0,
      snap([]),
      { k, count },
      { tree: snapshot(tree.root == null ? [] : [tree.root], tree.root) }
    )
  );

  const inorder = (id: number | null) => {
    if (id == null || done) return;
    const node = nodes[id];
    inorder(node.left);
    if (done) return;

    count += 1;
    settled.add(id);
    if (count === k) {
      answer = node.value as number;
      done = true;
    }
    steps.push(
      step(
        steps.length,
        count === k ? "Found" : "Visit",
        `In-order node ${count} is ${node.value}.`,
        2,
        snap(Array.from({ length: count }, (_, index) => index), {
          active: [count - 1],
          settled: Array.from({ length: count - 1 }, (_, index) => index),
          label: "visited values",
        }),
        { count, k, value: node.value },
        { tree: snapshot([id], id) }
      )
    );

    if (!done) inorder(node.right);
  };

  inorder(tree.root);

  steps.push(
    step(
      steps.length,
      "Done",
      answer == null ? "No kth node exists." : `The ${k}th smallest value is ${answer}.`,
      4,
      snap([answer ?? ""], { active: [0], label: "answer" }),
      { k, answer: answer ?? "null" },
      {
        tree: snapshot([], null),
        done: true,
        result: answer == null ? "" : String(answer),
      }
    )
  );

  return steps;
}

export const kthSmallestBSTEntry: VisualizerEntry = {
  slug: "kth-smallest-element-in-a-bst",
  title: "Kth Smallest Element in a BST",
  inputHint: "tree, then k",
  defaultInput: "5 3 6 2 4 null null 1\n3",
  presets: [
    { label: "example", value: "5 3 6 2 4 null null 1\n3" },
    { label: "second", value: "3 1 4 null 2\n1" },
    { label: "single", value: "1\n1" },
  ],
  pseudocode: [
    "count = 0",
    "inorder(node):",
    "  inorder(node.left)",
    "  count += 1; if count == k: return node.value",
    "  inorder(node.right)",
  ],
  parse: parseKthSmallestBST,
  generate: (input) => generateKthSmallestBST(input as KthSmallestBSTInput),
};
