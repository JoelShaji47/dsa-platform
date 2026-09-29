"""Author catalog shells into runnable problems (generate -> verify -> stage).

For each shell problem with a LeetCode cache file:
  1. LLM drafts description (paraphrased, our format), stdin/stdout I/O contract,
     3-language parse-only starters, test cases (3 visible + 2 hidden),
     and a Python reference solution.
  2. The reference is executed through Judge0 against ALL cases — only
     ACCEPTED batches are staged.
  3. Staged patches land in backend/app/seeds/data_authored.py, which wins
     seed dedupe (imported first), so a normal seed.py run applies them.

Usage:
    .venv/bin/python scripts/author_batch.py --pattern two-pointers [--limit N] [--apply]

Without --apply, patches are written to backend/artifacts/authored/{slug}.json
for inspection. With --apply they are merged into data_authored.py (DB update
happens on the next seed.py run).
"""

import asyncio
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

CACHE_DIR = BACKEND_DIR / "artifacts" / "leetcode"
PATCH_DIR = BACKEND_DIR / "artifacts" / "authored"
PATCH_DIR.mkdir(parents=True, exist_ok=True)
AUTHORED_MODULE = BACKEND_DIR / "app" / "seeds" / "data_authored.py"

SYSTEM = (
    "You author coding-interview problems for a practice platform. "
    "You MUST paraphrase any reference statement in original wording — never "
    "copy it verbatim. Output ONLY a JSON object, no fences, no commentary."
)


def build_prompt(title: str, difficulty: str, fetched: dict) -> str:
    examples = "\n".join(fetched.get("exampleTestcaseList") or [])[:800]
    content = (fetched.get("content") or "")[:1800]
    meta = (fetched.get("metaData") or "")[:400]
    if content.strip():
        reference = (
            f"Reference problem (PARAPHRASE, do not copy): {title} ({difficulty})\n"
            f"\nSTATEMENT (reference):\n{content}\n"
            f"\nEXAMPLE INPUTS (function args, one block per case):\n{examples}\n"
            f"\nFUNCTION SIGNATURE (reference):\n{meta}\n"
        )
    else:
        reference = (
            f"Problem to author from scratch (no reference available): {title} ({difficulty}).\n"
            "Invent a clean, classic version of this well-known problem with sensible constraints.\n"
            "(Be extra careful that your test cases are correct — they will be executed.)\n"
        )
    spec = """
{
  "description": "markdown UNDER 220 words: '# {title}\\n\\n## Statement\\n...\\n## Input Format\\n- Line 1: ...\\n## Output Format\\n...\\n## Constraints\\n...\\n## Example\\n**Input**\\n```\\n...\\n```\\n**Output**\\n```\\n...\\n```'. The I/O format MUST be plain stdin lines / stdout lines (no JSON). Example I/O MUST match test_cases[0].",
  "io_notes": "one line describing the stdin/stdout contract",
  "starter_code": {
    "python": "full program: parse stdin, then '# ===== YOUR CODE HERE =====', user prints answer",
    "cpp": "full program with bits header, parse cin, then '// ===== YOUR CODE HERE ====='",
    "java": "public class Main with Scanner parsing, then '// ===== YOUR CODE HERE ====='"
  },
  "test_cases": [
    {"input": "stdin text ending with newline", "expected_output": "exact stdout, no trailing newline", "is_hidden": false},
    {"input": "...", "expected_output": "...", "is_hidden": false},
    {"input": "...", "expected_output": "...", "is_hidden": false},
    {"input": "...", "expected_output": "...", "is_hidden": true},
    {"input": "...", "expected_output": "...", "is_hidden": true}
  ],
  "reference_python": "complete program reading stdin, printing the answer"
}

Rules: exactly 3 visible + 2 hidden cases; hidden cases MUST differ from visible (edge cases: empty/single/min/max/duplicates); expected outputs exact (numbers as plain ints, arrays space-separated on one line); starters must parse the SAME stdin layout the reference uses; reference must be efficient enough for n up to 10^4. CRITICAL: our judge compares stdout EXACTLY, so if multiple answers are valid you MUST define a canonical order (e.g. lines sorted lexicographically, numbers ascending) and state it in Output Format — never write 'any order'."""
    return reference + "\nProduce JSON with exactly these keys:\n" + spec


def extract_json(text: str) -> str:
    """Pull the first balanced {...} block (models add fences/commentary)."""
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object found")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    raise ValueError("unbalanced JSON object")


def parse_json(text: str) -> dict:
    return json.loads(extract_json(text.strip()))


def draft_problem(title: str, difficulty: str, fetched: dict) -> dict:
    from app.services import llm

    prompt = build_prompt(title, difficulty, fetched)
    last_exc: Exception | None = None
    for _ in range(2):
        text, _provider = llm.generate_chat(SYSTEM, prompt, max_tokens=8000)
        try:
            data = parse_json(text)
        except Exception as exc:
            last_exc = exc
            continue
        for key in ("description", "starter_code", "test_cases", "reference_python"):
            if key not in data:
                raise ValueError(f"draft missing key: {key}")
        if len([t for t in data["test_cases"] if not t.get("is_hidden")]) != 3:
            raise ValueError("need exactly 3 visible cases")
        return data
    raise ValueError(f"could not get valid draft: {last_exc}")


def verify_reference(reference: str, cases: list[dict]) -> tuple[bool, str]:
    from app.services.grader import grade_code

    async def _run():
        return await grade_code(reference, "python", cases)

    try:
        result = asyncio.run(_run())
    except Exception as exc:
        return False, f"judge error: {exc}"
    fails = [t for t in result.test_results if not t.passed]
    if fails:
        detail = "; ".join(
            f"case{t.index} out={((t.actual_output or '')[:120])!r} status={t.status_key}"
            for t in fails[:3]
        )
        return False, f"{result.status}: {detail}"
    return True, str(result.status)


