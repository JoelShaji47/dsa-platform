export type Difficulty = "EASY" | "MEDIUM" | "HARD";

export type SubmissionStatus =
  | "ACCEPTED"
  | "WRONG_ANSWER"
  | "TLE"
  | "RUNTIME_ERROR"
  | "COMPILATION_ERROR";

export type Language = "python" | "cpp" | "java";

export interface UserOut {
  id: string;
  username: string;
  email: string;
  xp: number;
  current_streak: number;
  created_at: string;
}

export interface ProblemListItem {
  id: string;
  title: string;
  slug: string;
  difficulty: Difficulty;
  topic: string;
  solved: boolean;
  sources: string[];
  pattern_key: string | null;
}

export interface TestCaseOut {
  input: string;
  expected_output: string;
}

export interface ProblemDetail {
  id: string;
  title: string;
  slug: string;
  description: string;
  difficulty: Difficulty;
  topic: string;
  starter_code: Record<string, string>;
  test_cases: TestCaseOut[];
  solvable: boolean;
  solved: boolean;
  hidden_test_count: number;
  sources: string[];
  pattern_key: string | null;
  companies: string[];
  editorial_url: string | null;
  video_url: string | null;
}

export interface VisibleTestResult {
  index: number;
  passed: boolean;
  input: string;
  expected_output: string;
  actual_output: string | null;
  status_key: string;
}

export interface RunResultOut {
  status: SubmissionStatus;
  runtime_ms: number;
  memory_kb: number;
  test_results: VisibleTestResult[];
}

export interface SubmissionTestResult {
  index: number;
  passed: boolean;
  hidden: boolean;
  status_key: string;
  input?: string | null;
  expected_output?: string | null;
  actual_output?: string | null;
}

export interface SubmissionResultOut {
  submission_id: string;
  status: SubmissionStatus;
  runtime_ms: number;
  memory_kb: number;
  xp_awarded: number;
  xp_forfeited: boolean;
  user_xp: number;
  current_streak: number;
  new_badges: string[];
  test_results: SubmissionTestResult[];
}

export interface SubmissionHistoryItem {
  submission_id: string;
  status: SubmissionStatus;
  language: string;
  code: string;
  runtime_ms: number | null;
  memory_kb: number | null;
  judge_summary: Array<{ index: number; passed: boolean }> | null;
  submitted_at: string;
}

export interface HintLevelInfo {
  level: number;
  label: string;
  revealed: boolean;
}

export interface HintMetaOut {
  total_levels: number;
  xp_forfeit_applies: boolean;
  levels: HintLevelInfo[];
}

export interface ReviewOut {
  verdict: string;
  bug_type: string;
  explanation: string;
  fix_hint: string;
}

export interface AssistantHistoryItem {
  role: "user" | "assistant";
  content: string;
}

export interface AssistantResponse {
  reply: string;
  provider: string;
}

export interface Bucket {
  solved: number;
  total: number;
}

export interface RecentSubmissionOut {
  id: string;
  problem_title: string;
  problem_slug: string;
  status: SubmissionStatus;
  language: string;
  runtime_ms: number | null;
  submitted_at: string;
}

export interface StatsOut {
  xp: number;
  current_streak: number;
  total_solved: number;
  total_submissions: number;
  acceptance_rate: number;
  solved_by_difficulty: Record<string, Bucket>;
  solved_by_topic: Record<string, Bucket>;
  recent_submissions: RecentSubmissionOut[];
}

export interface BadgeOut {
  criteria: string;
  name: string;
  description: string;
  earned: boolean;
  earned_at: string | null;
}

export interface ReviewDueItem {
  slug: string;
  title: string;
  difficulty: Difficulty;
  pattern_key: string | null;
  pattern_name: string | null;
  solved_at: string;
  hints_used: number;
  attempts: number;
}
