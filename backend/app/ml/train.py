"""LambdaRank training with group-aware time-based validation.

Group contract (A1): each ranking query/group holds a contiguous block of
rows for exactly one recommendation opportunity. Legacy engagement frames
use one query per user (``query_id == user_id``) — acceptable only because
those rows represent one post-hoc engagement ranking per user; the
impression task uses one query per recommendation opportunity. Rows are
always sorted deterministically by (group, cutoff, slug) before group
sizes are generated, the sum of group sizes is asserted against the row
count, and the same group is never split across train/validation.

Metrics: NDCG@5/10, Precision@5, coverage, topic diversity, cold-start and
history-segment slices. Heuristic-vs-ML comparison runs on identical
held-out candidate sets. Sparse data -> "inconclusive" report, never
invented numbers.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from app.ml.features import (
    CUTOFF_COLUMN,
    FEATURE_COLUMNS,
    FEATURE_SCHEMA_VERSION,
    GROUP_COLUMN,
    LABEL_COLUMN,
    QUERY_COLUMN,
    sanitize_frame,
    sort_frame,
)

ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "ranker.txt"
META_PATH = ARTIFACT_DIR / "ranker_meta.json"
MODEL_BACKUP_PATH = ARTIFACT_DIR / "ranker.txt.bak"
META_BACKUP_PATH = ARTIFACT_DIR / "ranker_meta.json.bak"

MIN_ROWS = 20
MIN_POSITIVE_GROUPS = 2
MIN_VALID_GROUPS = 1


class InsufficientData(Exception):
    pass


class ArtifactInvalid(Exception):
    pass


def _dcg_at_k(relevances: np.ndarray, k: int) -> float:
    rel = np.asarray(relevances)[:k]
    if rel.size == 0:
        return 0.0
    discounts = np.log2(np.arange(2, rel.size + 2))
    return float(np.sum((2**rel - 1) / discounts))


def ndcg_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 10) -> float:
    order = np.argsort(y_score)[::-1]
    ideal = np.argsort(y_true)[::-1]
    denom = _dcg_at_k(y_true[ideal], k)
    if denom == 0:
        return 0.0
    return _dcg_at_k(y_true[order], k) / denom


def precision_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 5) -> float:
    order = np.argsort(y_score)[::-1][:k]
    hits = sum(1 for i in order if y_true[i] > 0)
    return hits / min(k, len(y_true))


def _group_key_column(df: pd.DataFrame) -> str:
    return QUERY_COLUMN if QUERY_COLUMN in df.columns else GROUP_COLUMN


def grouped_metrics(
    df: pd.DataFrame, scores: np.ndarray, k_ndcg: int = 10, k_prec: int = 5
) -> dict:
    key = _group_key_column(df)
    ndcgs, ndcg5s, precs = [], [], []
    for _, group in df.groupby(key):
        y_true = group[LABEL_COLUMN].to_numpy()
        y_score = scores[group.index.to_numpy()]
        ndcgs.append(ndcg_at_k(y_true, y_score, k_ndcg))
        ndcg5s.append(ndcg_at_k(y_true, y_score, 5))
        precs.append(precision_at_k(y_true, y_score, k_prec))
    return {
        f"ndcg@{k_ndcg}": round(float(np.mean(ndcgs)), 4) if ndcgs else 0.0,
        "ndcg@5": round(float(np.mean(ndcg5s)), 4) if ndcg5s else 0.0,
        f"precision@{k_prec}": round(float(np.mean(precs)), 4) if precs else 0.0,
        "groups": len(ndcgs),
    }


def coverage_diversity(
    df: pd.DataFrame, scores: np.ndarray, k: int = 5,
    pattern_of_slug: dict | None = None,
) -> dict:
    """Coverage@k (share of distinct items surfaced) and topic diversity.

    Diversity = mean distinct patterns in the top-k per group (1.0 = all
    top-k from one pattern). Without a slug->pattern map, pattern diversity
    is reported as null rather than invented.
    """
    key = _group_key_column(df)
    top_items: set = set()
    total_items: set = set()
    divs = []
    for _, group in df.groupby(key):
        slugs = group["slug"].to_numpy() if "slug" in group.columns else np.arange(len(group))
        total_items.update(slugs.tolist())
        order = np.argsort(scores[group.index.to_numpy()])[::-1][:k]
        top = slugs[order]
        top_items.update(top.tolist())
        if pattern_of_slug:
            pats = {pattern_of_slug.get(s) for s in top.tolist()}
            pats.discard(None)
            divs.append(len(pats) / min(k, len(group)))
    return {
        f"coverage@{k}": round(len(top_items) / len(total_items), 4) if total_items else 0.0,
        f"pattern_diversity@{k}": round(float(np.mean(divs)), 4) if divs else None,
    }


def time_split(
    df: pd.DataFrame, valid_fraction: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Group-aware temporal split: whole queries go to train OR validation.

    Groups are ordered by their max cutoff; the most recent
    ``valid_fraction`` of groups form validation. The same recommendation
    opportunity is never split across the two sets.
    """
    key = _group_key_column(df)
    if CUTOFF_COLUMN not in df.columns:
        # No timestamps: deterministic fallback — last groups validate.
        groups = sorted(df[key].unique().tolist())
        n_valid = max(1, int(len(groups) * valid_fraction))
        valid_keys = set(groups[-n_valid:])
        return (
            df[~df[key].isin(valid_keys)].copy(),
            df[df[key].isin(valid_keys)].copy(),
        )
    cutoffs = df.copy()
    cutoffs[CUTOFF_COLUMN] = pd.to_datetime(cutoffs[CUTOFF_COLUMN], utc=True, errors="coerce")
    group_max = cutoffs.groupby(key)[CUTOFF_COLUMN].max().sort_values(kind="mergesort")
    n_valid = max(1, int(len(group_max) * valid_fraction))
    # Groups with NaT cutoffs stay in train (never validate on dateless rows).
    valid_keys = set(group_max.dropna().tail(n_valid).index.tolist())
    valid = df[df[key].isin(valid_keys)].copy()
    train = df[~df[key].isin(valid_keys)].copy()
    return train, valid


