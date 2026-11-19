"""Inject function_starter + function_driver into seed files.

Usage:
    PYTHONPATH=. .venv/bin/python scripts/inject_function_modes.py <file_path> <slug1> <slug2> ...

Or without args to process all known Batch 1 problems across all files.
"""

from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# Problem specs: slug -> {lang: (starter, driver_prefix, driver_suffix)}
# ---------------------------------------------------------------------------
SPECS = {
    "valid-anagram": {
        "python": (
            'def solve(s: str, t: str) -> bool:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\nlines = sys.stdin.read().splitlines()\ns = lines[0] if lines else ""\nt = lines[1] if len(lines) > 1 else ""\n',
            'print("true" if solve(s, t) else "false")\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nbool solve(string s, string t) {\n    // ===== YOUR CODE HERE =====\n    return false;\n}',
            '',
            'int main() {\n    string s, t;\n    cin >> s >> t;\n    cout << (solve(s, t) ? "true" : "false") << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public boolean solve(String s, String t) {\n        // ===== YOUR CODE HERE =====\n        return false;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        String t = sc.next();\n        System.out.println(new Solution().solve(s, t) ? "true" : "false");\n    }\n}\n',
        ),
    },
    "valid-palindrome": {
        "python": (
            'def solve(s: str) -> bool:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ns = sys.stdin.readline().rstrip("\\n")\n',
            'print("true" if solve(s) else "false")\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nbool solve(string s) {\n    // ===== YOUR CODE HERE =====\n    return false;\n}',
            '',
            'int main() {\n    string s;\n    getline(cin, s);\n    cout << (solve(s) ? "true" : "false") << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public boolean solve(String s) {\n        // ===== YOUR CODE HERE =====\n        return false;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n        System.out.println(new Solution().solve(s) ? "true" : "false");\n    }\n}\n',
        ),
    },
    "contains-duplicate": {
        "python": (
            'def solve(nums: list[int]) -> bool:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ndata = sys.stdin.read().split()\nif not data:\n    sys.exit()\nn = int(data[0])\nnums = [int(x) for x in data[1:1 + n]]\n',
            'print("true" if solve(nums) else "false")\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nbool solve(vector<int>& nums) {\n    // ===== YOUR CODE HERE =====\n    return false;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n    cout << (solve(nums) ? "true" : "false") << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public boolean solve(int[] nums) {\n        // ===== YOUR CODE HERE =====\n        return false;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n        System.out.println(new Solution().solve(nums) ? "true" : "false");\n    }\n}\n',
        ),
    },
    "happy-number": {
        "python": (
            'def solve(n: int) -> bool:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\nn = int(sys.stdin.readline().strip())\n',
            'print("true" if solve(n) else "false")\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nbool solve(int n) {\n    // ===== YOUR CODE HERE =====\n    return false;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    cout << (solve(n) ? "true" : "false") << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public boolean solve(int n) {\n        // ===== YOUR CODE HERE =====\n        return false;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        System.out.println(new Solution().solve(n) ? "true" : "false");\n    }\n}\n',
        ),
    },
    "plus-one": {
        "python": (
            'def solve(digits: list[int]) -> list[int]:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ndata = sys.stdin.read().split()\nif not data:\n    sys.exit()\nn = int(data[0])\ndigits = [int(x) for x in data[1:1 + n]]\n',
            'print(" ".join(map(str, solve(digits))))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nvector<int> solve(vector<int>& digits) {\n    // ===== YOUR CODE HERE =====\n    return {};\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    vector<int> digits(n);\n    for (int i = 0; i < n; i++) cin >> digits[i];\n    vector<int> ans = solve(digits);\n    for (size_t i = 0; i < ans.size(); i++) {\n        if (i) cout << " ";\n        cout << ans[i];\n    }\n    cout << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int[] solve(int[] digits) {\n        # ===== YOUR CODE HERE =====\n        return new int[0];\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] digits = new int[n];\n        for (int i = 0; i < n; i++) digits[i] = sc.nextInt();\n        int[] ans = new Solution().solve(digits);\n        for (int i = 0; i < ans.length; i++) {\n            if (i > 0) System.out.print(" ");\n            System.out.print(ans[i]);\n        }\n        System.out.println();\n    }\n}\n',
        ),
    },
    "missing-number": {
        "python": (
            'def solve(nums: list[int]) -> int:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ndata = sys.stdin.read().split()\nif not data:\n    sys.exit()\nn = int(data[0])\nnums = [int(x) for x in data[1:1 + n]]\n',
            'print(solve(nums))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nint solve(vector<int>& nums) {\n    // ===== YOUR CODE HERE =====\n    return 0;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n    cout << solve(nums) << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int solve(int[] nums) {\n        // ===== YOUR CODE HERE =====\n        return 0;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n        System.out.println(new Solution().solve(nums));\n    }\n}\n',
        ),
    },
    "single-number": {
        "python": (
            'def solve(nums: list[int]) -> int:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ndata = sys.stdin.read().split()\nif not data:\n    sys.exit()\nn = int(data[0])\nnums = [int(x) for x in data[1:1 + n]]\n',
            'print(solve(nums))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nint solve(vector<int>& nums) {\n    // ===== YOUR CODE HERE =====\n    return 0;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n    cout << solve(nums) << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int solve(int[] nums) {\n        // ===== YOUR CODE HERE =====\n        return 0;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n        System.out.println(new Solution().solve(nums));\n    }\n}\n',
        ),
    },
    "reverse-integer": {
        "python": (
            'def solve(x: int) -> int:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\nx = int(sys.stdin.readline().strip())\n',
            'print(solve(x))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nint solve(int x) {\n    // ===== YOUR CODE HERE =====\n    return 0;\n}',
            '',
            'int main() {\n    int x;\n    if (!(cin >> x)) return 0;\n    cout << solve(x) << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int solve(int x) {\n        // ===== YOUR CODE HERE =====\n        return 0;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int x = sc.nextInt();\n        System.out.println(new Solution().solve(x));\n    }\n}\n',
        ),
    },
    "best-time-to-buy-and-sell-stock": {
        "python": (
            'def solve(prices: list[int]) -> int:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\ndata = sys.stdin.read().split()\nif not data:\n    sys.exit()\nn = int(data[0])\nprices = [int(x) for x in data[1:1 + n]]\n',
            'print(solve(prices))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nint solve(vector<int>& prices) {\n    // ===== YOUR CODE HERE =====\n    return 0;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    vector<int> prices(n);\n    for (int i = 0; i < n; i++) cin >> prices[i];\n    cout << solve(prices) << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int solve(int[] prices) {\n        // ===== YOUR CODE HERE =====\n        return 0;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] prices = new int[n];\n        for (int i = 0; i < n; i++) prices[i] = sc.nextInt();\n        System.out.println(new Solution().solve(prices));\n    }\n}\n',
        ),
    },
    "climbing-stairs": {
        "python": (
            'def solve(n: int) -> int:\n    # ===== YOUR CODE HERE =====\n    pass',
            'import sys\n\nn = int(sys.stdin.readline().strip())\n',
            'print(solve(n))\n',
        ),
        "cpp": (
            '#include <bits/stdc++.h>\nusing namespace std;\n\nint solve(int n) {\n    // ===== YOUR CODE HERE =====\n    return 0;\n}',
            '',
            'int main() {\n    int n;\n    if (!(cin >> n)) return 0;\n    cout << solve(n) << "\\n";\n    return 0;\n}\n',
        ),
        "java": (
            'import java.util.*;\n\nclass Solution {\n    public int solve(int n) {\n        // ===== YOUR CODE HERE =====\n        return 0;\n    }\n}',
            '',
            '\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        System.out.println(new Solution().solve(n));\n    }\n}\n',
        ),
    },
}


