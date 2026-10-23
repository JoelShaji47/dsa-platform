/**
 * Tier identity for the Leagues surface — "Tier Worlds".
 *
 * Seven ranked worlds, each with its own colour. One colour cannot do every
 * job, so each tier carries four:
 *
 *   accent — identity fills: swatches, rails, the band hem, icons at >= 18px.
 *            Never small text, and never a pale swatch without a ring.
 *   deep   — tier-coloured text on LIGHT surfaces (>= 5.00:1 on paper,
 *            >= 5.31:1 on card).
 *   light  — tier-coloured text on DARK surfaces (>= 4.87:1 on dark card,
 *            >= 5.33:1 on dark paper).
 *   band   — the saturated hero field, which carries white text
 *            (>= 5.92:1 against #fff for every tier).
 *
 * The previous single `accent`-as-text-colour failed WCAG AA on three tiers
 * (Gold 2.22:1, Emerald 3.46:1, Sapphire 3.76:1 on paper) and Gold failed the
 * 3:1 non-text threshold for the ladder icons too — hence the split.
 *
 * Ratios are recorded per tier so a future palette edit is re-measured rather
 * than eyeballed.
 */
export interface TierTheme {
  name: string;
  /** Identity colour for fills, rails and borders. Not for text. */
  accent: string;
  /** Text on light surfaces. >= 4.5:1 on paper and card. */
  deep: string;
  /** Text on dark surfaces. >= 4.5:1 on dark paper and card. */
  light: string;
  /** Saturated tier field. Carries white text at >= 4.5:1. */
  band: string;
}

export const TIER_THEMES: TierTheme[] = [
  {
    name: "Bronze",
    accent: "#B45309",
    deep: "#9A4A08", // 5.74:1 paper
    light: "#D98E4E", // 5.89:1 dark paper
    band: "#8A4107", // 7.39:1 vs white
  },
  {
    name: "Silver",
    accent: "#64748B",
    deep: "#4A5A70", // 6.45:1 paper
    light: "#93A6BC", // 6.25:1 dark paper
    band: "#465768", // 7.44:1 vs white
  },
  {
    name: "Gold",
    accent: "#C9A227",
    deep: "#7E6316", // 5.23:1 paper
    light: "#D8BC58", // 8.35:1 dark paper
    band: "#7A6115", // 5.92:1 vs white
  },
  {
    name: "Sapphire",
    accent: "#0284C7",
    deep: "#026A9F", // 5.41:1 paper
    light: "#5AA9E2", // 6.09:1 dark paper
    band: "#02608F", // 6.84:1 vs white
  },
  {
    name: "Ruby",
    accent: "#DC2626",
    deep: "#B01E1E", // 6.32:1 paper
    light: "#EE7878", // 5.64:1 dark paper
    band: "#991A1A", // 8.34:1 vs white
  },
  {
    name: "Emerald",
    accent: "#059669",
    deep: "#04794F", // 5.00:1 paper
    light: "#4BBB8F", // 6.53:1 dark paper
    band: "#046145", // 7.50:1 vs white
  },
  {
    name: "Diamond",
    accent: "#7C3AED",
    deep: "#6A2FD4", // 6.49:1 paper
    light: "#A783F3", // 5.33:1 dark paper
    band: "#5B24B8", // 8.79:1 vs white
  },
];

export function tierTheme(tier: number): TierTheme {
  return TIER_THEMES[Math.max(0, Math.min(tier, TIER_THEMES.length - 1))];
}

/**
 * The four per-tier custom properties, set once on the page root.
 *
 * Everything tier-coloured then reads from CSS (`var(--tier-deep)`), so light
 * vs dark selection happens in one stylesheet rule instead of a JS branch in
 * every component.
 */
export function tierVars(theme: TierTheme): Record<string, string> {
  return {
    "--tier-accent": theme.accent,
    "--tier-deep": theme.deep,
    "--tier-light": theme.light,
    "--tier-band": theme.band,
  };
}
