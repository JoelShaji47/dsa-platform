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
