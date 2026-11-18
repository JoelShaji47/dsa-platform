import logging
from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.services import skill_model

logger = logging.getLogger(__name__)

# A pattern is a Neetcode-style study block. Problems are grouped into
# patterns and the patterns form a prerequisite DAG (the "roadmap tree").
PATTERNS: list[dict] = [
    {
        "key": "coding-basics",
        "name": "Coding Basics",
        "order": 0,
        "prerequisites": [],
        "snippet": "Language fundamentals, basic maths, recursion and hashing — the Striver A2Z starting block.",
        "problems": [],
    },
    {
        "key": "sorting",
        "name": "Sorting Techniques",
        "order": 1,
        "prerequisites": ["coding-basics"],
        "snippet": "Selection, bubble, insertion, merge, quick and recursive sorts.",
        "problems": [],
    },
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
            "subarray-sum-equals-k", "first-missing-positive",
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
            "container-with-most-water", "trapping-rain-water", "move-zeroes",
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
            "largest-rectangle-in-histogram", "next-greater-element",
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
            "middle-of-the-linked-list",
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
            "graph-valid-tree", "word-ladder", "flood-fill",
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

# Catalog growth: extra slugs per pattern, merged into the DAG below so the
# roadmap grows with the catalog without hand-editing the lists above.
from app.seeds.data_neetcode250 import NC250_PATTERN_EXTRAS as _NC250_EXTRAS
from app.seeds.data_tuf_a2z import TUF_PATTERN_EXTRAS as _TUF_EXTRAS

for _pattern in PATTERNS:
    for _extra_map in (_NC250_EXTRAS, _TUF_EXTRAS):
        for _slug in _extra_map.get(_pattern["key"], []):
            if _slug not in _pattern["problems"]:
                _pattern["problems"].append(_slug)

del _pattern, _slug, _extra_map, _NC250_EXTRAS, _TUF_EXTRAS

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
    # Layer 1 student model (see app.services.skill_model). ``solve_rate`` is
    # the mean P(solve) over this pattern's *solvable* problems; ``confidence``
    # says how much evidence backs it (0 with no graded observations).
    skill_theta: float = 0.0
    skill_n: int = 0
    solve_rate: float = 0.0
    confidence: float = 0.0
    solvable_total: int = 0

    @property
    def complete(self) -> bool:
        return self.total > 0 and self.solved >= self.total


def _load_problems(db: Session) -> dict[str, Problem]:
    return {p.slug: p for p in db.query(Problem).filter(Problem.is_published.is_(True)).all()}


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
            Submission.test_session_id.is_(None),
        )
        .distinct()
        .all()
    }
    solved_by_problem = {
        p.slug: (p.id in solved_ids) for p in problems.values()
    }

    attempt_rows = (
        db.query(Submission.problem_id, func.count(Submission.id))
        .filter(
            Submission.user_id == user.id,
            Submission.test_session_id.is_(None),
        )
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
    skill = skill_model.load_user_skill(db, user.id)
    solvable = skill_model.solvable_difficulties(problems.values())
    for pattern_key, pattern in PATTERN_BY_KEY.items():
        pp = PatternProgress(key=pattern_key, total=len(pattern["problems"]))
        for slug in pattern["problems"]:
            pp.solved += int(solved_by_problem.get(slug, False))
            pp.attempts += attempts_by_problem.get(slug, 0)
            pp.hints_used += hints_by_problem.get(slug, 0)

        # Layer 1: mastery is predicted solve rate over solvable problems, so
        # catalog placeholders can no longer deflate it. With no evidence the
        # prediction would just be the difficulty prior, so fall back to the
        # (honest, zero-for-untouched) evidence ratio instead.
        theta, n = skill.get(pattern_key, (0.0, 0))
        difficulties = solvable.get(pattern_key, [])
        prediction = skill_model.pattern_prediction(theta, n, difficulties)
        pp.skill_theta = prediction["theta"]
        pp.skill_n = prediction["n"]
        pp.solve_rate = prediction["solve_rate"]
        pp.confidence = prediction["confidence"]
        pp.solvable_total = prediction["solvable_total"]

        if n > 0 and difficulties:
            pp.mastery = round(100.0 * prediction["solve_rate"], 1)
        elif pp.solved > 0 and pp.total > 0:
            # No skill estimate yet (e.g. before the first replay): keep the
            # legacy ratio so nothing regresses to 0 mid-deploy.
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


def get_user_progress(
    db: Session, user: User
) -> dict[str, PatternProgress]:
    """Public progress helper for ML inference and other callers.

    Returns only the per-pattern progress map. Prefer this over
    ``_build_user_state`` (private, returns the full tuple).
    """
    return _build_user_state(db, user)[4]


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

    # NOTE: assemble pattern_out BEFORE create_opportunity commits. A commit
    # expires every loaded Problem attribute, and re-reading them afterwards
    # costs one roundtrip per attribute per problem (80s+ over a slow link).
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
                    "sources": p.sources or [],
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
                "solvable_total": pp.solvable_total,
                "mastery": pp.mastery,
                "skill": {
                    "theta": pp.skill_theta,
                    "n": pp.skill_n,
                    "solve_rate": pp.solve_rate,
                    "confidence": pp.confidence,
                },
                "complete": pp.complete,
                "problems": problem_out,
            }
        )

    # Layer 2: skill-aware pattern pathway. Built from the in-memory state
    # above (no extra queries) and before create_opportunity commits, since a
    # commit expires every loaded Problem attribute.
    plan = {"objective": "information_per_hour", "steps": []}
    try:
        from app.services import pathway as _pathway

        plan = _pathway.build_pathway(
            db,
            user,
            problems=problems,
            progress=progress,
            solved_by_problem=solved_by_problem,
        )
    except Exception:
        logger.debug("pathway simulation abstained", exc_info=True)

    # Fail-safe opportunity log so the highlighted node can be joined to a
    # later impression (generated tree != exposed node until rendered).
    opportunity_id = None
    try:
        from app.services import telemetry as _telemetry

        opportunity_id = _telemetry.create_opportunity(
            db, user, "heuristic-v1", len(recommended)
        )
    except Exception:
        logger.debug("roadmap opportunity logging abstained", exc_info=True)

    return {
        "patterns": pattern_out,
        "pathway": plan,
        "totals": {
            "solved": sum(p["solved"] for p in pattern_out),
            "total": sum(p["total"] for p in pattern_out),
        },
        "opportunity_id": str(opportunity_id) if opportunity_id else None,
    }


