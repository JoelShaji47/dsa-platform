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
            "contains-duplicate", "valid-anagram", "two-sum", "group-anagrams",
            "top-k-frequent-elements", "product-of-array-except-self",
            "valid-sudoku", "encode-and-decode-strings", "longest-consecutive-sequence",
        ],
    },
    {
        "key": "two-pointers",
        "name": "Two Pointers",
        "order": 2,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Move two indices through a sequence to find pairs or shrink windows.",
        "problems": [
            "valid-palindrome", "two-sum-ii-input-array-is-sorted", "3sum",
            "container-with-most-water", "trapping-rain-water",
        ],
    },
    {
        "key": "sliding-window",
        "name": "Sliding Window",
        "order": 2,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Maintain an expanding/shrinking window over an array or string.",
        "problems": [
            "best-time-to-buy-and-sell-stock",
            "longest-substring-without-repeating-characters",
            "longest-repeating-character-replacement", "permutation-in-string",
            "minimum-window-substring", "sliding-window-maximum",
        ],
    },
    {
        "key": "stack",
        "name": "Stack",
        "order": 2,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Last-in, first-out structures for matching and monotonic ordering.",
        "problems": [
            "valid-parentheses", "min-stack", "evaluate-reverse-polish-notation",
            "generate-parentheses", "daily-temperatures", "car-fleet",
            "largest-rectangle-in-histogram",
        ],
    },
    {
        "key": "binary-search",
        "name": "Binary Search",
        "order": 2,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Halve the search space on sorted data or monotonic answer spaces.",
        "problems": [
            "binary-search", "search-a-2d-matrix", "koko-eating-bananas",
            "find-minimum-in-rotated-sorted-array", "search-in-rotated-sorted-array",
            "time-based-key-value-store", "median-of-two-sorted-arrays",
        ],
    },
    {
        "key": "linked-list",
        "name": "Linked List",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Pointers, cycles, and merging nodes in a linear chain.",
        "problems": [
            "reverse-linked-list", "merge-two-sorted-lists", "reorder-list",
            "remove-nth-node-from-end-of-list", "copy-list-with-random-pointer",
            "add-two-numbers", "linked-list-cycle", "find-the-duplicate-number",
            "lru-cache", "merge-k-sorted-lists", "reverse-nodes-in-k-group",
        ],
    },
    {
        "key": "heap-priority-queue",
        "name": "Heap / Priority Queue",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Efficient access to min/max elements and k-th order statistics.",
        "problems": [
            "kth-largest-element-in-a-stream", "last-stone-weight",
            "k-closest-points-to-origin", "kth-largest-element-in-an-array",
            "task-scheduler", "design-twitter", "find-median-from-data-stream",
        ],
    },
    {
        "key": "math-geometry",
        "name": "Math & Geometry",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Number theory, matrix manipulation, and computational geometry.",
        "problems": [
            "rotate-image", "spiral-matrix", "set-matrix-zeroes", "happy-number",
            "plus-one", "powx-n", "multiply-strings", "detect-squares",
        ],
    },
    {
        "key": "bit-manipulation",
        "name": "Bit Manipulation",
        "order": 3,
        "prerequisites": ["arrays-hashing"],
        "snippet": "Bitwise operations, XOR tricks, and binary counting.",
        "problems": [
            "single-number", "number-of-1-bits", "counting-bits", "reverse-bits",
            "missing-number", "sum-of-two-integers", "reverse-integer",
        ],
    },
    {
        "key": "trees",
        "name": "Trees",
        "order": 4,
        "prerequisites": ["stack"],
        "snippet": "Recursive traversal, BST invariants, and tree properties.",
        "problems": [
            "invert-binary-tree", "maximum-depth-binary-tree", "diameter-of-binary-tree",
            "balanced-binary-tree", "same-tree", "subtree-of-another-tree",
            "lowest-common-ancestor-bst", "binary-tree-level-order-traversal",
            "binary-tree-right-side-view", "count-good-nodes-in-binary-tree",
            "validate-binary-search-tree", "kth-smallest-element-in-a-bst",
            "construct-binary-tree-from-preorder-and-inorder-traversal",
            "binary-tree-maximum-path-sum", "serialize-and-deserialize-binary-tree",
        ],
    },
    {
        "key": "tries",
        "name": "Tries",
        "order": 5,
        "prerequisites": ["trees"],
        "snippet": "Prefix trees for efficient string lookup and autocomplete.",
        "problems": [
            "implement-trie-prefix-tree",
            "design-add-and-search-words-data-structure", "word-search-ii",
        ],
    },
    {
        "key": "backtracking",
        "name": "Backtracking",
        "order": 4,
        "prerequisites": ["stack"],
        "snippet": "Enumerate combinations, permutations, and solutions via recursion.",
        "problems": [
            "subsets", "combination-sum", "permutations", "subsets-ii",
            "combination-sum-ii", "word-search", "palindrome-partitioning",
            "letter-combinations-of-a-phone-number", "n-queens",
        ],
    },
    {
        "key": "graphs",
        "name": "Graphs",
        "order": 5,
        "prerequisites": ["trees"],
        "snippet": "DFS/BFS traversal, connectivity, and topological ordering.",
        "problems": [
            "number-of-islands", "clone-graph", "max-area-of-island",
            "pacific-atlantic-water-flow", "surrounded-regions", "rotting-oranges",
            "walls-and-gates", "course-schedule", "course-schedule-ii",
            "redundant-connection",
            "number-of-connected-components-in-an-undirected-graph",
            "graph-valid-tree", "word-ladder",
        ],
    },
    {
        "key": "greedy",
        "name": "Greedy",
        "order": 4,
        "prerequisites": ["two-pointers"],
        "snippet": "Make locally optimal choices that lead to a global optimum.",
        "problems": [
            "maximum-subarray", "jump-game", "jump-game-ii", "gas-station",
            "hand-of-straights", "merge-triplets-to-form-target-triplet",
            "partition-labels", "valid-parenthesis-string",
        ],
    },
    {
        "key": "intervals",
        "name": "Intervals",
        "order": 4,
        "prerequisites": ["two-pointers"],
        "snippet": "Merge, overlap, and schedule interval-based constraints.",
        "problems": [
            "insert-interval", "merge-intervals", "non-overlapping-intervals",
            "meeting-rooms", "meeting-rooms-ii",
        ],
    },
    {
        "key": "dp-1d",
        "name": "1-D Dynamic Programming",
        "order": 5,
        "prerequisites": ["sliding-window", "backtracking"],
        "snippet": "Break problems into optimal substeps over a single dimension.",
        "problems": [
            "climbing-stairs", "min-cost-climbing-stairs", "house-robber",
            "house-robber-ii", "longest-palindromic-substring", "palindromic-substrings",
            "decode-ways", "coin-change", "maximum-product-subarray", "word-break",
            "longest-increasing-subsequence", "partition-equal-subset-sum",
        ],
    },
    {
        "key": "advanced-graphs",
        "name": "Advanced Graphs",
        "order": 6,
        "prerequisites": ["graphs", "heap-priority-queue"],
        "snippet": "Shortest path, MST, Eulerian path, and other advanced algorithms.",
        "problems": [
            "reconstruct-itinerary", "min-cost-to-connect-all-points",
            "network-delay-time", "swim-in-rising-water", "alien-dictionary",
            "cheapest-flights-within-k-stops",
        ],
    },
    {
        "key": "dp-2d",
        "name": "2-D Dynamic Programming",
        "order": 6,
        "prerequisites": ["dp-1d", "graphs"],
        "snippet": "Grids, edit distance, and path counting over two dimensions.",
        "problems": [
            "unique-paths", "longest-common-subsequence",
            "best-time-to-buy-and-sell-stock-with-cooldown", "coin-change-ii",
            "target-sum", "interleaving-string", "longest-increasing-path-in-a-matrix",
            "distinct-subsequences", "edit-distance", "burst-balloons",
            "regular-expression-matching",
        ],
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
                    "solvable": bool(p.starter_code and p.test_cases),
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
                "solvable": bool(p and p.starter_code and p.test_cases),
            }
        )
    return out


