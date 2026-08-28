"""Fully-authored content for catalog-only NeetCode 150 problems.

Each entry maps a problem slug to the fields the seed should apply on top of the
catalog row: a markdown `description`, a `starter_code` scaffold (python / cpp /
java — each a full stdin/stdout program with a `YOUR CODE HERE` marker), and a
set of serialized `test_cases`.

This module is enriched into the catalog in `data_neetcode150.py` at import time,
so `PROBLEMS` (used by both `scripts/seed.py` and `scripts/check_starters.py`)
sees the fully-authored content. Only slugs that are NOT already fully-authored
elsewhere are authored here; already-authored problems are preserved untouched.
"""

from app.seeds.schema import TestCase

NEETCODE_AUTHORING: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Arrays & Hashing
# ---------------------------------------------------------------------------
NEETCODE_AUTHORING["contains-duplicate"] = {
    "description": (
        '# Contains Duplicate\n\n'
        '## Statement\n'
        'Given an integer array `nums`, return `true` if any value appears **at least twice**\n'
        'in the array, and return `false` if every element is distinct.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n` — the number of elements\n'
        '- Line 2: `n` space-separated integers — the array `nums`\n\n'
        '## Output Format\n'
        'A single line: `true` if `nums` contains a duplicate, otherwise `false`.\n\n'
        '## Constraints\n'
        '- `1 <= n <= 10^5`\n'
        '- `-10^9 <= nums[i] <= 10^9`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n'
        '4\n'
        '1 2 3 1\n'
        '```\n'
        '**Output**\n'
        '```\n'
        'true\n'
        '```\n'
        'Explanation: `1` appears twice in the array.'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    n = int(data[0])\n'
            '    nums = [int(x) for x in data[1:n + 1]]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    int n;\n'
            '    cin >> n;\n'
            '    vector<int> nums(n);\n'
            '    for (auto& x : nums) cin >> x;\n\n'
            '    // ===== YOUR CODE HERE =====\n\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        int n = sc.nextInt();\n'
            '        int[] nums = new int[n];\n'
            '        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="4\n1 2 3 1\n", expected_output="true", is_hidden=False),
        TestCase(input="4\n1 2 3 4\n", expected_output="false", is_hidden=False),
        TestCase(input="10\n1 1 1 3 3 4 3 2 4 2\n", expected_output="true", is_hidden=False),
        TestCase(input="5\n1 2 3 4 5\n", expected_output="false", is_hidden=True),
        TestCase(input="2\n10 10\n", expected_output="true", is_hidden=True),
    ],
}

NEETCODE_AUTHORING["top-k-frequent-elements"] = {
    "description": (
        '# Top K Frequent Elements\n\n'
        '## Statement\n'
        'Given an integer array `nums` and an integer `k`, return the `k` most frequent\n'
        'elements. The answer is unique.\n\n'
        '## Input Format\n'
        '- Line 1: integers `n k`\n'
        '- Line 2: `n` space-separated integers — the array `nums`\n\n'
        '## Output Format\n'
        'The `k` most frequent elements as space-separated integers (order does not matter).\n\n'
        '## Constraints\n'
        '- `1 <= n <= 10^5`\n'
        '- `1 <= k <= n`\n'
        '- `-10^4 <= nums[i] <= 10^4`\n'
        '- The answer is guaranteed unique.\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n'
        '6 2\n'
        '1 1 1 2 2 3\n'
        '```\n'
        '**Output**\n'
        '```\n'
        '1 2\n'
        '```\n'
        'Explanation: `1` appears three times, `2` appears twice, `3` once.\n'
        'The two most frequent are `1` and `2`.'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    n = int(data[0])\n'
            '    k = int(data[1])\n'
            '    nums = [int(x) for x in data[2:2 + n]]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    int n, k;\n'
            '    cin >> n >> k;\n'
            '    vector<int> nums(n);\n'
            '    for (auto& x : nums) cin >> x;\n\n'
            '    // ===== YOUR CODE HERE =====\n\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        int n = sc.nextInt();\n'
            '        int k = sc.nextInt();\n'
            '        int[] nums = new int[n];\n'
            '        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="6 2\n1 1 1 2 2 3\n", expected_output="1 2", is_hidden=False),
        TestCase(input="1 1\n1\n", expected_output="1", is_hidden=False),
        TestCase(input="2 1\n4 4\n", expected_output="4", is_hidden=True),
        TestCase(input="8 3\n1 2 2 3 3 3 4 4\n", expected_output="3 2 4", is_hidden=True),
    ],
}

