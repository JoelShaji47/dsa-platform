"""Hybrid recommender: heuristic baseline + LightGBM learning-to-rank.

- features.py: per-(user, problem) training rows from submissions, hints,
  interaction events and catalog metadata.
- train.py: time-split LambdaRank training + NDCG/precision evaluation.
- infer.py: artifact loading + candidate scoring with heuristic fallback.

The API in app/services/roadmap.py keeps its response shape; only the ranking
behind get_recommendations() changes when a trained artifact exists.
"""
