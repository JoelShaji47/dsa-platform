from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User

# A pattern is a Neetcode-style study block. Problems are grouped into
# patterns and the patterns form a prerequisite DAG (the "roadmap tree").
PATTERNS: list[dict] = [
    {
        "key": "arrays-hashing",
        "name": "Arrays & Hashing",
        "order": 1,
        "prerequisites": [],
        "snippet": "Hash maps and array manipulation — the foundation of most interviews.",
        "problems": [
            "two-sum",
            "valid-anagram",
            "group-anagrams",
            "product-of-array-except-self",
            "first-missing-positive",
        ],
    },
    {
        "key": "two-pointers",
        "name": "Two Pointers",
        "order": 2,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Move two indices through a sequence to find pairs or shrink windows.",
        "problems": ["valid-palindrome", "move-zeroes"],
    },
    {
        "key": "sliding-window",
        "name": "Sliding Window",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Maintain an expanding/shrinking window over an array or string.",
        "problems": [
            "longest-substring-without-repeating-characters",
            "minimum-window-substring",
        ],
    },
    {
        "key": "subarray",
        "name": "Subarrays & Prefix Sums",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Contiguous subarray problems: Kadane, prefix sums, and running totals.",
        "problems": ["maximum-subarray", "subarray-sum-equals-k"],
    },
    {
        "key": "linked-list",
        "name": "Linked List",
        "order": 4,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Pointers, cycles, and merging nodes in a linear chain.",
        "problems": [
            "reverse-linked-list",
            "middle-of-the-linked-list",
            "linked-list-cycle",
            "merge-two-sorted-lists",
        ],
    },
    {
        "key": "stack",
        "name": "Stack",
        "order": 5,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Last-in, first-out structures for matching and monotonic ordering.",
        "problems": [
            "valid-parentheses",
            "next-greater-element",
            "daily-temperatures",
        ],
    },
    {
        "key": "queue",
        "name": "Queue & Deque",
        "order": 5,
        "prerequisites": ["sliding-window"],
        "snippet": "First-in, first-out structures and monotonic deques.",
        "problems": ["sliding-window-maximum"],
    },
    {
        "key": "binary-tree",
        "name": "Binary Tree",
        "order": 6,
        "prerequisites": ["stack"],
        "snippet": "Recursive traversal, BST invariants, and tree properties.",
        "problems": [
            "maximum-depth-binary-tree",
            "invert-binary-tree",
            "diameter-of-binary-tree",
            "binary-tree-level-order-traversal",
            "validate-binary-search-tree",
            "lowest-common-ancestor-bst",
        ],
    },
    {
        "key": "graph",
        "name": "Graphs",
        "order": 7,
        "prerequisites": ["binary-tree"],
        "snippet": "DFS/BFS traversal, connectivity, and topological ordering.",
        "problems": ["flood-fill", "number-of-islands", "course-schedule"],
    },
    {
        "key": "dp-1d",
        "name": "1-D Dynamic Programming",
        "order": 8,
        "prerequisites": ["sliding-window", "binary-tree"],
        "snippet": "Break problems into optimal substeps over a single dimension.",
        "problems": [
            "climbing-stairs",
            "longest-increasing-subsequence",
            "coin-change",
            "word-break",
        ],
    },
    {
        "key": "dp-2d",
        "name": "2-D Dynamic Programming",
        "order": 9,
        "prerequisites": ["dp-1d"],
        "snippet": "Grids, edit distance, and path counting over two dimensions.",
        "problems": ["unique-paths", "edit-distance"],
    },
]

PATTERN_BY_KEY = {p["key"]: p for p in PATTERNS}
SLUG_TO_PATTERN = {
    slug: p["key"] for p in PATTERNS for slug in p["problems"]
}


@dataclass
class PatternProgress:
    key: str
    solved: int = 0
    total: int = 0
    attempts: int = 0
    accepted: int = 0
    hints_used: int = 0
    mastery: float = 0.0

    @property
    def complete(self) -> bool:
        return self.total > 0 and self.solved >= self.total


def _load_problems(db: Session) -> dict[str, Problem]:
    return {p.slug: p for p in db.query(Problem).all()}


def _build_user_state(
    db: Session, user: User
) -> tuple[dict, dict, dict, dict, dict]:
    problems = _load_problems(db)

    solved_ids = {
        row[0]
        for row in db.query(Submission.problem_id)
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .distinct()
        .all()
    }
    solved_by_problem = {
        p.slug: (p.id in solved_ids) for p in problems.values()
    }

    attempt_rows = (
        db.query(Submission.problem_id, func.count(Submission.id))
        .filter(Submission.user_id == user.id)
        .group_by(Submission.problem_id)
        .all()
    )
    attempts_by_id = dict(attempt_rows)
    attempts_by_problem = {
        p.slug: attempts_by_id.get(p.id, 0) for p in problems.values()
    }

    hint_rows = (
        db.query(HintUsage.problem_id, func.count(HintUsage.id))
        .filter(HintUsage.user_id == user.id)
        .group_by(HintUsage.problem_id)
        .all()
    )
    hints_by_id = dict(hint_rows)
    hints_by_problem = {
        p.slug: hints_by_id.get(p.id, 0) for p in problems.values()
    }

    progress: dict[str, PatternProgress] = {}
    for pattern_key, pattern in PATTERN_BY_KEY.items():
        pp = PatternProgress(key=pattern_key, total=len(pattern["problems"]))
        for slug in pattern["problems"]:
            pp.solved += int(solved_by_problem.get(slug, False))
            pp.attempts += attempts_by_problem.get(slug, 0)
            pp.hints_used += hints_by_problem.get(slug, 0)
        if pp.solved > 0:
            # mastery between 0 and 100 influenced by solve ratio and hint independence
            resolved = min(pp.solved / pp.total, 1.0)
            hint_penalty = min(pp.hints_used / (pp.solved + pp.hints_used), 0.35)
            pp.mastery = round((resolved * 100) * (1 - hint_penalty), 1)
        progress[pattern_key] = pp

    return (
        problems,
        solved_by_problem,
        attempts_by_problem,
        hints_by_problem,
        progress,
    )


