"use client";

import { useId } from "react";
import type { GraphEdgeSnapshot, GraphNodeSnapshot, GraphPointerName, GraphSnapshot } from "../trace-types";

type GraphId = number | string;
type EdgeState = "default" | "active" | "settled";

const POINTER_ORDER: GraphPointerName[] = ["curr", "prev", "next", "node"];

const POINTER_COLOR: Record<GraphPointerName, string> = {
  curr: "#fcd34d",
  prev: "#7dd3fc",
  next: "#f0abfc",
  node: "#6ee7b7",
};

const ARROW_FILL: Record<EdgeState, string> = {
  default: "#6b7280",
  active: "#fcd34d",
  settled: "#34d399",
};

const SIZE = 340;
const RADIUS = 116;
const NODE_RADIUS = 20;

interface PositionedNode {
  node: GraphNodeSnapshot;
  x: number;
  y: number;
}

function layout(nodes: GraphNodeSnapshot[]): {
  items: PositionedNode[];
  byId: Map<GraphId, PositionedNode>;
} {
  const count = nodes.length;
  const byId = new Map<GraphId, PositionedNode>();
  const items = nodes.map((node, index) => {
    const angle = count === 0 ? 0 : -Math.PI / 2 + (2 * Math.PI * index) / count;
    const radius = count === 1 ? 0 : RADIUS;
    const item = {
      node,
      x: SIZE / 2 + Math.cos(angle) * radius,
      y: SIZE / 2 + Math.sin(angle) * radius,
    };
    byId.set(node.id, item);
    return item;
  });
  return { items, byId };
}

function edgePath(
  edge: GraphEdgeSnapshot,
  from: PositionedNode,
  to: PositionedNode,
  hasReverse: boolean
): string {
  if (edge.from === edge.to) {
    const { x, y } = from;
    return `M ${x - 12} ${y - 17} C ${x - 34} ${y - 58}, ${x + 34} ${y - 58}, ${x + 12} ${y - 17}`;
  }

  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const distance = Math.hypot(dx, dy) || 1;
  const ux = dx / distance;
  const uy = dy / distance;
  const startX = from.x + ux * (NODE_RADIUS + 3);
  const startY = from.y + uy * (NODE_RADIUS + 3);
  const endX = to.x - ux * (NODE_RADIUS + 3);
  const endY = to.y - uy * (NODE_RADIUS + 3);

  if (!edge.directed) {
    return `M ${startX} ${startY} L ${endX} ${endY}`;
  }

  const sign = hasReverse ? (String(edge.from) < String(edge.to) ? 1 : -1) : 1;
  const curve = hasReverse ? 18 : 10;
  const midX = (startX + endX) / 2 - uy * curve * sign;
  const midY = (startY + endY) / 2 + ux * curve * sign;
  return `M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`;
}

/** Abstract graph stage: circular layout, curved directed edges, optional labels. */
export function GraphRenderer({ snapshot }: { snapshot: GraphSnapshot }) {
  const rawId = useId();
  const markerId = `graph-${rawId.replace(/[^a-zA-Z0-9_-]/g, "")}`;
  const { nodes, edges, active, settled, pointers, annotations, label } = snapshot;
  const { items, byId } = layout(nodes);
  const byNode = new Map<GraphId, GraphPointerName[]>();
  (Object.entries(pointers) as [GraphPointerName, GraphId | undefined][]).forEach(([name, id]) => {
    if (id == null) return;
    const tags = byNode.get(id) ?? [];
    tags.push(name);
    byNode.set(id, tags);
  });

  return (
    <div className="flex flex-col items-center">
      {nodes.length === 0 ? (
        <div className="flex h-12 w-32 items-center justify-center rounded-lg border border-dashed border-white/15 font-mono text-[10px] text-gray-500">
          empty graph
        </div>
      ) : (
        <div className="overflow-x-auto pb-1">
          <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} role="img">
            <defs>
              {(["default", "active", "settled"] as EdgeState[]).map((state) => (
                <marker
                  key={state}
                  id={`${markerId}-${state}`}
                  viewBox="0 0 10 10"
                  refX={9}
                  refY={5}
                  markerWidth={6}
                  markerHeight={6}
                  orient="auto"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill={ARROW_FILL[state]} />
                </marker>
              ))}
            </defs>
            {edges.map((edge, index) => {
              const from = byId.get(edge.from);
              const to = byId.get(edge.to);
              if (!from || !to) return null;
              const hasReverse =
                edge.directed === true &&
                edges.some(
                  (other) =>
                    other.directed === true &&
                    other.from === edge.to &&
                    other.to === edge.from
                );
              const state: EdgeState =
                active.includes(edge.from) || active.includes(edge.to)
                  ? "active"
                  : settled.includes(edge.from) && settled.includes(edge.to)
                    ? "settled"
                    : "default";
              const rawLabel = edge.label;
              const dx = to.x - from.x;
              const dy = to.y - from.y;
              const distance = Math.hypot(dx, dy) || 1;
              const labelX =
                edge.from === edge.to
                  ? from.x
                  : (from.x + to.x) / 2 - (dy / distance) * 14;
              const labelY =
                edge.from === edge.to
                  ? from.y - NODE_RADIUS - 14
                  : (from.y + to.y) / 2 + (dx / distance) * 14;
              return (
                <g key={`${String(edge.from)}-${String(edge.to)}-${index}`}>
                  <path
                    d={edgePath(edge, from, to, hasReverse)}
                    fill="none"
                    stroke={
                      state === "active"
                        ? "rgba(252,211,77,0.7)"
                        : state === "settled"
                          ? "rgba(52,211,153,0.5)"
                          : "rgba(255,255,255,0.16)"
                    }
                    strokeWidth={2}
                    markerEnd={edge.directed ? `url(#${markerId}-${state})` : undefined}
                  />
                  {rawLabel && (
                    <text
                      x={labelX}
                      y={labelY}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize={9}
                      fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                      fill={state === "active" ? "#fcd34d" : "#9ca3af"}
                    >
                      {rawLabel}
                    </text>
                  )}
                </g>
              );
            })}
            {items.map(({ node, x, y }) => {
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
                <g key={String(node.id)}>
                  {tags.length > 0 && (
                    <text
                      x={x}
                      y={y - NODE_RADIUS - 7}
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
                  <circle
                    cx={x}
                    cy={y}
                    r={NODE_RADIUS}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={1.5}
                  />
                  <text
                    x={x}
                    y={y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={node.label.length > 2 ? 10 : 12}
                    fontWeight={700}
                    fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                    fill={text}
                  >
                    {node.label}
                  </text>
                  {annotations?.[String(node.id)] && (
                    <text
                      x={x}
                      y={y + NODE_RADIUS + 12}
                      textAnchor="middle"
                      fontSize={9}
                      fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
                      fill="#9ca3af"
                    >
                      {annotations[String(node.id)]}
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
