"use client";

import type { LinkedListNode, LinkedListSnapshot, ListPointerName } from "../trace-types";
import { cn } from "@/lib/utils";

const POINTER_ORDER: ListPointerName[] = [
  "head",
  "tail",
  "prev",
  "curr",
  "next",
  "slow",
  "fast",
  "a",
  "b",
  "p",
  "q",
];

const POINTER_COLOR: Record<ListPointerName, string> = {
  head: "text-emerald-300",
  tail: "text-emerald-300",
  prev: "text-sky-300",
  curr: "text-amber-300",
  next: "text-fuchsia-300",
  slow: "text-violet-300",
  fast: "text-orange-300",
  a: "text-sky-300",
  b: "text-orange-300",
  p: "text-sky-300",
  q: "text-orange-300",
};

/** Walk from the snapshot head so the visual order always follows `next`. */
function orderedNodes(snapshot: LinkedListSnapshot): LinkedListNode[] {
  const byId = new Map(snapshot.nodes.map((node) => [node.id, node]));
  const out: LinkedListNode[] = [];
  const seen = new Set<number>();
  let id = snapshot.head;
  while (id != null && !seen.has(id)) {
    const node = byId.get(id);
    if (!node) break;
    out.push(node);
    seen.add(id);
    id = node.next;
  }
  return out;
}

/** Horizontal linked-list stage with pointer labels and a cycle annotation. */
export function LinkedListRenderer({ snapshot }: { snapshot: LinkedListSnapshot }) {
  const { head, active, settled, pointers, label, cycleTo } = snapshot;
  const nodes = orderedNodes(snapshot);
  const byNode = new Map<number, ListPointerName[]>();
  (Object.entries(pointers) as [ListPointerName, number | undefined][]).forEach(([name, id]) => {
    if (id == null) return;
    const arr = byNode.get(id) ?? [];
    arr.push(name);
    byNode.set(id, arr);
  });

  return (
    <div className="flex flex-col items-center">
      <div className="overflow-x-auto pb-1">
        <div className="flex min-w-fit items-start gap-2">
          {nodes.length === 0 ? (
            <div className="flex h-12 w-28 items-center justify-center rounded-lg border border-dashed border-white/15 font-mono text-[10px] text-gray-500">
              empty list
            </div>
          ) : (
            nodes.map((node, k) => {
              const isActive = active.includes(node.id);
              const isSettled = settled.includes(node.id);
              const tags = (byNode.get(node.id) ?? []).sort(
                (a, b) => POINTER_ORDER.indexOf(a) - POINTER_ORDER.indexOf(b)
              );
              const isTail = k === nodes.length - 1;
              return (
                <div key={node.id} className="flex items-start gap-2">
                  <div className="flex w-16 shrink-0 flex-col items-center sm:w-20">
                    <div className="flex h-5 items-end gap-1 font-mono text-[10px] font-bold">
                      {tags.map((tag) => (
                        <span key={tag} className={POINTER_COLOR[tag]}>
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div
                      className={cn(
                        "flex h-12 w-full items-center justify-center rounded-lg border font-mono text-sm font-bold transition-all duration-300 sm:h-14",
                        isActive
                          ? "border-amber-300/80 bg-amber-400/15 text-amber-100 shadow-[0_0_12px_-2px_rgb(252_211_77/0.5)]"
                          : isSettled
                            ? "border-emerald-400/60 bg-emerald-500/10 text-emerald-200"
                            : "border-white/15 bg-white/[0.03] text-gray-100"
                      )}
                    >
                      {node.value}
                    </div>
                    <span className="mt-1 font-mono text-[10px] text-gray-500">
                      {node.id === head ? "head" : `#${node.id}`}
                    </span>
                    {node.random != null && (
                      <span className="font-mono text-[9px] text-fuchsia-300">
                        r&#8594;#{node.random}
                      </span>
                    )}
                  </div>
                  {!isTail ? (
                    <span className="mt-8 font-mono text-lg text-gray-500">→</span>
                  ) : cycleTo != null ? (
                    <span className="mt-8 font-mono text-lg text-violet-300">↺</span>
                  ) : (
                    <span className="mt-9 font-mono text-[10px] text-gray-600">null</span>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
      {cycleTo != null && (
        <span className="mt-1 font-mono text-[10px] text-violet-300">
          tail links back to node {cycleTo}
        </span>
      )}
      {label && <span className="mt-1.5 font-mono text-[10px] text-gray-500">{label}</span>}
    </div>
  );
}
