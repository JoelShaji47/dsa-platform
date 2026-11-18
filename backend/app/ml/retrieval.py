"""Layer 4a: collaborative-filtering candidate retrieval.

The LambdaRank model in ``app.ml.train`` is a *ranker* — it can only order the
candidates another policy hands it. This module adds a recall path that the
heuristic alone misses: users who solved similar problems probably want the
next item in that neighbourhood too.

Model
-----
An implicit user x problem matrix is factorised with truncated SVD
(``sklearn.decomposition.TruncatedSVD``), which needs no new dependency.
Feedback is graded, not binary:

    accepted with no hint      1.0  (independent success)
    accepted after hints       0.7  (assisted success)
    attempted, never accepted  0.2  (weak interest signal)

A user's score for an item is the dot product of their latent factors. The
artifact stores the factors plus the user/slug vocabularies, so serving never
touches the submission log.

Serving is fail-open: a missing/corrupt artifact, an unknown user (cold start)
or any exception returns an empty candidate list and the heuristic candidate
pool stands unchanged.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.submission import Submission

RETRIEVAL_SCHEMA_VERSION = 1
RETRIEVAL_COMPONENTS = 32
MIN_INTERACTIONS = 20
MIN_USERS = 2
MIN_ITEMS = 2

ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "artifacts"
RETRIEVAL_PATH = ARTIFACT_DIR / "retrieval.npz"
RETRIEVAL_META_PATH = ARTIFACT_DIR / "retrieval_meta.json"

# Weight of one (user, problem) pair in the implicit matrix.
WEIGHT_CLEAN_ACCEPT = 1.0
WEIGHT_HINTED_ACCEPT = 0.7
WEIGHT_ATTEMPT = 0.2

_cache: dict = {"mtime": None, "artifact": None}


# --------------------------------------------------------------------------
# Training
# --------------------------------------------------------------------------


def build_interactions(db: Session) -> list[tuple[str, str, float]]:
    """Return ``(user_id, slug, weight)`` for every observed pair."""
    problems = {p.id: p.slug for p in db.query(Problem.id, Problem.slug).all()}
    if not problems:
        return []

    hint_counts: dict[tuple, int] = defaultdict(int)
    for uid, pid in db.query(HintUsage.user_id, HintUsage.problem_id).all():
        hint_counts[(uid, pid)] += 1

    attempts: dict[tuple, int] = defaultdict(int)
    accepted: set[tuple] = set()
    rows = (
        db.query(
            Submission.user_id,
            Submission.problem_id,
            Submission.status,
        )
        .filter(Submission.test_session_id.is_(None))
        .all()
    )
    for uid, pid, status in rows:
        key = (uid, pid)
        attempts[key] += 1
        if status == SubmissionStatus.ACCEPTED:
            accepted.add(key)

    out: list[tuple[str, str, float]] = []
    for (uid, pid), n in attempts.items():
        slug = problems.get(pid)
        if slug is None:
            continue
        if (uid, pid) in accepted:
            weight = (
                WEIGHT_HINTED_ACCEPT
                if hint_counts.get((uid, pid), 0)
                else WEIGHT_CLEAN_ACCEPT
            )
        else:
            weight = WEIGHT_ATTEMPT
        out.append((str(uid), slug, float(weight)))
    return out


def fit_factors(
    interactions: list[tuple[str, str, float]],
    n_components: int = RETRIEVAL_COMPONENTS,
    seed: int = 7,
) -> tuple[list[str], list[str], np.ndarray, np.ndarray]:
    """Factorise the implicit matrix. Pure and deterministic.

    Returns ``(user_ids, slugs, user_factors, item_factors)`` where a score is
    ``user_factors[i] @ item_factors[j]``.
    """
    if not interactions:
        return [], [], np.zeros((0, 0)), np.zeros((0, 0))
    user_ids = sorted({u for u, _, _ in interactions})
    slugs = sorted({s for _, s, _ in interactions})
    if len(user_ids) < MIN_USERS or len(slugs) < MIN_ITEMS:
        return user_ids, slugs, np.zeros((0, 0)), np.zeros((0, 0))

    u_index = {u: i for i, u in enumerate(user_ids)}
    s_index = {s: j for j, s in enumerate(slugs)}
    # Duplicate pairs (same pair appearing twice) are summed by the COO
    # constructor, which is harmless here because build_interactions emits
    # exactly one weight per pair.
    row = [u_index[u] for u, _, _ in interactions]
    col = [s_index[s] for _, s, _ in interactions]
    data = [w for _, _, w in interactions]
    matrix = csr_matrix(
        (np.asarray(data, dtype=np.float32), (row, col)),
        shape=(len(user_ids), len(slugs)),
    )

    k = max(1, min(n_components, len(user_ids) - 1, len(slugs) - 1))
    svd = TruncatedSVD(n_components=k, random_state=seed)
    user_factors = svd.fit_transform(matrix).astype(np.float32)
    item_factors = svd.components_.T.astype(np.float32)
    return user_ids, slugs, user_factors, item_factors


def _atomic_savez(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".tmp", suffix=".npz")
    os.close(fd)
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def train_and_save(
    db: Session,
    n_components: int = RETRIEVAL_COMPONENTS,
) -> dict | None:
    """Fit the retrieval model and save it. Returns meta, or None if too thin."""
    interactions = build_interactions(db)

    if len(interactions) < MIN_INTERACTIONS:
        return None

    user_ids, slugs, user_factors, item_factors = fit_factors(
        interactions, n_components=n_components
    )
    if not len(user_ids) or not len(slugs) or user_factors.size == 0:
        return None

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_savez(
        RETRIEVAL_PATH,
        user_ids=np.asarray(user_ids),
        slugs=np.asarray(slugs),
        user_factors=user_factors,
        item_factors=item_factors,
    )
    meta = {
        "version": "cf-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": RETRIEVAL_SCHEMA_VERSION,
        "n_interactions": len(interactions),
        "n_users": len(user_ids),
        "n_items": len(slugs),
        "n_components": int(user_factors.shape[1]),
        "weights": {
            "clean_accept": WEIGHT_CLEAN_ACCEPT,
            "hinted_accept": WEIGHT_HINTED_ACCEPT,
            "attempt": WEIGHT_ATTEMPT,
        },
    }
    _atomic_write_text(RETRIEVAL_META_PATH, json.dumps(meta, indent=2))
    clear_cache()
    return meta


# --------------------------------------------------------------------------
# Serving
# --------------------------------------------------------------------------


def _load_uncached() -> dict | None:
    try:
        if not RETRIEVAL_PATH.exists():
            return None
        with np.load(RETRIEVAL_PATH, allow_pickle=False) as data:
            user_ids = [str(x) for x in data["user_ids"].tolist()]
            slugs = [str(x) for x in data["slugs"].tolist()]
            user_factors = np.asarray(data["user_factors"], dtype=np.float32)
            item_factors = np.asarray(data["item_factors"], dtype=np.float32)
    except Exception:
        return None
    if (
        not user_ids
        or not slugs
        or user_factors.ndim != 2
        or item_factors.ndim != 2
        or user_factors.shape[0] != len(user_ids)
        or item_factors.shape[0] != len(slugs)
        or user_factors.shape[1] != item_factors.shape[1]
    ):
        return None
    return {
        "user_index": {u: i for i, u in enumerate(user_ids)},
        "slugs": slugs,
        "user_factors": user_factors,
        "item_factors": item_factors,
    }


def load_artifact() -> dict | None:
    """Cached artifact with mtime-based reload (missing/corrupt -> None)."""
    try:
        mtime = RETRIEVAL_PATH.stat().st_mtime if RETRIEVAL_PATH.exists() else None
    except OSError:
        mtime = None
    if mtime is None:
        _cache["mtime"] = None
        _cache["artifact"] = None
        return None
    if _cache["artifact"] is None or _cache["mtime"] != mtime:
        _cache["artifact"] = _load_uncached()
        _cache["mtime"] = mtime
    return _cache["artifact"]


def clear_cache() -> None:
    _cache["mtime"] = None
    _cache["artifact"] = None


def model_version() -> str | None:
    try:
        meta = json.loads(RETRIEVAL_META_PATH.read_text())
    except (OSError, ValueError):
        return None
    return meta.get("version")


def retrieve_candidates(
    db: Session,
    user_id: UUID | str,
    limit: int = 8,
    eligible_slugs: set[str] | None = None,
    exclude_slugs: set[str] | None = None,
) -> list[tuple[str, float]]:
    """Top-``limit`` CF candidates as ``[(slug, score), ...]``.

    ``eligible_slugs`` restricts recall to the caller's policy (unlocked,
    unsolved, solvable); ``exclude_slugs`` drops already-chosen candidates.
    An unknown user (cold start) or missing artifact returns ``[]``.
    """
    artifact = load_artifact()
    if artifact is None or limit <= 0:
        return []
    idx = artifact["user_index"].get(str(user_id))
    if idx is None:
        return []
    scores = artifact["item_factors"] @ artifact["user_factors"][idx]
    order = np.argsort(-scores, kind="stable")
    exclude = exclude_slugs or set()
    out: list[tuple[str, float]] = []
    for j in order:
        slug = artifact["slugs"][int(j)]
        if slug in exclude:
            continue
        if eligible_slugs is not None and slug not in eligible_slugs:
            continue
        out.append((slug, float(scores[int(j)])))
        if len(out) >= limit:
            break
    return out
