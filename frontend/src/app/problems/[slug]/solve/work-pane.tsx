"use client";

import { useState } from "react";
import { ArrowUpDown } from "lucide-react";
import type { RefObject } from "react";
import type { PanelImperativeHandle } from "react-resizable-panels";
import { Group, Panel, Separator } from "react-resizable-panels";
import type {
  Language,
  ProblemDetail,
  ReviewOut,
  RunMode,
  RunResultOut,
  SubmissionResultOut,
  SubmissionStatus,
} from "@/lib/types";
import ConsolePanel from "./console-panel";
import EditorCell from "./editor-cell";
import { STATUS_STYLES } from "./status-utils";

export default function WorkPane({
  panelRef,
  editorRef,
  consoleRef,
  lang,
  mode,
  problem,
  code,
  runCount,
  onCode,
  onModeChange,
  consoleOpen,
  setConsoleOpen,
  shown,
  shownStatus,
  error,
  runResult,
  submitResult,
  consoleTab,
  setConsoleTab,
  review,
  reviewLoading,
  fetchReview,
}: {
  panelRef: RefObject<PanelImperativeHandle | null>;
  editorRef: RefObject<PanelImperativeHandle | null>;
  consoleRef: RefObject<PanelImperativeHandle | null>;
  lang: Language;
  mode: RunMode;
  problem: ProblemDetail;
  code: string;
  runCount: number;
  onCode: (v: string) => void;
  onModeChange: (m: RunMode) => void;
  consoleOpen: boolean;
  setConsoleOpen: (v: boolean | ((o: boolean) => boolean)) => void;
  shown: RunResultOut | SubmissionResultOut | null;
  shownStatus: SubmissionStatus | undefined;
  error: string | null;
  runResult: RunResultOut | null;
  submitResult: SubmissionResultOut | null;
  consoleTab: string;
  setConsoleTab: (t: string) => void;
  review: ReviewOut | null;
  reviewLoading: boolean;
  fetchReview: () => void;
}) {
  const [vFlip, setVFlip] = useState(false);

  const editorPane = (
    <Panel
      key="editor"
      panelRef={editorRef}
      defaultSize={62}
      minSize={25}
      className="min-h-0"
    >
      <EditorCell
        lang={lang}
        mode={mode}
        problem={problem}
        code={code}
        runCount={runCount}
        onCode={onCode}
        onModeChange={onModeChange}
      />
    </Panel>
  );

  const consolePane = consoleOpen ? (
    <Panel
      key="console"
      panelRef={consoleRef}
      defaultSize={38}
      minSize={15}
      collapsible
      className="min-h-0"
    >
      <section className="flex h-full min-h-0 flex-col">
        <div className="flex h-9 shrink-0 items-center justify-between border-t border-white/10 bg-[#1e1e30] px-4">
          <button
            onClick={() => setConsoleOpen((o) => !o)}
            className="font-mono text-xs font-medium text-gray-400 hover:text-gray-200"
          >
            Out [{runCount || "·"}] · Console
          </button>
          <span className="flex items-center gap-2">
            {shown && shownStatus && (
              <span
                className={`flex items-center gap-1.5 text-xs font-medium ${STATUS_STYLES[shownStatus]?.chip || "text-gray-400"}`}
              >
                {STATUS_STYLES[shownStatus]?.icon}
                {STATUS_STYLES[shownStatus]?.label}
              </span>
            )}
            <button
              onClick={() => setVFlip((v) => !v)}
              title="Move console above / below editor"
              className="rounded p-1 text-gray-600 transition-colors hover:text-gray-300"
            >
              <ArrowUpDown size={12} />
            </button>
          </span>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto">
          <ConsolePanel
            problem={problem}
            error={error}
            runResult={runResult}
            submitResult={submitResult}
            consoleTab={consoleTab}
            setConsoleTab={setConsoleTab}
            review={review}
            reviewLoading={reviewLoading}
            fetchReview={fetchReview}
          />
        </div>
      </section>
    </Panel>
  ) : null;

  return (
    <Panel
      key="w"
      panelRef={panelRef}
      defaultSize={58}
      minSize={25}
      className="min-h-0"
    >
      <Group orientation="vertical" className="h-full">
        {vFlip ? (
          <>
            {consolePane}
            {consolePane && (
              <Separator className="group flex h-2 cursor-row-resize items-center justify-center bg-[#1e1e30] outline-none">
                <span className="h-[3px] w-10 rounded-full bg-white/10 transition-colors group-hover:bg-quest group-data-[separator-active]:bg-quest" />
              </Separator>
            )}
            {editorPane}
          </>
        ) : (
          <>
            {editorPane}
            {consolePane && (
              <Separator className="group flex h-2 cursor-row-resize items-center justify-center bg-[#1e1e30] outline-none">
                <span className="h-[3px] w-10 rounded-full bg-white/10 transition-colors group-hover:bg-quest group-data-[separator-active]:bg-quest" />
              </Separator>
            )}
            {consolePane}
          </>
        )}
      </Group>
    </Panel>
  );
}
