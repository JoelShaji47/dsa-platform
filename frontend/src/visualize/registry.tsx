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
import { ArrayRenderer } from "./renderers/array-renderer";
import { StackRenderer } from "./renderers/stack-renderer";

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
};

export function lookupVisualizer(slug: string): RegistryItem | null {
  return REGISTRY[slug] ?? null;
}

export function supportedSlugs(): string[] {
  return Object.keys(REGISTRY);
}
