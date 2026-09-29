"""Fetch public LeetCode problem data for catalog shells.

Uses the public GraphQL endpoint (no auth) to pull statement HTML, examples,
function signature metadata, and per-language starter snippets. Results are
cached as raw JSON under backend/artifacts/leetcode/ (gitignored) so authoring
batches can run offline. Be polite: ~1.2s between requests.

Usage:
    .venv/bin/python scripts/fetch_leetcode.py [--limit N] [--pattern KEY] [--force]

Exit 0 always (misses are recorded, not fatal).
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

CACHE_DIR = BACKEND_DIR / "artifacts" / "leetcode"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

GRAPHQL_URL = "https://leetcode.com/graphql"
QUERY = """query q($s: String!) {
  question(titleSlug: $s) {
    questionId title content exampleTestcaseList
    metaData judgeType difficulty topicTags { name }
    codeSnippets { langSlug code }
  }
}"""


def fetch_one(slug: str) -> dict | None:
    body = json.dumps({"query": QUERY, "variables": {"s": slug}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
    except Exception as exc:
        return {"_error": f"http: {exc}"}
    q = (payload.get("data") or {}).get("question")
    if not q:
        return {"_error": f"no question: {(payload.get('errors') or [{}])[0].get('message', '?')[:120]}"}
    return q


def shell_slugs(pattern: str | None = None) -> list[dict]:
    from app.db.session import SessionLocal
    from app.models.problem import Problem

    with SessionLocal() as db:
        rows = db.query(
            Problem.slug, Problem.title, Problem.pattern_key,
            Problem.starter_code, Problem.test_cases,
        ).all()
        out = []
        for slug, title, pkey, sc, tc in rows:
            if sc and tc:
                continue
            if pattern and (pkey or "") != pattern:
                continue
            out.append({"slug": slug, "title": title, "pattern": pkey})
        return out


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pattern", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    slugs = shell_slugs(args.pattern)
    if args.limit:
        slugs = slugs[: args.limit]
    hits = misses = skipped = 0
    for i, item in enumerate(slugs):
        slug = item["slug"]
        dest = CACHE_DIR / f"{slug}.json"
        if dest.exists() and not args.force:
            skipped += 1
            continue
        data = fetch_one(slug)
        if data is None or "_error" in data:
            misses += 1
            dest.write_text(json.dumps({"slug": slug, **item, **(data or {"_error": "empty"})}, indent=1))
        else:
            hits += 1
            dest.write_text(json.dumps({"slug": slug, **item, "leetcode": data}, indent=1))
        print(f"[{i + 1}/{len(slugs)}] {slug}: {'HIT' if '_error' not in (data or {}) else 'miss'}", flush=True)
        time.sleep(1.2)
    print(f"done: hits={hits} misses={misses} skipped={skipped} total={len(slugs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