def _escape_for_py_string(s: str) -> str:
    """Escape a string for safe inclusion in a Python single-quoted literal."""
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")
    return f"'{s}'"


def _build_field_block(spec_entry: dict) -> str:
    """Build the function_starter + function_driver Python literal block."""
    parts = []
    parts.append("    'function_starter': {")
    langs = ["python", "cpp", "java"]
    for i, lang in enumerate(langs):
        starter, prefix, suffix = spec_entry[lang]
        trailing = "," if i < len(langs) - 1 else ""
        parts.append(f"        '{lang}': {_escape_for_py_string(starter)}{trailing}")
    parts.append("    },")
    parts.append("    'function_driver': {")
    for i, lang in enumerate(langs):
        starter, prefix, suffix = spec_entry[lang]
        trailing = "," if i < len(langs) - 1 else ""
        driver_entry = (
            f"        '{lang}': "
            "{"
            + f"'prefix': {_escape_for_py_string(prefix)}, "
            + f"'suffix': {_escape_for_py_string(suffix)}"
            + "}"
            + f"{trailing}"
        )
        parts.append(driver_entry)
    parts.append("    },")
    return "\n".join(parts)


def inject_into_file(file_path: Path, slugs_to_process: set[str]) -> int:
    """Inject function modes into the given seed file for the specified slugs."""
    raw = file_path.read_text(encoding="utf-8")
    injected_count = 0

    for slug in sorted(slugs_to_process):
        if slug not in SPECS:
            print(f"SKIP {slug}: no spec defined")
            continue

        spec_entry = SPECS[slug]

        # Try both slug marker formats
        markers = [f'"slug": "{slug}"', f'"slug": \'{slug}\'']
        idx = -1
        used_marker = None
        for m in markers:
            idx = raw.find(m)
            if idx >= 0:
                used_marker = m
                break

        if idx < 0:
            print(f"SKIP {slug}: not found in {file_path.name}")
            continue

        # Find entry start: the '{' before this slug
        entry_start = raw.rfind("{", 0, idx)
        if entry_start < 0:
            print(f"SKIP {slug}: could not find entry start in {file_path.name}")
            continue

        # Count braces from entry_start to find matching close brace
        depth = 0
        end = -1
        in_string = False
        string_char = None
        escape = False
        i = entry_start
        while i < len(raw):
            ch = raw[i]
            if escape:
                escape = False
            elif ch == "\\" and in_string:
                escape = True
            elif ch in ("'", '"') and not in_string:
                in_string = True
                string_char = ch
            elif ch == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            i += 1

        if end < 0:
            print(f"SKIP {slug}: could not find entry end in {file_path.name}")
            continue

        # Check if already injected
        entry_text = raw[entry_start : end + 1]
        if "'function_starter'" in entry_text:
            print(f"SKIP {slug}: already has function_starter in {file_path.name}")
            continue

        # Build injection text
        block = _build_field_block(spec_entry)

        # Insert the block before the closing '}' at position `end`
        raw = raw[:end] + "\n" + block + "\n" + raw[end:]
        injected_count += 1
        print(f"OK   {slug}: injected into {file_path.name}")

    if injected_count > 0:
        file_path.write_text(raw, encoding="utf-8")

    return injected_count


def main():
    # Determine which files to process based on arguments
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        slugs_to_process = set(sys.argv[2:])
    else:
        # Default: process all Batch 1 problems across all files
        file_path = Path("app/seeds/data_neetcode150.py")
        slugs_to_process = set(SPECS.keys())

    count = inject_into_file(file_path, slugs_to_process)
    print(f"\nInjected {count} problem(s) into {file_path}")


if __name__ == "__main__":
    main()
