"use client";

import { FileCode2, History } from "lucide-react";
import type { RefObject } from "react";
import type { PanelImperativeHandle } from "react-resizable-panels";
import { Panel } from "react-resizable-panels";
import type { HintMetaOut, ProblemDetail, SubmissionHistoryItem } from "@/lib/types";
import DescriptionPanel from "./description-panel";
import SubmissionsTab from "./submissions-tab";

export default function QuestionPane({
  panelRef,
  problem,
  leftTab,
  onLeftTab,
  submissions,
  submissionsLoading,
  hintMeta,
  revealedHints,
  armedHint,
  loadingHint,
  onHintClick,
}: {
  panelRef: RefObject<PanelImperativeHandle | null>;
  problem: ProblemDetail;
  leftTab: string;
  onLeftTab: (t: string) => void;
  submissions: SubmissionHistoryItem[];
  submissionsLoading: boolean;
  hintMeta: HintMetaOut | null;
  revealedHints: Record<number, string>;
  armedHint: number | null;
  loadingHint: number | null;
  onHintClick: (level: number) => void;
}) {
  return (
    <Panel
      key="q"
      panelRef={panelRef}
      defaultSize={42}
      minSize={20}
      collapsible
      className="min-h-0"
    >
      <section className="flex h-full min-h-0 w-full flex-col bg-paper">
        <div className="flex shrink-0 border-b border-ink/10 bg-white">
          <button
            onClick={() => onLeftTab("description")}
            className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-xs font-medium transition-colors ${
              leftTab === "description"
                ? "border-quest text-quest"
                : "border-transparent text-ink-faint hover:text-ink"
            }`}
          >
            <FileCode2 size={13} />
            Description
          </button>
          <button
            onClick={() => onLeftTab("submissions")}
            className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-xs font-medium transition-colors ${
              leftTab === "submissions"
                ? "border-quest text-quest"
                : "border-transparent text-ink-faint hover:text-ink"
            }`}
          >
            <History size={13} />
            Submissions
            {submissions.length > 0 && leftTab !== "submissions" && (
              <span className="rounded-full bg-paper-deep px-1.5 py-0.5 text-[10px] text-ink-soft">
                {submissions.length}
              </span>
            )}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto">
          {leftTab === "description" && (
            <DescriptionPanel
              problem={problem}
              hintMeta={hintMeta}
              revealedHints={revealedHints}
              armedHint={armedHint}
              loadingHint={loadingHint}
              onHintClick={onHintClick}
            />
          )}
          {leftTab === "submissions" && (
            <div className="bg-paper p-5">
              <SubmissionsTab
                submissions={submissions}
                loading={submissionsLoading}
              />
            </div>
          )}
        </div>
      </section>
    </Panel>
  );
}
