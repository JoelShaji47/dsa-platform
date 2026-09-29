export interface TierTheme {
  name: string;
  accent: string;
  soft: string;
  ring: string;
  text: string;
  glow: string;
}

export const TIER_THEMES: TierTheme[] = [
  { name: "Bronze", accent: "#B45309", soft: "bg-orange-900/10", ring: "ring-orange-700/40", text: "text-orange-700", glow: "0 0 42px -8px rgb(180 83 9 / 0.55)" },
  { name: "Silver", accent: "#64748B", soft: "bg-slate-500/10", ring: "ring-slate-500/40", text: "text-slate-500", glow: "0 0 42px -8px rgb(100 116 139 / 0.55)" },
  { name: "Gold", accent: "#C9A227", soft: "bg-gold/10", ring: "ring-gold/40", text: "text-gold-deep", glow: "0 0 42px -8px rgb(201 162 39 / 0.6)" },
  { name: "Sapphire", accent: "#0284C7", soft: "bg-sky-600/10", ring: "ring-sky-600/40", text: "text-sky-600", glow: "0 0 42px -8px rgb(2 132 199 / 0.55)" },
  { name: "Ruby", accent: "#DC2626", soft: "bg-rust/10", ring: "ring-rust/40", text: "text-rust", glow: "0 0 42px -8px rgb(220 38 38 / 0.55)" },
  { name: "Emerald", accent: "#059669", soft: "bg-quest/10", ring: "ring-quest/40", text: "text-quest", glow: "0 0 42px -8px rgb(5 150 105 / 0.55)" },
  { name: "Diamond", accent: "#7C3AED", soft: "bg-violet-600/10", ring: "ring-violet-600/40", text: "text-violet-600", glow: "0 0 48px -6px rgb(124 58 237 / 0.6)" },
];

export function tierTheme(tier: number): TierTheme {
  return TIER_THEMES[Math.max(0, Math.min(tier, TIER_THEMES.length - 1))];
}
