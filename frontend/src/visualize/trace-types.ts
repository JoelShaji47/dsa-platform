/** Shared trace model for the step-by-step visualizer.
 *
 * Traces are generated first (pure functions over an input), then played back
 * by the player. Snapshots are immutable so Previous/Next/Reset are exact.
 */

export type PointerName =
  | "low"
  | "mid"
  | "high"
  | "left"
  | "right"
  | "slow"
  | "fast"
  | "i"
  | "j";

export interface ArraySnapshot {
  /** Numbers for array problems, single chars for string problems. */
  values: (number | string)[];
  /** Indices part of the current comparison/operation. */
  active: number[];
  /** Indices already settled (sorted region, placed element, …). */
  settled: number[];
  /** Indices eliminated from consideration (binary search). */
  eliminated: number[];
  pointers: Partial<Record<PointerName, number>>;
}

/** Vertical stack snapshot. Index 0 is the bottom; top is values.at(-1). */
export interface StackSnapshot {
  values: (number | string)[];
  /** Positions (from bottom) touched by the current op — usually the top. */
  active: number[];
  /** Positions already resolved/consumed. */
  settled: number[];
  /** Caption rendered under the stack, e.g. "stack" / "min-stack". */
  label?: string;
}

export interface BaseStep {
  index: number;
  /** Short label, e.g. "Compare", "Swap", "Move left". */
  op: string;
  /** One-sentence explanation of this step. */
  explanation: string;
  /** Pseudocode line this step maps to (index into the entry's pseudocode). */
  line: number;
  array: ArraySnapshot;
  /** Primary stack (stack problems). Rendered when present. */
  stack?: StackSnapshot;
  /** Secondary stack (Min Stack's min-stack). Rendered beside `stack`. */
  stackAlt?: StackSnapshot;
  /** Named variable values shown beside the code, e.g. { target: 9 }. */
  vars: Record<string, string | number>;
  result?: string;
  done?: boolean;
}

export interface Trace<TInput = unknown> {
  steps: BaseStep[];
  input: TInput;
}

/** Registry-facing entry. Inputs cross this boundary as `unknown`; each trace
 * module owns the single narrowing cast for its own input shape. */
export interface VisualizerEntry {
  slug: string;
  title: string;
  /** Short input hint, e.g. "[2, 7, 11, 15], target 9". */
  inputHint: string;
  defaultInput: string;
  presets: { label: string; value: string }[];
  pseudocode: string[];
  parse: (raw: string) => unknown;
  generate: (input: unknown) => BaseStep[];
}

function emptyArray(values: (number | string)[]): ArraySnapshot {
  return { values: [...values], active: [], settled: [], eliminated: [], pointers: {} };
}

export function snapStack(
  values: (number | string)[],
  partial: Partial<StackSnapshot> = {}
): StackSnapshot {
  return { values: [...values], active: [], settled: [], ...partial };
}

export function step(
  index: number,
  op: string,
  explanation: string,
  line: number,
  array: ArraySnapshot,
  vars: Record<string, string | number> = {},
  extra: Partial<BaseStep> = {}
): BaseStep {
  return { index, op, explanation, line, array, vars, ...extra };
}

export function snap(
  values: (number | string)[],
  partial: Partial<ArraySnapshot> = {}
): ArraySnapshot {
  return { ...emptyArray(values), ...partial };
}
