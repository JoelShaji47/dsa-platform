"use client";

import type { TreePointerName, TreeSnapshot, TreeNodeSnapshot } from "../trace-types";

const POINTER_ORDER: TreePointerName[] = ["curr", "prev", "left", "right", "p", "q"];

const POINTER_COLOR: Record<TreePointerName, string> = {
  curr: "#fcd34d",
  prev: "#7dd3fc",
  left: "#7dd3fc",
  right: "#f0abfc",
  p: "#6ee7b7",
  q: "#fdba74",
};

interface PositionedNode {
  node: TreeNodeSnapshot;
  x: number;
  y: number;
}

const NODE_WIDTH = 52;
const NODE_HEIGHT = 40;
const X_GAP = 64;
const Y_GAP = 74;
const MARGIN = 30;

function layout(snapshot: TreeSnapshot): {
  nodes: PositionedNode[];
  edges: [PositionedNode, PositionedNode][];
  width: number;
  height: number;
} {
  const byId = new Map(snapshot.nodes.map((node) => [node.id, node]));
  const positions = new Map<number, { order: number; depth: number }>();
  let order = 0;
  let maxDepth = 0;

  const visit = (id: number | null, depth: number): void => {
    if (id == null) return;
    const node = byId.get(id);
    if (!node) return;
    visit(node.left, depth + 1);
    positions.set(id, { order: order++, depth });
    maxDepth = Math.max(maxDepth, depth);
    visit(node.right, depth + 1);
  };
  visit(snapshot.root, 0);

  const nodes: PositionedNode[] = [];
  const positioned = new Map<number, PositionedNode>();
  [...positions.entries()]
    .sort((a, b) => a[1].order - b[1].order)
    .forEach(([id, pos]) => {
      const node = byId.get(id);
      if (!node) return;
      const item = {
        node,
        x: MARGIN + pos.order * X_GAP,
        y: MARGIN + pos.depth * Y_GAP,
      };
      nodes.push(item);
      positioned.set(id, item);
    });

  const edges: [PositionedNode, PositionedNode][] = [];
  for (const item of nodes) {
    for (const childId of [item.node.left, item.node.right]) {
      if (childId == null) continue;
      const child = positioned.get(childId);
      if (child) edges.push([item, child]);
    }
  }

  return {
    nodes,
    edges,
    width: MARGIN * 2 + Math.max(0, order - 1) * X_GAP + NODE_WIDTH,
    height: MARGIN * 2 + maxDepth * Y_GAP + NODE_HEIGHT,
  };
}

/** Binary-tree stage: in-order horizontal layout, depth vertical layout, CSS/SVG only. */
export function TreeRenderer({ snapshot }: { snapshot: TreeSnapshot }) {
  const { active, settled, pointers, annotations, label } = snapshot;
  const { nodes, edges, width, height } = layout(snapshot);
  const byNode = new Map<number, TreePointerName[]>();
  (Object.entries(pointers) as [TreePointerName, number | undefined][]).forEach(([name, id]) => {
    if (id == null) return;
    const tags = byNode.get(id) ?? [];
    tags.push(name);
    byNode.set(id, tags);
  });

  return (
    <div className="flex flex-col items-center">
      {nodes.length === 0 ? (
        <div className="flex h-12 w-32 items-center justify-center rounded-lg border border-dashed border-white/15 font-mono text-[10px] text-gray-500">
          empty tree
        </div>
      ) : (
        <div className="overflow-x-auto pb-1">
          <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img">
            {edges.map(([parent, child], index) => {
              const parentActive =
                active.includes(parent.node.id) || active.includes(child.node.id);
              const bothSettled =
                settled.includes(parent.node.id) && settled.includes(child.node.id);
              return (
                <line
                  key={index}
                  x1={parent.x + NODE_WIDTH / 2}
                  y1={parent.y + NODE_HEIGHT / 2}
                  x2={child.x + NODE_WIDTH / 2}
                  y2={child.y + NODE_HEIGHT / 2}
                  stroke={
                    parentActive
                      ? "rgba(252,211,77,0.65)"
                      : bothSettled
                        ? "rgba(52,211,153,0.45)"
                        : "rgba(255,255,255,0.15)"
                  }
                  strokeWidth={2}
                />
              );
            })}
            {nodes.map(({ node, x, y }) => {
              const isActive = active.includes(node.id);
              const isSettled = settled.includes(node.id);
              const tags = (byNode.get(node.id) ?? []).sort(
                (a, b) => POINTER_ORDER.indexOf(a) - POINTER_ORDER.indexOf(b)
              );
              const fill = isActive
                ? "rgba(252,211,77,0.15)"
                : isSettled
                  ? "rgba(16,185,129,0.10)"
                  : "rgba(255,255,255,0.03)";
              const stroke = isActive
                ? "#fcd34d"
                : isSettled
                  ? "#34d399"
                  : "rgba(255,255,255,0.15)";
              const text = isActive ? "#fef3c7" : isSettled ? "#a7f3d0" : "#f3f4f6";
              return (
                <g key={node.id}>
                  {tags.length > 0 && (
                    <text
                      x={x + NODE_WIDTH / 2}
                      y={y - 7}
                      textAnchor="middle"
                      fontSize={10}
                      fontWeight={700}
                      fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                    >
                      {tags.map((tag, tagIndex) => (
                        <tspan key={tag} fill={POINTER_COLOR[tag]} dx={tagIndex === 0 ? 0 : 5}>
                          {tag}
                        </tspan>
                      ))}
                    </text>
                  )}
                  <rect
                    x={x}
                    y={y}
                    width={NODE_WIDTH}
                    height={NODE_HEIGHT}
                    rx={8}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={1.5}
                  />
                  <text
                    x={x + NODE_WIDTH / 2}
                    y={y + NODE_HEIGHT / 2}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={13}
                    fontWeight={700}
                    fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                    fill={text}
                  >
                    {node.value}
                  </text>
                  {annotations?.[node.id] && (
                    <text
                      x={x + NODE_WIDTH / 2}
                      y={y + NODE_HEIGHT + 12}
                      textAnchor="middle"
                      fontSize={9}
                      fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                      fill="#9ca3af"
                    >
                      {annotations[node.id]}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>
      )}
      {label && <span className="mt-1.5 font-mono text-[10px] text-gray-500">{label}</span>}
    </div>
  );
}
