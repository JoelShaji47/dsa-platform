import { describe, expect, it } from "vitest";
import type { VisualizerEntry } from "../trace-types";
import { maximumSubarrayEntry } from "./maximum-subarray";
import { mergeIntervalsEntry } from "./merge-intervals";
import { topKFrequentEntry } from "./top-k-frequent-elements";
import { trappingRainWaterEntry } from "./trapping-rain-water";
import { validAnagramEntry } from "./valid-anagram";
import { validPalindromeEntry } from "./valid-palindrome";
import { minimumWindowSubstringEntry } from "./minimum-window-substring";
import { groupAnagramsEntry } from "./group-anagrams";
import { containsDuplicateIIEntry } from "./contains-duplicate-ii";
import { fruitIntoBasketsEntry } from "./fruit-into-baskets";
import { addTwoNumbersEntry } from "./add-two-numbers";
import { removeNthNodeEntry } from "./remove-nth-node-from-end-of-list";
import { copyRandomPointerEntry } from "./copy-list-with-random-pointer";
import { mergeKSortedListsEntry } from "./merge-k-sorted-lists";
import { reverseKGroupEntry } from "./reverse-nodes-in-k-group";
import { reorderListEntry } from "./reorder-list";
import { palindromeLinkedListEntry } from "./palindrome-linked-list";
import { asteroidCollisionEntry } from "./asteroid-collision";
import { carFleetEntry } from "./car-fleet";
import { generateParenthesesEntry } from "./generate-parentheses";
import { nextGreaterElementEntry } from "./next-greater-element";
import { largestRectangleEntry } from "./largest-rectangle-in-histogram";
import { baseballGameEntry } from "./baseball-game";
import { kthLargestStreamEntry } from "./kth-largest-element-in-a-stream";
import { lastStoneWeightEntry } from "./last-stone-weight";
import { carPoolingEntry } from "./car-pooling";
import { kClosestPointsEntry } from "./k-closest-points-to-origin";
import { kthLargestArrayEntry } from "./kth-largest-element-in-an-array";
import { medianStreamEntry } from "./find-median-from-data-stream";
import { balancedTreeEntry } from "./balanced-binary-tree";
import { diameterTreeEntry } from "./diameter-of-binary-tree";
import { sameTreeEntry } from "./same-tree";
import { rightSideViewEntry } from "./binary-tree-right-side-view";
import { kthSmallestBSTEntry } from "./kth-smallest-element-in-a-bst";
import { lcaBstEntry } from "./lowest-common-ancestor-bst";
import { maxAreaIslandEntry } from "./max-area-of-island";
import { rottingOrangesEntry } from "./rotting-oranges";
import { pacificAtlanticEntry } from "./pacific-atlantic-water-flow";
import { wordLadderEntry } from "./word-ladder";
import { courseScheduleIIEntry } from "./course-schedule-ii";
import { networkDelayEntry } from "./network-delay-time";
import { houseRobberEntry } from "./house-robber";
import { houseRobberIIEntry } from "./house-robber-ii";
import { lisEntry } from "./longest-increasing-subsequence";
import { lcsEntry } from "./longest-common-subsequence";
import { wordBreakEntry } from "./word-break";
import { partitionSubsetEntry } from "./partition-equal-subset-sum";

interface Case {
  entry: VisualizerEntry;
  expected: string;
}

