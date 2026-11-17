import { describe, expect, it } from "vitest";
import { generateBinarySearch, parseBinarySearch } from "./binary-search";
import { generateTwoSum, parseTwoSum } from "./two-sum";
import { generateTwoSumII, parseTwoSumII } from "./two-sum-ii";
import { generateMoveZeroes, parseMoveZeroes } from "./move-zeroes";
import { generateContainer, parseContainer } from "./container-with-most-water";
import { generateThreeSum, parseThreeSum } from "./three-sum";
import { generateStock, parseStock } from "./best-time-to-buy-and-sell-stock";
import { generateValidParentheses, parseValidParentheses } from "./valid-parentheses";
import { generateMinStack, parseMinStack } from "./min-stack";
import { generateEvalRpn, parseEvalRpn } from "./eval-rpn";
import { generateDailyTemperatures, parseDailyTemperatures } from "./daily-temperatures";
import { generateLongestSubstring, parseLongestSubstring } from "./longest-substring";
import { generatePermutationInString, parsePermutationInString } from "./permutation-in-string";
import { generateCharReplacement, parseCharReplacement } from "./char-replacement";
import {
  generateSlidingWindowMaximum,
  parseSlidingWindowMaximum,
} from "./sliding-window-maximum";
import { generateTaskScheduler, parseTaskScheduler } from "./task-scheduler";
import { generateDesignTwitter, parseDesignTwitter } from "./design-twitter";
import { generateReverseLinkedList, parseReverseLinkedList } from "./reverse-linked-list";
import { generateMergeTwoLists, parseMergeTwoLists } from "./merge-two-sorted-lists";
import { generateLinkedListCycle, parseLinkedListCycle } from "./linked-list-cycle";
import { generateMaximumDepth, parseMaximumDepth } from "./maximum-depth-binary-tree";
import { generateInvertBinaryTree, parseInvertBinaryTree } from "./invert-binary-tree";
import { generateValidateBst, parseValidateBst } from "./validate-binary-search-tree";
import { generateLevelOrder, parseLevelOrder } from "./binary-tree-level-order-traversal";
import { generateFloodFill, parseFloodFill } from "./flood-fill";
import { generateNumberOfIslands, parseNumberOfIslands } from "./number-of-islands";
import { generateCourseSchedule, parseCourseSchedule } from "./course-schedule";
import { generateCloneGraph, parseCloneGraph } from "./clone-graph";
import { generateClimbingStairs, parseClimbingStairs } from "./climbing-stairs";
import { generateUniquePaths, parseUniquePaths } from "./unique-paths";
import { generateCoinChange, parseCoinChange } from "./coin-change";
import { generateEditDistance, parseEditDistance } from "./edit-distance";

