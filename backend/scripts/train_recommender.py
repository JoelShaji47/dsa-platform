"""Nightly/weekly recommender training: ETL -> features -> rank -> evaluate.

Reads submissions, hints, interaction events and the catalog from Postgres,
trains a LightGBM LambdaRank model with a time-based validation split, prints
NDCG@10 / Precision@5, and saves backend/artifacts/ranker.txt + meta.

Exit 0: trained + saved. Exit 2: not enough behavioral data yet — the API
keeps serving the heuristic, so this is safe to run on a fresh database.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal
from app.ml import infer
from app.ml.features import build_training_frame
from app.ml.train import InsufficientData, save_artifact, train_frame


def main() -> int:
    with SessionLocal() as db:
        frame = build_training_frame(db)
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

    version = "ml-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    meta = save_artifact(booster, metrics, version)
    infer.clear_cache()
    print(f"saved {meta['version']}: {metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
