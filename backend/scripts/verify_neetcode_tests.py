import sys
sys.path.insert(0, "/Users/dylanmascarenhas/Developer/dsa-platform/backend")
from app.seeds import PROBLEMS


def solve_contains_duplicate(inp):
    n, *rest = inp.split()
    n = int(n)
    nums = [int(x) for x in rest[:n]]
    return "true" if len(set(nums)) < len(nums) else "false"


def solve_top_k(inp):
    parts = inp.split()
    n, k = int(parts[0]), int(parts[1])
    nums = [int(x) for x in parts[2:2 + n]]
    from collections import Counter
    return " ".join(str(x) for x, _ in Counter(nums).most_common(k))


def solve_valid_sudoku(inp):
    rows = inp.split()
    rows = [list(r) for r in rows]
    for i in range(9):
        s = [c for c in rows[i] if c != "."]
        if len(s) != len(set(s)):
            return "false"
        col = [r[i] for r in rows if r[i] != "."]
        if len(col) != len(set(col)):
            return "false"
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            s = []
            for i in range(br, br + 3):
                for j in range(bc, bc + 3):
                    if rows[i][j] != ".":
                        s.append(rows[i][j])
            if len(s) != len(set(s)):
                return "false"
    return "true"


def solve_encode_decode(inp):
    lines = inp.split("\n")
    n = int(lines[0])
    return "\n".join(lines[1:1 + n])


def solve_lcs(inp):
    parts = inp.split()
    n = int(parts[0])
    nums = [int(x) for x in parts[1:n + 1]]
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            ln = 1
            while x + ln in s:
                ln += 1
            best = max(best, ln)
    return str(best)


SOLVERS = {
    "contains-duplicate": solve_contains_duplicate,
    "top-k-frequent-elements": solve_top_k,
    "valid-sudoku": solve_valid_sudoku,
    "encode-and-decode-strings": solve_encode_decode,
    "longest-consecutive-sequence": solve_lcs,
}

fails = 0
total = 0
for slug, solver in SOLVERS.items():
    entry = next(p for p in PROBLEMS if p["slug"] == slug and p.get("category"))
    for tc in entry["test_cases"]:
        total += 1
        got = solver(tc.input)
        want = tc.expected_output
        if got != want:
            fails += 1
            print(f"[FAIL] {slug}: got={got!r} want={want!r}")
print(f"Arrays & Hashing tests checked: {total}, fails={fails}")
sys.exit(1 if fails else 0)