def get_roadmap(
    db: Session, user: User
) -> dict:
    (
        problems,
        solved_by_problem,
        attempts_by_problem,
        hints_by_problem,
        progress,
    ) = _build_user_state(db, user)

    recommended = recommend_next(
        db, user, solved_by_problem, progress
    )
    # Only the single highest-priority recommendation is surfaced to the UI,
    # so the tree highlights exactly one "Recommended next" node/problem.
    top_recommended = recommended[0]["slug"] if recommended else None

    pattern_out = []
    for pattern in PATTERNS:
        pp = progress[pattern["key"]]
        problem_out = []
        for slug in pattern["problems"]:
            p = problems.get(slug)
            if p is None:
                continue
            problem_out.append(
                {
                    "slug": slug,
                    "title": p.title,
                    "difficulty": p.difficulty.value,
                    "solved": solved_by_problem.get(slug, False),
                    "attempts": attempts_by_problem.get(slug, 0),
                    "hints_used": hints_by_problem.get(slug, 0),
                    "recommended": slug == top_recommended,
                }
            )
        pattern_out.append(
            {
                "key": pattern["key"],
                "name": pattern["name"],
                "order": pattern["order"],
                "prerequisites": pattern["prerequisites"],
                "snippet": pattern["snippet"],
                "solved": pp.solved,
                "total": pp.total,
                "mastery": pp.mastery,
                "complete": pp.complete,
                "problems": problem_out,
            }
        )

    return {
        "patterns": pattern_out,
        "totals": {
            "solved": sum(p["solved"] for p in pattern_out),
            "total": sum(p["total"] for p in pattern_out),
        },
    }


def _unlocked_patterns(
    progress: dict[str, PatternProgress],
) -> set[str]:
    unlocked = set()
    changed = True
    while changed:
        changed = False
        for pattern in PATTERNS:
            if pattern["key"] in unlocked:
                continue
            if all(
                progress[pk].solved > 0 or pk in unlocked
                for pk in pattern["prerequisites"]
            ):
                unlocked.add(pattern["key"])
                changed = True
    return unlocked


def recommend_next(
    db: Session,
    user: User,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
) -> list[dict]:
    unlocked = _unlocked_patterns(progress)

    candidates: list[dict] = []
    for pattern in PATTERNS:
        if pattern["key"] not in unlocked:
            continue
        pp = progress[pattern["key"]]
        for slug in pattern["problems"]:
            if solved_by_problem.get(slug, False):
                continue
            candidates.append(
                {
                    "slug": slug,
                    "pattern_key": pattern["key"],
                    "pattern_name": pattern["name"],
                    "order": pattern["order"],
                    "mastery": pp.mastery,
                }
            )

    # score candidates: prefer weak patterns, in pattern order, and unsolved
    def score(c: dict) -> float:
        mastery = c["mastery"]
        return (100.0 - mastery) + c["order"] * 0.1

    candidates.sort(key=score)
    recommendations = []
    for c in candidates[:12]:
        recommendations.append(
            {
                "slug": c["slug"],
                "pattern_key": c["pattern_key"],
                "pattern_name": c["pattern_name"],
                "mastery": c["mastery"],
                "reason": _reason(c, progress),
            }
        )
    return recommendations


def _reason(c: dict, progress: dict[str, PatternProgress]) -> str:
    pp = progress[c["pattern_key"]]
    if pp.solved == 0:
        return f"Kick off {c['pattern_name']} — you haven't solved any problem here yet."
    if pp.mastery < 60:
        return f"{c['pattern_name']} needs work ({pp.mastery:.0f}% mastered)."
    return f"Next up in {c['pattern_name']} to keep the momentum."


def get_recommendations(db: Session, user: User) -> list[dict]:
    (
        problems,
        solved_by_problem,
        attempts_by_problem,
        hints_by_problem,
        progress,
    ) = _build_user_state(db, user)
    recommendations = recommend_next(db, user, solved_by_problem, progress)
    out = []
    for r in recommendations:
        p = problems.get(r["slug"])
        out.append(
            {
                **r,
                "title": p.title if p else r["slug"],
                "difficulty": p.difficulty.value if p else "MEDIUM",
            }
        )
    return out
