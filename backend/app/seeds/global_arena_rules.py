"""Global arena rules: exactly three visible test cases and exactly two examples.

For every solvable problem (has test cases and a statement example) the rules
guarantee that:
- hidden test cases are promoted until exactly RUN_VISIBLE_CASE_LIMIT (3) are
  visible;
- the single "## Example" section is rewritten into "## Example 1" + "## Example
  2", each with Input/Output/Explanation (Example 2 is taken from the second
  visible case, explanations come from global_arena_explanations.py; an existing
  explanation for Example 1 is preserved);
- a hand-authored third case is appended to valid-sudoku, the only problem with
  fewer than three total cases.

These functions are pure (they never touch the database) and are shared by
scripts/seed.py (applied during every seed) and scripts/normalize_global_arena_rules.py
(applied to an existing database).
"""

import re

from app.seeds.global_arena_explanations import EXPLANATIONS

RUN_VISIBLE_CASE_LIMIT = 3

VALID_SUDOKU_EXTRA_CASE = {
    "input": "55..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n",
    "expected_output": "false",
    "is_hidden": False,
}


def fence(text: str) -> str:
    return "```\n" + text.rstrip("\n") + "\n```"


def key(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def parse_example_block(block: str) -> dict:
    m = re.search(
        r"\*\*Input\*\*[ \t]*\n```\n(?P<inp>.*?)\n```\s*\n\*\*Output\*\*\s*\n```\n(?P<out>.*?)\n```(?P<rest>.*)$",
        block,
        re.DOTALL,
    )
    if not m:
        raise ValueError("could not parse example block")
    rest = m.group("rest")
    cut = rest.find("\n## Example ")
    if cut != -1:
        rest = rest[:cut]
    rest = rest.strip()
    explanation = None
    if rest.startswith("Explanation:"):
        explanation = rest[len("Explanation:"):].strip()
    elif rest:
        raise ValueError("unexpected trailing example content: " + rest[:60])
    return {"input": m.group("inp"), "output": m.group("out"), "explanation": explanation}


def build_description(prefix, ex1, ex2) -> str:
    blocks = []
    for label, item in (("1", ex1), ("2", ex2)):
        blocks.append(
            "## Example %s\n\n**Input**\n%s\n**Output**\n%s\n\nExplanation: %s"
            % (label, fence(item["input"]), fence(item["output"]), item["explanation"])
        )
    return prefix.rstrip("\n") + "\n\n" + "\n\n".join(blocks) + "\n"


def promote_cases(test_cases: list) -> list:
    cases = [dict(tc) for tc in test_cases]
    hidden = [tc for tc in cases if tc["is_hidden"]]
    visible = [tc for tc in cases if not tc["is_hidden"]]
    needed = RUN_VISIBLE_CASE_LIMIT - len(visible)
    for tc in hidden[: max(needed, 0)]:
        tc["is_hidden"] = False
    return visible + hidden


def normalize_problem(slug: str, description: str, test_cases: list, warnings: list) -> tuple:
    if slug not in EXPLANATIONS:
        warnings.append(f"{slug}: no authored explanations, skipping rewrite")
        return description, promote_cases(test_cases), False

    pos = description.find("## Example")
    prefix = description[:pos]
    parsed = parse_example_block(description[pos:])

    visible = [tc for tc in test_cases if not tc["is_hidden"]]
    if len(visible) < 2:
        warnings.append(f"{slug}: fewer than two visible cases, cannot build two examples")
        return description, promote_cases(test_cases), False

    ex1_matches = key(parsed["input"]) == key(visible[0]["input"])
    if not ex1_matches:
        warnings.append(
            f"{slug}: statement example differs from first visible case; rebuilt from the test case"
        )
    explanation = (
        parsed["explanation"]
        if ex1_matches and parsed["explanation"]
        else EXPLANATIONS[slug].get("ex1") or ""
    )
    ex1 = {
        "input": visible[0]["input"],
        "output": visible[0]["expected_output"],
        "explanation": explanation,
    }
    ex2 = {
        "input": visible[1]["input"],
        "output": visible[1]["expected_output"],
        "explanation": EXPLANATIONS[slug].get("ex2", ""),
    }

    new_cases = promote_cases(test_cases)
    if len(new_cases) < RUN_VISIBLE_CASE_LIMIT:
        if slug == "valid-sudoku":
            new_cases.append(dict(VALID_SUDOKU_EXTRA_CASE))
        else:
            warnings.append(f"{slug}: only {len(new_cases)} total cases and no authored extra case")

    new_desc = build_description(prefix, ex1, ex2)
    return new_desc, new_cases, (new_desc != description or new_cases != test_cases)