NEETCODE_AUTHORING["valid-sudoku"] = {
    "description": (
        '# Valid Sudoku\n\n'
        '## Statement\n'
        'Determine if a `9 x 9` Sudoku board is valid. Only the filled cells need to be\n'
        'validated **according to the following rules**:\n'
        '1. Each row must contain the digits `1-9` without repetition.\n'
        '2. Each column must contain the digits `1-9` without repetition.\n'
        '3. Each of the nine `3 x 3` sub-boxes must contain the digits `1-9` without repetition.\n\n'
        '## Input Format\n'
        '- `9` lines, each containing 9 characters (`.` for empty, `1-9` for digits), no spaces.\n\n'
        '## Output Format\n'
        'A single line: `true` if the board is valid, otherwise `false`.\n\n'
        '## Constraints\n'
        '- `board.length == 9`, `board[i].length == 9`\n'
        '- Each cell holds `"."` or a digit from `1` to `9`.\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n'
        '53..7....\n'
        '6..195...\n'
        '.98....6.\n'
        '8...6...3\n'
        '4..8.3..1\n'
        '7...2...6\n'
        '.6....28.\n'
        '...419..5\n'
        '....8..79\n'
        '```\n'
        '**Output**\n'
        '```\n'
        'true\n'
        '```'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    board = sys.stdin.read().split()\n'
            '    board = [list(row.rstrip()) for row in board]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    vector<string> board(9);\n'
            '    for (auto& row : board) cin >> row;\n\n'
            '    // ===== YOUR CODE HERE =====\n\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        String[] board = new String[9];\n'
            '        for (int i = 0; i < 9; i++) board[i] = sc.next();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(
            input=(
                '53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n'
                '7...2...6\n.6....28.\n...419..5\n....8..79\n'
            ),
            expected_output="true",
            is_hidden=False,
        ),
        TestCase(
            input=(
                '83..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n'
                '7...2...6\n.6....28.\n...419..5\n....8..79\n'
            ),
            expected_output="false",
            is_hidden=False,
        ),
        TestCase(
            input=(
                '.23456789\n4567.9123\n78912345.\n23.567891\n567891.34\n'
                '8.1234567\n34567.912\n.78912345\n912.45678\n'
            ),
            expected_output="true",
            is_hidden=True,
        ),
    ],
}