def _unlocked_patterns(
    progress: dict[str, PatternProgress],
) -> set[str]:
    """Prerequisite gate.

    A prerequisite is satisfied by evidence, not by a single solve: either the
    learner has solved something there (legacy, always honoured) or the student
    model has enough observations in the pattern to predict, with confidence,
    that they can solve half of it. The second path is what lets a learner who
    is strong but unlucky past one problem keep moving.
    """
    unlocked = set()
    changed = True
    while changed:
        changed = False
        for pattern in PATTERNS:
            if pattern["key"] in unlocked:
                continue
            if all(
                _prerequisite_ready(progress[pk])
                for pk in pattern["prerequisites"]
            ):
                unlocked.add(pattern["key"])
                changed = True
    return unlocked


def _prerequisite_ready(pp: PatternProgress) -> bool:
    """Is this pattern's learning objective actually met?

    Evidence wins when we have it: the student model must predict at least
    ``UNLOCK_SOLVE_RATE`` across the pattern from ``MIN_UNLOCK_EVIDENCE``
    observations. Without any estimate (cold user, or a deploy before the
    first replay) the legacy "solved at least one" signal keeps the roadmap
    from emptying out.
    """
    if pp.skill_n >= skill_model.MIN_UNLOCK_EVIDENCE:
        return pp.solve_rate >= skill_model.UNLOCK_SOLVE_RATE
    return pp.solved > 0


