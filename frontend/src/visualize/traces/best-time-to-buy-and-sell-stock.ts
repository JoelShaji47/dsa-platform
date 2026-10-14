import { snap, step, type BaseStep, type VisualizerEntry } from "../trace-types";

export interface StockInput {
  prices: number[];
}

export function parseStock(raw: string): StockInput {
  const bracket = raw.trim().match(/\[([^\]]*)\]/);
  if (!bracket) throw new Error("Use the form [7, 1, 5, 3, 6, 4]");
  const prices = bracket[1]
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
    .map(Number);
  if (prices.length < 2 || prices.some((n) => !Number.isFinite(n) || n < 0)) {
    throw new Error("Need at least 2 non-negative prices, e.g. [7, 1, 5, 3, 6, 4]");
  }
  if (prices.length > 12) throw new Error("Keep it to 12 days so the trace stays readable");
  return { prices };
}

export function generateStock({ prices }: StockInput): BaseStep[] {
  const steps: BaseStep[] = [];
  let buy = 0;
  let best = 0;
  steps.push(
    step(0, "Start", `One pass: track the cheapest buy day seen, sell today. Buy starts at day 0 (price ${prices[0]}).`, 0,
      snap(prices, { pointers: { left: buy, right: 0 } }), { buy, best })
  );
  for (let sell = 1; sell < prices.length; sell++) {
    steps.push(
      step(steps.length, "Sell today?", `Sell day ${sell} at ${prices[sell]}. Buy day ${buy} at ${prices[buy]}. Profit: ${prices[sell] - prices[buy]}.`, 1,
        snap(prices, { active: [buy, sell], pointers: { left: buy, right: sell } }), { buy, sell })
    );
    const profit = prices[sell] - prices[buy];
    if (profit > best) {
      const old = best;
      best = profit;
      steps.push(
        step(steps.length, "New best", `Profit ${profit} beats ${old} — buy day ${buy}, sell day ${sell}.`, 2,
          snap(prices, { active: [buy, sell], settled: [buy, sell], pointers: { left: buy, right: sell } }), { buy, sell, best })
      );
    }
    if (prices[sell] < prices[buy]) {
      buy = sell;
      steps.push(
        step(steps.length, "Cheaper buy", `Day ${sell} (${prices[sell]}) is the cheapest so far — future sells use it as buy.`, 3,
          snap(prices, { pointers: { left: buy, right: sell } }), { buy, best })
      );
    }
  }
  steps.push(
    step(steps.length, "Done", `Maximum profit: ${best}.`, 4,
      snap(prices, {}), { best }, { result: `${best}`, done: true })
  );
  return steps;
}

export const stockEntry: VisualizerEntry = {
  slug: "best-time-to-buy-and-sell-stock",
  title: "Best Time to Buy and Sell Stock",
  inputHint: "[7, 1, 5, 3, 6, 4]",
  defaultInput: "[7, 1, 5, 3, 6, 4]",
  presets: [
    { label: "Classic (5)", value: "[7, 1, 5, 3, 6, 4]" },
    { label: "Falling (0)", value: "[7, 6, 4, 3, 1]" },
    { label: "Rising", value: "[1, 2, 3, 4, 5]" },
  ],
  pseudocode: [
    "buy = 0, best = 0",
    "for sell in 1..n-1:",
    "    best = max(best, prices[sell] - prices[buy])",
    "    if prices[sell] < prices[buy]: buy = sell",
    "return best",
  ],
  // Boundary casts: parse produced this shape, so narrowing is sound.
  parse: (raw: string) => parseStock(raw),
  generate: (input: unknown) => generateStock(input as StockInput),
};
