"""Apply and verify the global arena rules against an existing database.

The rule logic itself lives in app/seeds/global_arena_rules.py and is reused by
scripts/seed.py, so every seed run applies the rules automatically. This script
exists for databases that were seeded before that integration (or were reset in
between): it runs the same rules against the solvable problems already stored in
the database, then mirrors the normalized state back into the fully-authored
seed entries in app/seeds/data_*.py so re-seeding preserves the rules.

The script is idempotent: running it twice produces no changes.
"""

import ast
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.problem import Problem
from app.seeds.global_arena_rules import normalize_problem

SEED_DATA_FILES = [
    BACKEND_DIR / "app" / "seeds" / "data_arrays.py",
    BACKEND_DIR / "app" / "seeds" / "data_graphs_dp.py",
    BACKEND_DIR / "app" / "seeds" / "data_linked_stack.py",
    BACKEND_DIR / "app" / "seeds" / "data_strings.py",
    BACKEND_DIR / "app" / "seeds" / "data_trees.py",
]


def solvable_query():
    return (
        "SELECT slug, description, test_cases "
        "FROM problems "
        "WHERE jsonb_array_length(test_cases) > 0 "
        "AND description LIKE '%## Example%'"
    )


def find_position(node, lines):
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)
    return line_offsets[node.lineno - 1] + node.col_offset, line_offsets[node.end_lineno - 1] + node.end_col_offset


def literals_for_slug(src: str, slug: str):
    tree = ast.parse(src)
    results = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = {k.value: v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if (
                isinstance(keys.get("slug"), ast.Constant)
                and keys["slug"].value == slug
                and isinstance(keys.get("description"), ast.Constant)
                and isinstance(keys.get("test_cases"), ast.List)
            ):
                results["description"] = keys["description"]
                results["test_cases"] = keys["test_cases"]
                return results
    return None


def mirror_seeds(normalized: dict) -> list:
    changed_files = []
    for path in SEED_DATA_FILES:
        src = path.read_text(encoding="utf-8")
        lines = src.split("\n")
        edits = []
        for slug, (new_desc, new_cases) in normalized.items():
            slots = literals_for_slug(src, slug)
            if not slots:
                continue
            dstart, dend = find_position(slots["description"], lines)
            tstart, tend = find_position(slots["test_cases"], lines)
            desc_literal = '"""' + new_desc + '"""'
            old_desc = src[dstart:dend]
            if old_desc != desc_literal:
                edits.append((dstart, dend, desc_literal))
            old_cases = src[tstart:tend]
            new_cases_literal = "[\n" + "".join(
                '            {"input": %s, "expected_output": %s, "is_hidden": %s},\n'
                % (json.dumps(tc["input"]), json.dumps(tc["expected_output"]), "True" if tc["is_hidden"] else "False")
                for tc in new_cases
            ) + "        ]"
            if old_cases != new_cases_literal:
                edits.append((tstart, tend, new_cases_literal))

        if not edits:
            continue
        for start, end, text in sorted(edits, reverse=True):
            src = src[:start] + text + src[end:]
        ast.parse(src)
        path.write_text(src, encoding="utf-8")
        changed_files.append(str(path.relative_to(BACKEND_DIR)) + f" ({len(edits)} edits)")
    return changed_files


def main() -> None:
    warnings = []
    changed = []
    untouched = []
    with SessionLocal() as db:
        rows = db.execute(text(solvable_query())).fetchall()
        normalized = {}
        for slug, description, test_cases in rows:
            new_desc, new_cases, did_change = normalize_problem(slug, description, test_cases, warnings)
            normalized[slug] = (new_desc, new_cases)
            if did_change or new_cases != test_cases:
                prob = db.query(Problem).filter(Problem.slug == slug).first()
                prob.description = new_desc
                prob.test_cases = new_cases
                changed.append(slug)
            else:
                untouched.append(slug)
        db.commit()

    mirrored = mirror_seeds(normalized)

    print(f"solvable problems: {len(rows)}")
    print(f"updated: {len(changed)}")
    print(f"unchanged: {len(untouched)}")
    print(f"seed files mirrored: {mirrored if mirrored else 'none'}")
    if warnings:
        print(f"\nwarnings ({len(warnings)}):")
        for w in warnings:
            print("  -", w)
    else:
        print("\nno warnings")

    with SessionLocal() as db:
        check = db.execute(text(
            "SELECT count(*) FROM problems WHERE jsonb_array_length(test_cases) > 0 "
            "AND description LIKE '%## Example%' "
            "AND description NOT LIKE '%## Example 2%'"
        )).scalar()
        print(f"\nself-check: solvable problems still missing '## Example 2': {check}")
        too_few = db.execute(text(
            "SELECT count(*) FROM problems WHERE jsonb_array_length(test_cases) > 0 "
            "AND description LIKE '%## Example%' "
            "AND jsonb_array_length(test_cases) < 3"
        )).scalar()
        print(f"self-check: solvable problems with fewer than 3 total cases: {too_few}")


if __name__ == "__main__":
    main()