def load_authored() -> list[dict]:
    if not AUTHORED_MODULE.exists():
        return []
    ns: dict = {}
    exec(compile(AUTHORED_MODULE.read_text(), str(AUTHORED_MODULE), "exec"), ns)
    return list(ns.get("AUTHORED_PROBLEMS", []))


def save_authored(entries: list[dict]) -> None:
    header = (
        '"""LLM-authored catalog problems (generate -> Judge0-verify -> stage).\n\n'
        'Managed by backend/scripts/author_batch.py --apply. Entries win seed\n'
        'dedupe (imported first in app/seeds/__init__.py) and are validated by\n'
        'app/seeds/schema.py like any other seed source.\n'
        '"""\n\n\n'
    )
    AUTHORED_MODULE.write_text(header + "AUTHORED_PROBLEMS = " + repr(entries) + "\n")


def process_one(slug: str, apply: bool) -> str:
    from app.db.session import SessionLocal
    from app.models.problem import Problem

    cache_file = CACHE_DIR / f"{slug}.json"
    cached: dict = {}
    if cache_file.exists():
        cached = json.loads(cache_file.read_text())
    if "_error" in cached and "leetcode" not in cached:
        cached = {}
    fetched = cached.get("leetcode", {})
    with SessionLocal() as db:
        row = db.query(Problem.title, Problem.difficulty).filter(Problem.slug == slug).first()
    db_title = row[0] if row else slug
    db_diff = row[1].value if row else "MEDIUM"
    title = fetched.get("title") or cached.get("title") or db_title
    difficulty = (fetched.get("difficulty") or db_diff or "Medium").upper()
    if difficulty not in ("EASY", "MEDIUM", "HARD"):
        difficulty = "MEDIUM"

    patch_file = PATCH_DIR / f"{slug}.json"
    if patch_file.exists():
        staged = json.loads(patch_file.read_text())
        if staged.get("verified"):
            if apply:
                merge_entry(
                    slug,
                    staged["title"],
                    staged["difficulty"],
                    staged["description"],
                    staged["starter_code"],
                    staged["test_cases"],
                )
                return "applied"
            return "already-staged"

    try:
        draft = draft_problem(title, difficulty, fetched)
    except Exception as exc:
        (PATCH_DIR / f"{slug}.error.txt").write_text(f"draft: {exc}")
        return f"draft-fail"

    ok, note = verify_reference(draft["reference_python"], draft["test_cases"])
    if not ok:
        (PATCH_DIR / f"{slug}.error.txt").write_text(f"verify: {note}")
        return "verify-fail"

    patch = {
        "slug": slug,
        "title": title,
        "difficulty": difficulty,
        "description": draft["description"],
        "starter_code": draft["starter_code"],
        "test_cases": draft["test_cases"],
        "verified": True,
        "verify_note": note,
    }
    patch_file.write_text(json.dumps(patch, indent=1))
    if apply:
        merge_entry(
            slug,
            title,
            difficulty,
            draft["description"],
            draft["starter_code"],
            draft["test_cases"],
        )
    return "staged"


def merge_entry(
    slug: str,
    title: str,
    difficulty: str,
    description: str,
    starter_code: dict,
    test_cases: list,
) -> None:
    from app.db.session import SessionLocal
    from app.models.problem import Problem

    with SessionLocal() as db:
        row = db.query(Problem.topic).filter(Problem.slug == slug).first()
        topic = row[0].value if row else "ARRAY"
    entries = [e for e in load_authored() if e.get("slug") != slug]
    entries.append(
        {
            "title": title,
            "slug": slug,
            "difficulty": difficulty,
            "topic": topic,
            "description": description,
            "starter_code": starter_code,
            "test_cases": test_cases,
        }
    )
    save_authored(entries)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sleep", type=float, default=25.0,
                    help="Seconds to pause between problems (provider rate limits).")
    args = ap.parse_args()

    files = sorted(CACHE_DIR.glob("*.json"))
    if args.pattern:
        from app.db.session import SessionLocal
        from app.models.problem import Problem

        with SessionLocal() as db:
            wanted = {
                r[0]
                for r in db.query(Problem.slug)
                .filter(Problem.pattern_key == args.pattern)
                .all()
            }
        files = [f for f in files if f.stem in wanted]
    if args.limit:
        files = files[: args.limit]

    from collections import Counter

    outcomes: Counter = Counter()
    import time as _time

    for i, f in enumerate(files):
        try:
            result = process_one(f.stem, args.apply)
            if result in ("draft-fail", "verify-fail", "error") and i + 1 < len(files):
                err = (PATCH_DIR / f"{f.stem}.error.txt").read_text() if (PATCH_DIR / f"{f.stem}.error.txt").exists() else ""
                if any(s in err for s in ("429", "rate-limited", "503", "cooldown", "UNAVAILABLE", "overloaded")):
                    print(f"[{f.stem}] quota hit — backing off 90s", flush=True)
                    _time.sleep(90)
        except Exception as exc:
            result = "error"
            (PATCH_DIR / f"{f.stem}.error.txt").write_text(f"unexpected: {exc}")
        outcomes[result] += 1
        print(f"[{i + 1}/{len(files)}] {f.stem}: {result}", flush=True)
        if result not in ("already-staged", "applied") and i + 1 < len(files):
            _time.sleep(args.sleep)
    print("outcomes:", dict(outcomes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