def _to_dataset(df: pd.DataFrame) -> tuple[lgb.Dataset, list[int]]:
    """Build a LightGBM Dataset with validated, contiguous group sizes."""
    if df.empty:
        raise InsufficientData("cannot build a dataset from zero rows")
    df = sort_frame(sanitize_frame(df))
    key = _group_key_column(df)
    groups = df.groupby(key, sort=False).size().tolist()
    if sum(groups) != len(df):
        raise ArtifactInvalid(
            f"group sizes sum to {sum(groups)} but frame has {len(df)} rows"
        )
    if any(g <= 0 for g in groups):
        raise ArtifactInvalid("empty ranking group detected")
    return (
        lgb.Dataset(
            df[FEATURE_COLUMNS].to_numpy(dtype=float),
            label=df[LABEL_COLUMN].to_numpy(dtype=float),
            group=groups,
        ),
        groups,
    )


def _check_frame(df: pd.DataFrame) -> None:
    if df.empty or len(df) < MIN_ROWS:
        raise InsufficientData(f"need >= {MIN_ROWS} training rows, have {len(df)}")
    key = _group_key_column(df)
    pos_groups = sum(1 for _, g in df.groupby(key) if (g[LABEL_COLUMN] > 0).any())
    if pos_groups < MIN_POSITIVE_GROUPS:
        raise InsufficientData(
            f"need >= {MIN_POSITIVE_GROUPS} queries with a solve, have {pos_groups}"
        )
    varied = sum(1 for _, g in df.groupby(key) if g[LABEL_COLUMN].nunique() > 1)
    if varied < MIN_POSITIVE_GROUPS:
        raise InsufficientData(
            f"need >= {MIN_POSITIVE_GROUPS} queries with relevance variation, "
            f"have {varied} (all-same-label groups teach nothing)"
        )


def evaluate_frame(
    df: pd.DataFrame,
    scores: np.ndarray,
    name: str = "valid",
    pattern_of_slug: dict | None = None,
) -> dict:
    """Full machine-readable evaluation report for one scored frame."""
    df = df.reset_index(drop=True)
    report = {"set": name, "rows": len(df)}
    report.update(grouped_metrics(df, scores))
    report.update(coverage_diversity(df, scores, pattern_of_slug=pattern_of_slug))
    # Cold-start slice: queries whose users have <= 1 solved pair in frame.
    key = _group_key_column(df)
    try:
        solved_per_group = df.groupby(key)[LABEL_COLUMN].apply(lambda s: int((s > 0).sum()))
        cold_keys = set(solved_per_group[solved_per_group <= 1].index.tolist())
        if cold_keys:
            mask = df[key].isin(cold_keys)
            sub = df[mask].reset_index(drop=True)
            cold = grouped_metrics(sub, scores[mask.to_numpy()])
            report["cold_ndcg@10"] = cold["ndcg@10"]
            report["cold_precision@5"] = cold["precision@5"]
            report["cold_groups"] = cold["groups"]
        else:
            report["cold_ndcg@10"] = None
            report["cold_precision@5"] = None
            report["cold_groups"] = 0
    except Exception:
        report["cold_ndcg@10"] = None
        report["cold_precision@5"] = None
        report["cold_groups"] = 0
    if report["groups"] < 3:
        report["note"] = (
            "inconclusive: fewer than 3 validation queries; "
            "metrics are descriptive, not a promotion signal"
        )
    return report