NEETCODE_AUTHORING["encode-and-decode-strings"] = {
    "description": (
        '# Encode and Decode Strings\n\n'
        '## Statement\n'
        'Design an algorithm to encode a list of strings to a single string. The encoded\n'
        'string is then decoded back to the original list of strings. Implement an **encoder**\n'
        'and a **decoder** that round-trip correctly.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n` — the number of strings\n'
        '- Next `n` lines: each string (may contain any characters)\n\n'
        '## Output Format\n'
        '`n` lines — the decoded strings, one per line, in the original order. Print an empty\n'
        'line for each empty string.\n\n'
        '## Constraints\n'
        '- `0 <= n <= 200`\n'
        '- `0 <= length(str) <= 200`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n'
        '3\n'
        'hello\n'
        'world\n'
        'foo#bar\n'
        '```\n'
        '**Output**\n'
        '```\n'
        'hello\n'
        'world\n'
        'foo#bar\n'
        '```'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def encode(strings):\n'
            '    # ===== YOUR CODE HERE =====\n'
            '    pass\n\n\n'
            'def decode(encoded):\n'
            '    # ===== YOUR CODE HERE =====\n'
            '    pass\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read()\n'
            '    lines = data.split("\\n")\n'
            '    n = int(lines[0])\n'
            '    strings = lines[1:1 + n]\n'
            '    result = decode(encode(strings))\n'
            '    sys.stdout.write("\\n".join(result))\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'string encode(const vector<string>& strs) {\n'
            '    // ===== YOUR CODE HERE =====\n'
            '    return "";\n'
            '}\n\n'
            'vector<string> decode(const string& s) {\n'
            '    // ===== YOUR CODE HERE =====\n'
            '    return {};\n'
            '}\n\n'
            'int main() {\n'
            '    int n;\n'
            '    cin >> n;\n'
            '    cin.ignore();\n'
            '    vector<string> strs(n);\n'
            '    for (auto& s : strs) getline(cin, s);\n'
            '    auto res = decode(encode(strs));\n'
            '    for (size_t i = 0; i < res.size(); i++) {\n'
            '        if (i) cout << "\\n";\n'
            '        cout << res[i];\n'
            '    }\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static String encode(List<String> strs) {\n'
            '        // ===== YOUR CODE HERE =====\n'
            '        return "";\n'
            '    }\n\n'
            '    public static List<String> decode(String s) {\n'
            '        // ===== YOUR CODE HERE =====\n'
            '        return new ArrayList<>();\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        int n = sc.nextInt();\n'
            '        sc.nextLine();\n'
            '        List<String> strs = new ArrayList<>();\n'
            '        for (int i = 0; i < n; i++) strs.add(sc.nextLine());\n'
            '        List<String> res = decode(encode(strs));\n'
            '        for (int i = 0; i < res.size(); i++) {\n'
            '            if (i > 0) System.out.println();\n'
            '            System.out.print(res.get(i));\n'
            '        }\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="3\nhello\nworld\nfoo#bar\n", expected_output="hello\nworld\nfoo#bar", is_hidden=False),
        TestCase(input="2\n\nabc\n", expected_output="\nabc", is_hidden=True),
        TestCase(input="3\nleet\ncode\nlove\n", expected_output="leet\ncode\nlove", is_hidden=False),
    ],
}

NEETCODE_AUTHORING["longest-consecutive-sequence"] = {
    "description": (
        '# Longest Consecutive Sequence\n\n'
        '## Statement\n'
        'Given an unsorted array of integers `nums`, return the length of the longest\n'
        'consecutive elements sequence. The algorithm must run in `O(n)` time.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n` — the number of elements\n'
        '- Line 2: `n` space-separated integers — the array `nums`\n\n'
        '## Output Format\n'
        'A single integer — the length of the longest consecutive sequence.\n\n'
        '## Constraints\n'
        '- `0 <= n <= 10^5`\n'
        '- `-10^9 <= nums[i] <= 10^9`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n'
        '6\n'
        '100 4 200 1 3 2\n'
        '```\n'
        '**Output**\n'
        '```\n'
        '4\n'
        '```\n'
        'Explanation: The longest consecutive sequence is `1, 2, 3, 4` of length 4.'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    n = int(data[0])\n'
            '    nums = [int(x) for x in data[1:n + 1]]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    int n;\n'
            '    cin >> n;\n'
            '    vector<int> nums(n);\n'
            '    for (auto& x : nums) cin >> x;\n\n'
            '    // ===== YOUR CODE HERE =====\n\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        int n = sc.nextInt();\n'
            '        int[] nums = new int[n];\n'
            '        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="6\n100 4 200 1 3 2\n", expected_output="4", is_hidden=False),
        TestCase(input="2\n0 3\n", expected_output="1", is_hidden=False),
        TestCase(input="2\n1 2\n", expected_output="2", is_hidden=False),
        TestCase(input="5\n9 1 4 7 3\n", expected_output="2", is_hidden=True),
        TestCase(input="8\n1 2 0 1 3 4 5 6\n", expected_output="7", is_hidden=True),
    ],
}
