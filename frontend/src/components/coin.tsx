"use client";

import { cn } from "@/lib/utils";

/** Platform coin — the face of XP. Flat layered gold, no gradients. */
export function Coin({
  size = 16,
  className,
}: {
  size?: number;
  className?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
      className={cn("shrink-0", className)}
    >
      <circle cx="12" cy="12" r="10" fill="#C9A227" />
      <circle cx="12" cy="12" r="7.5" fill="none" stroke="#96760F" strokeWidth="1.4" opacity="0.7" />
      <circle cx="12" cy="12" r="7.5" fill="#E3BC3F" opacity="0.35" />
      <path
        d="M13.2 6.5 8.4 13.2h3l-1 4.3 4.8-6.7h-3l1-4.3Z"
        fill="#5E4A08"
      />
    </svg>
  );
}

/** Coin + amount inline label. */
export function CoinAmount({
  amount,
  size = 14,
  className,
}: {
  amount: number | string;
  size?: number;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <Coin size={size} />
      <span className="font-mono font-bold">{amount}</span>
    </span>
  );
}
