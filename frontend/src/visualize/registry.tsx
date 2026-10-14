"use client";

import type { ReactNode } from "react";
import type { BaseStep, VisualizerEntry } from "./trace-types";
import { twoSumEntry } from "./traces/two-sum";
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
  "binary-search": arrayItem(binarySearchEntry),
};

export function lookupVisualizer(slug: string): RegistryItem | null {
  return REGISTRY[slug] ?? null;
}

export function supportedSlugs(): string[] {
  return Object.keys(REGISTRY);
}
