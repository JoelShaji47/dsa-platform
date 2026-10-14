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
import { ArrayRenderer } from "./renderers/array-renderer";

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

/** slug → trace generator + renderer. Unlisted slugs show "coming soon". */
const REGISTRY: Record<string, RegistryItem> = {
  "two-sum": arrayItem(twoSumEntry),
  "two-sum-ii-input-array-is-sorted": arrayItem(twoSumIIEntry),
  "move-zeroes": arrayItem(moveZeroesEntry),
  "container-with-most-water": arrayItem(containerEntry),
  "3sum": arrayItem(threeSumEntry),
  "best-time-to-buy-and-sell-stock": arrayItem(stockEntry),
  "binary-search": arrayItem(binarySearchEntry),
};

export function lookupVisualizer(slug: string): RegistryItem | null {
  return REGISTRY[slug] ?? null;
}

export function supportedSlugs(): string[] {
  return Object.keys(REGISTRY);
}
