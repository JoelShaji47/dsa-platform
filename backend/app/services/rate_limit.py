"""Shared in-process sliding-window rate limiting.

The tutor routes have always carried their own copy of this guard; the judge
endpoints need the same treatment against a far more expensive resource (one
Java submission can reserve ~4 GB), so the window logic lives here once and
every caller shares it.

Process-local by design: the app runs a single uvicorn process, and the goal is
to stop runaway client loops from saturating the shared Judge0 pool — not to
enforce a distributed quota. If the deployment ever grows past one worker this
should move to a shared store (Redis) behind the same ``check`` API.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Hashable

from fastapi import HTTPException, status

# Every limiter registers itself so tests (and operators) can reset them all
# without importing each call site.
_registry: list["SlidingWindowLimiter"] = []


class SlidingWindowLimiter:
    """Allow at most ``limit`` events per ``window_seconds`` for a given key.

    ``check`` either records the event or raises HTTP 429 with a ``Retry-After``
    header sized to the window, matching the cooldown semantics the tutor guard
    already used.
    """

    def __init__(self, limit: int, window_seconds: float, message: str) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.message = message
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        _registry.append(self)

    def check(self, key: Hashable) -> None:
        now = time.monotonic()
        bucket = str(key)
        with self._lock:
            hits = [t for t in self._hits.get(bucket, []) if now - t < self.window_seconds]
            if len(hits) >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.message,
                    headers={"Retry-After": str(int(self.window_seconds))},
                )
            hits.append(now)
            self._hits[bucket] = hits

    def reset(self, key: Hashable | None = None) -> None:
        """Drop recorded hits for one key, or all keys when ``key`` is None."""
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(str(key), None)


def reset_all_limiters() -> None:
    for limiter in _registry:
        limiter.reset()


# Judge endpoints. A run grades the handful of visible cases; a submit grades
# every stored case, so submits get the tighter budget. Both are generous
# enough for a human iterating and tight enough to bound a scripted loop.
JUDGE_RUN_LIMITER = SlidingWindowLimiter(
    limit=60,
    window_seconds=60.0,
    message="Too many code runs. Give it a few seconds before running again.",
)
JUDGE_SUBMIT_LIMITER = SlidingWindowLimiter(
    limit=30,
    window_seconds=60.0,
    message="Too many submissions. Give it a few seconds before submitting again.",
)
