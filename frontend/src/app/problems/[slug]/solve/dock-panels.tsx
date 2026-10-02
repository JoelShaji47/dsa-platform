"use client";

import { useEffect } from "react";
import { useTheme } from "@/context/theme-context";
import { useDock } from "./dock-context";
import AssistantPanel from "./assistant-panel";
import ConsolePanel from "./console-panel";
import DescriptionPanel from "./description-panel";
import EditorCell from "./editor-cell";
import SubmissionsTab from "./submissions-tab";
import { STATUS_STYLES } from "./status-utils";

export function DescriptionTabPanel() {
  const d = useDock();
  return (
    <div className="h-full overflow-y-auto">
      <DescriptionPanel
        problem={d.problem}
        hintMeta={d.hintMeta}
        revealedHints={d.revealedHints}
        armedHint={d.armedHint}
        loadingHint={d.loadingHint}
        onHintClick={d.onHintClick}
      />
    </div>
  );
}

export function SubmissionsTabPanel() {
  const d = useDock();
  useEffect(() => {
    d.refreshSubmissions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <div className="h-full overflow-y-auto bg-paper p-5">
      <SubmissionsTab submissions={d.submissions} loading={d.submissionsLoading} />
    </div>
  );
}

export function CodeTabPanel() {
  const d = useDock();
  return (
    <EditorCell
      lang={d.lang}
      mode={d.mode}
      problem={d.problem}
      code={d.code}
      runCount={d.runCount}
      onCode={d.onCode}
      onModeChange={d.onModeChange}
    />
  );
}

export function ConsoleTabPanel() {
  const d = useDock();
  const dark = useTheme() === "dark";
  const th = (dc: string, l: string) => (dark ? dc : l);
  return (
    <div className={th("flex h-full min-h-0 flex-col bg-[#16162a]", "flex h-full min-h-0 flex-col bg-card")}>
      <div className={th("flex h-9 shrink-0 items-center justify-between border-b border-white/10 bg-[#1e1e30] px-4", "flex h-9 shrink-0 items-center justify-between border-b border-ink/10 bg-white px-4")}>
        <span className={th("font-mono text-xs font-medium text-gray-400", "font-mono text-xs font-medium text-ink-faint")}>
          Out [{d.runCount || "·"}] · Console
        </span>
        {d.shown && d.shownStatus && (
          <span
            className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[d.shownStatus]?.chip || "text-gray-400"}`}
          >
            {STATUS_STYLES[d.shownStatus]?.icon}
            {STATUS_STYLES[d.shownStatus]?.label}
          </span>
        )}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <ConsolePanel
          problem={d.problem}
          error={d.error}
          runResult={d.runResult}
          submitResult={d.submitResult}
          consoleTab={d.consoleTab}
          setConsoleTab={d.setConsoleTab}
          review={d.review}
          reviewLoading={d.reviewLoading}
          fetchReview={d.fetchReview}
          runAnalyze={d.runAnalyze}
          editableCases={d.editableCases}
          onEditCase={d.onEditCase}
          onRunEditableCases={d.onRunEditableCases}
          editableRunning={d.editableRunning}
          onResetEditableCases={d.onResetEditableCases}
        />
      </div>
    </div>
  );
}

export function CoachTabPanel() {
  const d = useDock();
  return (
    <AssistantPanel
      messages={d.coachMessages}
      loading={d.coachLoading}
      provider={d.coachProvider}
      includeCode={d.includeCode}
      contextNote={d.contextNote}
      onToggleInclude={d.onToggleInclude}
      onSend={d.onSendCoach}
      onClear={d.onClearCoach}
      onClose={d.closeCoach}
    />
  );
}
