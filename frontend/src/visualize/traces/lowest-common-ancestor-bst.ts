import { snap, snapTree, step, type BaseStep, type VisualizerEntry } from "../trace-types";
import { inputLines, integersFrom } from "./input-utils";
import { parseLevelOrderTree, type ParsedTree } from "./tree-utils";

export interface LcaBstInput {
  tree: ParsedTree;
  p: number;
  q: number;
}

export function parseLcaBst(raw: string): LcaBstInput {
  const lines = inputLines(raw);
  if (lines.length < 3) throw new Error("Use: tree, p, q");
  const tree = parseLevelOrderTree(lines[0], { maxNodes: 15 });
  const p = integersFrom(lines[1])[0];
  const q = integersFrom(lines[2])[0];
  if (p == null || q == null) throw new Error("Provide numeric p and q values");
  const values = new Set(tree.nodes.map((node) => node.value));
  if (!values.has(p) || !values.has(q)) throw new Error("p and q must exist in the tree");
  return { tree, p, q };
}

export function generateLcaBst({ tree, p, q }: LcaBstInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const nodes = tree.nodes;
  const settled = new Set<number>();
  const low = Math.min(p, q);
  const high = Math.max(p, q);
  let curr = tree.root;
  let answer: number | null = null;

  const snapshot = (active: number[] = [], current: number | null = curr) =>
    snapTree(nodes, {
      root: tree.root,
      active,
      settled: [...settled],
      pointers: current == null ? {} : { curr: current },
      label: "BST",
    });

  steps.push(
    step(
      0,
      "Start",
      `Find the split point for ${low} and ${high}; the first node between them is the LCA.`,
      0,
      snap([]),
      { p: low, q: high },
      { tree: snapshot(curr == null ? [] : [curr], curr) }
    )
  );

  while (curr != null) {
    const node = nodes[curr];
    const value = node.value as number;

    if (high < value) {
      steps.push(
        step(
          steps.length,
          "Go left",
          `Both targets are smaller than ${value}; move left.`,
          2,
          snap([]),
          { at: value, p: low, q: high },
          { tree: snapshot([curr], curr) }
        )
      );
      settled.add(curr);
      curr = node.left;
    } else if (low > value) {
      steps.push(
        step(
          steps.length,
          "Go right",
          `Both targets are larger than ${value}; move right.`,
          3,
          snap([]),
          { at: value, p: low, q: high },
          { tree: snapshot([curr], curr) }
        )
      );
      settled.add(curr);
      curr = node.right;
    } else {
      answer = value;
      steps.push(
        step(
          steps.length,
          "Split",
          `${value} lies between ${low} and ${high}; it is the lowest common ancestor.`,
          4,
          snap([]),
          { at: value, p: low, q: high },
          { tree: snapshot([curr], curr) }
        )
      );
      break;
    }
  }

  steps.push(
    step(
      steps.length,
      "Done",
      answer == null ? "No common ancestor found." : `The LCA is ${answer}.`,
      5,
      snap([answer ?? ""], { active: [0], label: "answer" }),
      { answer: answer ?? "null" },
      { tree: snapshot([], null), done: true, result: answer == null ? "" : String(answer) }
    )
  );

  return steps;
}

export const lcaBstEntry: VisualizerEntry = {
  slug: "lowest-common-ancestor-bst",
  title: "Lowest Common Ancestor of a BST",
  inputHint: "tree, then p, then q",
  defaultInput: "6 2 8 0 4 7 9 null null 3 5\n2\n8",
  presets: [
    { label: "example", value: "6 2 8 0 4 7 9 null null 3 5\n2\n8" },
    { label: "inside left", value: "6 2 8 0 4 7 9 null null 3 5\n2\n4" },
    { label: "small", value: "2 1 3\n2\n3" },
  ],
  pseudocode: [
    "curr = root",
    "while curr:",
    "  if p and q are both less: curr = curr.left",
    "  else if p and q are both greater: curr = curr.right",
    "  else: return curr",
  ],
  parse: parseLcaBst,
  generate: (input) => generateLcaBst(input as LcaBstInput),
};
