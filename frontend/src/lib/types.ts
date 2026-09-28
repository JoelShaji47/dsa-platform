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
  stderr?: string | null;
  status_key: string;
}

export interface RunResultOut {
  status: SubmissionStatus;
  runtime_ms: number;
  memory_kb: number;
  test_results: VisibleTestResult[];
}

export interface CustomRunOut {
  status_key: string;
  status: SubmissionStatus | null;
  stdout: string | null;
  stderr: string | null;
  compile_output: string | null;
  runtime_ms: number;
  memory_kb: number;
}

export interface SubmissionTestResult {
  index: number;
  passed: boolean;
  hidden: boolean;
  status_key: string;
  input?: string | null;
  expected_output?: string | null;
  actual_output?: string | null;
  stderr?: string | null;
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

export type TestStatus = "IN_PROGRESS" | "SUBMITTED" | "EXPIRED" | "ABANDONED";

export interface TopicAvailability {
  topic: string;
  easy: number;
  medium: number;
  hard: number;
  total: number;
}

export interface TestConfigOut {
  topics: TopicAvailability[];
  default_duration_seconds: number;
}

export interface TestQuestion {
  id: string;
  problem_id: string;
  slug: string;
  title: string;
  description: string;
  position: number;
  difficulty: Difficulty;
  category: string;
  starter_code: Record<string, string>;
  test_cases: TestCaseOut[];
  hidden_test_count: number;
  code: string | null;
  language: Language | null;
  attempts: number;
  status: SubmissionStatus | null;
  passed: boolean | null;
  runtime_ms: number | null;
  memory_kb: number | null;
  submitted_at: string | null;
}

export interface TestSession {
  id: string;
  status: TestStatus;
  topics: string[];
  assigned_topics: string[];
  duration_seconds: number;
  started_at: string;
  deadline_at: string;
  time_remaining_seconds: number;
  violations: number;
  problems: TestQuestion[];
}

export interface TestCaseResult {
  index: number;
  passed: boolean;
  hidden: boolean;
  status_key: string;
}

export interface TestSubmitOut {
  problem_id: string;
  status: SubmissionStatus;
  passed: boolean;
  attempts: number;
  runtime_ms: number;
  memory_kb: number;
  test_results: TestCaseResult[];
}

export interface TestResultItem {
  position: number;
  slug: string;
  title: string;
  difficulty: Difficulty;
  category: string;
  passed: boolean;
  status: SubmissionStatus | null;
  attempts: number;
  runtime_ms: number | null;
  memory_kb: number | null;
}

export interface TestResults {
  id: string;
  status: TestStatus;
  score: number;
  passed_count: number;
  total: number;
  time_taken_seconds: number;
  topics: string[];
  assigned_topics: string[];
  started_at: string;
  ended_at: string | null;
  results: TestResultItem[];
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
