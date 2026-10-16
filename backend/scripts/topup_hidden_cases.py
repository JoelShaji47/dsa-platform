"""Top up hidden test cases for runnable problems using local REFS solutions.

For each slug in GENERATORS: run the verify_seeds reference on hand-designed
edge inputs, print computed outputs for eyeball review, and (with --apply)
append them as hidden cases until the problem holds 5 hidden (8 total).

No LLM, no Judge0 — safe to run alongside the author loop.

Usage:
    .venv/bin/python scripts/topup_hidden_cases.py [--apply]
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

from verify_seeds import REFS, normalize, run_reference  # noqa: E402

TARGET_HIDDEN = 5

# slug -> extra stdin inputs (must differ from existing cases; ref computes outputs)
GENERATORS: dict[str, list[str]] = {
    "reverse-linked-list": [
        "3\n9 9 9\n",
        "4\n-1 -2 -3 -4\n",
        "8\n-5 0 5 -5 0 5 100 -100\n",
        "10\n1 2 3 4 5 6 7 8 9 10\n",
    ],
    "daily-temperatures": [
        "6\n30 30 30 30 30 30\n",
        "2\n10 20\n",
        "7\n50 40 30 20 10 0 100\n",
        "6\n90 80 70 60 50 40\n",
    ],
    "binary-tree-level-order-traversal": [
        "2 1 3\n",
        "4 2 6 1 3 5 7\n",
        "1 null 2 null 3 null 4\n",
        "5 3 8 1 4 null 9\n",
    ],
}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    from app.db.session import SessionLocal
    from app.models.problem import Problem

    with SessionLocal() as db:
        for slug, inputs in GENERATORS.items():
            ref = REFS.get(slug)
            if ref is None:
                print(f"[{slug}] no REFS coverage, skipped")
                continue
            row = db.query(Problem).filter(Problem.slug == slug).first()
            if row is None:
                print(f"[{slug}] not in DB, skipped")
                continue
            cases = list(row.test_cases or [])
            have_inputs = {c["input"] for c in cases}
            hidden_now = sum(1 for c in cases if c.get("is_hidden"))
            added = 0
            for stdin_text in inputs:
                if hidden_now + added >= TARGET_HIDDEN:
                    break
                if stdin_text in have_inputs:
                    continue
                try:
                    out = run_reference(ref, stdin_text)
                except Exception as exc:
                    print(f"[{slug}] ref crashed on {stdin_text!r}: {exc!r}")
                    continue
                print(f"[{slug}] in={stdin_text!r} out={out!r}")
                cases.append({"input": stdin_text, "expected_output": out, "is_hidden": True})
                have_inputs.add(stdin_text)
                added += 1
            if args.apply and added:
                row.test_cases = cases
                print(f"[{slug}] appended {added} hidden (total {len(cases)})")
            elif not added:
                print(f"[{slug}] nothing to add")
        if args.apply:
            db.commit()
            print("committed")
        else:
            print("dry run — pass --apply to persist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
