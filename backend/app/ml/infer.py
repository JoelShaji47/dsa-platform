"""Serving: score recommendation candidates with the trained ranker.

Cold paths fall back to the heuristic (return {} = "no model opinion"):
- no artifact on disk, artifact unreadable / feature or schema mismatch,
- the user has fewer than MIN_INTERACTIONS logged submissions,
- prediction raises.

Reloads are explicit: the booster is cached with its file mtime and
reloaded when the artifact changes (``reload_if_updated``); the training
script also calls ``clear_cache`` after saving. Inference exceptions never
break the recommendation endpoint — callers treat {} as "serve heuristic".
The served ``model`` version tag is always the version actually used.
"""

import logging
import time
from functools import lru_cache

import lightgbm as lgb
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ml.features import (
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    candidate_feature_rows,
)
from app.ml.train import META_PATH, MODEL_PATH, load_meta
from app.models.submission import Submission
from app.models.user import User
from app.models.enums import SubmissionStatus

logger = logging.getLogger(__name__)

MIN_INTERACTIONS = 3

# Serving fast path: global problem priors aggregated in SQL and cached
# briefly so recommendation requests never fetch every user's submissions.
_PRIORS_TTL_S = 60.0
_priors_cache: dict = {"at": 0.0, "pop": {}, "acc": {}}

_booster_cache: dict = {"mtime": None, "booster": None}


def _load_booster_uncached() -> lgb.Booster | None:
    try:
        if not MODEL_PATH.exists():
            return None
        return lgb.Booster(model_file=str(MODEL_PATH))
    except Exception:
        logger.debug("ranker artifact unloadable; abstaining", exc_info=True)
        return None


def _load_booster() -> lgb.Booster | None:
    """Cached booster with mtime-based reload (explicit, tested)."""
    try:
        mtime = MODEL_PATH.stat().st_mtime if MODEL_PATH.exists() else None
    except OSError:
        mtime = None
    if mtime is None:
        _booster_cache["mtime"] = None
        _booster_cache["booster"] = None
        return None
    if _booster_cache["booster"] is None or _booster_cache["mtime"] != mtime:
        _booster_cache["booster"] = _load_booster_uncached()
        _booster_cache["mtime"] = mtime
    return _booster_cache["booster"]


def reload_if_updated() -> bool:
    """Reload the artifact if the file changed since last load.

    Returns True when a (re)load happened, False when the cache is current.
    """
    try:
        mtime = MODEL_PATH.stat().st_mtime if MODEL_PATH.exists() else None
    except OSError:
        mtime = None
    if mtime != _booster_cache["mtime"]:
        _booster_cache["booster"] = _load_booster_uncached()
        _booster_cache["mtime"] = mtime
        return True
    return False


def clear_cache() -> None:
    _booster_cache["mtime"] = None
    _booster_cache["booster"] = None
    _priors_cache["at"] = 0.0
    _priors_cache["pop"] = {}
    _priors_cache["acc"] = {}


def model_version() -> str | None:
    meta = load_meta()
    return meta.get("version") if meta else None


def artifact_compatible() -> bool:
    """Schema/version gate: the artifact must match serving columns."""
    meta = load_meta()
    if not meta:
        return False
    return (
        meta.get("features") == FEATURE_COLUMNS
        and meta.get("feature_schema_version", 1) == FEATURE_SCHEMA_VERSION
    )


def artifact_loaded() -> bool:
    """True when the ranker file exists and LightGBM can actually load it."""
    return _load_booster() is not None


def _global_priors(db: Session) -> dict:
    """Aggregate (popularity, accept-rate) per problem in SQL, cached 60s."""
    now = time.monotonic()
    if now - _priors_cache["at"] < _PRIORS_TTL_S and _priors_cache["pop"]:
        return {"pop": _priors_cache["pop"], "acc": _priors_cache["acc"]}
    try:
        total_rows = (
            db.query(
                Submission.problem_id,
                func.count(func.distinct(Submission.user_id)),
            )
            .filter(Submission.test_session_id.is_(None))
            .group_by(Submission.problem_id)
            .all()
        )
        pop = {pid: float(n) for pid, n in total_rows}
        # Count distinct accepting users per problem (second aggregate).
        acc_rows = (
            db.query(
                Submission.problem_id,
                func.count(func.distinct(Submission.user_id)),
            )
            .filter(
                Submission.test_session_id.is_(None),
                Submission.status == SubmissionStatus.ACCEPTED,
            )
            .group_by(Submission.problem_id)
            .all()
        )
        acc = {pid: 0.5 for pid in pop}
        for pid, n_acc in acc_rows:
            denom = pop.get(pid, 0.0)
            acc[pid] = (n_acc / denom) if denom else 0.5
    except Exception:
        logger.debug("priors aggregation failed; using empty priors", exc_info=True)
        return {"pop": {}, "acc": {}}
    _priors_cache.update({"at": now, "pop": pop, "acc": acc})
    return {"pop": pop, "acc": acc}


def _candidate_frame(
    db: Session, user: User, slugs: list[str]
) -> tuple[pd.DataFrame, list[str]]:
    priors = _global_priors(db)
    rows = candidate_feature_rows(
        db, user.id, slugs, as_of=None, global_priors=priors
    )
    ordered = [r["slug"] for r in rows]
    if not rows:
        return pd.DataFrame(columns=FEATURE_COLUMNS), []
    frame = pd.DataFrame(rows)
    return frame[FEATURE_COLUMNS], ordered


def score_candidates(
    db: Session, user: User, slugs: list[str]
) -> dict[str, float]:
    """Return {slug: model_score}; empty dict when the model abstains."""
    reload_if_updated()
    booster = _load_booster()
    if booster is None or not slugs:
        return {}
    try:
        n_subs = (
            db.query(Submission.id).filter(Submission.user_id == user.id).count()
        )
    except Exception:
        return {}
    if n_subs < MIN_INTERACTIONS:
        return {}
    if not artifact_compatible():
        return {}
    frame, ordered = _candidate_frame(db, user, slugs)
    if frame.empty:
        return {}
    try:
        scores = booster.predict(frame.to_numpy(dtype=float))
    except Exception:
        logger.debug("ranker predict failed; abstaining", exc_info=True)
        return {}
    return {slug: float(score) for slug, score in zip(ordered, scores)}
