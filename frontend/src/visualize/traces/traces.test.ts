import { describe, expect, it } from "vitest";
import { generateBinarySearch, parseBinarySearch } from "./binary-search";
import { generateTwoSum, parseTwoSum } from "./two-sum";

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