def recommend_next(
    db: Session,
    user: User,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
) -> list[dict]:
    unlocked = _unlocked_patterns(progress)
    loaded = _load_problems(db)
    solvable_by_slug = {
        slug: bool(p.starter_code and p.test_cases)
        for slug, p in loaded.items()
    }

    candidates: list[dict] = []
    for pattern in PATTERNS:
        if pattern["key"] not in unlocked:
            continue
        pp = progress[pattern["key"]]
        for slug in pattern["problems"]:
            if solved_by_problem.get(slug, False):
                continue
            # Catalog-only entries (no starter code / test cases) open a
            # "coming soon" page, so they are never recommendable — see AGENTS.md.
            if not solvable_by_slug.get(slug, False):
                continue
            problem = loaded.get(slug)
            predicted = (
                skill_model.problem_solve_rate(pp.skill_theta, problem)
                if problem is not None
                else 0.0
            )
            candidates.append(
                {
                    "slug": slug,
                    "pattern_key": pattern["key"],
                    "pattern_name": pattern["name"],
                    "order": pattern["order"],
                    "mastery": pp.mastery,
                    "solvable": True,
                    "predicted_solve_rate": predicted,
                    "zone_fit": skill_model.zone_fit(predicted),
                    "confidence": pp.confidence,
                }
            )

    # score candidates: weak patterns first, then pattern order, with a bonus
    # for problems inside the target difficulty band. The band only nudges the
    # order and only as far as we trust theta — a cold user has no evidence,
    # so their ordering is unchanged.
    def score(c: dict) -> float:
        base = (100.0 - c["mastery"]) + c["order"] * 0.1
        return base - 20.0 * c["zone_fit"] * c["confidence"]

    candidates.sort(key=score)
    recommendations = []
    for c in candidates[:12]:
        recommendations.append(
            {
                "slug": c["slug"],
                "pattern_key": c["pattern_key"],
                "pattern_name": c["pattern_name"],
                "mastery": c["mastery"],
                "predicted_solve_rate": round(c["predicted_solve_rate"], 4),
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


# ---- Candidate intents (C4): one interpretable policy per learning goal. ----
# All intents reuse recommend_next / get_review_due and respect the same
# eligibility: unlocked patterns, unsolved, solvable. No duplicated
# candidate-generation logic.
INTENTS = ("balanced", "skill", "retention", "transfer", "exploration")

# Two-stage hybrid knobs (docs/ml-recommendation-plan.md §4a/§4c).
MAX_RECOMMENDATIONS = 12
RETRIEVAL_CANDIDATES = 6
DEFAULT_EXPLORATION_EPSILON = 0.1


def _as_rec(slug: str, problems: dict, progress: dict[str, PatternProgress]) -> dict | None:
    pattern_key = SLUG_TO_PATTERN.get(slug)
    if pattern_key is None:
        return None
    p = problems.get(slug)
    if p is None or not (p.starter_code and p.test_cases):
        return None
    pp = progress.get(pattern_key)
    if pp is None:
        return None
    pattern_name = PATTERN_BY_KEY.get(pattern_key, {}).get("name", pattern_key)
    c = {"slug": slug, "pattern_key": pattern_key,
         "pattern_name": pattern_name, "mastery": pp.mastery}
    return {"slug": slug, "pattern_key": pattern_key, "pattern_name": pattern_name,
            "mastery": pp.mastery, "reason": _reason(c, progress)}


def generate_candidates(
    db: Session,
    user: User,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
    problems: dict,
    intent: str = "balanced",
    limit: int = 12,
    pattern: str | None = None,
) -> list[dict]:
    """Intent-aware candidate generation over the existing heuristic pool.

    ``pattern`` scopes the drill to one roadmap block; filtering happens on the
    full ranked pool *before* the top-``limit`` truncation, so a drill is never
    emptied just because the pattern's candidates fell outside the global top.
    """
    if intent not in INTENTS:
        intent = "balanced"
    base = recommend_next(db, user, solved_by_problem, progress)
    if pattern is not None:
        base = [r for r in base if r["pattern_key"] == pattern]
    if intent == "skill":
        return base[:limit]

    if intent == "retention":
        # Spaced revision first (friction solves due), then skill backlog.
        due = get_review_due(db, user, limit=limit)
        out, seen = [], set()
        for d in due:
            if d["slug"] in seen or solved_by_problem.get(d["slug"], False):
                continue
            rec = _as_rec(d["slug"], problems, progress)
            if rec is None:
                continue
            if pattern is not None and rec["pattern_key"] != pattern:
                continue
            rec["reason"] = (
                f"Revision due — solved {d['hints_used']} hint(s) in "
                f"{d['attempts']} attempt(s); spaced recall locks it in."
            )
            rec["intent"] = "retention"
            out.append(rec)
            seen.add(d["slug"])
        for r in base:
            if r["slug"] not in seen and len(out) < limit:
                out.append({**r, "intent": "skill"})
        return out[:limit]

    if intent == "transfer":
        # New problems in patterns whose prerequisites are solid (>=60%).
        ready = [
            k for k, pp in progress.items()
            if pp.mastery >= 60 and pp.solved > 0
        ]
        unlocked = _unlocked_patterns(progress)
        out = []
        for r in base:
            pat = PATTERN_BY_KEY.get(r["pattern_key"], {})
            prereqs = pat.get("prerequisites", [])
            if prereqs and all(p in ready for p in prereqs):
                out.append({**r, "intent": "transfer",
                            "reason": f"Apply your {r['pattern_name']} foundations to a new challenge."})
        for r in base:  # backfill with skill picks
            if r["slug"] not in {o["slug"] for o in out} and len(out) < limit:
                out.append({**r, "intent": "skill"})
        return out[:limit]

    if intent == "exploration":
        # Limited exposure to untouched patterns (max 3), then skill backlog.
        fresh = [r for r in base if progress[r["pattern_key"]].solved == 0][:3]
        out = [{**r, "intent": "exploration",
                "reason": f"Explore {r['pattern_name']} — a new pattern to broaden your range."}
               for r in fresh]
        for r in base:
            if r["slug"] not in {o["slug"] for o in out} and len(out) < limit:
                out.append({**r, "intent": "skill"})
        return out[:limit]

    # balanced: skill order with retention injection (every 4th slot) and
    # bounded exploration (first fresh pick appended when present).
    due = get_review_due(db, user, limit=3)
    due_recs = []
    for d in due:
        rec = _as_rec(d["slug"], problems, progress)
        if rec is not None and not solved_by_problem.get(d["slug"], False):
            rec["intent"] = "retention"
            due_recs.append(rec)
    out, di = [], 0
    for i, r in enumerate(base):
        if due_recs and (i + 1) % 4 == 0 and di < len(due_recs):
            if due_recs[di]["slug"] not in {o["slug"] for o in out}:
                out.append(due_recs[di])
                di += 1
                continue
        out.append({**r, "intent": "skill"})
        if len(out) >= limit:
            break
    return out[:limit]


def _eligible_slugs(
    problems: dict,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
    pattern: str | None = None,
) -> list[str]:
    """Stable, policy-legal recall pool: unlocked, unsolved, solvable."""
    unlocked = _unlocked_patterns(progress)
    out = []
    for slug, problem in problems.items():
        pattern_key = SLUG_TO_PATTERN.get(slug)
        if pattern_key is None or pattern_key not in unlocked:
            continue
        if pattern is not None and pattern_key != pattern:
            continue
        if solved_by_problem.get(slug, False):
            continue
        if not (problem.starter_code and problem.test_cases):
            continue
        order = PATTERN_BY_KEY.get(pattern_key, {}).get("order", 99)
        out.append((order, slug))
    out.sort()
    return [slug for _, slug in out]


def _retrieval_recommendations(
    db: Session,
    user: User,
    problems: dict,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
    existing: set[str],
    limit: int = RETRIEVAL_CANDIDATES,
    pattern: str | None = None,
) -> list[dict]:
    """§4a: collaborative-filtering recall, constrained by roadmap policy."""
    from app.ml import retrieval as _retrieval

    eligible = set(
        _eligible_slugs(problems, solved_by_problem, progress, pattern=pattern)
    )
    if not eligible:
        return []
    rows = _retrieval.retrieve_candidates(
        db,
        user.id,
        limit=limit,
        eligible_slugs=eligible,
        exclude_slugs=existing,
    )
    out = []
    for slug, score in rows:
        rec = _as_rec(slug, problems, progress)
        if rec is None:
            continue
        rec.update(
            {
                "intent": "skill",
                "candidate_source": "cf",
                "retrieval_score": round(float(score), 4),
            }
        )
        out.append(rec)
    return out


def _exploration_epsilon() -> float:
    import os

    raw = os.environ.get("ML_EXPLORATION_EPSILON")
    if raw is None:
        return DEFAULT_EXPLORATION_EPSILON
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return DEFAULT_EXPLORATION_EPSILON
    return min(max(value, 0.0), 1.0)


def _maybe_explore(
    user: User,
    problems: dict,
    solved_by_problem: dict[str, bool],
    progress: dict[str, PatternProgress],
    chosen: set[str],
    intent: str,
    epsilon: float | None = None,
    pattern: str | None = None,
) -> dict | None:
    """§4c: epsilon-greedy exploration for one eligible surprise pick.

    Stable per (user, day, intent) so a learner does not see the recommended
    list reshuffle on every poll, while still guaranteeing fresh items a
    share of exposure.
    """
    import random
    from datetime import date

    eps = _exploration_epsilon() if epsilon is None else epsilon
    if eps <= 0.0:
        return None
    pool = [
        slug
        for slug in _eligible_slugs(
            problems, solved_by_problem, progress, pattern=pattern
        )
        if slug not in chosen
    ]
    if not pool:
        return None
    rng = random.Random(f"explore:{user.id}:{date.today().isoformat()}:{intent}")
    if rng.random() >= eps:
        return None
    rec = _as_rec(rng.choice(pool), problems, progress)
    if rec is None:
        return None
    rec.update(
        {
            "intent": "exploration",
            "candidate_source": "exploration",
            "reason": f"Explore {rec['pattern_name']} — broaden your range today.",
        }
    )
    return rec


def explain_recommendation(
    rec: dict, progress: dict[str, PatternProgress], review_due_slugs: set[str] | None = None
) -> str:
    """Lightweight explanation from real selection signals only.

    Never fabricates feature importance or causal claims: every sentence is
    backed by the progress map, the intent tag, or review-due membership.
    """
    if review_due_slugs and rec["slug"] in review_due_slugs:
        return "Needs revision — you solved this with friction before; recall now to retain it."
    if rec.get("candidate_source") == "cf":
        return f"Similar learners advanced here — a natural next step in {rec['pattern_name']}."
    if rec.get("intent") == "transfer":
        return f"Ready to transfer — your prerequisites for {rec['pattern_name']} are solid."
    if rec.get("intent") == "exploration":
        return f"Adds variety — a first step into {rec['pattern_name']}."
    if rec.get("intent") == "retention":
        return f"Spaced revision in {rec['pattern_name']} to lock in past learning."
    pp = progress.get(rec.get("pattern_key", ""), None)
    if pp is not None:
        if pp.solved == 0:
            return f"Reasonable next step — kick off {rec['pattern_name']}."
        if pp.mastery < 60:
            return f"Targets a weak spot — {rec['pattern_name']} is {pp.mastery:.0f}% mastered."
        return f"Next step in {rec['pattern_name']} to keep the momentum."
    return "Reasonable next step from your roadmap."


def get_recommendations(
    db: Session,
    user: User,
    explain: bool = False,
    intent: str = "balanced",
    pattern: str | None = None,
) -> list[dict]:
    """Two-stage recommendations: heuristic + CF recall, ML rank, explore.

    Stage 1 builds a policy-legal pool (unlocked, unsolved, solvable) from the
    heuristic and, for balanced/skill intents, adds collaborative-filtering
    neighbours the heuristic missed. Stage 2 lets the LambdaRank model re-score
    the union when an artifact exists AND the user has enough logged history;
    otherwise the heuristic order stands (CF fills only the tail). Finally an
    epsilon-greedy exploration slot may replace the lowest-ranked item.

    ``intent`` selects the candidate policy (balanced/skill/retention/
    transfer/exploration). Each request logs a fail-safe
    ``recommendation_opportunity`` row; the client reports actually-rendered
    items via POST /roadmap/impressions (generated != exposed).
    """
    (
        problems,
        solved_by_problem,
        attempts_by_problem,
        hints_by_problem,
        progress,
    ) = _build_user_state(db, user)
    if intent not in INTENTS:
        intent = "balanced"
    heuristic_recs = generate_candidates(
        db, user, solved_by_problem, progress, problems, intent=intent, pattern=pattern
    )

    # Stage 1b (§4a): widen recall with collaborative-filtering candidates.
    # The ranker below is the stage-2 fine scorer; the roadmap policy (unlocked,
    # unsolved, solvable) still constrains every retrieved slug.
    retrieved_recs: list[dict] = []
    if intent in ("balanced", "skill"):
        try:
            retrieved_recs = _retrieval_recommendations(
                db,
                user,
                problems,
                solved_by_problem,
                progress,
                {r["slug"] for r in heuristic_recs},
                pattern=pattern,
            )
        except Exception:
            logger.debug("CF retrieval abstained", exc_info=True)

    recommendations = heuristic_recs + retrieved_recs

    model_tag = "heuristic-v1"
    try:
        from app.ml import infer as _infer

        scores = _infer.score_candidates(
            db, user, [r["slug"] for r in recommendations]
        )
        if scores:
            version = _infer.model_version() or "ml-unknown"
            model_tag = version
            # Stable re-rank: model score first, heuristic order breaks ties.
            order = {r["slug"]: i for i, r in enumerate(recommendations)}
            recommendations.sort(
                key=lambda r: (-scores.get(r["slug"], 0.0), order[r["slug"]])
            )
            recommendations = recommendations[:MAX_RECOMMENDATIONS]
    except Exception:
        logger.debug("ML re-rank abstained; serving heuristic order", exc_info=True)
        scores = {}

    if not scores and retrieved_recs:
        # No stage-2 scorer: still expose recall, but never let CF crowd out
        # the whole heuristic core.
        budget = max(0, MAX_RECOMMENDATIONS - len(retrieved_recs))
        recommendations = (heuristic_recs[:budget] + retrieved_recs)[
            :MAX_RECOMMENDATIONS
        ]
    elif not scores:
        recommendations = recommendations[:MAX_RECOMMENDATIONS]

    # Stage 2b (§4c): epsilon-greedy exploration. Replaces the lowest-ranked
    # slot so the list length and ranked core stay intact. Explicit intent
    # requests (retention/transfer/exploration) keep their policy untouched.
    try:
        explored = None
        if intent in ("balanced", "skill"):
            explored = _maybe_explore(
                user,
                problems,
                solved_by_problem,
                progress,
                {r["slug"] for r in recommendations},
                intent,
                pattern=pattern,
            )
        if explored is not None:
            recommendations = recommendations[: MAX_RECOMMENDATIONS - 1] + [explored]
    except Exception:
        logger.debug("exploration abstained", exc_info=True)

    # Fail-safe opportunity log (telemetry never breaks recommendations).
    opportunity_id = None
    try:
        from app.services import telemetry as _telemetry

        opportunity_id = _telemetry.create_opportunity(
            db, user, model_tag, len(recommendations)
        )
    except Exception:
        logger.debug("opportunity logging abstained", exc_info=True)

    review_slugs: set[str] = set()
    try:
        review_slugs = {d["slug"] for d in get_review_due(db, user, limit=10)}
    except Exception:
        pass

    out = []
    for r in recommendations:
        p = problems.get(r["slug"])
        item = {
            **r,
            "title": p.title if p else r["slug"],
            "difficulty": p.difficulty.value if p else "MEDIUM",
            "solvable": bool(p and p.starter_code and p.test_cases),
            "model": model_tag,
            "intent": r.get("intent", intent),
            "explanation": explain_recommendation(r, progress, review_slugs),
        }
        if opportunity_id is not None:
            item["opportunity_id"] = str(opportunity_id)
        if explain and r["slug"] in scores:
            item["score"] = round(scores[r["slug"]], 4)
        out.append(item)
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


def get_review_due(db: Session, user: User, older_than_days: int = 7, limit: int = 10) -> list[dict]:
    """Spaced-repetition queue: solved problems worth revisiting.

    Surfaces accepted problems first solved more than ``older_than_days`` ago
    where the original solve showed friction (hints used or >= 3 attempts).
    Frictionless recent solves are assumed retained.
    """
    from datetime import datetime, timedelta, timezone

    problems = {p.id: p for p in db.query(Problem).filter(Problem.is_published.is_(True)).all()}
    subs = (
        db.query(Submission)
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .order_by(Submission.submitted_at)
        .all()
    )
    first_accept: dict = {}
    attempts: dict = defaultdict(int)
    for s in subs:
        attempts[s.problem_id] += 1
        first_accept.setdefault(s.problem_id, s.submitted_at)

    hint_counts: dict = defaultdict(int)
    for (pid,) in (
        db.query(HintUsage.problem_id)
        .filter(HintUsage.user_id == user.id)
        .all()
    ):
        hint_counts[pid] += 1

    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    due = []
    for pid, accepted_at in first_accept.items():
        if accepted_at.tzinfo is None:
            accepted_at = accepted_at.replace(tzinfo=timezone.utc)
        if accepted_at >= cutoff:
            continue
        hints = hint_counts.get(pid, 0)
        tries = attempts.get(pid, 0)
        if hints == 0 and tries < 3:
            continue
        problem = problems.get(pid)
        if problem is None:
            continue
        due.append(
            {
                "slug": problem.slug,
                "title": problem.title,
                "difficulty": problem.difficulty.value,
                "pattern_key": problem.pattern_key,
                "pattern_name": PATTERN_BY_KEY.get(problem.pattern_key or {}, {}).get(
                    "name", problem.pattern_key
                ),
                "solved_at": accepted_at.isoformat(),
                "hints_used": hints,
                "attempts": tries,
            }
        )
    due.sort(key=lambda d: d["solved_at"])
    return due[:limit]


def get_activity(db: Session, user: User, days: int = 140) -> dict:
    """Accepted submissions counted per calendar day for the roadmap heatmap.

    Returns a dict { "days": [{"date": "YYYY-MM-DD", "count": int,
    "problems": [{"slug", "title", "difficulty"}]}, ...] } covering
    the trailing `days` days (oldest to newest) so the frontend can render a
    submission calendar where each day the user solved shows up as a tile,
    with the solved questions available for hover details. ``problems`` is
    deduplicated per day and sorted by title; empty days carry [].
    """
    from datetime import datetime, timedelta, timezone

    start = datetime.now(timezone.utc).date() - timedelta(days=days - 1)
    day_expr = func.date(func.timezone("UTC", Submission.submitted_at))

    rows = (
        db.query(day_expr.label("day"), func.count(Submission.id).label("n"))
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
            day_expr >= start,
        )
        .group_by(day_expr)
        .all()
    )
    counts = {str(day): int(n) for day, n in rows}

    window_start = datetime.combine(start, datetime.min.time()).replace(tzinfo=timezone.utc)
    submitted_utc = func.timezone("UTC", Submission.submitted_at)
    per_day: dict[str, dict[str, dict]] = {}
    for sub, problem in (
        db.query(Submission, Problem)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
            submitted_utc >= window_start,
        )
        .all()
    ):
        ts = sub.submitted_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        key = ts.date().isoformat()
        bucket = per_day.setdefault(key, {})
        bucket[problem.slug] = {
            "slug": problem.slug,
            "title": problem.title,
            "difficulty": problem.difficulty.value,
        }

    out = []
    for offset in range(days):
        d = start + timedelta(days=offset)
        key = d.isoformat()
        solved = sorted(per_day.get(key, {}).values(), key=lambda p: p["title"])
        out.append({"date": key, "count": counts.get(key, 0), "problems": solved})
    return {"days": out}
