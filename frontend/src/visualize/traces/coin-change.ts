import {
  snap,
  step,
  type BaseStep,
  type VisualizerEntry,
} from "../trace-types";

export interface CoinChangeInput {
  coins: number[];
  amount: number;
}

export function parseCoinChange(raw: string): CoinChangeInput {
  const lines = raw
    .replace(/\r/g, "")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  if (lines.length < 2) {
    throw new Error("Use one line of coins, then one line with the amount");
  }

  const bracket = lines[0].match(/\[([^\]]*)\]/);
  const coinLine = bracket ? bracket[1] : lines[0];
  const coins = coinLine
    .split(/[\s,]+/)
    .filter((token) => token.length > 0)
    .map(Number);
  const amount = Number(lines[1]);

  if (coins.length === 0 || coins.some((coin) => !Number.isInteger(coin) || coin < 1)) {
    throw new Error("Coins must be positive integers");
  }
  if (coins.length > 12) throw new Error("Keep it to 12 denominations");
  if (!Number.isInteger(amount) || amount < 0) {
    throw new Error("The amount must be a non-negative integer");
  }
  if (amount > 20) throw new Error("Keep the amount <= 20 so the trace stays readable");

  return { coins: Array.from(new Set(coins)), amount };
}

export function generateCoinChange({ coins, amount }: CoinChangeInput): BaseStep[] {
  const steps: BaseStep[] = [];
  const dp = Array.from({ length: amount + 1 }, () => Infinity);
  const computed = new Set<number>();

  const display = () =>
    dp.map((value, index) =>
      computed.has(index) ? (value === Infinity ? "∞" : value) : ""
    );
  const settled = () => [...computed].sort((a, b) => a - b);

  steps.push(
    step(
      0,
      "Start",
      `Find the fewest coins from [${coins.join(", ")}] that sum to ${amount}.`,
      0,
      snap(display()),
      { amount, coins: coins.join(",") },
      {}
    )
  );

  dp[0] = 0;
  computed.add(0);
  steps.push(
    step(
      steps.length,
      "Base",
      "Amount 0 needs zero coins.",
      0,
      snap(display(), { active: [0], settled: settled() }),
      { amount: 0, coins: 0 },
      {}
    )
  );

  for (let value = 1; value <= amount; value += 1) {
    steps.push(
      step(
        steps.length,
        "Amount",
        `Compute the fewest coins for amount ${value}.`,
        1,
        snap(display(), { active: [value], settled: settled() }),
        { amount: value, best: dp[value] === Infinity ? "∞" : dp[value] },
        {}
      )
    );

    let best = Infinity;
    let bestFrom: number | null = null;

    for (const coin of coins) {
      if (coin > value) continue;
      const previous = dp[value - coin];
      if (previous === Infinity) continue;
      const candidate = previous + 1;

      steps.push(
        step(
          steps.length,
          "Coin",
          `Use coin ${coin}: dp[${value - coin}] + 1 = ${candidate}.`,
          3,
          snap(display(), {
            active: [value],
            deps: [value - coin],
            settled: settled(),
          }),
          { amount: value, coin, candidate, best: best === Infinity ? "∞" : best },
          {}
        )
      );

      if (candidate < best) {
        best = candidate;
        bestFrom = value - coin;
      }
    }

    computed.add(value);
    if (best === Infinity) {
      dp[value] = Infinity;
      steps.push(
        step(
          steps.length,
          "Unreachable",
          `No coin combination reaches amount ${value}, so it stays infinity.`,
          4,
          snap(display(), { active: [value], settled: settled() }),
          { amount: value, best: "∞" },
          {}
        )
      );
    } else {
      dp[value] = best;
      steps.push(
        step(
          steps.length,
          "Store",
          `The best choice gives ${best} coin${best === 1 ? "" : "s"} for amount ${value}.`,
          4,
          snap(display(), {
            active: [value],
            deps: bestFrom == null ? [] : [bestFrom],
            settled: settled(),
          }),
          { amount: value, best },
          {}
        )
      );
    }
  }

  const result = dp[amount] === Infinity ? "-1" : String(dp[amount]);
  steps.push(
    step(
      steps.length,
      "Done",
      dp[amount] === Infinity
        ? `Amount ${amount} cannot be formed from the given coins.`
        : `Amount ${amount} needs ${dp[amount]} coin${dp[amount] === 1 ? "" : "s"}.`,
      5,
      snap(display(), { settled: settled() }),
      { amount, best: dp[amount] === Infinity ? "∞" : dp[amount] },
      { result, done: true }
    )
  );

  return steps;
}

export const coinChangeEntry: VisualizerEntry = {
  slug: "coin-change",
  title: "Coin Change",
  inputHint: "1 2 5 / 11",
  defaultInput: "1 2 5\n11",
  presets: [
    { label: "Classic", value: "1 2 5\n11" },
    { label: "Impossible", value: "2\n3" },
    { label: "Zero", value: "1\n0" },
  ],
  pseudocode: [
    "dp = [inf] * (amount + 1); dp[0] = 0",
    "for a in range(1, amount + 1):",
    "    for coin in coins:",
    "        if coin <= a and dp[a-coin] + 1 < dp[a]:",
    "            dp[a] = dp[a-coin] + 1",
    "return -1 if dp[amount] == inf else dp[amount]",
  ],
  parse: (raw: string) => parseCoinChange(raw),
  generate: (input: unknown) => generateCoinChange(input as CoinChangeInput),
};
