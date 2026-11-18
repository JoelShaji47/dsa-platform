"""Nightly/weekly recommender training: ETL -> features -> rank -> evaluate.

Reads submissions, hints, interaction events, impressions and the catalog
from Postgres, trains a LightGBM LambdaRank model with a group-aware
time-based validation split, prints NDCG@10 / Precision@5 plus coverage /
diversity / cold-start slices, and saves backend/artifacts/ranker.txt + meta.

Task selection: the impression task (leak-free, opportunity-grouped) is
preferred when it has enough rows; otherwise the legacy engagement task
trains (with its documented limitations). Writes a machine-readable
backend/artifacts/eval_report.json with the heuristic-vs-ML comparison.

Exit 0: trained + saved. Exit 2: not enough behavioral data yet — the API
keeps serving the heuristic, so this is safe to run on a fresh database.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal
from app.ml import infer
from app.ml.features import (
    FEATURE_COLUMNS,
    build_impression_training_frame,
    build_training_frame,
)
from app.ml.train import (
    ARTIFACT_DIR,
    InsufficientData,
    compare_heuristic_vs_ml,
    save_artifact,
    train_frame,
)


def main() -> int:
    with SessionLocal() as db:
        imp_frame = build_impression_training_frame(db)
        legacy_frame = build_training_frame(db)

    task = "legacy-engagement"
    frame = legacy_frame
    if len(imp_frame) >= 20:
        try:
            # Prefer the leak-free task only if it passes the data gate.
            from app.ml.train import _check_frame

            _check_frame(imp_frame)
            frame, task = imp_frame, "impression"
        except InsufficientData as exc:
            print(f"impression task not usable ({exc}); falling back to legacy")

    print(f"task: {task}")
    print(f"training rows: {len(frame)} across {frame['user_id'].nunique() if len(frame) else 0} users")
    if len(frame):
        print(
            "label mix:",
            frame["relevance"].value_counts().sort_index().to_dict(),
        )
    try:
        booster, metrics = train_frame(frame)
    except InsufficientData as exc:
        print(f"SKIP: {exc} — heuristic remains in service")
        return 2

    # Held-out comparison on the validation slice is inside metrics; add an
    # explicit heuristic-vs-ML head-to-head on the same frame for the report.
    try:
        from app.ml.train import time_split

        _, valid = time_split(frame)
        if len(valid):
            scores = booster.predict(
                valid[FEATURE_COLUMNS].to_numpy(dtype=float)
            )
            comparison = compare_heuristic_vs_ml(
                valid.reset_index(drop=True), scores
            )
        else:
            comparison = {"note": "no validation slice; comparison inconclusive"}
    except Exception as exc:
        comparison = {"note": f"comparison failed safely: {exc}"}

    version = "ml-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    meta = save_artifact(booster, metrics, version)
    report = {
        "version": version,
        "task": task,
        "trained_at": meta["trained_at"],
        "metrics": metrics,
        "comparison": comparison,
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "eval_report.json").write_text(json.dumps(report, indent=2))
    infer.clear_cache()
    print(f"saved {meta['version']}: {metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