def get_daily_question(db: Session, user: User) -> dict | None:
    """Pick the single daily question for a user.

    Uses the adaptive recommendation ranking (weak/unlocked/unsolved patterns)
    and selects one deterministically per user per day, so the problem is stable
    all day but personalised. This is the rule that an ML model will later
    replace: once a trained recommender is live, it predicts the daily pick.
    """
    import hashlib
    from datetime import date

    recommended = get_recommendations(db, user)
    if not recommended:
        return {"problem": None}

    # A larger pool keeps the daily pick fresh while still drawing from the
    # strongest candidates the heuristic surfaced first.
    pool = recommended[:8]
    seed = int(hashlib.sha256(
        f"{user.id}:{date.today().isoformat()}".encode()
    ).hexdigest(), 16)
    daily = pool[seed % len(pool)]
    return {"problem": daily}


def get_activity(db: Session, user: User, days: int = 140) -> dict:
    """Accepted submissions counted per calendar day for the roadmap heatmap.

    Returns a dict { "days": [{"date": "YYYY-MM-DD", "count": int}, ...] } covering
    the trailing `days` days (oldest to newest) so the frontend can render a
    submission calendar where each day the user solved shows up as a tile.
    """
    from datetime import date, timedelta

    start = date.today() - timedelta(days=days - 1)

    rows = (
        db.query(
            func.date(Submission.submitted_at).label("day"),
            func.count(Submission.id).label("n"),
        )
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            func.date(Submission.submitted_at) >= start,
        )
        .group_by(func.date(Submission.submitted_at))
        .all()
    )
    counts = {str(day): int(n) for day, n in rows}

    out = []
    for offset in range(days):
        d = start + timedelta(days=offset)
        key = d.isoformat()
        out.append({"date": key, "count": counts.get(key, 0)})
    return {"days": out}