const CASES: Case[] = [
  { entry: maximumSubarrayEntry, expected: "6" },
  { entry: mergeIntervalsEntry, expected: "1 6\n8 10\n15 18" },
  { entry: topKFrequentEntry, expected: "1 2" },
  { entry: trappingRainWaterEntry, expected: "6" },
  { entry: validAnagramEntry, expected: "true" },
  { entry: validPalindromeEntry, expected: "true" },
  { entry: minimumWindowSubstringEntry, expected: "BANC" },
  { entry: groupAnagramsEntry, expected: "ate eat tea\nbat\nnat tan" },
  { entry: containsDuplicateIIEntry, expected: "true" },
  { entry: fruitIntoBasketsEntry, expected: "3" },
  { entry: addTwoNumbersEntry, expected: "7 0 8" },
  { entry: removeNthNodeEntry, expected: "1 2 3 5" },
  { entry: copyRandomPointerEntry, expected: "7 13 11 10 1" },
  { entry: mergeKSortedListsEntry, expected: "0 1 2 3 4 5 6" },
  { entry: reverseKGroupEntry, expected: "2 1 4 3 5" },
  { entry: reorderListEntry, expected: "1 4 2 3" },
  { entry: palindromeLinkedListEntry, expected: "true" },
  { entry: asteroidCollisionEntry, expected: "5 10" },
  { entry: carFleetEntry, expected: "4" },
  {
    entry: generateParenthesesEntry,
    expected: "((()))\n(()())\n(())()\n()(())\n()()()",
  },
  { entry: nextGreaterElementEntry, expected: "5 25 25 -1" },
  { entry: largestRectangleEntry, expected: "10" },
  { entry: baseballGameEntry, expected: "30" },
  { entry: kthLargestStreamEntry, expected: "4 5 5" },
  { entry: lastStoneWeightEntry, expected: "0" },
  { entry: carPoolingEntry, expected: "false" },
  { entry: kClosestPointsEntry, expected: "-2 2\n2 -2" },
  { entry: kthLargestArrayEntry, expected: "5" },
  { entry: medianStreamEntry, expected: "1.0\n1.5\n2.0\n2.5\n3.0" },
  { entry: balancedTreeEntry, expected: "true" },
  { entry: diameterTreeEntry, expected: "3" },
  { entry: sameTreeEntry, expected: "true" },
  { entry: rightSideViewEntry, expected: "1 3 4" },
  { entry: kthSmallestBSTEntry, expected: "3" },
  { entry: lcaBstEntry, expected: "6" },
  { entry: maxAreaIslandEntry, expected: "4" },
  { entry: rottingOrangesEntry, expected: "4" },
  {
    entry: pacificAtlanticEntry,
    expected: "0 4\n1 3\n1 4\n2 2\n3 0\n3 1\n4 0",
  },
  { entry: wordLadderEntry, expected: "5" },
  { entry: courseScheduleIIEntry, expected: "0 1 2 3" },
  { entry: networkDelayEntry, expected: "2" },
  { entry: houseRobberEntry, expected: "4" },
  { entry: houseRobberIIEntry, expected: "3" },
  { entry: lisEntry, expected: "4" },
  { entry: lcsEntry, expected: "3" },
  { entry: wordBreakEntry, expected: "true" },
  { entry: partitionSubsetEntry, expected: "true" },
];

describe("new visualizer traces", () => {
  it("covers 47 new problems", () => {
    expect(CASES).toHaveLength(47);
    expect(new Set(CASES.map(({ entry }) => entry.slug)).size).toBe(47);
  });

  for (const { entry, expected } of CASES) {
    describe(entry.slug, () => {
      it("runs the seeded default input to completion", () => {
        const input = entry.parse(entry.defaultInput);
        const steps = entry.generate(input);
        expect(steps.length).toBeGreaterThan(1);
        const last = steps[steps.length - 1];
        expect(last.done).toBe(true);
        expect(last.result).toBe(expected);
      });

      it("renders at least one visual snapshot and runs every preset", () => {
        const steps = entry.generate(entry.parse(entry.defaultInput));
        expect(
          steps.some(
            (step) =>
              step.array.values.length > 0 ||
              step.arrayAlt ||
              step.stack ||
              step.queue ||
              step.linkedList ||
              step.tree ||
              step.graph ||
              step.grid
          )
        ).toBe(true);

        for (const preset of entry.presets) {
          const presetSteps = entry.generate(entry.parse(preset.value));
          expect(presetSteps.length).toBeGreaterThan(1);
          expect(presetSteps[presetSteps.length - 1].done).toBe(true);
        }
      });
    });
  }
});
