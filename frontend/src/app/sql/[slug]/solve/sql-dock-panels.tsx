"use client";

import { useEffect } from "react";
import { useTheme } from "@/context/theme-context";
import { useSqlDock } from "./sql-dock-context";
import AssistantPanel from "../../../problems/[slug]/solve/assistant-panel";
import ConsolePanel from "../../../problems/[slug]/solve/console-panel";
import SubmissionsTab from "../../../problems/[slug]/solve/submissions-tab";
import { STATUS_STYLES } from "../../../problems/[slug]/solve/status-utils";
import SqlDescriptionPanel from "./sql-description-panel";
import SqlEditorCell from "./sql-editor-cell";

export function SqlDescriptionTabPanel() {
  const d = useSqlDock();
  return (
    <div className="h-full overflow-y-auto">
      <SqlDescriptionPanel
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

export function SqlSubmissionsTabPanel() {
  const d = useSqlDock();
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

export function SqlCodeTabPanel() {
  const d = useSqlDock();
  return (
    <SqlEditorCell code={d.code} runCount={d.runCount} onCode={d.onCode} />
  );
}

export function SqlConsoleTabPanel() {
  const d = useSqlDock();
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
          editableCases={d.editableCases}
          onEditCase={d.onEditCase}
          onRunEditableCases={d.onRunEditableCases}
          editableRunning={d.editableRunning}
          onResetEditableCases={d.onResetEditableCases}
          customRunResult={d.customRunResult}
        />
      </div>
    </div>
  );
}

export function SqlCoachTabPanel() {
  const d = useSqlDock();
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