def compare_heuristic_vs_ml(
    df: pd.DataFrame,
    ml_scores: np.ndarray,
    heuristic_scores: np.ndarray | None = None,
    pattern_of_slug: dict | None = None,
) -> dict:
    """Fair head-to-head on identical held-out candidate sets.

    ``heuristic_scores`` defaults to the legacy heuristic order proxy
    (pattern order then difficulty) when an explicit heuristic score is
    unavailable; the comparison frame and cutoffs are always identical.
    """
    df = df.reset_index(drop=True)
    if heuristic_scores is None:
        # Deterministic heuristic proxy: earlier pattern order + easier first.
        heur = np.zeros(len(df))
        if "p_pattern_order" in df.columns:
            heur -= df["p_pattern_order"].to_numpy(dtype=float)
        if "p_diff_ord" in df.columns:
            heur -= 0.1 * df["p_diff_ord"].to_numpy(dtype=float)
        heuristic_scores = heur
    ml = evaluate_frame(df, ml_scores, name="ml", pattern_of_slug=pattern_of_slug)
    heu = evaluate_frame(df, heuristic_scores, name="heuristic", pattern_of_slug=pattern_of_slug)
    return {
        "ml": ml,
        "heuristic": heu,
        "delta_ndcg@10": round(ml["ndcg@10"] - heu["ndcg@10"], 4),
        "delta_precision@5": round(ml["precision@5"] - heu["precision@5"], 4),
        "same_candidates": True,
    }


def train_frame(df: pd.DataFrame, seed: int = 7) -> tuple[lgb.Booster, dict]:
    df = sort_frame(sanitize_frame(df))
    _check_frame(df)

    train_df, valid_df = time_split(df)
    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [10],
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": 5,
        "verbose": -1,
        "seed": seed,
        "deterministic": True,
    }
    try:
        train_set, _ = _to_dataset(train_df)
    except InsufficientData:
        raise InsufficientData("training split is empty after time_split")

    key = _group_key_column(valid_df)
    valid_usable = (
        len(valid_df) > 0
        and (valid_df[LABEL_COLUMN] > 0).any()
        and valid_df[key].nunique() >= MIN_VALID_GROUPS
        and len(train_df) >= MIN_ROWS
    )
    if valid_usable:
        valid_set, _ = _to_dataset(valid_df)
        booster = lgb.train(
            params,
            train_set,
            num_boost_round=500,
            valid_sets=[valid_set],
            callbacks=[lgb.early_stopping(30, verbose=False)],
        )
        valid_scores = booster.predict(valid_df[FEATURE_COLUMNS].to_numpy(dtype=float))
        metrics = evaluate_frame(valid_df.reset_index(drop=True), valid_scores, name="valid")
        metrics["split"] = "time"
    else:
        booster = lgb.train(params, train_set, num_boost_round=100)
        train_scores = booster.predict(train_df[FEATURE_COLUMNS].to_numpy(dtype=float))
        metrics = evaluate_frame(train_df.reset_index(drop=True), train_scores, name="train")
        metrics["split"] = "train-only (too little recent data for validation)"

    metrics["train_rows"] = len(train_df)
    metrics["valid_rows"] = len(valid_df)
    metrics["best_iteration"] = booster.best_iteration
    metrics["feature_schema_version"] = FEATURE_SCHEMA_VERSION
    return booster, metrics


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


def validate_artifact(model_path: Path, meta: dict) -> None:
    """Fail-closed artifact check before a serving switch."""
    if not model_path.exists() or model_path.stat().st_size == 0:
        raise ArtifactInvalid(f"model file missing or empty: {model_path}")
    if meta.get("features") != FEATURE_COLUMNS:
        raise ArtifactInvalid(
            "feature schema mismatch: artifact does not match serving columns"
        )
    if meta.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        raise ArtifactInvalid("feature schema version mismatch")
    booster = lgb.Booster(model_file=str(model_path))
    probe = np.zeros((1, len(FEATURE_COLUMNS)), dtype=float)
    booster.predict(probe)  # raises if the model is unloadable


def save_artifact(booster: lgb.Booster, metrics: dict, version: str) -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep last known-good before overwriting.
    if MODEL_PATH.exists():
        try:
            MODEL_PATH.replace(MODEL_BACKUP_PATH)
        except OSError:
            pass
    if META_PATH.exists():
        try:
            META_PATH.replace(META_BACKUP_PATH)
        except OSError:
            pass
    booster.save_model(str(MODEL_PATH))
    meta = {
        "version": version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": FEATURE_COLUMNS,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "metrics": metrics,
        "config": {"objective": "lambdarank", "min_rows": MIN_ROWS},
    }
    validate_artifact(MODEL_PATH, meta)  # fail before publishing meta
    _atomic_write_text(META_PATH, json.dumps(meta, indent=2))
    return meta


def load_meta() -> dict | None:
    if not META_PATH.exists():
        return None
    try:
        return json.loads(META_PATH.read_text())
    except (OSError, ValueError):
        return None