describe("two-sum trace", () => {
  it("finds the pair and ends done with the right result", () => {
    const steps = generateTwoSum(parseTwoSum("[2, 7, 11, 15], 9"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[0, 1]");
    expect(steps[0].array.values).toEqual([2, 7, 11, 15]);
  });

  it("handles duplicates and missing pairs", () => {
    const dup = generateTwoSum(parseTwoSum("[3, 3], 6"));
    expect(dup[dup.length - 1].result).toBe("[0, 1]");
    const miss = generateTwoSum(parseTwoSum("[1, 2, 3], 7"));
    expect(miss[miss.length - 1].done).toBe(true);
    expect(miss[miss.length - 1].result).toBeUndefined();
  });

  it("rejects bad input", () => {
    expect(() => parseTwoSum("nope")).toThrow();
    expect(() => parseTwoSum("[1], 1")).toThrow();
    expect(() => parseTwoSum("[1, 2]")).toThrow();
  });
});

describe("two-sum-ii trace", () => {
  it("returns 1-indexed indices", () => {
    const steps = generateTwoSumII(parseTwoSumII("[2, 7, 11, 15], 9"));
    expect(steps[steps.length - 1].result).toBe("[1, 2]");
    expect(steps[steps.length - 1].done).toBe(true);
  });

  it("squeezes from the correct end and reports misses", () => {
    const steps = generateTwoSumII(parseTwoSumII("[1, 2, 3, 4, 5], 9"));
    expect(steps[steps.length - 1].result).toBe("[4, 5]");
    const miss = generateTwoSumII(parseTwoSumII("[1, 2, 3], 7"));
    expect(miss[miss.length - 1].done).toBe(true);
    expect(miss[miss.length - 1].result).toBeUndefined();
  });
});

describe("move-zeroes trace", () => {
  it("front-loads non-zeroes in order", () => {
    const steps = generateMoveZeroes(parseMoveZeroes("[0, 1, 0, 3, 12]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[1, 3, 12, 0, 0]");
    expect(last.array.values).toEqual([1, 3, 12, 0, 0]);
  });

  it("handles all-zero and zero-free inputs", () => {
    expect(generateMoveZeroes(parseMoveZeroes("[0, 0]"))[0]).toBeTruthy();
    const clean = generateMoveZeroes(parseMoveZeroes("[1, 2]"));
    expect(clean[clean.length - 1].result).toBe("[1, 2]");
  });
});

describe("container trace", () => {
  it("finds 49 for the classic input", () => {
    const steps = generateContainer(parseContainer("[1, 8, 6, 2, 5, 4, 8, 3, 7]"));
    const last = steps[steps.length - 1];
    expect(last.result).toBe("49");
    expect(last.done).toBe(true);
  });

  it("handles two bars and rejects negatives", () => {
    expect(generateContainer(parseContainer("[1, 1]"))[1]).toBeTruthy();
    expect(() => parseContainer("[-1, 2]")).toThrow();
  });
});

describe("3sum trace", () => {
  it("finds both triplets for the classic input", () => {
    const steps = generateThreeSum(parseThreeSum("[-1, 0, 1, 2, -1, -4]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toContain("[-1, -1, 2]");
    expect(last.result).toContain("[-1, 0, 1]");
  });

  it("reports empty for no-triplet input and rejects short input", () => {
    const none = generateThreeSum(parseThreeSum("[1, 2, 3]"));
    expect(none[none.length - 1].result).toBe("[]");
    expect(() => parseThreeSum("[1, 2]")).toThrow();
  });
});

describe("buy-sell trace", () => {
  it("finds profit 5 and 0 for falling prices", () => {
    const steps = generateStock(parseStock("[7, 1, 5, 3, 6, 4]"));
    expect(steps[steps.length - 1].result).toBe("5");
    const flat = generateStock(parseStock("[7, 6, 4, 3, 1]"));
    expect(flat[flat.length - 1].result).toBe("0");
  });
});

describe("binary-search trace", () => {
  it("finds the target with correct low/mid/high progression", () => {
    const steps = generateBinarySearch(parseBinarySearch("[-1, 0, 3, 5, 9, 12], 9"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("4");
    const probes = steps.filter((s) => s.op === "Probe mid");
    expect(probes[0].array.pointers).toMatchObject({ low: 0, mid: 2, high: 5 });
  });

  it("reports -1 for a missing target and single-element arrays", () => {
    const miss = generateBinarySearch(parseBinarySearch("[-1, 0, 3, 5, 9, 12], 2"));
    expect(miss[miss.length - 1].result).toBe("-1");
    const one = generateBinarySearch(parseBinarySearch("[5], 5"));
    expect(one[one.length - 1].result).toBe("0");
  });

  it("rejects unsorted arrays and bad input", () => {
    expect(() => parseBinarySearch("[3, 1, 2], 1")).toThrow();
    expect(() => parseBinarySearch("hello")).toThrow();
  });
});

describe("valid-parentheses trace", () => {
  it("accepts nested and rejects mismatched brackets", () => {
    const ok = generateValidParentheses(parseValidParentheses("{[()]}"));
    expect(ok[ok.length - 1].result).toBe("true");
    expect(ok[ok.length - 1].done).toBe(true);
    const bad = generateValidParentheses(parseValidParentheses("([)]"));
    expect(bad[bad.length - 1].result).toBe("false");
  });

  it("rejects non-bracket input", () => {
    expect(() => parseValidParentheses("abc")).toThrow();
    expect(() => parseValidParentheses("(")).toThrow();
  });
});

describe("min-stack trace", () => {
  it("tracks the minimum across pushes and pops", () => {
    const steps = generateMinStack(parseMinStack("push 3, push 5, getMin, push 2, getMin, pop, getMin"));
    const mins = steps.filter((s) => s.op === "getMin").map((s) => s.result ?? s.vars.min);
    expect(steps[steps.length - 1].result).toBe("3");
    expect(steps[steps.length - 1].done).toBe(true);
    expect(mins).toEqual([3, 2, 3]);
  });

  it("rejects bad ops", () => {
    expect(() => parseMinStack("push, pop")).toThrow();
    expect(() => parseMinStack("")).toThrow();
  });
});

describe("eval-rpn trace", () => {
  it("evaluates the classic examples", () => {
    const basic = generateEvalRpn(parseEvalRpn("2 1 + 3 *"));
    expect(basic[basic.length - 1].result).toBe("9");
    const last = generateEvalRpn(parseEvalRpn("4 13 5 / +"));
    expect(last[last.length - 1].result).toBe("6");
  });

  it("rejects bad tokens", () => {
    expect(() => parseEvalRpn("2 +")).toThrow();
    expect(() => parseEvalRpn("2 a +")).toThrow();
  });
});

describe("daily-temperatures trace", () => {
  it("produces [1,1,4,2,1,1,0,0] for the classic input", () => {
    const steps = generateDailyTemperatures(parseDailyTemperatures("[73, 74, 75, 71, 69, 72, 76, 73]"));
    const last = steps[steps.length - 1];
    expect(last.result).toBe("[1,1,4,2,1,1,0,0]");
    expect(last.done).toBe(true);
  });

  it("handles falling temperatures", () => {
    const steps = generateDailyTemperatures(parseDailyTemperatures("[60, 50, 40]"));
    expect(steps[steps.length - 1].result).toBe("[0,0,0]");
  });
});

describe("longest-substring trace", () => {
  it("finds 3 for abcabcbb and 1 for bbbbb", () => {
    expect(generateLongestSubstring(parseLongestSubstring("abcabcbb")).at(-1)!.result).toBe("3");
    expect(generateLongestSubstring(parseLongestSubstring("bbbbb")).at(-1)!.result).toBe("1");
  });

  it("rejects short input", () => {
    expect(() => parseLongestSubstring("a")).toThrow();
  });
});

describe("permutation-in-string trace", () => {
  it("finds the permutation and reports misses", () => {
    expect(generatePermutationInString(parsePermutationInString("ab, eidbaooo")).at(-1)!.result).toBe("true");
    expect(generatePermutationInString(parsePermutationInString("ab, eidboaoo")).at(-1)!.result).toBe("false");
  });

  it("rejects malformed input", () => {
    expect(() => parsePermutationInString("ab")).toThrow();
    expect(() => parsePermutationInString("abcdefg, ab")).toThrow();
  });
});

describe("char-replacement trace", () => {
  it("finds 4 for AABABBA with k=1", () => {
    const steps = generateCharReplacement(parseCharReplacement("AABABBA, 1"));
    expect(steps[steps.length - 1].result).toBe("4");
    expect(steps[steps.length - 1].done).toBe(true);
  });

  it("rejects bad k", () => {
    expect(() => parseCharReplacement("AABABBA")).toThrow();
    expect(() => parseCharReplacement("AABABBA, x")).toThrow();
  });
});

describe("sliding-window-maximum trace", () => {
  it("records the maximum for every window", () => {
    const steps = generateSlidingWindowMaximum(
      parseSlidingWindowMaximum("[1, 3, -1, -3, 5, 3, 6, 7], 3")
    );
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[3, 3, 5, 5, 6, 7]");
    expect(steps[0].queue?.label).toBe("deque (indices)");
  });

  it("handles k=1 and rejects bad windows", () => {
    expect(
      generateSlidingWindowMaximum(parseSlidingWindowMaximum("[9, 7, 5], 1")).at(-1)!.result
    ).toBe("[9, 7, 5]");
    expect(() => parseSlidingWindowMaximum("[1, 2, 3]")).toThrow();
    expect(() => parseSlidingWindowMaximum("[1, 2, 3], 4")).toThrow();
  });
});

describe("task-scheduler trace", () => {
  it("schedules AAABBB with a 2-slot cooldown in 8 intervals", () => {
    const steps = generateTaskScheduler(parseTaskScheduler("AAABBB, 2"));
    expect(steps[steps.length - 1].done).toBe(true);
    expect(steps[steps.length - 1].result).toBe("8");
    expect(steps.some((s) => s.op === "Idle")).toBe(true);
  });

  it("handles no cooldown and rejects bad input", () => {
    expect(generateTaskScheduler(parseTaskScheduler("A, 0")).at(-1)!.result).toBe("1");
    expect(() => parseTaskScheduler("AAABBB")).toThrow();
    expect(() => parseTaskScheduler("AAABBB, -1")).toThrow();
    expect(() => parseTaskScheduler("AAABBB, 5")).toThrow();
  });
});

describe("design-twitter trace", () => {
  it("merges own tweets with followees newest-first", () => {
    const steps = generateDesignTwitter(
      parseDesignTwitter(
        "post 1 5, post 2 6, newsfeed 1, follow 1 2, newsfeed 1, unfollow 1 2, newsfeed 1"
      )
    );
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("5 | 6 5 | 5");
    expect(steps.some((s) => s.queue?.values.includes("#6"))).toBe(true);
  });

  it("handles a solo feed and rejects bad ops", () => {
    expect(
      generateDesignTwitter(parseDesignTwitter("post 1 1, newsfeed 1")).at(-1)!.result
    ).toBe("1");
    expect(() => parseDesignTwitter("post x 1")).toThrow();
    expect(() => parseDesignTwitter("newsfeed")).toThrow();
    expect(() => parseDesignTwitter("")).toThrow();
  });
});

describe("reverse-linked-list trace", () => {
  it("reverses the classic list", () => {
    const steps = generateReverseLinkedList(parseReverseLinkedList("[1, 2, 3, 4, 5]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[5, 4, 3, 2, 1]");
    expect(steps[0].linkedListAlt?.head).toBe(0);
  });

  it("handles single and empty lists", () => {
    expect(generateReverseLinkedList(parseReverseLinkedList("[7]")).at(-1)!.result).toBe("[7]");
    expect(generateReverseLinkedList(parseReverseLinkedList("[]")).at(-1)!.result).toBe("[]");
    expect(() => parseReverseLinkedList("1 2 3")).toThrow();
  });
});

describe("merge-two-sorted-lists trace", () => {
  it("merges the classic lists", () => {
    const steps = generateMergeTwoLists(parseMergeTwoLists("[1, 2, 4], [1, 3, 4]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[1, 1, 2, 3, 4, 4]");
    expect(last.array.values).toEqual([1, 1, 2, 3, 4, 4]);
  });

  it("handles an empty list and rejects bad input", () => {
    expect(generateMergeTwoLists(parseMergeTwoLists("[], [1, 2, 3]")).at(-1)!.result).toBe(
      "[1, 2, 3]"
    );
    expect(() => parseMergeTwoLists("[1, 2]")).toThrow();
    expect(() => parseMergeTwoLists("[2, 1], [3]")).toThrow();
  });
});

describe("linked-list-cycle trace", () => {
  it("detects cycles and reports clean lists", () => {
    expect(generateLinkedListCycle(parseLinkedListCycle("[3, 2, 0, -4], 1")).at(-1)!.result).toBe(
      "true"
    );
    expect(generateLinkedListCycle(parseLinkedListCycle("[1, 2, 3], -1")).at(-1)!.result).toBe(
      "false"
    );
    expect(generateLinkedListCycle(parseLinkedListCycle("[1, 2], 1")).at(-1)!.result).toBe(
      "true"
    );
  });

  it("rejects a missing or out-of-range pos", () => {
    expect(() => parseLinkedListCycle("[1, 2, 3]")).toThrow();
    expect(() => parseLinkedListCycle("[1, 2, 3], 3")).toThrow();
  });
});

describe("maximum-depth-binary-tree trace", () => {
  it("computes the depth bottom-up", () => {
    const steps = generateMaximumDepth(parseMaximumDepth("[3, 9, 20, null, null, 15, 7]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("3");
    expect(steps.some((s) => s.tree?.annotations?.[0] === "d=3")).toBe(true);
  });

  it("handles skewed, single, and empty trees", () => {
    expect(generateMaximumDepth(parseMaximumDepth("[1, 2, null, 3, null, 4]")).at(-1)!.result).toBe(
      "4"
    );
    expect(generateMaximumDepth(parseMaximumDepth("[1]")).at(-1)!.result).toBe("1");
    expect(generateMaximumDepth(parseMaximumDepth("[]")).at(-1)!.result).toBe("0");
  });
});

describe("invert-binary-tree trace", () => {
  it("swaps every node's children", () => {
    const steps = generateInvertBinaryTree(parseInvertBinaryTree("[4, 2, 7, 1, 3, 6, 9]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[4, 7, 2, 9, 6, 3, 1]");
    expect(steps.some((s) => s.op === "Swap")).toBe(true);
  });

  it("handles single and empty trees", () => {
    expect(generateInvertBinaryTree(parseInvertBinaryTree("[1]")).at(-1)!.result).toBe("[1]");
    expect(generateInvertBinaryTree(parseInvertBinaryTree("[]")).at(-1)!.result).toBe("[]");
  });
});

describe("validate-binary-search-tree trace", () => {
  it("rejects a deep node outside its allowed range", () => {
    const steps = generateValidateBst(parseValidateBst("[5, 1, 4, null, null, 3, 6]"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("false");
    expect(steps.some((s) => s.op === "Invalid")).toBe(true);
  });

  it("accepts valid and empty trees", () => {
    expect(generateValidateBst(parseValidateBst("[2, 1, 3]")).at(-1)!.result).toBe("true");
    expect(generateValidateBst(parseValidateBst("[]")).at(-1)!.result).toBe("true");
  });

  it("catches a right-subtree violation", () => {
    expect(generateValidateBst(parseValidateBst("[5, 4, 6, null, null, 3, 7]")).at(-1)!.result).toBe(
      "false"
    );
  });
});

describe("binary-tree-level-order-traversal trace", () => {
  it("collects each level left-to-right", () => {
    const steps = generateLevelOrder(
      parseLevelOrder("[3, 9, 20, null, null, 15, 7]")
    );
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("[[3], [9, 20], [15, 7]]");
    expect(steps.some((s) => s.queue?.values.length === 2)).toBe(true);
  });

  it("handles single and empty trees", () => {
    expect(generateLevelOrder(parseLevelOrder("[1]")).at(-1)!.result).toBe("[[1]]");
    expect(generateLevelOrder(parseLevelOrder("[]")).at(-1)!.result).toBe("[]");
  });
});

describe("flood-fill trace", () => {
  it("recolors the connected region", () => {
    const steps = generateFloodFill(
      parseFloodFill("3 3\n1 1 1\n1 1 0\n1 0 1\n1 1 2")
    );
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("2 2 2 / 2 2 0 / 2 0 1");
    expect(last.grid?.values).toEqual([
      [2, 2, 2],
      [2, 2, 0],
      [2, 0, 1],
    ]);
  });

  it("leaves the image unchanged when the color matches", () => {
    const last = generateFloodFill(parseFloodFill("2 2\n1 1\n1 1\n0 0 1")).at(-1)!;
    expect(last.result).toBe("1 1 / 1 1");
    expect(last.op).toBe("No change");
  });

  it("rejects malformed grids", () => {
    expect(() => parseFloodFill("3 3\n1 1\n1 1 2")).toThrow();
    expect(() => parseFloodFill("1 1\n0\n1 0 2")).toThrow();
  });
});

describe("number-of-islands trace", () => {
  it("counts connected land", () => {
    expect(
      generateNumberOfIslands(parseNumberOfIslands("4 5\n11110\n11010\n11000\n00000")).at(-1)!
        .result
    ).toBe("1");
    expect(
      generateNumberOfIslands(parseNumberOfIslands("4 5\n11000\n11000\n00100\n00011")).at(-1)!
        .result
    ).toBe("3");
  });

  it("handles all water and rejects bad rows", () => {
    expect(generateNumberOfIslands(parseNumberOfIslands("2 3\n000\n000")).at(-1)!.result).toBe(
      "0"
    );
    expect(() => parseNumberOfIslands("2 3\n11\n000")).toThrow();
  });
});

describe("course-schedule trace", () => {
  it("accepts a DAG and rejects a cycle", () => {
    expect(generateCourseSchedule(parseCourseSchedule("4 3\n1 0\n2 1\n3 2")).at(-1)!.result).toBe(
      "true"
    );
    expect(generateCourseSchedule(parseCourseSchedule("2 2\n1 0\n0 1")).at(-1)!.result).toBe(
      "false"
    );
    expect(generateCourseSchedule(parseCourseSchedule("4 0")).at(-1)!.result).toBe("true");
  });

  it("shows Kahn's queue and rejects bad course ids", () => {
    const steps = generateCourseSchedule(parseCourseSchedule("4 3\n1 0\n2 1\n3 2"));
    expect(steps.some((s) => s.graph?.edges.some((e) => e.directed))).toBe(true);
    expect(steps.some((s) => s.queue?.values.length === 1)).toBe(true);
    expect(() => parseCourseSchedule("2 1\n2 0")).toThrow();
  });
});

describe("clone-graph trace", () => {
  it("copies nodes and edges depth-first", () => {
    const steps = generateCloneGraph(parseCloneGraph("4\n2 4\n1 3\n2 4\n1 3"));
    const last = steps[steps.length - 1];
    expect(last.done).toBe(true);
    expect(last.result).toBe("1 2 3 4");
    expect(last.graphAlt?.nodes).toHaveLength(4);
    expect(last.graphAlt?.edges.length).toBeGreaterThanOrEqual(4);
  });

  it("handles single, path, and star graphs", () => {
    expect(generateCloneGraph(parseCloneGraph("1\n")).at(-1)!.result).toBe("1");
    expect(generateCloneGraph(parseCloneGraph("3\n2\n1 3\n2")).at(-1)!.result).toBe("1 2 3");
    expect(generateCloneGraph(parseCloneGraph("4\n2 3 4\n1\n1\n1")).at(-1)!.result).toBe(
      "1 2 3 4"
    );
  });

  it("rejects invalid neighbors", () => {
    expect(() => parseCloneGraph("2\n3\n1")).toThrow();
    expect(() => parseCloneGraph("2\n1\n1")).toThrow();
  });
});

describe("climbing-stairs trace", () => {
  it("computes the Fibonacci-style ways", () => {
    expect(generateClimbingStairs(parseClimbingStairs("3")).at(-1)!.result).toBe("3");
    expect(generateClimbingStairs(parseClimbingStairs("5")).at(-1)!.result).toBe("8");
    expect(generateClimbingStairs(parseClimbingStairs("1")).at(-1)!.result).toBe("1");
  });

  it("highlights the two source cells", () => {
    const steps = generateClimbingStairs(parseClimbingStairs("5"));
    expect(steps.some((s) => s.array.deps?.length === 2)).toBe(true);
    expect(() => parseClimbingStairs("0")).toThrow();
    expect(() => parseClimbingStairs("13")).toThrow();
  });
});

describe("unique-paths trace", () => {
  it("fills the 2-D table", () => {
    expect(generateUniquePaths(parseUniquePaths("3 7")).at(-1)!.result).toBe("28");
    expect(generateUniquePaths(parseUniquePaths("3 2")).at(-1)!.result).toBe("3");
    expect(generateUniquePaths(parseUniquePaths("1 1")).at(-1)!.result).toBe("1");
  });

  it("marks top and left dependencies", () => {
    const steps = generateUniquePaths(parseUniquePaths("3 3"));
    expect(steps.some((s) => s.grid?.deps.length === 2)).toBe(true);
    expect(() => parseUniquePaths("9 9")).toThrow();
  });
});

describe("coin-change trace", () => {
  it("finds the minimum coin count", () => {
    expect(generateCoinChange(parseCoinChange("1 2 5\n11")).at(-1)!.result).toBe("3");
    expect(generateCoinChange(parseCoinChange("2\n3")).at(-1)!.result).toBe("-1");
    expect(generateCoinChange(parseCoinChange("1\n0")).at(-1)!.result).toBe("0");
  });

  it("shows unreachable amounts and rejects bad input", () => {
    const steps = generateCoinChange(parseCoinChange("2\n3"));
    expect(steps.some((s) => s.op === "Unreachable")).toBe(true);
    expect(() => parseCoinChange("0\n5")).toThrow();
    expect(() => parseCoinChange("1\n21")).toThrow();
  });
});

describe("edit-distance trace", () => {
  it("computes the minimum edit distance", () => {
    expect(generateEditDistance(parseEditDistance("horse\nros")).at(-1)!.result).toBe("3");
    expect(generateEditDistance(parseEditDistance("cat\ncut")).at(-1)!.result).toBe("1");
    expect(generateEditDistance(parseEditDistance("\n")).at(-1)!.result).toBe("0");
  });

  it("uses match and replace branches", () => {
    const steps = generateEditDistance(parseEditDistance("horse\nros"));
    expect(steps.some((s) => s.op === "Match")).toBe(true);
    expect(steps.some((s) => s.op === "Choose")).toBe(true);
    expect(() => parseEditDistance("horse")).toThrow();
    expect(() => parseEditDistance("abcdefg\nx")).toThrow();
  });
});
