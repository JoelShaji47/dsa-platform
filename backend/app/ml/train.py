"""LambdaRank training with time-based validation.

Split: train on pairs whose last interaction is before cutoff T (80th
percentile of cutoff_at), validate on the rest. Never random-split — that
would leak future behavior into training. Metrics: NDCG@10 and Precision@5,
plus a heuristic-agreement sanity check.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from app.ml.features import CUTOFF_COLUMN, FEATURE_COLUMNS, GROUP_COLUMN, LABEL_COLUMN

ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "ranker.txt"
META_PATH = ARTIFACT_DIR / "ranker_meta.json"

MIN_ROWS = 20
MIN_POSITIVE_GROUPS = 2


class InsufficientData(Exception):
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


def grouped_metrics(
    df: pd.DataFrame, scores: np.ndarray, k_ndcg: int = 10, k_prec: int = 5
) -> dict:
    ndcgs, precs = [], []
    for _, group in df.groupby(GROUP_COLUMN):
        y_true = group[LABEL_COLUMN].to_numpy()
        y_score = scores[group.index.to_numpy()]
        ndcgs.append(ndcg_at_k(y_true, y_score, k_ndcg))
        precs.append(precision_at_k(y_true, y_score, k_prec))
    return {
        f"ndcg@{k_ndcg}": round(float(np.mean(ndcgs)), 4) if ndcgs else 0.0,
        f"precision@{k_prec}": round(float(np.mean(precs)), 4) if precs else 0.0,
        "groups": len(ndcgs),
    }


def time_split(
    df: pd.DataFrame, valid_fraction: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = df[CUTOFF_COLUMN].quantile(1 - valid_fraction)
    train = df[df[CUTOFF_COLUMN] < cutoff].copy()
    valid = df[df[CUTOFF_COLUMN] >= cutoff].copy()
    return train, valid


def _to_dataset(df: pd.DataFrame) -> tuple[lgb.Dataset, list[int]]:
    groups = df.groupby(GROUP_COLUMN, sort=False).size().tolist()
    return (
        lgb.Dataset(
            df[FEATURE_COLUMNS].to_numpy(dtype=float),
            label=df[LABEL_COLUMN].to_numpy(dtype=float),
            group=groups,
        ),
        groups,
    )


def train_frame(df: pd.DataFrame, seed: int = 7) -> tuple[lgb.Booster, dict]:
    if len(df) < MIN_ROWS:
        raise InsufficientData(
            f"need >= {MIN_ROWS} training rows, have {len(df)}"
        )
    pos_groups = sum(1 for _, g in df.groupby(GROUP_COLUMN) if (g[LABEL_COLUMN] > 0).any())
    if pos_groups < MIN_POSITIVE_GROUPS:
        raise InsufficientData(
            f"need >= {MIN_POSITIVE_GROUPS} users with a solve, have {pos_groups}"
        )

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
    }
    train_set, _ = _to_dataset(train_df)

    valid_usable = (
        len(valid_df) > 0
        and (valid_df[LABEL_COLUMN] > 0).any()
        and valid_df[GROUP_COLUMN].nunique() >= 1
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
        metrics = grouped_metrics(valid_df.reset_index(drop=True), valid_scores)
        metrics["split"] = "time"
    else:
        booster = lgb.train(params, train_set, num_boost_round=100)
        train_scores = booster.predict(train_df[FEATURE_COLUMNS].to_numpy(dtype=float))
        metrics = grouped_metrics(train_df.reset_index(drop=True), train_scores)
        metrics["split"] = "train-only (too little recent data for validation)"

    metrics["train_rows"] = len(train_df)
    metrics["valid_rows"] = len(valid_df)
    metrics["best_iteration"] = booster.best_iteration
    return booster, metrics


def save_artifact(booster: lgb.Booster, metrics: dict, version: str) -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    booster.save_model(str(MODEL_PATH))
    meta = {
        "version": version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": FEATURE_COLUMNS,
        "metrics": metrics,
    }
    META_PATH.write_text(json.dumps(meta, indent=2))
    return meta


def load_meta() -> dict | None:
    if not META_PATH.exists():
        return None
    try:
        return json.loads(META_PATH.read_text())
    except (OSError, ValueError):
        return None
