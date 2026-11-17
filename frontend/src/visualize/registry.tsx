"use client";

import type { ReactNode } from "react";
import type { BaseStep, VisualizerEntry } from "./trace-types";
import { twoSumEntry } from "./traces/two-sum";
import { twoSumIIEntry } from "./traces/two-sum-ii";
import { moveZeroesEntry } from "./traces/move-zeroes";
import { containerEntry } from "./traces/container-with-most-water";
import { threeSumEntry } from "./traces/three-sum";
import { stockEntry } from "./traces/best-time-to-buy-and-sell-stock";
import { binarySearchEntry } from "./traces/binary-search";
import { validParenthesesEntry } from "./traces/valid-parentheses";
import { minStackEntry } from "./traces/min-stack";
import { evalRpnEntry } from "./traces/eval-rpn";
import { dailyTemperaturesEntry } from "./traces/daily-temperatures";
import { longestSubstringEntry } from "./traces/longest-substring";
import { permutationInStringEntry } from "./traces/permutation-in-string";
import { charReplacementEntry } from "./traces/char-replacement";
import { slidingWindowMaximumEntry } from "./traces/sliding-window-maximum";
import { taskSchedulerEntry } from "./traces/task-scheduler";
import { designTwitterEntry } from "./traces/design-twitter";
import { reverseLinkedListEntry } from "./traces/reverse-linked-list";
import { mergeTwoListsEntry } from "./traces/merge-two-sorted-lists";
import { linkedListCycleEntry } from "./traces/linked-list-cycle";
import { maximumDepthEntry } from "./traces/maximum-depth-binary-tree";
import { invertBinaryTreeEntry } from "./traces/invert-binary-tree";
import { validateBstEntry } from "./traces/validate-binary-search-tree";
import { levelOrderEntry } from "./traces/binary-tree-level-order-traversal";
import { floodFillEntry } from "./traces/flood-fill";
import { numberOfIslandsEntry } from "./traces/number-of-islands";
import { courseScheduleEntry } from "./traces/course-schedule";
import { cloneGraphEntry } from "./traces/clone-graph";
import { climbingStairsEntry } from "./traces/climbing-stairs";
import { uniquePathsEntry } from "./traces/unique-paths";
import { coinChangeEntry } from "./traces/coin-change";
import { editDistanceEntry } from "./traces/edit-distance";
import { ArrayRenderer } from "./renderers/array-renderer";
import { StackRenderer } from "./renderers/stack-renderer";
import { QueueRenderer } from "./renderers/queue-renderer";
import { LinkedListRenderer } from "./renderers/linked-list-renderer";
import { TreeRenderer } from "./renderers/tree-renderer";
import { GraphRenderer } from "./renderers/graph-renderer";
import { GridRenderer } from "./renderers/grid-renderer";

export interface RegistryItem {
  entry: VisualizerEntry;
  render: (step: BaseStep) => ReactNode;
}

function arrayItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => <ArrayRenderer snapshot={step.array} />,
  };
}

function stackItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {step.array.values.length > 0 && <ArrayRenderer snapshot={step.array} />}
        {(step.stack ?? step.stackAlt) && (
          <div className="flex items-start justify-center gap-8">
            {step.stack && <StackRenderer snapshot={step.stack} />}
            {step.stackAlt && <StackRenderer snapshot={step.stackAlt} />}
          </div>
        )}
      </div>
    ),
  };
}

function queueItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {step.array.values.length > 0 && <ArrayRenderer snapshot={step.array} />}
        {(step.queue ?? step.queueAlt) && (
          <div className="flex flex-wrap items-start justify-center gap-8">
            {step.queue && <QueueRenderer snapshot={step.queue} />}
            {step.queueAlt && <QueueRenderer snapshot={step.queueAlt} />}
          </div>
        )}
      </div>
    ),
  };
}

function linkedItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {(step.linkedList ?? step.linkedListAlt) && (
          <div className="flex flex-wrap items-start justify-center gap-8">
            {step.linkedList && <LinkedListRenderer snapshot={step.linkedList} />}
            {step.linkedListAlt && <LinkedListRenderer snapshot={step.linkedListAlt} />}
          </div>
        )}
        {step.array.values.length > 0 && (
          <div>
            <p className="mb-1 text-center font-mono text-[10px] uppercase tracking-widest text-gray-500">
              merged
            </p>
            <ArrayRenderer snapshot={step.array} />
          </div>
        )}
      </div>
    ),
  };
}

function treeItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {step.tree && <TreeRenderer snapshot={step.tree} />}
        {step.queue && <QueueRenderer snapshot={step.queue} />}
        {step.array.values.length > 0 && <ArrayRenderer snapshot={step.array} />}
      </div>
    ),
  };
}

function graphItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {(step.graph ?? step.graphAlt) && (
          <div className="flex flex-wrap items-start justify-center gap-8">
            {step.graph && <GraphRenderer snapshot={step.graph} />}
            {step.graphAlt && <GraphRenderer snapshot={step.graphAlt} />}
          </div>
        )}
        {step.queue && <QueueRenderer snapshot={step.queue} />}
        {step.array.values.length > 0 && (
          <div>
            <p className="mb-1 text-center font-mono text-[10px] uppercase tracking-widest text-gray-500">
              order
            </p>
            <ArrayRenderer snapshot={step.array} />
          </div>
        )}
      </div>
    ),
  };
}

function gridItem(entry: VisualizerEntry): RegistryItem {
  return {
    entry,
    render: (step) => (
      <div className="flex flex-col gap-4">
        {step.grid && <GridRenderer snapshot={step.grid} />}
        {step.queue && <QueueRenderer snapshot={step.queue} />}
        {step.array.values.length > 0 && <ArrayRenderer snapshot={step.array} />}
      </div>
    ),
  };
}

/** slug → trace generator + renderer. Unlisted slugs show "coming soon". */
const REGISTRY: Record<string, RegistryItem> = {
  "two-sum": arrayItem(twoSumEntry),
  "two-sum-ii-input-array-is-sorted": arrayItem(twoSumIIEntry),
  "move-zeroes": arrayItem(moveZeroesEntry),
  "container-with-most-water": arrayItem(containerEntry),
  "3sum": arrayItem(threeSumEntry),
  "best-time-to-buy-and-sell-stock": arrayItem(stockEntry),
  "binary-search": arrayItem(binarySearchEntry),
  "valid-parentheses": stackItem(validParenthesesEntry),
  "min-stack": stackItem(minStackEntry),
  "evaluate-reverse-polish-notation": stackItem(evalRpnEntry),
  "daily-temperatures": stackItem(dailyTemperaturesEntry),
  "longest-substring-without-repeating-characters": arrayItem(longestSubstringEntry),
  "permutation-in-string": arrayItem(permutationInStringEntry),
  "longest-repeating-character-replacement": arrayItem(charReplacementEntry),
  "sliding-window-maximum": queueItem(slidingWindowMaximumEntry),
  "task-scheduler": queueItem(taskSchedulerEntry),
  "design-twitter": queueItem(designTwitterEntry),
  "reverse-linked-list": linkedItem(reverseLinkedListEntry),
  "merge-two-sorted-lists": linkedItem(mergeTwoListsEntry),
  "linked-list-cycle": linkedItem(linkedListCycleEntry),
  "maximum-depth-binary-tree": treeItem(maximumDepthEntry),
  "invert-binary-tree": treeItem(invertBinaryTreeEntry),
  "validate-binary-search-tree": treeItem(validateBstEntry),
  "binary-tree-level-order-traversal": treeItem(levelOrderEntry),
  "flood-fill": gridItem(floodFillEntry),
  "number-of-islands": gridItem(numberOfIslandsEntry),
  "course-schedule": graphItem(courseScheduleEntry),
  "clone-graph": graphItem(cloneGraphEntry),
  "climbing-stairs": arrayItem(climbingStairsEntry),
  "unique-paths": gridItem(uniquePathsEntry),
  "coin-change": arrayItem(coinChangeEntry),
  "edit-distance": gridItem(editDistanceEntry),
};

export function lookupVisualizer(slug: string): RegistryItem | null {
  return REGISTRY[slug] ?? null;
}

export function supportedSlugs(): string[] {
  return Object.keys(REGISTRY);
}
