import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml import infer
from app.ml.features import CUTOFF_COLUMN, FEATURE_COLUMNS, GROUP_COLUMN, LABEL_COLUMN
from app.ml.train import (
    InsufficientData,
    grouped_metrics,
    ndcg_at_k,
    precision_at_k,
    train_frame,
)

client = TestClient(app)


def synthetic_frame(
    n_users: int = 4, n_problems: int = 8, seed: int = 0
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    base = pd.Timestamp("2026-01-01", tz="UTC")
    for u in range(n_users):
        for p in range(n_problems):
            solved = bool(rng.random() < 0.5)
            attempts = int(rng.integers(1, 6)) if solved or rng.random() < 0.7 else 0
            if attempts == 0:
                continue
            hints = int(rng.integers(0, 3))
            relevance = (
                2 if (solved and hints <= 1 and attempts <= 3)
                else (1 if solved else 0)
            )
            rows.append(
                {
                    **{c: float(rng.random()) for c in FEATURE_COLUMNS},
                    "i_attempts": float(attempts),
                    "i_ever_solved": float(solved),
                    LABEL_COLUMN: relevance,
                    GROUP_COLUMN: f"user-{u}",
                    CUTOFF_COLUMN: base + pd.Timedelta(days=int(rng.integers(0, 60))),
                    "slug": f"problem-{p}",
                }
            )
    return pd.DataFrame(rows)


def test_ranking_metrics_sane_on_perfect_order():
    y_true = np.array([2, 1, 0, 0])
    y_score = np.array([0.9, 0.5, 0.2, 0.1])
    assert ndcg_at_k(y_true, y_score) == pytest.approx(1.0)
    assert precision_at_k(y_true, y_score, k=2) == pytest.approx(1.0)
    assert precision_at_k(y_true, np.array([0.1, 0.2, 0.9, 0.5]), k=2) == pytest.approx(0.0)


def test_trainer_rejects_tiny_data():
    df = synthetic_frame(n_users=1, n_problems=2, seed=1)
    assert len(df) < 20
    with pytest.raises(InsufficientData):
        train_frame(df)


def test_trainer_trains_and_scores_on_synthetic_data():
    df = synthetic_frame()
    assert len(df) >= 20
    booster, metrics = train_frame(df)
    assert 0.0 <= metrics["ndcg@10"] <= 1.0
    assert 0.0 <= metrics["precision@5"] <= 1.0
    assert metrics["train_rows"] > 0
    scores = booster.predict(df[FEATURE_COLUMNS].to_numpy(dtype=float))
    assert len(scores) == len(df)
    check = grouped_metrics(df.reset_index(drop=True), scores)
    assert 0.0 <= check["ndcg@10"] <= 1.0


def test_infer_abstains_without_artifact(monkeypatch, tmp_path):
    from app.ml import train as train_module

    monkeypatch.setattr(infer, "MODEL_PATH", tmp_path / "missing.txt")
    monkeypatch.setattr(train_module, "MODEL_PATH", tmp_path / "missing.txt")
    monkeypatch.setattr(train_module, "META_PATH", tmp_path / "missing.json")
    infer.clear_cache()
    try:
        assert infer._load_booster() is None
        assert infer.model_version() is None
    finally:
        infer.clear_cache()


def test_recommendations_response_carries_model_tag():
    from tests.test_roadmap import make_user_and_token

    headers = make_user_and_token()
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    assert body["recommendations"]
    assert all("model" in item for item in body["recommendations"])
    explained = client.get(
        "/api/v1/roadmap/recommendations",
        params={"explain": "true"},
        headers=headers,
    ).json()
    assert explained["recommendations"]
