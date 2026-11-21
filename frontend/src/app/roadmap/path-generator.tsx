"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ChevronRight, Loader2, Route } from "lucide-react";
import client from "@/lib/api";
import { cn } from "@/lib/utils";

const GOAL_OPTIONS = [
  { key: "fundamentals", label: "Strong fundamentals" },
  { key: "interview_soon", label: "Interview soon" },
  { key: "company", label: "Target a company" },
  { key: "curious", label: "Just exploring" },
];

const LEVEL_OPTIONS = [
  { key: "never_started", label: "Never started" },
  { key: "basics", label: "Know the basics" },
  { key: "50_plus", label: "Solved 50+" },
  { key: "interview_ready", label: "Interview-ready" },
];

const DAY_PRESETS = [7, 14, 21, 30];
const MIN_PRESETS = [15, 30, 45, 60];

function PickRow<T extends string | number>({
  label,
  options,
  value,
  onChange,
  format,
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (v: T) => void;
  format?: (v: T) => string;
}) {
  return (
    <div>
      <p className="text-xs font-medium text-ink-faint">{label}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {options.map((o) => (
          <button
            key={String(o)}
            type="button"
            onClick={() => onChange(o)}
            className={cn(
              "fluid-ease rounded-full border px-4 py-1.5 text-sm transition-all duration-300 ease-out active:scale-[0.98]",
              value === o
                ? "border-quest/50 bg-quest/10 font-medium text-ink"
                : "border-ink/10 bg-card font-normal text-ink-soft hover:border-ink/20 hover:text-ink"
            )}
          >
            {format ? format(o) : String(o)}
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Inline "tell us about your path" questionnaire. Creates a custom roadmap
 * and routes to its detail page. Shown on the roadmap overview whenever the
 * learner has no active custom plan.
 */
export default function PathGenerator() {
  const router = useRouter();
  const [goal, setGoal] = useState("fundamentals");
  const [level, setLevel] = useState("basics");
  const [company, setCompany] = useState("");
  const [days, setDays] = useState(21);
  const [mins, setMins] = useState(30);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await client.post("/roadmaps/custom", {
        level,
        goal,
        company: goal === "company" && company.trim() ? company.trim() : undefined,
        mins_per_day: mins,
        total_days: days,
      });
      router.push(`/roadmap/custom/${res.data.id}`);
    } catch (e) {
      const detail =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || "Couldn't generate your path. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="lux-shell">
      <div className="lux-core panel border-0 p-6 md:p-8">
        <p className="lux-eyebrow fluid-ease">
          <Route size={11} strokeWidth={1.5} />
          Start here
        </p>
        <h2 className="mt-3 font-display text-2xl font-medium tracking-tight text-ink md:text-[28px]">
          Let&apos;s build your study path
        </h2>
        <p className="mt-2 max-w-lg text-[15px] leading-relaxed text-ink-soft">
          Tell us where you stand and where you&apos;re headed. We&apos;ll map
          a day-by-day plan from the problem library — your daily pick and
          calendar grow from it.
        </p>

        <div className="mt-6 space-y-5">
          <PickRow
            label="Your goal"
            options={GOAL_OPTIONS.map((g) => g.key)}
            value={goal}
            onChange={setGoal}
            format={(k) => GOAL_OPTIONS.find((g) => g.key === k)?.label ?? k}
          />
          {goal === "company" && (
            <div>
              <p className="text-xs font-medium text-ink-faint">Company</p>
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g. Google, Stripe, a startup"
                maxLength={100}
                className="field mt-2 max-w-sm"
              />
            </div>
          )}
          <PickRow
            label="Your level"
            options={LEVEL_OPTIONS.map((l) => l.key)}
            value={level}
            onChange={setLevel}
            format={(k) => LEVEL_OPTIONS.find((l) => l.key === k)?.label ?? k}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <PickRow
              label="Plan length"
              options={DAY_PRESETS}
              value={days}
              onChange={setDays}
              format={(d) => `${d} days`}
            />
            <PickRow
              label="Minutes per day"
              options={MIN_PRESETS}
              value={mins}
              onChange={setMins}
              format={(m) => `${m} min`}
            />
          </div>
        </div>

        {error && <p className="mt-5 text-sm text-rust">{error}</p>}

        <div className="mt-7 flex flex-wrap items-center gap-4">
          <button
            type="button"
            onClick={submit}
            disabled={busy}
            className="btn-island group fluid-ease bg-quest text-sm text-white disabled:opacity-60"
          >
            {busy ? "Building your path…" : "Generate my path"}
            <span className="btn-island-icon">
              {busy ? (
                <Loader2 size={14} strokeWidth={1.5} className="animate-spin" />
              ) : (
                <ChevronRight size={14} strokeWidth={1.5} />
              )}
            </span>
          </button>
          <Link href="/roadmap/custom" className="text-sm text-ink-soft hover:text-ink hover:underline">
            or fine-tune it with more options
          </Link>
        </div>
      </div>
    </div>
  );
}
