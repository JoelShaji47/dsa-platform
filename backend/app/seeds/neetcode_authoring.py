"""Fully-authored content for catalog-only NeetCode 150 problems."""

from app.seeds.schema import TestCase

NEETCODE_AUTHORING: dict[str, dict] = {}

NEETCODE_AUTHORING["contains-duplicate"] = {
    "description": (
        '# Contains Duplicate\n\n'
        '## Statement\n'
        'Given an integer array `nums`, return `true` if any value appears **at least twice**\n'
        'in the array, and return `false` if every element is distinct.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n` \u2014 the number of elements\n'
        '- Line 2: `n` space-separated integers \u2014 the array `nums`\n\n'
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

NEETCODE_AUTHORING["valid-anagram"] = {
    "description": (
        '# Valid Anagram\n\n'
        '## Statement\n'
        'Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`,\n'
        'and `false` otherwise.\n\n'
        '## Input Format\n'
        '- Line 1: string `s`\n'
        '- Line 2: string `t`\n\n'
        '## Output Format\n'
        '`true` if anagram, `false` otherwise.\n\n'
        '## Constraints\n'
        '- `1 <= s.length, t.length <= 5 * 10^4`\n'
        '- `s` and `t` consist of lowercase English letters.\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\nanagram\nratman\n```\n'
        '**Output**\n'
        '```\ntrue\n```'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    s = data[0]\n'
            '    t = data[1]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    string s, t;\n'
            '    cin >> s >> t;\n\n'
            '    // ===== YOUR CODE HERE =====\n\n'
            '    return 0;\n'
            '}\n'
        ),
        "java": (
            'import java.util.*;\n\n'
            'public class Main {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        String s = sc.next();\n'
            '        String t = sc.next();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="anagram\nratman\n", expected_output="true", is_hidden=False),
        TestCase(input="car\nrat\n", expected_output="false", is_hidden=False),
        TestCase(input="a\na\n", expected_output="true", is_hidden=False),
        TestCase(input="ab\na\n", expected_output="false", is_hidden=True),
    ],
}

NEETCODE_AUTHORING["two-sum"] = {
    "description": (
        '# Two Sum\n\n'
        '## Statement\n'
        'Given an array of integers `nums` and an integer `target`, return the indices\n'
        'of the two numbers such that they add up to `target`. You may assume that each\n'
        'input would have **exactly one solution**. Return 0-indexed indices.\n\n'
        '## Input Format\n'
        '- Line 1: integers `n target`\n'
        '- Line 2: `n` space-separated integers\n\n'
        '## Output Format\n'
        'Two space-separated integers (0-indexed).\n\n'
        '## Constraints\n'
        '- `2 <= n <= 10^4`\n'
        '- `-10^9 <= nums[i] <= 10^9`\n'
        '- Exactly one valid answer exists.\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n4 9\n2 7 11 15\n```\n'
        '**Output**\n'
        '```\n0 1\n```\n'
        'Explanation: nums[0] + nums[1] = 2 + 7 = 9.'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    n = int(data[0])\n'
            '    target = int(data[1])\n'
            '    nums = [int(x) for x in data[2:2 + n]]\n\n'
            '    # ===== YOUR CODE HERE =====\n\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ),
        "cpp": (
            '#include <bits/stdc++.h>\n'
            'using namespace std;\n\n'
            'int main() {\n'
            '    int n, target;\n'
            '    cin >> n >> target;\n'
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
            '        int target = sc.nextInt();\n'
            '        int[] nums = new int[n];\n'
            '        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="4 9\n2 7 11 15\n", expected_output="0 1", is_hidden=False),
        TestCase(input="3 6\n3 2 4\n", expected_output="1 2", is_hidden=False),
        TestCase(input="2 6\n3 3\n", expected_output="0 1", is_hidden=False),
        TestCase(input="4 0\n1 -1 2 -2\n", expected_output="0 1", is_hidden=True),
    ],
}

NEETCODE_AUTHORING["group-anagrams"] = {
    "description": (
        '# Group Anagrams\n\n'
        '## Statement\n'
        'Given an array of strings `strs`, group the anagrams together.\n'
        'Return the groups in any order.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n`\n'
        '- Next `n` lines: one string per line\n\n'
        '## Output Format\n'
        'Each group on its own line, with words space-separated. Groups sorted by first word.\n\n'
        '## Constraints\n'
        '- `1 <= n <= 10^4`\n'
        '- `0 <= strs[i].length <= 100`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n6\neat\ntea\ntan\nate\nbat\nnat\n```\n'
        '**Output**\n'
        '```\nbat\nate eat tea\nnat tan\n```'
    ),
    "starter_code": {
        "python": (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split("\n")\n'
            '    n = int(data[0])\n'
            '    strs = data[1:1 + n]\n\n'
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
            '    vector<string> strs(n);\n'
            '    for (auto& s : strs) cin >> s;\n\n'
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
            '        String[] strs = new String[n];\n'
            '        for (int i = 0; i < n; i++) strs[i] = sc.next();\n\n'
            '        // ===== YOUR CODE HERE =====\n'
            '    }\n'
            '}\n'
        ),
    },
    "test_cases": [
        TestCase(input="6\nate\neat\ntea\ntan\nbat\nnat\n", expected_output="ate eat tea\ntan nat\nbat", is_hidden=False),
        TestCase(input="1\na\n", expected_output="a", is_hidden=False),
        TestCase(input="2\na\nb\n", expected_output="a\nb", is_hidden=True),
    ],
}

NEETCODE_AUTHORING["product-of-array-except-self"] = {
    "description": (
        '# Product of Array Except Self\n\n'
        '## Statement\n'
        'Given an integer array `nums`, return an array `answer` such that `answer[i]`\n'
        'is the product of all elements of `nums` except `nums[i]`. You must solve it\n'
        'without using division and in `O(n)` time.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n`\n'
        '- Line 2: `n` space-separated integers\n\n'
        '## Output Format\n'
        'Space-separated integers.\n\n'
        '## Constraints\n'
        '- `2 <= n <= 10^5`\n'
        '- `-30 <= nums[i] <= 30`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n4\n1 2 3 4\n```\n'
        '**Output**\n'
        '```\n24 12 8 6\n```'
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
        TestCase(input="4\n1 2 3 4\n", expected_output="24 12 8 6", is_hidden=False),
        TestCase(input="3\n-1 1 0\n", expected_output="0 0 -1", is_hidden=False),
        TestCase(input="2\n2 3\n", expected_output="3 2", is_hidden=True),
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
        '- Line 2: `n` space-separated integers\n\n'
        '## Output Format\n'
        'The `k` most frequent elements as space-separated integers.\n\n'
        '## Constraints\n'
        '- `1 <= n <= 10^5`\n'
        '- `1 <= k <= n`\n'
        '- `-10^4 <= nums[i] <= 10^4`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n6 2\n1 1 1 2 2 3\n```\n'
        '**Output**\n'
        '```\n1 2\n```'
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
        'Determine if a `9 x 9` Sudoku board is valid.\n\n'
        '## Input Format\n'
        '- `9` lines, each 9 characters (`.` or `1-9`).\n\n'
        '## Output Format\n'
        '`true` or `false`.\n\n'
        '## Constraints\n'
        '- `board.length == 9`, `board[i].length == 9`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n```\n'
        '**Output**\n'
        '```\ntrue\n```'
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
        TestCase(input="53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n", expected_output="true", is_hidden=False),
        TestCase(input="83..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n", expected_output="false", is_hidden=False),
    ],
}

NEETCODE_AUTHORING["encode-and-decode-strings"] = {
    "description": (
        '# Encode and Decode Strings\n\n'
        '## Statement\n'
        'Design an algorithm to encode a list of strings to a single string and decode it back.\n\n'
        '## Input Format\n'
        '- Line 1: integer `n`\n'
        '- Next `n` lines: one string per line\n\n'
        '## Output Format\n'
        '`n` lines \u2014 the decoded strings.\n\n'
        '## Constraints\n'
        '- `0 <= n <= 200`\n'
        '- `0 <= length(str) <= 200`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n3\nhello\nworld\nfoo#bar\n```\n'
        '**Output**\n'
        '```\nhello\nworld\nfoo#bar\n```'
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
        '- Line 1: integer `n`\n'
        '- Line 2: `n` space-separated integers\n\n'
        '## Output Format\n'
        'A single integer.\n\n'
        '## Constraints\n'
        '- `0 <= n <= 10^5`\n'
        '- `-10^9 <= nums[i] <= 10^9`\n\n'
        '## Example\n\n'
        '**Input**\n'
        '```\n6\n100 4 200 1 3 2\n```\n'
        '**Output**\n'
        '```\n4\n```'
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


# ===========================================================================
# Arrays & Hashing
# ===========================================================================

# ===========================================================================
# Two Pointers
# ===========================================================================

NEETCODE_AUTHORING['3sum'] = {
    "description": '# 3Sum\n\n## Statement\nGiven an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]`\nsuch that `i != j`, `i != k`, `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\nNotice that the solution set must not contain duplicate triplets.\n\n## Input Format\n- Line 1: integer `n` — the number of elements\n- Line 2: `n` space-separated integers — the array `nums`\n\n## Output Format\nEach triplet on its own line, with values sorted and separated by spaces.\nTriplets themselves should be sorted lexicographically. If no triplets exist, output nothing.\n\n## Constraints\n- `3 <= n <= 3000`\n- `-10^5 <= nums[i] <= 10^5`\n\n## Example\n\n**Input**\n```\n6\n-1 0 1 2 -1 -4\n```\n**Output**\n```\n-1 -1 2\n-1 0 1\n```\nExplanation: The triplets that sum to zero are [-1, -1, 2] and [-1, 0, 1].',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(x) for x in data[1:n + 1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (auto& x : nums) cin >> x;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6\n-1 0 1 2 -1 -4\n', expected_output='-1 -1 2\n-1 0 1', is_hidden=False),
        TestCase(input='3\n0 0 0\n', expected_output='0 0 0', is_hidden=False),
        TestCase(input='3\n1 2 3\n', expected_output='', is_hidden=True),
        TestCase(input='5\n-2 -1 0 1 2\n', expected_output='-2 0 2\n-1 0 1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['container-with-most-water'] = {
    "description": '# Container With Most Water\n\n## Statement\nYou are given an integer array `height` of length `n`. There are `n` vertical lines\ndrawn at positions `(i, 0)` to `(i, height[i])`. Find two lines that together with\nthe x-axis form a container that holds the most water.\n\nReturn the maximum area of water the container can store.\n\n## Input Format\n- Line 1: integer `n` — the number of elements\n- Line 2: `n` space-separated integers — the array `height`\n\n## Output Format\nA single integer — the maximum area.\n\n## Constraints\n- `2 <= n <= 10^5`\n- `1 <= height[i] <= 10^4`\n\n## Example\n\n**Input**\n```\n9\n1 8 6 2 5 4 8 3 7\n```\n**Output**\n```\n49\n```\nExplanation: The maximum area is achieved by selecting lines at indices 1 and 8\n(heights 8 and 7). Area = min(8, 7) * (8 - 1) = 7 * 7 = 49.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    height = [int(x) for x in data[1:n + 1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> height(n);\n    for (auto& x : height) cin >> x;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] height = new int[n];\n        for (int i = 0; i < n; i++) height[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='9\n1 8 6 2 5 4 8 3 7\n', expected_output='49', is_hidden=False),
        TestCase(input='2\n1 1\n', expected_output='1', is_hidden=False),
        TestCase(input='3\n1 2 1\n', expected_output='2', is_hidden=True),
        TestCase(input='4\n4 3 2 1 4\n', expected_output='16', is_hidden=True),
        TestCase(input='5\n1 2 1 3 2\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['trapping-rain-water'] = {
    "description": '# Trapping Rain Water\n\n## Statement\nGiven `n` non-negative integers representing an elevation map where the width of each\nbar is `1`, compute how much water it can trap after raining.\n\n## Input Format\n- Line 1: integer `n` — the number of elements\n- Line 2: `n` space-separated integers — the array `height`\n\n## Output Format\nA single integer — the total units of water trapped.\n\n## Constraints\n- `1 <= n <= 2 * 10^4`\n- `0 <= height[i] <= 10^5`\n\n## Example\n\n**Input**\n```\n12\n0 1 0 2 1 0 1 3 2 1 2 1\n```\n**Output**\n```\n6\n```\nExplanation: The elevation map traps 6 units of rain water (visualized as water\nstored between the bars).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    height = [int(x) for x in data[1:n + 1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> height(n);\n    for (auto& x : height) cin >> x;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] height = new int[n];\n        for (int i = 0; i < n; i++) height[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='12\n0 1 0 2 1 0 1 3 2 1 2 1\n', expected_output='6', is_hidden=False),
        TestCase(input='6\n4 2 0 3 2 5\n', expected_output='9', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='0', is_hidden=True),
        TestCase(input='3\n1 0 1\n', expected_output='1', is_hidden=True),
        TestCase(input='2\n1 2\n', expected_output='0', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['two-sum-ii-input-array-is-sorted'] = {
    "description": '# Two Sum II - Input Array Is Sorted\n\n## Statement\nGiven a 1-indexed sorted array of integers `numbers` and an integer `target`, return\nthe indices of the two numbers such that they add up to `target`.\n\nYou may assume that the input has exactly one solution, and you may not use the same\nelement twice. The answer should be returned as two space-separated 1-indexed integers.\n\n## Input Format\n- Line 1: integers `n target`\n- Line 2: `n` space-separated integers — the sorted array\n\n## Output Format\nTwo space-separated integers: the 1-indexed positions of the two numbers.\n\n## Constraints\n- `2 <= n <= 3 * 10^4`\n- `-1000 <= numbers[i] <= 1000`\n- `numbers` is sorted in non-decreasing order.\n- Exactly one solution exists.\n\n## Example\n\n**Input**\n```\n4 9\n2 7 11 15\n```\n**Output**\n```\n1 2\n```\nExplanation: `numbers[1] + numbers[2] = 2 + 7 = 9`.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, target = int(data[0]), int(data[1])\n    numbers = [int(x) for x in data[2:2 + n]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, target;\n    cin >> n >> target;\n    vector<int> numbers(n);\n    for (auto& x : numbers) cin >> x;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), target = sc.nextInt();\n        int[] numbers = new int[n];\n        for (int i = 0; i < n; i++) numbers[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 9\n2 7 11 15\n', expected_output='1 2', is_hidden=False),
        TestCase(input='2 6\n3 3\n', expected_output='1 2', is_hidden=False),
        TestCase(input='5 10\n1 3 5 7 9\n', expected_output='1 4', is_hidden=True),
        TestCase(input='3 -1\n-3 0 3\n', expected_output='1 3', is_hidden=True),
        TestCase(input='4 6\n1 2 3 4\n', expected_output='1 4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['valid-palindrome'] = {
    "description": '# Valid Palindrome\n\n## Statement\nA phrase is a palindrome if, after converting all uppercase letters into lowercase\nletters and removing all non-alphanumeric characters, it reads the same forward and\nbackward. Alphanumeric characters include letters and numbers.\n\nGiven a string `s`, return `true` if it is a palindrome, or `false` otherwise.\n\n## Input Format\n- Line 1: a string `s`\n\n## Output Format\nA single line: `true` if `s` is a palindrome, otherwise `false`.\n\n## Constraints\n- `1 <= s.length <= 2 * 10^5`\n- `s` consists only of printable ASCII characters.\n\n## Example\n\n**Input**\n```\nA man, a plan, a canal: Panama\n```\n**Output**\n```\ntrue\n```\nExplanation: After removing non-alphanumeric characters and converting to\nlowercase, the string becomes "amanaplanacanalpanama", which is a palindrome.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    s = sys.stdin.readline().rstrip("\\n")\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    getline(cin, s);\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='A man, a plan, a canal: Panama\n', expected_output='true', is_hidden=False),
        TestCase(input='race a car\n', expected_output='false', is_hidden=False),
        TestCase(input=' \n', expected_output='true', is_hidden=True),
        TestCase(input='0P\n', expected_output='false', is_hidden=True),
    ],
}

# ===========================================================================
# Sliding Window
# ===========================================================================

NEETCODE_AUTHORING['best-time-to-buy-and-sell-stock'] = {
    "description": '# Best Time to Buy and Sell Stock\n\n## Statement\n\nYou are given an array `prices` where `prices[i]` is the price of a given stock on the `i`th day.\n\nYou want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.\n\nReturn the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return `0`.\n\n## Input Format\n\n- The first line contains an integer `n` (1 <= n <= 10^5), the number of days.\n- The second line contains `n` space-separated integers representing the prices.\n\n## Output Format\n\n- A single integer representing the maximum profit.\n\n## Constraints\n\n- 1 <= n <= 10^5\n- 0 <= prices[i] <= 10^4\n\n## Example\n\n**Input**\n```\n6\n7 1 5 3 6 4\n```\n**Output**\n```\n5\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    prices = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> prices(n);\n    for (int i = 0; i < n; i++) cin >> prices[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] prices = new int[n];\n        for (int i = 0; i < n; i++) prices[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6\n7 1 5 3 6 4\n', expected_output='5', is_hidden=False),
        TestCase(input='5\n7 6 4 3 1\n', expected_output='0', is_hidden=False),
        TestCase(input='1\n5\n', expected_output='0', is_hidden=True),
        TestCase(input='2\n1 5\n', expected_output='4', is_hidden=True),
        TestCase(input='8\n2 4 1 7 5 3 6 8\n', expected_output='7', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-repeating-character-replacement'] = {
    "description": '# Longest Repeating Character Replacement\n\n## Statement\n\nYou are given a string `s` consisting of uppercase English letters and an integer `k`.\n\nYou are allowed to choose at most `k` characters from the string and replace them with any other uppercase English character.\n\nReturn the length of the longest substring containing the same letter you can achieve after performing at most `k` replacements.\n\n## Input Format\n\n- The first line contains the string `s`.\n- The second line contains an integer `k`.\n\n## Output Format\n\n- A single integer representing the maximum length.\n\n## Constraints\n\n- 1 <= s.length <= 10^5\n- `s` consists of uppercase English letters only.\n- 0 <= k <= s.length\n\n## Example\n\n**Input**\n```\nAABABBA\n1\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0]\n    k = int(data[1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    int k;\n    cin >> s >> k;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        int k = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='AABABBA\n1\n', expected_output='4', is_hidden=False),
        TestCase(input='ABAB\n2\n', expected_output='4', is_hidden=False),
        TestCase(input='AAAA\n0\n', expected_output='4', is_hidden=True),
        TestCase(input='ABAA\n0\n', expected_output='2', is_hidden=True),
        TestCase(input='ABBB\n1\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-substring-without-repeating-characters'] = {
    "description": '# Longest Substring Without Repeating Characters\n\n## Statement\n\nGiven a string `s`, find the length of the longest substring without repeating characters.\n\n## Input Format\n\n- A single line containing the string `s`.\n\n## Output Format\n\n- A single integer representing the length of the longest substring.\n\n## Constraints\n\n- 0 <= s.length <= 5 * 10^4\n- `s` consists of English letters, digits, symbols, and spaces.\n\n## Example\n\n**Input**\n```\nabcabcbb\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0] if data else ""\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    getline(cin, s);\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='abcabcbb\n', expected_output='3', is_hidden=False),
        TestCase(input='bbbbb\n', expected_output='1', is_hidden=False),
        TestCase(input='pwwkew\n', expected_output='3', is_hidden=True),
        TestCase(input='\n', expected_output='0', is_hidden=True),
        TestCase(input='dvdf\n', expected_output='3', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['minimum-window-substring'] = {
    "description": '# Minimum Window Substring\n\n## Statement\n\nGiven two strings `s` and `t` of lengths `m` and `n` respectively, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window.\n\nIf there is no such substring, return an empty string `""`.\n\n## Input Format\n\n- The first line contains the string `s`.\n- The second line contains the string `t`.\n\n## Output Format\n\n- The minimum window substring, or empty if none exists.\n\n## Constraints\n\n- m == s.length\n- n == t.length\n- 1 <= m, n <= 10^5\n- `s` and `t` consist of uppercase and lowercase English letters.\n\n## Example\n\n**Input**\n```\nADOBECODEBANC\nABC\n```\n**Output**\n```\nBANC\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0]\n    t = data[1]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s, t;\n    cin >> s >> t;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n        String t = sc.next();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='ADOBECODEBANC\nABC\n', expected_output='BANC', is_hidden=False),
        TestCase(input='a\na\n', expected_output='a', is_hidden=False),
        TestCase(input='a\naa\n', expected_output='', is_hidden=True),
        TestCase(input='abc\ndef\n', expected_output='', is_hidden=True),
        TestCase(input='aaflslflsldkjf\naa\n', expected_output='aa', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['permutation-in-string'] = {
    "description": "# Permutation in String\n\n## Statement\n\nGiven two strings `s1` and `s2`, return `true` if `s2` contains a permutation of `s1`, or `false` otherwise.\n\nIn other words, return `true` if one of `s1`'s permutations is a substring of `s2`.\n\n## Input Format\n\n- The first line contains the string `s1`.\n- The second line contains the string `s2`.\n\n## Output Format\n\n- `true` or `false` (lowercase).\n\n## Constraints\n\n- 1 <= s1.length, s2.length <= 10^4\n- `s1` and `s2` consist of lowercase English letters only.\n\n## Example\n\n**Input**\n```\nab\neidbaooo\n```\n**Output**\n```\ntrue\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s1 = data[0]\n    s2 = data[1]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s1, s2;\n    cin >> s1 >> s2;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s1 = sc.next();\n        String s2 = sc.next();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='ab\neidbaooo\n', expected_output='true', is_hidden=False),
        TestCase(input='ab\neidboaoo\n', expected_output='false', is_hidden=False),
        TestCase(input='a\na\n', expected_output='true', is_hidden=True),
        TestCase(input='abc\ncbaxyz\n', expected_output='true', is_hidden=True),
        TestCase(input='abc\ndef\n', expected_output='false', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['sliding-window-maximum'] = {
    "description": '# Sliding Window Maximum\n\n## Statement\n\nYou are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. You can only see the `k` numbers in the window. Each time the sliding window moves right by one position.\n\nReturn the max sliding window.\n\n## Input Format\n\n- The first line contains two integers `n` and `k`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- Space-separated integers representing the maximum in each window position.\n\n## Constraints\n\n- 1 <= n <= 10^5\n- 1 <= k <= n\n- -10^4 <= nums[i] <= 10^4\n\n## Example\n\n**Input**\n```\n8 3\n1 3 -1 -3 5 3 6 7\n```\n**Output**\n```\n3 3 5 5 6 7\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, k = int(data[0]), int(data[1])\n    nums = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, k;\n    cin >> n >> k;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), k = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='8 3\n1 3 -1 -3 5 3 6 7\n', expected_output='3 3 5 5 6 7', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='1', is_hidden=False),
        TestCase(input='5 1\n1 2 3 4 5\n', expected_output='1 2 3 4 5', is_hidden=True),
        TestCase(input='6 2\n-1 -2 -3 -4 -5 -6\n', expected_output='-1 -2 -3 -4 -5', is_hidden=True),
        TestCase(input='3 3\n1 2 3\n', expected_output='3', is_hidden=True),
    ],
}

# ===========================================================================
# Stack
# ===========================================================================

NEETCODE_AUTHORING['car-fleet'] = {
    "description": "# Car Fleet\n\n## Statement\n\nThere are `n` cars going to the same destination along a one-lane road. The destination is `target` miles away.\n\nYou are given two integer arrays `position` and `speed`, both of length `n`, where `position[i]` is the position of the `i`th car and `speed[i]` is the speed of the `i`th car in miles per hour.\n\nA car can never pass another car ahead of it, but it can catch up to it and drive bumper to bumper at the same speed. The faster car will slow down to match the slower car's speed. The distance between these two cars is ignored (i.e., they are assumed to have the same position).\n\nA car fleet is some non-empty set of cars driving at the same position and same speed. Note that a single car is also a car fleet.\n\nReturn the number of car fleets that will arrive at the destination.\n\n## Input Format\n\n- The first line contains the integer `target`.\n- The second line contains an integer `n`.\n- The third line contains `n` space-separated integers (positions).\n- The fourth line contains `n` space-separated integers (speeds).\n\n## Output Format\n\n- A single integer representing the number of car fleets.\n\n## Constraints\n\n- 1 <= position.length == speed.length <= 10^5\n- 1 <= target <= 10^6\n- 1 <= position[i] < target\n- 1 <= speed[i] <= 10^6\n- All the values of `position` are unique.\n\n## Example\n\n**Input**\n```\n10\n4\n8 3 7 6\n4 4 4 4\n```\n**Output**\n```\n2\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    target = int(data[idx]); idx += 1\n    n = int(data[idx]); idx += 1\n    positions = [int(data[idx+j]) for j in range(n)]; idx += n\n    speeds = [int(data[idx+j]) for j in range(n)]; idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int target, n;\n    cin >> target >> n;\n    vector<int> positions(n), speeds(n);\n    for (int i = 0; i < n; i++) cin >> positions[i];\n    for (int i = 0; i < n; i++) cin >> speeds[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int target = sc.nextInt(), n = sc.nextInt();\n        int[] positions = new int[n], speeds = new int[n];\n        for (int i = 0; i < n; i++) positions[i] = sc.nextInt();\n        for (int i = 0; i < n; i++) speeds[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='10\n4\n8 3 7 6\n4 4 4 4\n', expected_output='2', is_hidden=False),
        TestCase(input='10\n5\n3 4 5 6 7\n3 4 5 6 7\n', expected_output='5', is_hidden=False),
        TestCase(input='10\n1\n2\n3\n', expected_output='1', is_hidden=True),
        TestCase(input='100\n3\n0 2 4\n4 2 1\n', expected_output='2', is_hidden=True),
        TestCase(input='10\n4\n4 1 8 2\n2 2 4 4\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['daily-temperatures'] = {
    "description": '# Daily Temperatures\n\n## Statement\n\nGiven an array of integers `temperatures` representing the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i`th day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0` instead.\n\n## Input Format\n\n- The first line contains an integer `n`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- Space-separated integers representing the answer array.\n\n## Constraints\n\n- 1 <= n <= 10^5\n- 30 <= temperatures[i] <= 100\n- There is at most one answer for each day.\n\n## Example\n\n**Input**\n```\n4\n73 74 75 71\n```\n**Output**\n```\n1 1 4 0\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    temps = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> temps(n);\n    for (int i = 0; i < n; i++) cin >> temps[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] temps = new int[n];\n        for (int i = 0; i < n; i++) temps[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n73 74 75 71\n', expected_output='1 1 4 0', is_hidden=False),
        TestCase(input='3\n72 72 72\n', expected_output='0 0 0', is_hidden=False),
        TestCase(input='1\n30\n', expected_output='0', is_hidden=True),
        TestCase(input='5\n73 71 69 72 70\n', expected_output='2 1 1 2 0', is_hidden=True),
        TestCase(input='4\n73 74 75 76\n', expected_output='1 1 1 0', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['evaluate-reverse-polish-notation'] = {
    "description": "# Evaluate Reverse Polish Notation\n\n## Statement\n\nYou are given an array of strings `tokens` that represents an arithmetic expression in Reverse Polish Notation.\n\nEvaluate the expression. Return an integer that represents the value of the expression.\n\nNote:\n- The valid operators are '+', '-', '*', and '/'.\n- Each operand may be an integer or another expression.\n- Division between two integers should truncate toward zero.\n- There will not be any division by zero.\n\n## Input Format\n\n- A single line containing space-separated tokens.\n\n## Output Format\n\n- A single integer representing the result.\n\n## Constraints\n\n- 1 <= tokens.length <= 10^4\n- `tokens[i]` is either an operator: '+', '-', '*', '/', or an integer in the range [-200, 200].\n\n## Example\n\n**Input**\n```\n2 1 + 3 *\n```\n**Output**\n```\n9\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    tokens = data[0].split()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string line;\n    getline(cin, line);\n    stringstream ss(line);\n    vector<string> tokens;\n    string token;\n    while (ss >> token) tokens.push_back(token);\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] tokens = sc.nextLine().split(" ");\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2 1 + 3 *\n', expected_output='9', is_hidden=False),
        TestCase(input='4 13 5 / +\n', expected_output='6', is_hidden=False),
        TestCase(input='10 6 9 3 + -11 * / * 17 + 5 +\n', expected_output='22', is_hidden=True),
        TestCase(input='3 4 +\n', expected_output='7', is_hidden=True),
        TestCase(input='5 1 -\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['generate-parentheses'] = {
    "description": '# Generate Parentheses\n\n## Statement\n\nGiven `n` pairs of parentheses, write a function to generate all combinations of well-formed parentheses.\n\n## Input Format\n\n- A single integer `n`.\n\n## Output Format\n\n- One combination per line, sorted lexicographically.\n\n## Constraints\n\n- 1 <= n <= 8\n\n## Example\n\n**Input**\n```\n3\n```\n**Output**\n```\n((()))\n(()())\n(())()\n()(())\n()()()\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n', expected_output='((()))\n(()())\n(())()\n()(())\n()()()', is_hidden=False),
        TestCase(input='1\n', expected_output='()', is_hidden=False),
        TestCase(input='2\n', expected_output='(())\n()()', is_hidden=True),
        TestCase(input='4\n', expected_output='(((())))\n((()()))\n((())())\n((()))()\n(()(()))\n(()()())\n(()())()\n(())(())\n(())()()\n()((()))\n()(()())\n()(())()\n()()(())\n()()()()', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['largest-rectangle-in-histogram'] = {
    "description": "# Largest Rectangle in Histogram\n\n## Statement\n\nGiven an array of integers `heights` representing the histogram's bar height where the width of each bar is `1`, return the area of the largest rectangle in the histogram.\n\n## Input Format\n\n- The first line contains an integer `n`.\n- The second line contains `n` space-separated integers representing heights.\n\n## Output Format\n\n- A single integer representing the maximum rectangular area.\n\n## Constraints\n\n- 1 <= heights.length <= 10^5\n- 0 <= heights[i] <= 10^4\n\n## Example\n\n**Input**\n```\n6\n2 1 5 6 2 3\n```\n**Output**\n```\n10\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    heights = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> heights(n);\n    for (int i = 0; i < n; i++) cin >> heights[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] heights = new int[n];\n        for (int i = 0; i < n; i++) heights[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6\n2 1 5 6 2 3\n', expected_output='10', is_hidden=False),
        TestCase(input='3\n2 2 2\n', expected_output='6', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1', is_hidden=True),
        TestCase(input='5\n1 2 3 4 5\n', expected_output='9', is_hidden=True),
        TestCase(input='4\n2 4 6 8\n', expected_output='12', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['min-stack'] = {
    "description": '# Min Stack\n\n## Statement\n\nDesign a stack that supports push, pop, top, and retrieving the minimum element in constant time.\n\nImplement the `MinStack` class:\n\n- `push(val)` pushes the element `val` onto the stack.\n- `pop()` removes the element on the top of the stack.\n- `top()` gets the top element of the stack.\n- `getMin()` retrieves the minimum element in the stack.\n\n## Input Format\n\n- Multiple lines. Each line is an operation:\n  - `push val`: push val\n  - `pop`: pop top\n  - `top`: get top\n  - `getMin`: get minimum\n\n## Output Format\n\n- For each `pop`, `top`, or `getMin` operation, output the result on its own line.\n\n## Constraints\n\n- -2^31 <= val <= 2^31 - 1\n- `pop`, `top`, and `getMin` operations will always be called on non-empty stacks.\n- At most 3 * 10^4 calls will be made to `push`, `pop`, `top`, and `getMin`.\n\n## Example\n\n**Input**\n```\npush -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin\n```\n**Output**\n```\n-3\n-3\n0\n-2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='push -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin\n', expected_output='-3\n-3\n0\n-2', is_hidden=False),
        TestCase(input='push 1\npush 2\ngetMin\ntop\npop\ngetMin\n', expected_output='1\n2\n1', is_hidden=False),
        TestCase(input='push 5\ngetMin\ngetMin\npop\ngetMin\n', expected_output='5\n5\n5', is_hidden=True),
        TestCase(input='push 0\npush -1\npush -1\ngetMin\npop\ngetMin\n', expected_output='-1\n-1\n-1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['valid-parentheses'] = {
    "description": "# Valid Parentheses\n\n## Statement\n\nGiven a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.\n\n## Input Format\n\n- A single line containing the string `s`.\n\n## Output Format\n\n- `true` or `false` (lowercase).\n\n## Constraints\n\n- 1 <= s.length <= 10^4\n- `s` consists of parentheses only '()[]{}.'\n\n## Example\n\n**Input**\n```\n()\n```\n**Output**\n```\ntrue\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0] if data else ""\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.next();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='()\n', expected_output='true', is_hidden=False),
        TestCase(input='()[]{}\n', expected_output='true', is_hidden=False),
        TestCase(input='(]\n', expected_output='false', is_hidden=True),
        TestCase(input='([)]\n', expected_output='false', is_hidden=True),
        TestCase(input='{[]}\n', expected_output='true', is_hidden=True),
    ],
}

# ===========================================================================
# Binary Search
# ===========================================================================

NEETCODE_AUTHORING['binary-search'] = {
    "description": '# Binary Search\n\n## Statement\n\nGiven an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.\n\nYou must write an algorithm with O(log n) runtime complexity.\n\n## Input Format\n\n- The first line contains two integers `n` and `target`.\n- The second line contains `n` space-separated integers in ascending order.\n\n## Output Format\n\n- A single integer: the index of target, or -1.\n\n## Constraints\n\n- 1 <= n <= 10^4\n- -10^4 < nums[i], target < 10^4\n- All the integers in `nums` are unique.\n- `nums` is sorted in ascending order.\n\n## Example\n\n**Input**\n```\n6 9\n-1 0 3 5 9 12\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, target = int(data[0]), int(data[1])\n    nums = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, target;\n    cin >> n >> target;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), target = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6 9\n-1 0 3 5 9 12\n', expected_output='4', is_hidden=False),
        TestCase(input='6 2\n-1 0 3 5 9 12\n', expected_output='-1', is_hidden=False),
        TestCase(input='1 5\n5\n', expected_output='0', is_hidden=True),
        TestCase(input='5 3\n1 2 3 4 5\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['find-minimum-in-rotated-sorted-array'] = {
    "description": '# Find Minimum in Rotated Sorted Array\n\n## Statement\n\nSuppose an array of length `n` sorted in ascending order is rotated between `1` and `n` times. Given the sorted rotated array `nums` of unique elements, return the minimum element of this array.\n\nYou must write an algorithm that runs in O(log n) time.\n\n## Input Format\n\n- The first line contains an integer `n`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- A single integer representing the minimum element.\n\n## Constraints\n\n- n == nums.length\n- 1 <= n <= 5000\n- -5000 <= nums[i] <= 5000\n- All the integers of `nums` are unique.\n- `nums` is sorted and rotated between 1 and n times.\n\n## Example\n\n**Input**\n```\n5\n4 5 6 7 0\n```\n**Output**\n```\n0\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n4 5 6 7 0\n', expected_output='0', is_hidden=False),
        TestCase(input='5\n2 3 4 5 1\n', expected_output='1', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1', is_hidden=True),
        TestCase(input='4\n3 4 5 1\n', expected_output='1', is_hidden=True),
        TestCase(input='6\n2 3 4 5 6 1\n', expected_output='1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['koko-eating-bananas'] = {
    "description": '# Koko Eating Bananas\n\n## Statement\n\nKoko loves to eat bananas. There are `n` piles of bananas, the `i`th pile has `piles[i]` bananas. The guards have gone and will come back in `h` hours.\n\nKoko can decide her bananas-per-hour eating speed of `k`. Each hour, she chooses some pile of bananas and eats `k` bananas from that pile. If the pile has less than `k` bananas, she eats all of them instead and will not eat any more bananas during this hour.\n\nKoko likes to eat slowly but still wants to finish eating all the bananas before the guards return.\n\nReturn the integer `k` such that she can eat all the bananas within `h` hours. It is guaranteed there is an answer.\n\n## Input Format\n\n- The first line contains two integers `n` and `h`.\n- The second line contains `n` space-separated integers representing the piles.\n\n## Output Format\n\n- A single integer representing the minimum eating speed.\n\n## Constraints\n\n- 1 <= n <= 10^4\n- n <= h <= 10^9\n- 1 <= piles[i] <= 10^9\n\n## Example\n\n**Input**\n```\n4 8\n3 6 7 11\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, h = int(data[0]), int(data[1])\n    piles = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, h;\n    cin >> n >> h;\n    vector<int> piles(n);\n    for (int i = 0; i < n; i++) cin >> piles[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), h = sc.nextInt();\n        int[] piles = new int[n];\n        for (int i = 0; i < n; i++) piles[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 8\n3 6 7 11\n', expected_output='4', is_hidden=False),
        TestCase(input='5 7\n30 11 23 4 20\n', expected_output='30', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='1', is_hidden=True),
        TestCase(input='4 9\n30 11 23 4 20\n', expected_output='23', is_hidden=True),
        TestCase(input='3 5\n100 50 150\n', expected_output='100', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['median-of-two-sorted-arrays'] = {
    "description": '# Median of Two Sorted Arrays\n\n## Statement\n\nGiven two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays.\n\nThe overall run time complexity should be O(log (m+n)).\n\n## Input Format\n\n- The first line contains `m` followed by `m` integers (array 1).\n- The second line contains `n` followed by `n` integers (array 2).\n\n## Output Format\n\n- A single floating-point number with exactly 5 decimal places.\n\n## Constraints\n\n- 0 <= m, n <= 1000\n- 1 <= m + n <= 2000\n- -10^6 <= nums1[i], nums2[i] <= 10^6\n\n## Example\n\n**Input**\n```\n3 1 3 5\n2 2 4\n```\n**Output**\n```\n3.00000\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m = int(data[idx]); idx += 1\n    nums1 = [int(data[idx+j]) for j in range(m)]; idx += m\n    n = int(data[idx]); idx += 1\n    nums2 = [int(data[idx+j]) for j in range(n)]; idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m;\n    vector<int> nums1(m);\n    for (int i = 0; i < m; i++) cin >> nums1[i];\n    cin >> n;\n    vector<int> nums2(n);\n    for (int i = 0; i < n; i++) cin >> nums2[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt();\n        int[] nums1 = new int[m];\n        for (int i = 0; i < m; i++) nums1[i] = sc.nextInt();\n        int n = sc.nextInt();\n        int[] nums2 = new int[n];\n        for (int i = 0; i < n; i++) nums2[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 1 3 5\n2 2 4\n', expected_output='3.00000', is_hidden=False),
        TestCase(input='2 1 2\n1 3 4\n', expected_output='2.50000', is_hidden=False),
        TestCase(input='0\n1 1\n', expected_output='1.00000', is_hidden=True),
        TestCase(input='1 2\n1 3\n', expected_output='2.00000', is_hidden=True),
        TestCase(input='1 1\n1 1\n', expected_output='1.00000', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['search-a-2d-matrix'] = {
    "description": '# Search a 2D Matrix\n\n## Statement\n\nYou are given an `m x n` integer matrix `matrix` with the following two properties:\n\n- Each row is sorted in non-decreasing order.\n- The first integer of each row is greater than the last integer of the previous row.\n\nGiven an integer `target`, return `true` if `target` is in `matrix` or `false` otherwise.\n\n## Input Format\n\n- The first line contains three integers `m`, `n`, and `target`.\n- The next `m` lines each contain `n` space-separated integers.\n\n## Output Format\n\n- `true` or `false` (lowercase).\n\n## Constraints\n\n- 1 <= m, n <= 100\n- -10^4 <= matrix[i][j], target <= 10^4\n\n## Example\n\n**Input**\n```\n3 4 3\n1 3 5 7\n10 11 16 20\n23 30 34 60\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m, n, target = int(data[idx]), int(data[idx+1]), int(data[idx+2])\n    idx += 3\n    matrix = []\n    for i in range(m):\n        matrix.append([int(data[idx+j]) for j in range(n)])\n        idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n, target;\n    cin >> m >> n >> target;\n    vector<vector<int>> matrix(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> matrix[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt(), target = sc.nextInt();\n        int[][] matrix = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                matrix[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 4 3\n1 3 5 7\n10 11 16 20\n23 30 34 60\n', expected_output='true', is_hidden=False),
        TestCase(input='3 4 13\n1 3 5 7\n10 11 16 20\n23 30 34 60\n', expected_output='false', is_hidden=False),
        TestCase(input='1 1 1\n1\n', expected_output='true', is_hidden=True),
        TestCase(input='1 1 0\n1\n', expected_output='false', is_hidden=True),
        TestCase(input='2 2 3\n1 3\n5 7\n', expected_output='true', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['search-in-rotated-sorted-array'] = {
    "description": '# Search in Rotated Sorted Array\n\n## Statement\n\nThere is an integer array `nums` sorted in ascending order (with distinct values).\n\nPrior to being passed to your function, `nums` is possibly rotated at an unknown pivot index `k` (1 <= k < nums.length) such that the resulting array is `[nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]]` (0-indexed).\n\nGiven the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in `nums`.\n\nYou must write an algorithm with O(log n) runtime complexity.\n\n## Input Format\n\n- The first line contains two integers `n` and `target`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- A single integer: the index of target, or -1.\n\n## Constraints\n\n- 1 <= n <= 5000\n- -10^4 <= nums[i], target <= 10^4\n- All values of `nums` are unique.\n- `nums` is an ascending array that is possibly rotated.\n\n## Example\n\n**Input**\n```\n6 3\n4 5 6 7 0 1 2\n```\n**Output**\n```\n-1\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, target = int(data[0]), int(data[1])\n    nums = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, target;\n    cin >> n >> target;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), target = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6 3\n4 5 6 7 0 1 2\n', expected_output='-1', is_hidden=False),
        TestCase(input='4 0\n4 5 6 7 0 1 2\n', expected_output='4', is_hidden=False),
        TestCase(input='1 0\n0\n', expected_output='0', is_hidden=True),
        TestCase(input='5 3\n3 1\n', expected_output='0', is_hidden=True),
        TestCase(input='7 5\n4 5 6 7 0 1 2\n', expected_output='1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['time-based-key-value-store'] = {
    "description": '# Time Based Key-Value Store\n\n## Statement\n\nDesign a time-based key-value data structure that can store multiple values for the same key at different time stamps and retrieve the key\'s value at a certain timestamp.\n\nImplement the `TimeMap` class:\n\n- `TimeMap()` Initializes the object.\n- `set(key, value, timestamp)` Stores the key `key` with the value `value` at the given time `timestamp`.\n- `get(key, timestamp)` Returns a value such that `set` was called previously with `timestamp_prev <= timestamp`. If there are multiple such values, it returns the one associated with the largest `timestamp_prev`. If no values are found, it returns `""`.\n\n## Input Format\n\n- Multiple lines. Each line is an operation:\n  - `set key value timestamp`\n  - `get key timestamp`\n\n## Output Format\n\n- For each `get` operation, output the result on its own line.\n\n## Constraints\n\n- 1 <= key.length, value.length <= 100\n- 1 <= timestamp <= 10^7\n- All `set` operations have timestamps in strictly increasing order.\n- At most 2 * 10^5 calls will be made to `set` and `get`.\n\n## Example\n\n**Input**\n```\nset foo bar 1\nget foo 1\nget foo 3\nset foo bar2 4\nget foo 4\nget foo 5\n```\n**Output**\n```\nbar\nbar\nbar2\nbar2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='set foo bar 1\nget foo 1\nget foo 3\nset foo bar2 4\nget foo 4\nget foo 5\n', expected_output='bar\nbar\nbar2\nbar2', is_hidden=False),
        TestCase(input='set a b 1\nset a c 2\nget a 1\nget a 2\nget a 3\n', expected_output='b\nc\nc', is_hidden=False),
        TestCase(input='get x 1\nset x y 1\nget x 1\nget x 2\n', expected_output='\ny\ny', is_hidden=True),
        TestCase(input='set key val 5\nget key 1\nget key 5\nget key 10\n', expected_output='\nval\nval', is_hidden=True),
    ],
}

# ===========================================================================
# Tries
# ===========================================================================

NEETCODE_AUTHORING['design-add-and-search-words-data-structure'] = {
    "description": '# Design Add and Search Words Data Structure\n\n## Statement\nDesign a data structure that supports adding new words and finding if a string matches\nany previously added string. The search operation can match the `.` character, which\ncan represent any letter.\n\n## Input Format\n- Line 1: integer `n` — the number of operations\n- Next `n` lines: each line contains an operation and a string, separated by a space:\n  `addWord <word>` or `search <word>`\n\n## Output Format\nFor each `search` operation, output a line with `true` or `false`.\nDo not output anything for `addWord` operations.\n\n## Constraints\n- `1 <= n <= 10^4`\n- `word` consists of lowercase English letters or `.`.\n- `1 <= word.length <= 25`\n- At most `10^4` calls will be made to `addWord` and `search`.\n\n## Example\n\n**Input**\n```\n7\naddWord bad\naddWord dad\naddWord mad\nsearch pad\nsearch bad\nsearch .ad\nsearch b..\n```\n**Output**\n```\nfalse\ntrue\ntrue\ntrue\n```\nExplanation: The wildcard `.` matches any single character. So ".ad" matches\n"bad", "dad", and "mad".',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    words = []\n    results = []\n\n    for i in range(1, n + 1):\n        parts = data[i].split()\n        op = parts[0]\n        word = parts[1]\n        if op == "addWord":\n            words.append(word)\n        elif op == "search":\n            results.append("true" if any(word == w or len(word) == len(w) and all(a == b or c == "." for a, b, c in zip(word, w)) for w in words) else "false")\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<string> words;\n    string op, word;\n    for (int i = 0; i < n; i++) {\n        cin >> op >> word;\n        if (op == "addWord") {\n            words.push_back(word);\n        } else if (op == "search") {\n            bool found = false;\n            for (auto& w : words) {\n                if (w.size() != word.size()) continue;\n                bool match = true;\n                for (int j = 0; j < (int)word.size(); j++) {\n                    if (word[j] != \'.\' && word[j] != w[j]) { match = false; break; }\n                }\n                if (match) { found = true; break; }\n            }\n            cout << (found ? "true" : "false") << "\\n";\n        }\n    }\n    // ===== YOUR CODE HERE =====\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Integer.parseInt(sc.nextLine().trim());\n        List<String> words = new ArrayList<>();\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < n; i++) {\n            String line = sc.nextLine().trim();\n            String[] parts = line.split(" ");\n            String op = parts[0];\n            String word = parts[1];\n            if (op.equals("addWord")) {\n                words.add(word);\n            } else if (op.equals("search")) {\n                boolean found = false;\n                for (String w : words) {\n                    if (w.length() != word.length()) continue;\n                    boolean match = true;\n                    for (int j = 0; j < word.length(); j++) {\n                        if (word.charAt(j) != \'.\' && word.charAt(j) != w.charAt(j)) { match = false; break; }\n                    }\n                    if (match) { found = true; break; }\n                }\n                sb.append(found ? "true" : "false").append("\\n");\n            }\n        }\n        // ===== YOUR CODE HERE =====\n        System.out.print(sb.toString());\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='7\naddWord bad\naddWord dad\naddWord mad\nsearch pad\nsearch bad\nsearch .ad\nsearch b..\n', expected_output='false\ntrue\ntrue\ntrue', is_hidden=False),
        TestCase(input='5\naddWord a\naddWord ab\nsearch a\nsearch .\nsearch ..\n', expected_output='true\ntrue\nfalse', is_hidden=False),
        TestCase(input='4\naddWord abc\nsearch abc\nsearch .bc\nsearch a.c\n', expected_output='true\ntrue\ntrue', is_hidden=True),
        TestCase(input='6\naddWord cat\naddWord bat\naddWord rat\nsearch .at\nsearch c.t\nsearch dog\n', expected_output='true\ntrue\nfalse', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['implement-trie-prefix-tree'] = {
    "description": '# Implement Trie (Prefix Tree)\n\n## Statement\nA trie or prefix tree is a tree data structure used to efficiently store and retrieve\nkeys in a dataset of strings. Implement a trie with the following operations:\n- `insert(word)`: Inserts the string `word` into the trie.\n- `search(word)`: Returns `true` if the string `word` is in the trie (i.e., was inserted\n  before), and `false` otherwise.\n- `startsWith(prefix)`: Returns `true` if there is a previously inserted string `word`\n  that has the prefix `prefix`, and `false` otherwise.\n\n## Input Format\n- Line 1: integer `n` — the number of operations\n- Next `n` lines: each line contains an operation and a string, separated by a space:\n  `insert <word>`, `search <word>`, or `startsWith <prefix>`\n\n## Output Format\nFor each `search` or `startsWith` operation, output a line with `true` or `false`.\nDo not output anything for `insert` operations.\n\n## Constraints\n- `1 <= n <= 10^4`\n- `word` and `prefix` consist of only lowercase English letters.\n- `1 <= word.length, prefix.length <= 20`\n- At most `10^4` calls will be made to `insert`, `search`, and `startsWith`.\n\n## Example\n\n**Input**\n```\n7\ninsert apple\nsearch apple\nsearch app\nstartsWith app\ninsert app\nsearch app\nstartsWith app\n```\n**Output**\n```\ntrue\nfalse\ntrue\ntrue\ntrue\n```\nExplanation: After inserting "apple", searching for "apple" returns true, but\nsearching for "app" returns false. After inserting "app", searching for "app" returns true.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    results = []\n    trie = set()\n    words = []\n\n    for i in range(1, n + 1):\n        parts = data[i].split()\n        op = parts[0]\n        word = parts[1]\n        if op == "insert":\n            words.append(word)\n        elif op == "search":\n            results.append("true" if word in words else "false")\n        elif op == "startsWith":\n            results.append("true" if any(w.startswith(word) for w in words) else "false")\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<string> words;\n    string op, word;\n    for (int i = 0; i < n; i++) {\n        cin >> op >> word;\n        if (op == "insert") {\n            words.push_back(word);\n        } else if (op == "search") {\n            bool found = false;\n            for (auto& w : words) if (w == word) { found = true; break; }\n            cout << (found ? "true" : "false") << "\\n";\n        } else if (op == "startsWith") {\n            bool found = false;\n            for (auto& w : words) if (w.substr(0, word.size()) == word) { found = true; break; }\n            cout << (found ? "true" : "false") << "\\n";\n        }\n    }\n    // ===== YOUR CODE HERE =====\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Integer.parseInt(sc.nextLine().trim());\n        List<String> words = new ArrayList<>();\n        StringBuilder sb = new StringBuilder();\n        for (int i = 0; i < n; i++) {\n            String line = sc.nextLine().trim();\n            String[] parts = line.split(" ");\n            String op = parts[0];\n            String word = parts[1];\n            if (op.equals("insert")) {\n                words.add(word);\n            } else if (op.equals("search")) {\n                sb.append(words.contains(word) ? "true" : "false").append("\\n");\n            } else if (op.equals("startsWith")) {\n                boolean found = false;\n                for (String w : words) {\n                    if (w.startsWith(word)) { found = true; break; }\n                }\n                sb.append(found ? "true" : "false").append("\\n");\n            }\n        }\n        // ===== YOUR CODE HERE =====\n        System.out.print(sb.toString());\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='7\ninsert apple\nsearch apple\nsearch app\nstartsWith app\ninsert app\nsearch app\nstartsWith app\n', expected_output='true\nfalse\ntrue\ntrue\ntrue', is_hidden=False),
        TestCase(input='3\ninsert hello\nsearch world\nstartsWith hel\n', expected_output='false\ntrue', is_hidden=False),
        TestCase(input='5\ninsert a\ninsert ab\nsearch a\nstartsWith a\nsearch b\n', expected_output='true\ntrue\nfalse', is_hidden=True),
        TestCase(input='4\ninsert abc\nsearch abc\nsearch ab\nstartsWith ab\n', expected_output='true\nfalse\ntrue', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['word-search-ii'] = {
    "description": '# Word Search II\n\n## Statement\nGiven an `m x n` grid of characters `board` and a list of strings `words`, return all\nwords on the board that can be found. Each word must be constructed from letters of\nadjacent cells (horizontally or vertically), and each cell may only be used once per word.\n\n## Input Format\n- Line 1: integers `m n` — the dimensions of the board\n- Next `m` lines: each line contains `n` characters separated by spaces\n- Next line: integer `k` — the number of words\n- Next `k` lines: each line contains a word\n\n## Output Format\nThe found words sorted lexicographically, one per line. If no words are found, output nothing.\n\n## Constraints\n- `1 <= m, n <= 12`\n- `1 <= k <= 10^3`\n- `1 <= word.length <= 10`\n- All strings in `words` are unique.\n- `board` and `words` consist of lowercase English letters.\n\n## Example\n\n**Input**\n```\n3 4\no a a n\ne t a e\ni h k r\n5\noath\npea\neat\nrain\noat\n```\n**Output**\n```\neat\noath\noat\n```\nExplanation: "rain" and "pea" are not found on the board.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m, n = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    board = []\n    for _ in range(m):\n        board.append(data[idx:idx + n])\n        idx += n\n    k = int(data[idx])\n    idx += 1\n    words = data[idx:idx + k]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<char>> board(m, vector<char>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> board[i][j];\n    int k;\n    cin >> k;\n    vector<string> words(k);\n    for (auto& w : words) cin >> w;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        char[][] board = new char[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                board[i][j] = sc.next().charAt(0);\n        int k = sc.nextInt();\n        String[] words = new String[k];\n        for (int i = 0; i < k; i++) words[i] = sc.next();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 4\no a a n\ne t a e\ni h k r\n5\noath\npea\neat\nrain\noat\n', expected_output='eat\noath\noat', is_hidden=False),
        TestCase(input='2 2\na b\nc d\n1\nab\n', expected_output='ab', is_hidden=False),
        TestCase(input='1 3\na b c\n2\nab\nabc\n', expected_output='ab\nabc', is_hidden=True),
        TestCase(input='2 2\na b\nc d\n1\nacbd\n', expected_output='', is_hidden=True),
    ],
}

# ===========================================================================
# Heap / Priority Queue
# ===========================================================================

NEETCODE_AUTHORING['design-twitter'] = {
    "description": "# Design Twitter\n\n## Statement\n\nDesign a simplified version of Twitter where users can post tweets, follow/unfollow another user, and is able to see the 10 most recent tweets in the user's news feed.\n\nImplement the Twitter class:\n- `Twitter()`: Initializes your twitter object.\n- `void postTweet(int userId, int tweetId)`: Composes a new tweet with ID tweetId by the user userId. Each call to this function will be made with a unique tweetId.\n- `List<Integer> getNewsFeed(int userId)`: Returns the 10 most recent tweet IDs in the user's news feed. Each item in the news feed must be posted by users who the user is following, or by the user themself. Tweets should be ordered from most recent to least recent.\n- `void follow(int followerId, int followeeId)`: The user with ID followerId started following the user with ID followeeId.\n- `void unfollow(int followerId, int followeeId)`: The user with ID followerId started unfollowing the user with ID followeeId.\n\n## Input Format\n- First line: integer q (number of operations)\n- Next q lines: operations\n  - `post userId tweetId`\n  - `follow uid1 uid2`\n  - `unfollow uid1 uid2`\n  - `newsfeed uid`\n\n## Output Format\n- For each newsfeed operation, output tweet IDs space-separated\n\n## Constraints\n- 1 <= userId <= 500\n- 1 <= followerId, followeeId <= 500\n- 1 <= tweetId <= 10^4\n- All the calls to postTweet will be made with unique tweetIds\n- At most 10 calls will be made to getNewsFeed\n\n## Example\n\n**Input**\n```\n7\npost 1 5\npost 2 6\nnewsfeed 1\nfollow 1 2\nnewsfeed 1\nunfollow 1 2\nnewsfeed 1\n```\n\n**Output**\n```\n5\n6 5\n5\n```",
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    q = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int q;\n    cin >> q;\n    cin.ignore();\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int q = Integer.parseInt(sc.nextLine().trim());\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='7\npost 1 5\npost 2 6\nnewsfeed 1\nfollow 1 2\nnewsfeed 1\nunfollow 1 2\nnewsfeed 1\n', expected_output='5\n6 5\n5\n', is_hidden=False),
        TestCase(input='4\npost 1 1\npost 1 2\nnewsfeed 1\n', expected_output='2 1\n', is_hidden=False),
        TestCase(input='5\npost 1 10\npost 2 20\nfollow 1 2\nnewsfeed 1\nunfollow 1 2\n', expected_output='20 10\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['find-median-from-data-stream'] = {
    "description": '# Find Median from Data Stream\n\n## Statement\n\nThe median is the middle value in an ordered integer list. If the size of the list is even, there is no middle value, and the median is the mean of the two middle values.\n\nImplement the MedianFinder class:\n- `MedianFinder()`: Initializes the MedianFinder object.\n- `void addNum(int num)`: Adds the integer num from the data stream to the data structure.\n- `double findMedian()`: Returns the median of all elements so far.\n\n## Input Format\n- First line: integer n (number of elements)\n- Second line: n integers\n\n## Output Format\n- n lines, each containing the median after each addition (formatted to 1 decimal place if needed)\n\n## Constraints\n- -10^5 <= num <= 10^5\n- There will be at least one element in the data structure before calling findMedian\n- At most 5 * 10^4 calls will be made to addNum and findMedian\n\n## Example\n\n**Input**\n```\n5\n1 2 3 4 5\n```\n\n**Output**\n```\n1.0\n1.5\n2.0\n2.5\n3.0\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(data[i + 1]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n1 2 3 4 5\n', expected_output='1.0\n1.5\n2.0\n2.5\n3.0\n', is_hidden=False),
        TestCase(input='3\n2 1 3\n', expected_output='2.0\n1.5\n2.0\n', is_hidden=False),
        TestCase(input='4\n1 1 1 1\n', expected_output='1.0\n1.0\n1.0\n1.0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['k-closest-points-to-origin'] = {
    "description": '# K Closest Points to Origin\n\n## Statement\n\nGiven an array of points where points[i] = [xi, yi] represents a point on the X-Y plane and an integer k, return the k closest points to the origin (0, 0).\n\nThe distance between a point (x, y) and the origin is sqrt(x^2 + y^2).\n\nYou may return the answer in any order. The answer is guaranteed to be unique (except for the order it is in).\n\n## Input Format\n- First line: two integers n and k\n- Next n lines: two integers x y per line\n\n## Output Format\n- k lines, each containing x y (the closest points)\n\n## Constraints\n- 1 <= k <= n <= 10^4\n- -10^4 <= xi, yi <= 10^4\n\n## Example\n\n**Input**\n```\n3 2\n1 3\n-2 2\n2 -2\n```\n\n**Output**\n```\n-2 2\n2 -2\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n, k = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    points = []\n    for i in range(n):\n        x, y = int(data[idx]), int(data[idx + 1])\n        points.append((x, y))\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, k;\n    cin >> n >> k;\n    vector<pair<int,int>> points(n);\n    for (int i = 0; i < n; i++) cin >> points[i].first >> points[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), k = sc.nextInt();\n        int[][] points = new int[n][2];\n        for (int i = 0; i < n; i++) { points[i][0] = sc.nextInt(); points[i][1] = sc.nextInt(); }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 2\n1 3\n-2 2\n2 -2\n', expected_output='-2 2\n2 -2\n', is_hidden=False),
        TestCase(input='2 1\n0 1\n0 -1\n', expected_output='0 1\n', is_hidden=False),
        TestCase(input='3 3\n3 3\n5 -1\n-2 4\n', expected_output='3 3\n-2 4\n5 -1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['kth-largest-element-in-a-stream'] = {
    "description": '# Kth Largest Element in a Stream\n\n## Statement\n\nDesign a class to find the kth largest element in a stream. Note that it is the kth largest element in the sorted order, not the kth distinct element.\n\nImplement the KthLargest class with the following operations:\n- `KthLargest(int k, int[] nums)`: Initializes the object with the integer k and the stream of integers nums.\n- `int add(int val)`: Appends the integer val to the stream and returns the element representing the kth largest element in the stream.\n\n## Input Format\n- First line: two integers k and m (number of initial elements)\n- Second line: m integers (initial elements, may be empty)\n- Third line: number of additions q\n- Next q lines: one integer per line (value to add)\n\n## Output Format\n- Output q lines, each containing the kth largest after each addition\n\n## Constraints\n- 1 <= k <= 10^5\n- 0 <= nums.length <= 10^5\n- -10^9 <= val <= 10^9\n- At most 10^4 calls will be made to add\n\n## Example\n\n**Input**\n```\n3 4\n4 5 8 2\n3\n3\n5\n10\n```\n\n**Output**\n```\n4\n5\n5\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    k, m = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    nums = []\n    if m > 0:\n        nums = [int(data[idx + i]) for i in range(m)]\n        idx += m\n    q = int(data[idx])\n    idx += 1\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int k, m;\n    cin >> k >> m;\n    vector<int> nums(m);\n    for (int i = 0; i < m; i++) cin >> nums[i];\n    int q;\n    cin >> q;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int k = sc.nextInt(), m = sc.nextInt();\n        int[] nums = new int[m];\n        for (int i = 0; i < m; i++) nums[i] = sc.nextInt();\n        int q = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 4\n4 5 8 2\n3\n3\n5\n10\n', expected_output='4\n5\n5\n', is_hidden=False),
        TestCase(input='1 0\n2\n1\n', expected_output='2\n', is_hidden=False),
        TestCase(input='2 3\n4 1 3\n2\n5\n', expected_output='4\n4\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['kth-largest-element-in-an-array'] = {
    "description": '# Kth Largest Element in an Array\n\n## Statement\n\nGiven an integer array nums and an integer k, return the kth largest element in the array.\n\nNote that it is the kth largest element in the sorted order, not the kth distinct element.\n\n## Input Format\n- First line: two integers n and k\n- Second line: n integers\n\n## Output Format\n- Single integer (kth largest)\n\n## Constraints\n- 1 <= k <= n <= 10^5\n- -10^4 <= nums[i] <= 10^4\n\n## Example\n\n**Input**\n```\n6 2\n3 2 1 5 6 4\n```\n\n**Output**\n```\n5\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, k = int(data[0]), int(data[1])\n    nums = [int(data[i + 2]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, k;\n    cin >> n >> k;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), k = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6 2\n3 2 1 5 6 4\n', expected_output='5\n', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='4 2\n3 2 3 1\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['last-stone-weight'] = {
    "description": '# Last Stone Weight\n\n## Statement\n\nYou are given an array of integers stones where stones[i] is the weight of the ith stone.\n\nWe are playing a game with the stones. On each turn, we choose the heaviest two stones and smash them together. Let the weight of the two stones be x and y with x <= y. The result of this smash is:\n- If x == y, both stones are destroyed, and\n- If x != y, the stone of weight x is destroyed, and the stone of weight y has new weight y - x.\n\nAt the end of the game, there is at most one stone left. Return the weight of the last remaining stone. If there are no stones left, return 0.\n\n## Input Format\n- First line: integer n\n- Second line: n integers (weights)\n\n## Output Format\n- Single integer (last stone weight or 0)\n\n## Constraints\n- 1 <= stones.length <= 30\n- 1 <= stones[i] <= 1000\n\n## Example\n\n**Input**\n```\n4\n2 7 4 1 8 1\n```\n\n**Output**\n```\n1\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    stones = [int(data[i + 1]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    priority_queue<int> pq;\n    for (int i = 0; i < n; i++) { int x; cin >> x; pq.push(x); }\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());\n        for (int i = 0; i < n; i++) pq.add(sc.nextInt());\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n2 7 4 1\n', expected_output='0\n', is_hidden=False),
        TestCase(input='6\n2 7 4 1 8 1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='1\n5\n', expected_output='5\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['task-scheduler'] = {
    "description": '# Task Scheduler\n\n## Statement\n\nYou are given a characters array tasks, representing the tasks a CPU needs to do, where each letter represents a different task. Tasks could be done in any order. Each task is done in one unit of time. For each unit of time, the CPU can complete only one task or be idle.\n\nHowever, there is a non-negative integer n that represents the cooldown period between two same tasks (the same letter) — that is, there must be at least n units of time between any two same tasks.\n\nReturn the least number of units of time that will be required to complete all the given tasks.\n\n## Input Format\n- First line: string of characters (tasks)\n- Second line: integer n (cooldown)\n\n## Output Format\n- Single integer (minimum intervals)\n\n## Constraints\n- 1 <= tasks.length <= 10^4\n- tasks[i] is upper-case English letter\n- 0 <= n <= 100\n\n## Example\n\n**Input**\n```\nAAABBB\n2\n```\n\n**Output**\n```\n8\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    tasks = data[0]\n    n = int(data[1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string tasks;\n    int n;\n    cin >> tasks >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String tasks = sc.next();\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='AAABBB\n2\n', expected_output='8\n', is_hidden=False),
        TestCase(input='A\n0\n', expected_output='1\n', is_hidden=False),
        TestCase(input='AAAAABBBBB\n2\n', expected_output='10\n', is_hidden=True),
    ],
}

# ===========================================================================
# Backtracking
# ===========================================================================

NEETCODE_AUTHORING['combination-sum'] = {
    "description": '# Combination Sum\n\n## Statement\nGiven an array of distinct integers `candidates` and a target integer `target`, return a list of all unique combinations of candidates where the chosen numbers sum to target. The same number may be chosen from candidates an unlimited number of times. Two combinations are unique if the frequency of at least one of the chosen numbers is different. Return the combinations in any order.\n\n## Input Format\n- First line: integer `n` then integer `target`\n- Second line: `n` space-separated integers (candidates)\n\n## Output Format\n- Combinations sorted lexicographically, one per line, space-separated values within each combination\n\n## Constraints\n- 1 <= n <= 30\n- 1 <= candidates[i] <= 200\n- All elements of candidates are distinct\n- 1 <= target <= 500\n\n## Example\n\n**Input**\n```\n4 7\n2 3 6 7\n```\n**Output**\n```\n2 2 3\n7\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 7\n2 3 6 7\n', expected_output='2 2 3\n7\n', is_hidden=False),
        TestCase(input='3 8\n2 3 5\n', expected_output='2 2 2 2\n2 3 3\n3 5\n', is_hidden=False),
        TestCase(input='2 1\n1 2\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['combination-sum-ii'] = {
    "description": '# Combination Sum II\n\n## Statement\nGiven a collection of candidate numbers `candidates` (which may contain duplicates) and a target number `target`, find all unique combinations in candidates where the candidate numbers sum to target. Each number in candidates may only be used once in the combination. The solution set must not contain duplicate combinations.\n\n## Input Format\n- First line: integer `n` then integer `target`\n- Second line: `n` space-separated integers\n\n## Output Format\n- Combinations sorted lexicographically, one per line, space-separated values within each combination\n\n## Constraints\n- 1 <= n <= 30\n- 1 <= candidates[i] <= 50\n- 1 <= target <= 50\n\n## Example\n\n**Input**\n```\n5 8\n2 5 2 1 2\n```\n**Output**\n```\n1 2 5\n2 2 2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5 8\n2 5 2 1 2\n', expected_output='1 2 5\n2 2 2\n', is_hidden=False),
        TestCase(input='2 1\n1 2\n', expected_output='1\n', is_hidden=False),
        TestCase(input='3 7\n3 2 1\n', expected_output='1 2 3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['letter-combinations-of-a-phone-number'] = {
    "description": '# Letter Combinations of a Phone Number\n\n## Statement\nGiven a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order. The mapping of digits to letters is the same as on a telephone keypad.\n\n## Input Format\n- A single string of digits\n\n## Output Format\n- Combinations sorted lexicographically, space-separated\n\n## Constraints\n- 1 <= digits.length <= 4\n- digits[i] is a digit in the range [2, 9]\n\n## Example\n\n**Input**\n```\n23\n```\n**Output**\n```\nad ae af bd be bf cd ce cf\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='23\n', expected_output='ad ae af bd be bf cd ce cf\n', is_hidden=False),
        TestCase(input='2\n', expected_output='a b c\n', is_hidden=False),
        TestCase(input='73\n', expected_output='pd pe pf qd qe qf rd re rf sd se sf\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['n-queens'] = {
    "description": '# N-Queens\n\n## Statement\nThe n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other. Given an integer n, return the number of distinct solutions to the n-queens puzzle, and all distinct solutions.\n\n## Input Format\n- A single integer `n`\n\n## Output Format\n- For each solution, output n rows of n characters where Q represents a queen and . represents an empty cell\n- Separate solutions with a blank line\n- Solutions should be sorted lexicographically\n\n## Constraints\n- 1 <= n <= 9\n\n## Example\n\n**Input**\n```\n4\n```\n**Output**\n```\n.Q..\n...Q\nQ...\n..Q.\n\n..Q.\nQ...\n...Q\n.Q..\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n', expected_output='.Q..\n...Q\nQ...\n..Q.\n\n..Q.\nQ...\n...Q\n.Q..\n', is_hidden=False),
        TestCase(input='1\n', expected_output='Q\n', is_hidden=False),
        TestCase(input='5\n', expected_output='Q....\n..Q..\n....Q\n.Q...\n...Q.\n\nQ....\n...Q.\n.Q...\n....Q\n..Q..\n\n..Q..\nQ....\n....Q\n.Q...\n...Q.\n\n..Q..\n...Q.\nQ....\n....Q\n.Q...\n\n...Q.\nQ....\n..Q..\n....Q\n.Q...\n\n...Q.\n.Q...\n....Q\nQ....\n..Q..\n\n.Q...\n...Q.\nQ....\n..Q..\n....Q\n\n.Q...\n....Q\n..Q..\nQ....\n...Q.\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['palindrome-partitioning'] = {
    "description": '# Palindrome Partitioning\n\n## Statement\nGiven a string `s`, partition s such that every substring of the partition is a palindrome. Return all possible palindrome partitioning of s.\n\n## Input Format\n- A single string `s`\n\n## Output Format\n- Partitions sorted lexicographically, one per line, values (substrings) space-separated\n\n## Constraints\n- 1 <= s.length <= 16\n- s consists of lowercase English letters only\n\n## Example\n\n**Input**\n```\naab\n```\n**Output**\n```\na a b\naa b\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='aab\n', expected_output='a a b\naa b\n', is_hidden=False),
        TestCase(input='a\n', expected_output='a\n', is_hidden=False),
        TestCase(input='aba\n', expected_output='a b a\naba\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['permutations'] = {
    "description": '# Permutations\n\n## Statement\nGiven an array `nums` of distinct integers, return all possible permutations. You can return the answer in any order.\n\n## Input Format\n- First line: integer `n` (number of elements)\n- Second line: `n` space-separated integers\n\n## Output Format\n- Permutations sorted lexicographically, one per line, space-separated values within each permutation\n\n## Constraints\n- 1 <= n <= 6\n- -10 <= nums[i] <= 10\n- All integers in nums are unique\n\n## Example\n\n**Input**\n```\n3\n1 2 3\n```\n**Output**\n```\n1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 3\n', expected_output='1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='2\n0 1\n', expected_output='0 1\n1 0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['subsets'] = {
    "description": '# Subsets\n\n## Statement\nGiven an integer array `nums` of unique elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.\n\n## Input Format\n- First line: integer `n` (number of elements)\n- Second line: `n` space-separated integers\n\n## Output Format\n- Subsets sorted lexicographically, one per line, space-separated values within each subset\n\n## Constraints\n- 1 <= n <= 10\n- -10 <= nums[i] <= 10\n- All integers in nums are unique\n\n## Example\n\n**Input**\n```\n3\n1 2 3\n```\n**Output**\n```\n\n1\n1 2\n1 2 3\n1 3\n2\n2 3\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 3\n', expected_output='\n1\n1 2\n1 2 3\n1 3\n2\n2 3\n3\n', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='\n0\n', is_hidden=False),
        TestCase(input='3\n-1 0 1\n', expected_output='\n-1\n-1 0\n-1 0 1\n-1 1\n0\n0 1\n1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['subsets-ii'] = {
    "description": '# Subsets II\n\n## Statement\nGiven an integer array `nums` that may contain duplicates, return all possible subsets (the power set). The solution set must not contain duplicate subsets. Return the solution in any order.\n\n## Input Format\n- First line: integer `n` (number of elements)\n- Second line: `n` space-separated integers\n\n## Output Format\n- Subsets sorted lexicographically, one per line, space-separated values within each subset\n\n## Constraints\n- 1 <= n <= 10\n- -10 <= nums[i] <= 10\n\n## Example\n\n**Input**\n```\n4\n1 2 2 2\n```\n**Output**\n```\n\n1\n1 2\n1 2 2\n1 2 2 2\n2\n2 2\n2 2 2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 2 2 2\n', expected_output='\n1\n1 2\n1 2 2\n1 2 2 2\n2\n2 2\n2 2 2\n', is_hidden=False),
        TestCase(input='2\n0 1\n', expected_output='\n0\n0 1\n1\n', is_hidden=False),
        TestCase(input='3\n2 2 2\n', expected_output='\n2\n2 2\n2 2 2\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['word-search'] = {
    "description": '# Word Search\n\n## Statement\nGiven an m x n grid of characters `board` and a string `word`, return true if word exists in the grid. The word can be constructed from letters of sequentially adjacent cells (horizontally or vertically). The same cell may not be used more than once.\n\n## Input Format\n- First line: integer `m` (rows) then integer `n` (columns)\n- Next m lines: strings of length n representing the board\n- Last line: string representing the word\n\n## Output Format\n- `true` if the word exists, `false` otherwise\n\n## Constraints\n- 1 <= m, n <= 6\n- 1 <= word.length <= 15\n- board and word consist of lowercase English letters\n\n## Example\n\n**Input**\n```\n3 4\nABCE\nSFCS\nADEE\nABCCED\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 4\nABCE\nSFCS\nADEE\nABCCED\n', expected_output='true\n', is_hidden=False),
        TestCase(input='2 2\nAB\nCD\nAB\n', expected_output='true\n', is_hidden=False),
        TestCase(input='1 1\nA\nB\n', expected_output='false\n', is_hidden=True),
    ],
}

# ===========================================================================
# Greedy
# ===========================================================================

NEETCODE_AUTHORING['gas-station'] = {
    "description": "# Gas Station\n\n## Statement\n\nThere are n gas stations along a circular route, where the amount of gas at the ith station is gas[i].\n\nYou have a car with an unlimited gas tank and it costs cost[i] of gas to travel from the ith station to its next (i + 1)th station. You begin the journey with an empty tank at one of the gas stations.\n\nGiven two integer arrays gas and cost, return the starting gas station's index if you can travel around the circuit once in the clockwise direction, otherwise return -1. If there exists a solution, it is guaranteed to be unique.\n\n## Input Format\n- First line: integer n\n- Second line: n integers (gas amounts)\n- Third line: n integers (costs)\n\n## Output Format\n- Single integer (starting index or -1)\n\n## Constraints\n- n == gas.length == cost.length\n- 1 <= n <= 10^4\n- 0 <= gas[i], cost[i] <= 10^4\n\n## Example\n\n**Input**\n```\n3\n1 2 3\n2 2 2\n```\n\n**Output**\n```\n1\n```",
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    gas = [int(data[idx + i]) for i in range(n)]\n    idx += n\n    cost = [int(data[idx + i]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> gas(n), cost(n);\n    for (int i = 0; i < n; i++) cin >> gas[i];\n    for (int i = 0; i < n; i++) cin >> cost[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] gas = new int[n];\n        for (int i = 0; i < n; i++) gas[i] = sc.nextInt();\n        int[] cost = new int[n];\n        for (int i = 0; i < n; i++) cost[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 3\n2 2 2\n', expected_output='1\n', is_hidden=False),
        TestCase(input='3\n2 3 4\n3 4 3\n', expected_output='-1\n', is_hidden=False),
        TestCase(input='1\n5\n5\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['hand-of-straights'] = {
    "description": '# Hand of Straights\n\n## Statement\n\nAlice has some number of cards and she wants to rearrange the cards into groups so that each group is of size groupSize, and consists of groupSize consecutive cards.\n\nGiven an integer array hand where hand[i] is the value written on the ith card and an integer groupSize, return true if she can rearrange the cards, or false otherwise.\n\n## Input Format\n- First line: two integers n and W (number of cards, group size)\n- Second line: n integers (card values)\n\n## Output Format\n- "true" or "false"\n\n## Constraints\n- 1 <= hand.length <= 10^4\n- 0 <= hand[i] <= 10^9\n- 1 <= groupSize <= hand.length\n\n## Example\n\n**Input**\n```\n6 2\n1 2 3 6 2 3 4 7 8\n```\n\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n, W = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    hand = [int(data[idx + i]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, W;\n    cin >> n >> W;\n    vector<int> hand(n);\n    for (int i = 0; i < n; i++) cin >> hand[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), W = sc.nextInt();\n        int[] hand = new int[n];\n        for (int i = 0; i < n; i++) hand[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='9 3\n1 2 3 6 2 3 4 7 8\n', expected_output='true\n', is_hidden=False),
        TestCase(input='6 2\n1 2 3 4 5 6\n', expected_output='true\n', is_hidden=False),
        TestCase(input='3 3\n1 2 3\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['jump-game'] = {
    "description": '# Jump Game\n\n## Statement\n\nYou are given an integer array nums. You are initially positioned at the array\'s first index, and each element in the array represents your maximum jump length at that position.\n\nReturn true if you can reach the last index, or false otherwise.\n\n## Input Format\n- First line: integer n\n- Second line: n integers\n\n## Output Format\n- "true" or "false"\n\n## Constraints\n- 1 <= nums.length <= 10^4\n- 0 <= nums[i] <= 10^5\n\n## Example\n\n**Input**\n```\n5\n2 3 1 1 4\n```\n\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(data[i + 1]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n2 3 1 1 4\n', expected_output='true\n', is_hidden=False),
        TestCase(input='5\n3 2 1 0 4\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['jump-game-ii'] = {
    "description": "# Jump Game II\n\n## Statement\n\nGiven a non-empty integer array nums, you are initially positioned at the first index of the array. Each element in the array represents your maximum jump length at that position.\n\nYour goal is to reach the last index in the minimum number of jumps.\n\nYou can assume that you can always reach the last index.\n\n## Input Format\n- First line: integer n\n- Second line: n integers\n\n## Output Format\n- Single integer (minimum jumps)\n\n## Constraints\n- 1 <= nums.length <= 10^4\n- 0 <= nums[i] <= 1000\n- It's guaranteed that you can reach nums[n - 1]\n\n## Example\n\n**Input**\n```\n5\n2 3 1 1 4\n```\n\n**Output**\n```\n2\n```",
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(data[i + 1]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n2 3 1 1 4\n', expected_output='2\n', is_hidden=False),
        TestCase(input='5\n2 3 0 1 4\n', expected_output='2\n', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['maximum-subarray'] = {
    "description": '# Maximum Subarray\n\n## Statement\n\nGiven an integer array nums, find the subarray with the largest sum, and return its sum.\n\n## Input Format\n- First line: integer n\n- Second line: n integers\n\n## Output Format\n- Single integer (maximum subarray sum)\n\n## Constraints\n- 1 <= nums.length <= 10^5\n- -10^4 <= nums[i] <= 10^4\n\n## Example\n\n**Input**\n```\n9\n-2 1 -3 4 -1 2 1 -5 4\n```\n\n**Output**\n```\n6\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(data[i + 1]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='9\n-2 1 -3 4 -1 2 1 -5 4\n', expected_output='6\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='5\n5 4 -1 7 8\n', expected_output='23\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['merge-triplets-to-form-target-triplet'] = {
    "description": '# Merge Triplets to Form Target Triplet\n\n## Statement\n\nA triplet is an array of three integers. You are given a 2D integer array triplets, where triplets[i] = [ai, bi, ci] describes the ith triplet. You are also given an integer array target = [x, y, z] that describes the triplet you want to obtain.\n\nTo obtain the target triplet, you may apply the following operation on triplets any number of times (possibly zero):\n- Choose two different triplets [ai, bi, ci] and [aj, bj, cj] and update the triplet to [max(ai, aj), max(bi, bj), max(ci, cj)].\n\nReturn true if it is possible to obtain the target triplet [x, y, z] as an element in triplets using the above operation any number of times. Otherwise, return false.\n\n## Input Format\n- First line: integer m (number of triplets)\n- Next m lines: three integers per line (triplet)\n- Last line: three integers (target)\n\n## Output Format\n- "true" or "false"\n\n## Constraints\n- 1 <= triplets.length <= 10^5\n- triplets[i].length == target.length == 3\n- 1 <= ai, bi, ci, x, y, z <= 1000\n\n## Example\n\n**Input**\n```\n3\n2 5 3\n1 8 4\n1 7 5\n2 7 5\n```\n\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m = int(data[idx])\n    idx += 1\n    triplets = []\n    for i in range(m):\n        a, b, c = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])\n        triplets.append((a, b, c))\n        idx += 3\n    target = (int(data[idx]), int(data[idx + 1]), int(data[idx + 2]))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m;\n    cin >> m;\n    vector<tuple<int,int,int>> triplets(m);\n    for (int i = 0; i < m; i++) {\n        int a, b, c; cin >> a >> b >> c;\n        triplets[i] = {a, b, c};\n    }\n    int x, y, z; cin >> x >> y >> z;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt();\n        int[][] triplets = new int[m][3];\n        for (int i = 0; i < m; i++) { triplets[i][0] = sc.nextInt(); triplets[i][1] = sc.nextInt(); triplets[i][2] = sc.nextInt(); }\n        int x = sc.nextInt(), y = sc.nextInt(), z = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n2 5 3\n1 8 4\n1 7 5\n2 7 5\n', expected_output='true\n', is_hidden=False),
        TestCase(input='2\n2 5 3\n2 3 5\n2 7 5\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1\n1 2 3\n1 2 3\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['partition-labels'] = {
    "description": '# Partition Labels\n\n## Statement\n\nYou are given a string s. We want to partition the string into as many parts as possible so that each letter appears in at most one part. Note that the partition is done so that after concatenating all the parts, the resultant string should be s.\n\nReturn a list of integers representing the size of these parts.\n\n## Input Format\n- Single line: string s\n\n## Output Format\n- Space-separated integers (sizes of parts)\n\n## Constraints\n- 1 <= s.length <= 500\n- s consists of only lowercase English letters\n\n## Example\n\n**Input**\n```\nababcbacadefegdehijhklij\n```\n\n**Output**\n```\n9 7 8\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    s = data\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='ababcbacadefegdehijhklij\n', expected_output='9 7 8\n', is_hidden=False),
        TestCase(input='abcabc\n', expected_output='1 1 1 1 1 1\n', is_hidden=False),
        TestCase(input='a\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['valid-parenthesis-string'] = {
    "description": '# Valid Parenthesis String\n\n## Statement\n\nGiven a string s containing only three types of characters: \'(\', \')\' and \'*\', return true if s is valid.\n\nThe following rules define a valid string:\n- Any left parenthesis \'(\' must have a corresponding right parenthesis \')\'.\n- Any right parenthesis \')\' must have a corresponding left parenthesis \'(\'.\n- Left parenthesis \'(\' must go before the corresponding right parenthesis \')\'.\n- \'*\' could be treated as a single right parenthesis \')\' or a single left parenthesis \'(\' or an empty string.\n\n## Input Format\n- Single line: string s\n\n## Output Format\n- "true" or "false"\n\n## Constraints\n- 1 <= s.length <= 100\n- s[i] is \'(\', \')\' or \'*\'\n\n## Example\n\n**Input**\n```\n(*)\n```\n\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    s = data\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='(*)\n', expected_output='true\n', is_hidden=False),
        TestCase(input='(*))\n', expected_output='true\n', is_hidden=False),
        TestCase(input='(())\n', expected_output='true\n', is_hidden=True),
    ],
}

# ===========================================================================
# Intervals
# ===========================================================================

NEETCODE_AUTHORING['insert-interval'] = {
    "description": '# Insert Interval\n\n## Statement\nYou are given an array of non-overlapping intervals where each interval is sorted\nby its start time. Insert a new interval into the intervals list, merging if necessary.\n\nReturn the resulting array of intervals.\n\n## Input Format\n- Line 1: integer `n` — the number of existing intervals\n- Next `n` lines: each line contains two space-separated integers `start end` — the interval\n- Last line: two space-separated integers `newStart newEnd` — the new interval to insert\n\n## Output Format\nThe merged intervals, one per line, each as `start end`.\n\n## Constraints\n- `0 <= n <= 10^4`\n- `0 <= start <= end <= 10^5`\nThe intervals are sorted by start time.\n\n## Example\n\n**Input**\n```\n4\n1 3\n6 9\n2 7\n10 15\n```\n**Output**\n```\n1 9\n10 15\n```\nExplanation: The new interval [2, 7] overlaps with [1, 3] and [6, 9],\nso they merge into [1, 9].',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    intervals = []\n    for _ in range(n):\n        intervals.append([int(data[idx]), int(data[idx + 1])])\n        idx += 2\n    newStart = int(data[idx])\n    newEnd = int(data[idx + 1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> intervals(n, vector<int>(2));\n    for (auto& iv : intervals) cin >> iv[0] >> iv[1];\n    int newStart, newEnd;\n    cin >> newStart >> newEnd;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        List<int[]> intervals = new ArrayList<>();\n        for (int i = 0; i < n; i++) {\n            intervals.add(new int[]{sc.nextInt(), sc.nextInt()});\n        }\n        int newStart = sc.nextInt(), newEnd = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 3\n6 9\n2 7\n10 15\n', expected_output='1 9\n10 15', is_hidden=False),
        TestCase(input='0\n2 5\n', expected_output='2 5', is_hidden=False),
        TestCase(input='2\n1 2\n3 5\n6 7\n', expected_output='1 2\n3 5\n6 7', is_hidden=True),
        TestCase(input='1\n1 5\n2 3\n', expected_output='1 5', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['meeting-rooms'] = {
    "description": '# Meeting Rooms\n\n## Statement\nGiven an array of meeting time intervals where each interval is `[start, end]`,\ndetermine if a person could attend all meetings without any overlaps.\n\n## Input Format\n- Line 1: integer `n` — the number of intervals\n- Next `n` lines: each line contains two space-separated integers `start end`\n\n## Output Format\nA single line: `true` if all meetings can be attended, otherwise `false`.\n\n## Constraints\n- `0 <= n <= 10^4`\n- `0 <= start < end <= 10^6`\n\n## Example\n\n**Input**\n```\n3\n0 30\n5 10\n15 20\n```\n**Output**\n```\nfalse\n```\nExplanation: The person cannot attend all meetings because [5, 10] and [15, 20]\noverlap with [0, 30].',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    intervals = []\n    for _ in range(n):\n        intervals.append([int(data[idx]), int(data[idx + 1])])\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> intervals(n, vector<int>(2));\n    for (auto& iv : intervals) cin >> iv[0] >> iv[1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        List<int[]> intervals = new ArrayList<>();\n        for (int i = 0; i < n; i++) {\n            intervals.add(new int[]{sc.nextInt(), sc.nextInt()});\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n0 30\n5 10\n15 20\n', expected_output='false', is_hidden=False),
        TestCase(input='2\n7 10\n2 4\n', expected_output='true', is_hidden=False),
        TestCase(input='0\n', expected_output='true', is_hidden=True),
        TestCase(input='1\n0 5\n', expected_output='true', is_hidden=True),
        TestCase(input='3\n1 2\n3 4\n5 6\n', expected_output='true', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['meeting-rooms-ii'] = {
    "description": "# Meeting Rooms II\n\n## Statement\nGiven an array of meeting time intervals where each interval is `[start, end]`,\nfind the minimum number of conference rooms required.\n\n## Input Format\n- Line 1: integer `n` — the number of intervals\n- Next `n` lines: each line contains two space-separated integers `start end`\n\n## Output Format\nA single integer — the minimum number of conference rooms required.\n\n## Constraints\n- `1 <= n <= 10^4`\n- `0 <= start < end <= 10^6`\n\n## Example\n\n**Input**\n```\n3\n0 30\n5 10\n15 20\n```\n**Output**\n```\n2\n```\nExplanation: The meeting [0, 30] runs the entire time. [5, 10] and [15, 20]\ncan use a second room since they don't overlap with each other but do overlap\nwith [0, 30].",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    intervals = []\n    for _ in range(n):\n        intervals.append([int(data[idx]), int(data[idx + 1])])\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> intervals(n, vector<int>(2));\n    for (auto& iv : intervals) cin >> iv[0] >> iv[1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        List<int[]> intervals = new ArrayList<>();\n        for (int i = 0; i < n; i++) {\n            intervals.add(new int[]{sc.nextInt(), sc.nextInt()});\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n0 30\n5 10\n15 20\n', expected_output='2', is_hidden=False),
        TestCase(input='2\n7 10\n2 4\n', expected_output='1', is_hidden=False),
        TestCase(input='3\n1 3\n2 4\n5 6\n', expected_output='2', is_hidden=True),
        TestCase(input='1\n0 5\n', expected_output='1', is_hidden=True),
        TestCase(input='4\n1 5\n2 3\n4 6\n5 7\n', expected_output='3', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['merge-intervals'] = {
    "description": '# Merge Intervals\n\n## Statement\nGiven an array of intervals where `intervals[i] = [starti, endi]`, merge all\noverlapping intervals, and return an array of the non-overlapping intervals that\ncover all the intervals in the input. The intervals are not necessarily sorted.\n\n## Input Format\n- Line 1: integer `n` — the number of intervals\n- Next `n` lines: each line contains two space-separated integers `start end`\n\n## Output Format\nThe merged intervals, one per line, each as `start end`, sorted by start time.\n\n## Constraints\n- `1 <= n <= 10^4`\n- `0 <= starti <= endi <= 10^4`\n\n## Example\n\n**Input**\n```\n4\n1 3\n2 6\n8 10\n15 18\n```\n**Output**\n```\n1 6\n8 10\n15 18\n```\nExplanation: Since intervals [1, 3] and [2, 6] overlap, they merge into [1, 6].',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    intervals = []\n    for _ in range(n):\n        intervals.append([int(data[idx]), int(data[idx + 1])])\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> intervals(n, vector<int>(2));\n    for (auto& iv : intervals) cin >> iv[0] >> iv[1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        List<int[]> intervals = new ArrayList<>();\n        for (int i = 0; i < n; i++) {\n            intervals.add(new int[]{sc.nextInt(), sc.nextInt()});\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 3\n2 6\n8 10\n15 18\n', expected_output='1 6\n8 10\n15 18', is_hidden=False),
        TestCase(input='2\n1 4\n4 5\n', expected_output='1 5', is_hidden=False),
        TestCase(input='1\n1 1\n', expected_output='1 1', is_hidden=True),
        TestCase(input='3\n1 10\n2 3\n5 8\n', expected_output='1 10', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['non-overlapping-intervals'] = {
    "description": '# Non-overlapping Intervals\n\n## Statement\nGiven an array of intervals where `intervals[i] = [starti, endi]`, return the\nminimum number of intervals you need to remove to make the rest of the intervals\nnon-overlapping.\n\nTwo intervals overlap if their intersection is non-empty.\n\n## Input Format\n- Line 1: integer `n` — the number of intervals\n- Next `n` lines: each line contains two space-separated integers `start end`\n\n## Output Format\nA single integer — the minimum number of intervals to remove.\n\n## Constraints\n- `1 <= n <= 10^4`\n- `-5 * 10^4 <= starti < endi <= 5 * 10^4`\n\n## Example\n\n**Input**\n```\n4\n1 2\n2 3\n3 4\n1 3\n```\n**Output**\n```\n1\n```\nExplanation: Remove interval [1, 3] to make the rest [1, 2], [2, 3], [3, 4]\nnon-overlapping.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    intervals = []\n    for _ in range(n):\n        intervals.append([int(data[idx]), int(data[idx + 1])])\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> intervals(n, vector<int>(2));\n    for (auto& iv : intervals) cin >> iv[0] >> iv[1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        List<int[]> intervals = new ArrayList<>();\n        for (int i = 0; i < n; i++) {\n            intervals.add(new int[]{sc.nextInt(), sc.nextInt()});\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 2\n2 3\n3 4\n1 3\n', expected_output='1', is_hidden=False),
        TestCase(input='2\n1 2\n1 2\n', expected_output='1', is_hidden=False),
        TestCase(input='1\n1 2\n', expected_output='0', is_hidden=True),
        TestCase(input='3\n1 2\n2 3\n3 4\n', expected_output='0', is_hidden=True),
    ],
}

# ===========================================================================
# Math & Geometry
# ===========================================================================

NEETCODE_AUTHORING['detect-squares'] = {
    "description": '# Detect Squares\n\n## Statement\n\nYou are given an array of points in the X-Y plane points where points[i] = [xi, yi].\n\nDesign an algorithm to:\n- Add new points from a given stream of points one at a time.\n- Count the number of squares that can be formed from a given set of points.\n\nImplement the DetectSquares class:\n- `DetectSquares()`: Initializes the object of an empty data structure.\n- `void add(int[] point)`: Adds a new point to the data structure.\n- `int count(int[] point)`: Counts the number of squares that can be formed using the point as one of the vertices. Note that the point can be one of the previously added points.\n\n## Input Format\n- First line: integer q (number of operations)\n- Next q lines: operations\n  - `add x y`\n  - `count x y`\n\n## Output Format\n- For each count operation, output the count\n\n## Constraints\n- 1 <= points.length <= 1000\n- 1 <= q <= 1000\n- 1 <= point.length <= 2\n- -10^4 <= x, y <= 10^4\n- All added points are unique\n\n## Example\n\n**Input**\n```\n6\nadd 3 10\nadd 1 2\nadd 2 2\nadd 4 2\ncount 3 10\ncount 1 2\n```\n\n**Output**\n```\n1\n1\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    q = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int q;\n    cin >> q;\n    cin.ignore();\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int q = Integer.parseInt(sc.nextLine().trim());\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6\nadd 3 10\nadd 1 2\nadd 2 2\nadd 4 2\ncount 3 10\ncount 1 2\n', expected_output='1\n1\n', is_hidden=False),
        TestCase(input='4\nadd 0 0\nadd 0 1\nadd 1 1\ncount 0 0\n', expected_output='1\n', is_hidden=False),
        TestCase(input='3\nadd 1 1\nadd 2 2\ncount 1 1\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['happy-number'] = {
    "description": '# Happy Number\n\n## Statement\n\nWrite an algorithm to determine if a number n is happy.\n\nA happy number is a number defined by the following process:\n- Starting with any positive integer, replace the number by the sum of the squares of its digits.\n- Repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a cycle which does not include 1.\n- Those numbers for which this process ends in 1 are happy.\n\nReturn true if n is happy, otherwise false.\n\n## Input Format\n- Single line: integer n\n\n## Output Format\n- "true" or "false"\n\n## Constraints\n- 1 <= n <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n19\n```\n\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    n = int(data)\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='19\n', expected_output='true\n', is_hidden=False),
        TestCase(input='2\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['multiply-strings'] = {
    "description": '# Multiply Strings\n\n## Statement\n\nGiven two non-negative integers num1 and num2 represented as strings, return the product of num1 and num2, also represented as a string.\n\nYou must not use any built-in BigInteger library or convert the inputs to integer directly.\n\n## Input Format\n- First line: string num1\n- Second line: string num2\n\n## Output Format\n- Single string (product)\n\n## Constraints\n- 1 <= num1.length, num2.length <= 200\n- num1 and num2 consist of digits only\n- Both num1 and num2 do not contain any leading zero, except the number 0 itself\n\n## Example\n\n**Input**\n```\n2\n3\n```\n\n**Output**\n```\n6\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    num1 = data[0].strip()\n    num2 = data[1].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string num1, num2;\n    cin >> num1 >> num2;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String num1 = sc.nextLine().trim();\n        String num2 = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2\n3\n', expected_output='6\n', is_hidden=False),
        TestCase(input='123\n456\n', expected_output='56088\n', is_hidden=False),
        TestCase(input='0\n0\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['plus-one'] = {
    "description": '# Plus One\n\n## Statement\n\nYou are given a large integer represented as an integer array digits, where each digits[i] is the ith digit of the number. The digits are ordered from most significant to least significant in left-to-right order. The large integer does not contain any leading zeros.\n\nIncrement the large integer by one and return the resulting array of digits.\n\n## Input Format\n- First line: integer n (number of digits)\n- Second line: n digits separated by spaces\n\n## Output Format\n- Space-separated integers (resulting digits)\n\n## Constraints\n- 1 <= digits.length <= 100\n- 0 <= digits[i] <= 9\n- digits does not contain any leading zeros\n\n## Example\n\n**Input**\n```\n3\n1 2 3\n```\n\n**Output**\n```\n1 2 4\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    digits = [int(data[idx + i]) for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> digits(n);\n    for (int i = 0; i < n; i++) cin >> digits[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] digits = new int[n];\n        for (int i = 0; i < n; i++) digits[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 3\n', expected_output='1 2 4\n', is_hidden=False),
        TestCase(input='4\n4 3 2 1\n', expected_output='4 3 2 2\n', is_hidden=False),
        TestCase(input='1\n9\n', expected_output='1 0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['powx-n'] = {
    "description": '# Pow(x, n)\n\n## Statement\n\nImplement pow(x, n), which calculates x raised to the power n (i.e., x^n).\n\n## Input Format\n- Single line: two numbers x and n (separated by space)\n\n## Output Format\n- Single float (x^n formatted to 5 decimal places)\n\n## Constraints\n- -100.0 < x < 100.0\n- -2^31 <= n <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n2.00000 10\n```\n\n**Output**\n```\n1024.00000\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    x = float(data[0])\n    n = int(data[1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    double x;\n    int n;\n    cin >> x >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        double x = sc.nextDouble();\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2.00000 10\n', expected_output='1024.00000\n', is_hidden=False),
        TestCase(input='2.10000 3\n', expected_output='9.26100\n', is_hidden=False),
        TestCase(input='0.00001 2147483647\n', expected_output='0.00000\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['rotate-image'] = {
    "description": '# Rotate Image\n\n## Statement\n\nYou are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).\n\nYou have to rotate the image in-place, which means you have to modify the input 2D matrix directly. Do not allocate another 2D matrix and do the rotation.\n\n## Input Format\n- First line: integer n\n- Next n lines: n integers per line\n\n## Output Format\n- n lines: n integers per line (rotated matrix)\n\n## Constraints\n- n == matrix.length == matrix[i].length\n- 1 <= n <= 20\n- -1000 <= matrix[i][j] <= 1000\n\n## Example\n\n**Input**\n```\n3\n1 2 3\n4 5 6\n7 8 9\n```\n\n**Output**\n```\n7 4 1\n8 5 2\n9 6 3\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    matrix = []\n    for i in range(n):\n        row = [int(data[idx + j]) for j in range(n)]\n        matrix.append(row)\n        idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> matrix(n, vector<int>(n));\n    for (int i = 0; i < n; i++)\n        for (int j = 0; j < n; j++) cin >> matrix[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[][] matrix = new int[n][n];\n        for (int i = 0; i < n; i++)\n            for (int j = 0; j < n; j++) matrix[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 3\n4 5 6\n7 8 9\n', expected_output='7 4 1\n8 5 2\n9 6 3\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='2\n1 2\n3 4\n', expected_output='3 1\n4 2\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['set-matrix-zeroes'] = {
    "description": "# Set Matrix Zeroes\n\n## Statement\n\nGiven an m x n matrix, if an element is 0, set its entire row and column to 0's.\n\nYou must do it in place.\n\n## Input Format\n- First line: two integers m and n\n- Next m lines: n integers per line\n\n## Output Format\n- m lines: n integers per line (modified matrix)\n\n## Constraints\n- 1 <= m, n <= 200\n- -2^31 <= matrix[i][j] <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n3 3\n1 1 1\n1 0 1\n1 1 1\n```\n\n**Output**\n```\n1 0 1\n0 0 0\n1 0 1\n```",
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m, n = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    matrix = []\n    for i in range(m):\n        row = [int(data[idx + j]) for j in range(n)]\n        matrix.append(row)\n        idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> matrix(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++) cin >> matrix[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] matrix = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++) matrix[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 3\n1 1 1\n1 0 1\n1 1 1\n', expected_output='1 0 1\n0 0 0\n1 0 1\n', is_hidden=False),
        TestCase(input='2 3\n0 1 2 0 5 6\n', expected_output='0 0 0\n0 5 6\n', is_hidden=False),
        TestCase(input='1 1\n0\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['spiral-matrix'] = {
    "description": '# Spiral Matrix\n\n## Statement\n\nGiven an m x n matrix, return all elements of the matrix in spiral order.\n\n## Input Format\n- First line: two integers m and n\n- Next m lines: n integers per line\n\n## Output Format\n- Space-separated integers (spiral order)\n\n## Constraints\n- 1 <= m, n <= 10\n- -100 <= matrix[i][j] <= 100\n\n## Example\n\n**Input**\n```\n3 3\n1 2 3\n4 5 6\n7 8 9\n```\n\n**Output**\n```\n1 2 3 6 9 8 7 4 5\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m, n = int(data[idx]), int(data[idx + 1])\n    idx += 2\n    matrix = []\n    for i in range(m):\n        row = [int(data[idx + j]) for j in range(n)]\n        matrix.append(row)\n        idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> matrix(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++) cin >> matrix[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] matrix = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++) matrix[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 3\n1 2 3\n4 5 6\n7 8 9\n', expected_output='1 2 3 6 9 8 7 4 5\n', is_hidden=False),
        TestCase(input='1 4\n1 2 3 4\n', expected_output='1 2 3 4\n', is_hidden=False),
        TestCase(input='3 1\n1\n2\n3\n', expected_output='1 2 3\n', is_hidden=True),
    ],
}

# ===========================================================================
# Bit Manipulation
# ===========================================================================

NEETCODE_AUTHORING['counting-bits'] = {
    "description": "# Counting Bits\n\n## Statement\n\nGiven an integer `n`, return an array `ans` of length `n + 1` such that for each `i` (0 <= i <= n), `ans[i]` is the number of 1's in the binary representation of `i`.\n\n## Input Format\n\n- A single integer `n`.\n\n## Output Format\n\n- Space-separated integers representing the count of 1 bits from 0 to n.\n\n## Constraints\n\n- 0 <= n <= 2 * 10^5\n\n## Example\n\n**Input**\n```\n5\n```\n**Output**\n```\n0 1 1 2 1 2\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n', expected_output='0 1 1 2 1 2', is_hidden=False),
        TestCase(input='0\n', expected_output='0', is_hidden=False),
        TestCase(input='10\n', expected_output='0 1 1 2 1 2 2 3 1 2 2', is_hidden=True),
        TestCase(input='2\n', expected_output='0 1 1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['missing-number'] = {
    "description": '# Missing Number\n\n## Statement\n\nGiven an array `nums` containing `n` distinct numbers in the range `[0, n]`, return the only number in the range that is missing from the array.\n\n## Input Format\n\n- The first line contains an integer `n`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- A single integer representing the missing number.\n\n## Constraints\n\n- n == nums.length\n- 1 <= n <= 10^4\n- 0 <= nums[i] <= n\n- All the numbers of `nums` are unique.\n\n## Example\n\n**Input**\n```\n3\n3 0 1\n```\n**Output**\n```\n2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n3 0 1\n', expected_output='2', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='1', is_hidden=False),
        TestCase(input='9\n9 6 4 2 3 5 7 0 1\n', expected_output='8', is_hidden=True),
        TestCase(input='2\n1 0\n', expected_output='2', is_hidden=True),
        TestCase(input='2\n0 1\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['number-of-1-bits'] = {
    "description": '# Number of 1 Bits\n\n## Statement\n\nWrite a function that takes the binary representation of a positive integer and returns the number of set bits it has (also known as the Hamming weight).\n\n## Input Format\n\n- A single integer `n`.\n\n## Output Format\n\n- A single integer representing the number of 1 bits.\n\n## Constraints\n\n- 1 <= n <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n11\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    unsigned int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='11\n', expected_output='3', is_hidden=False),
        TestCase(input='128\n', expected_output='1', is_hidden=False),
        TestCase(input='2147483645\n', expected_output='30', is_hidden=True),
        TestCase(input='1\n', expected_output='1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reverse-bits'] = {
    "description": '# Reverse Bits\n\n## Statement\n\nReverse bits of a given 32 bits unsigned integer.\n\n## Input Format\n\n- A single integer `n`.\n\n## Output Format\n\n- A single integer representing the reversed bits.\n\n## Constraints\n\n- The input must be a 32-bit unsigned integer.\n- 0 <= n <= 2^32 - 1\n\n## Example\n\n**Input**\n```\n43261596\n```\n**Output**\n```\n964176192\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    uint32_t n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        long n = sc.nextLong();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='43261596\n', expected_output='964176192', is_hidden=False),
        TestCase(input='4294967293\n', expected_output='3221225471', is_hidden=False),
        TestCase(input='0\n', expected_output='0', is_hidden=True),
        TestCase(input='1\n', expected_output='2147483648', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reverse-integer'] = {
    "description": '# Reverse Integer\n\n## Statement\n\nGiven a signed 32-bit integer `x`, return `x` with its digits reversed. If reversing `x` causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return `0`.\n\n## Input Format\n\n- A single integer `n`.\n\n## Output Format\n\n- A single integer representing the reversed number, or `0` if overflow.\n\n## Constraints\n\n- -2^31 <= n <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n123\n```\n**Output**\n```\n321\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='123\n', expected_output='321', is_hidden=False),
        TestCase(input='-123\n', expected_output='-321', is_hidden=False),
        TestCase(input='120\n', expected_output='21', is_hidden=True),
        TestCase(input='1534236469\n', expected_output='0', is_hidden=True),
        TestCase(input='0\n', expected_output='0', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['single-number'] = {
    "description": '# Single Number\n\n## Statement\n\nGiven a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.\n\nYou must implement a solution with a linear runtime complexity and use only constant extra space.\n\n## Input Format\n\n- The first line contains an integer `n`.\n- The second line contains `n` space-separated integers.\n\n## Output Format\n\n- A single integer representing the number that appears only once.\n\n## Constraints\n\n- 1 <= n <= 3 * 10^4\n- -3 * 10^4 <= nums[i] <= 3 * 10^4\n- Each element in the array appears twice except for one element which appears only once.\n\n## Example\n\n**Input**\n```\n5\n4 1 2 1 2\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n4 1 2 1 2\n', expected_output='4', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1', is_hidden=False),
        TestCase(input='7\n2 2 3 3 4 4 5\n', expected_output='5', is_hidden=True),
        TestCase(input='3\n-1 -1 -2\n', expected_output='-2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['sum-of-two-integers'] = {
    "description": '# Sum of Two Integers\n\n## Statement\n\nGiven two integers `a` and `b`, return the sum of the two integers without using the operators `+` and `-`.\n\n## Input Format\n\n- A single line containing two integers `a` and `b`.\n\n## Output Format\n\n- A single integer representing the sum.\n\n## Constraints\n\n- -1000 <= a, b <= 1000\n\n## Example\n\n**Input**\n```\n1 2\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    a, b = int(data[0]), int(data[1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt(), b = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2\n', expected_output='3', is_hidden=False),
        TestCase(input='2 3\n', expected_output='5', is_hidden=False),
        TestCase(input='-1 1\n', expected_output='0', is_hidden=True),
        TestCase(input='0 0\n', expected_output='0', is_hidden=True),
        TestCase(input='-5 -3\n', expected_output='-8', is_hidden=True),
    ],
}

# ===========================================================================
# Graphs
# ===========================================================================

NEETCODE_AUTHORING['clone-graph'] = {
    "description": '# Clone Graph\n\n## Statement\nGiven a reference of a node in a connected undirected graph, return a deep copy\n(clone) of the graph. Each node contains a value (integer) and a list of neighbors.\n\n## Input Format\n- Line 1: integer `n` -- the number of nodes (labeled 1 to n)\n- Next `n` lines: for node `i`, the line contains its neighbors as space-separated\n  integers. An empty line means no neighbors.\n\n## Output Format\nBFS traversal of the cloned graph starting from node 1, as space-separated integers.\n\n## Constraints\n- `1 <= n <= 100`\n- `1 <= Node.val <= 100`\n- The graph is connected and has no self-loops or duplicate edges.\n\n## Example\n\n**Input**\n```\n4\n2 4\n1 3\n2 4\n1 3\n```\n**Output**\n```\n1 2 3 4\n```\nExplanation: The graph is a cycle 1-2-3-4-1. The clone is an identical copy.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    adj = [[] for _ in range(n + 1)]\n    for i in range(1, n + 1):\n        if data[i].strip():\n            adj[i] = list(map(int, data[i].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    cin.ignore();\n    vector<vector<int>> adj(n + 1);\n    for (int i = 1; i <= n; i++) {\n        string line;\n        getline(cin, line);\n        if (!line.empty()) {\n            stringstream ss(line);\n            int x;\n            while (ss >> x) adj[i].push_back(x);\n        }\n    }\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Integer.parseInt(sc.nextLine().trim());\n        List<List<Integer>> adj = new ArrayList<>();\n        adj.add(new ArrayList<>());\n        for (int i = 0; i < n; i++) {\n            String line = sc.nextLine().trim();\n            List<Integer> neighbors = new ArrayList<>();\n            if (!line.isEmpty()) {\n                for (String s : line.split(" ")) neighbors.add(Integer.parseInt(s));\n            }\n            adj.add(neighbors);\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n2 4\n1 3\n2 4\n1 3\n', expected_output='1 2 3 4', is_hidden=False),
        TestCase(input='1\n\n', expected_output='1', is_hidden=False),
        TestCase(input='2\n2\n1\n', expected_output='1 2', is_hidden=True),
        TestCase(input='3\n2 3\n1 3\n1 2\n', expected_output='1 2 3', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['course-schedule'] = {
    "description": '# Course Schedule\n\n## Statement\nThere are a total of `numCourses` courses you have to take, labeled from 0 to\n`numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] =\n[a, b]` indicates that you must take course `b` before course `a`. Return `true` if\nyou can finish all courses. Otherwise, return `false`.\n\n## Input Format\n- Line 1: integer `numCourses` and integer `p` -- the number of courses and prerequisites\n- Next `p` lines: each line contains two integers `a b` (prerequisite: take `b` before `a`)\n\n## Output Format\n`true` or `false`\n\n## Constraints\n- `1 <= numCourses <= 2000`\n- `0 <= p <= 5000`\n- All prerequisite pairs are unique.\n\n## Example\n\n**Input**\n```\n4 3\n1 0\n2 1\n3 2\n```\n**Output**\n```\ntrue\n```\nExplanation: You can take courses in order: 0, 1, 2, 3.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    parts = data[0].split()\n    numCourses = int(parts[0])\n    p = int(parts[1])\n    prerequisites = []\n    for i in range(1, p + 1):\n        a, b = map(int, data[i].split())\n        prerequisites.append([a, b])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int numCourses, p;\n    cin >> numCourses >> p;\n    vector<vector<int>> prerequisites(p, vector<int>(2));\n    for (int i = 0; i < p; i++)\n        cin >> prerequisites[i][0] >> prerequisites[i][1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int numCourses = sc.nextInt(), p = sc.nextInt();\n        int[][] prerequisites = new int[p][2];\n        for (int i = 0; i < p; i++) {\n            prerequisites[i][0] = sc.nextInt();\n            prerequisites[i][1] = sc.nextInt();\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 3\n1 0\n2 1\n3 2\n', expected_output='true', is_hidden=False),
        TestCase(input='2 2\n1 0\n0 1\n', expected_output='false', is_hidden=False),
        TestCase(input='1 0\n', expected_output='true', is_hidden=True),
        TestCase(input='3 2\n1 0\n2 0\n', expected_output='true', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['course-schedule-ii'] = {
    "description": '# Course Schedule II\n\n## Statement\nThere are a total of `numCourses` courses you have to take, labeled from 0 to\n`numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] =\n[a, b]` indicates that you must take course `b` before course `a`. Return the ordering\nof courses you should take to finish all courses. If there are multiple valid orders,\nreturn any. If impossible, return an empty array.\n\n## Input Format\n- Line 1: integers `numCourses p` -- the number of courses and prerequisites\n- Next `p` lines: each line contains two integers `a b`\n\n## Output Format\nSpace-separated course order, or an empty line if impossible.\n\n## Constraints\n- `1 <= numCourses <= 2000`\n- `0 <= p <= 5000`\n\n## Example\n\n**Input**\n```\n4 3\n1 0\n2 1\n3 2\n```\n**Output**\n```\n0 1 2 3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    parts = data[0].split()\n    numCourses = int(parts[0])\n    p = int(parts[1])\n    prerequisites = []\n    for i in range(1, p + 1):\n        a, b = map(int, data[i].split())\n        prerequisites.append([a, b])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int numCourses, p;\n    cin >> numCourses >> p;\n    vector<vector<int>> prerequisites(p, vector<int>(2));\n    for (int i = 0; i < p; i++)\n        cin >> prerequisites[i][0] >> prerequisites[i][1];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int numCourses = sc.nextInt(), p = sc.nextInt();\n        int[][] prerequisites = new int[p][2];\n        for (int i = 0; i < p; i++) {\n            prerequisites[i][0] = sc.nextInt();\n            prerequisites[i][1] = sc.nextInt();\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 3\n1 0\n2 1\n3 2\n', expected_output='0 1 2 3', is_hidden=False),
        TestCase(input='2 2\n1 0\n0 1\n', expected_output='', is_hidden=False),
        TestCase(input='3 0\n', expected_output='0 1 2', is_hidden=True),
        TestCase(input='1 0\n', expected_output='0', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['graph-valid-tree'] = {
    "description": '# Graph Valid Tree\n\n## Statement\nGiven `n` nodes labeled from 0 to n-1 and a list of undirected edges, determine if\nthe edges form a valid tree. A valid tree is connected and has exactly `n - 1` edges.\n\n## Input Format\n- Line 1: integers `n m` -- the number of nodes and edges\n- Next `m` lines: each line contains two integers `a b` -- an edge\n\n## Output Format\n`true` or `false`\n\n## Constraints\n- `1 <= n <= 100`\n- `0 <= m <= n * (n-1) / 2`\n\n## Example\n\n**Input**\n```\n5 4\n0 1\n0 2\n0 3\n3 4\n```\n**Output**\n```\ntrue\n```\nExplanation: This is a valid tree with 5 nodes and 4 edges.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n, m = map(int, data[0].split())\n    edges = []\n    for i in range(1, m + 1):\n        a, b = map(int, data[i].split())\n        edges.append([a, b])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, m;\n    cin >> n >> m;\n    vector<pair<int,int>> edges(m);\n    for (int i = 0; i < m; i++)\n        cin >> edges[i].first >> edges[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), m = sc.nextInt();\n        int[][] edges = new int[m][2];\n        for (int i = 0; i < m; i++) {\n            edges[i][0] = sc.nextInt();\n            edges[i][1] = sc.nextInt();\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5 4\n0 1\n0 2\n0 3\n3 4\n', expected_output='true', is_hidden=False),
        TestCase(input='4 4\n0 1\n1 2\n2 3\n3 0\n', expected_output='false', is_hidden=False),
        TestCase(input='1 0\n', expected_output='true', is_hidden=True),
        TestCase(input='3 2\n0 1\n1 2\n', expected_output='true', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['max-area-of-island'] = {
    "description": '# Max Area of Island\n\n## Statement\nYou are given an `m x n` binary matrix `grid`. An island is a group of `1`s\n(land) connected 4-directionally. The area of an island is the number of cells\nwith `1` values on the island. Return the maximum area of any island in the grid.\nIf there is no island, return 0.\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the grid\n- Next `m` lines: each line contains `n` characters (`0` or `1`) separated by spaces\n\n## Output Format\nA single integer -- the maximum area.\n\n## Constraints\n- `1 <= m, n <= 50`\n- `grid[i][j]` is `0` or `1`.\n\n## Example\n\n**Input**\n```\n4 5\n0 0 1 0 0\n0 0 1 1 0\n0 0 0 1 0\n0 0 0 0 0\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    grid = []\n    for i in range(1, m + 1):\n        grid.append(data[i].split())\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<char>> grid(m, vector<char>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> grid[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] grid = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                grid[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 5\n0 0 1 0 0\n0 0 1 1 0\n0 0 0 1 0\n0 0 0 0 0\n', expected_output='4', is_hidden=False),
        TestCase(input='3 3\n1 1 1\n1 0 1\n1 1 1\n', expected_output='8', is_hidden=False),
        TestCase(input='2 2\n0 0\n0 0\n', expected_output='0', is_hidden=True),
        TestCase(input='2 2\n1 1\n1 1\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['number-of-connected-components-in-an-undirected-graph'] = {
    "description": '# Number of Connected Components in an Undirected Graph\n\n## Statement\nYou have `n` nodes labeled from 0 to n-1 and a list of undirected edges. Count the\nnumber of connected components in the graph.\n\n## Input Format\n- Line 1: integer `n` -- the number of nodes\n- Line 2: integer `m` -- the number of edges\n- Next `m` lines: each line contains two integers `a b` -- an edge\n\n## Output Format\nA single integer -- the number of connected components.\n\n## Constraints\n- `1 <= n <= 100`\n- `0 <= m <= n * (n-1) / 2`\n- No duplicate edges or self-loops.\n\n## Example\n\n**Input**\n```\n5\n4\n0 1\n1 2\n3 4\n```\n**Output**\n```\n2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    m = int(data[1])\n    edges = []\n    for i in range(2, 2 + m):\n        a, b = map(int, data[i].split())\n        edges.append([a, b])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, m;\n    cin >> n >> m;\n    vector<pair<int,int>> edges(m);\n    for (int i = 0; i < m; i++)\n        cin >> edges[i].first >> edges[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), m = sc.nextInt();\n        int[][] edges = new int[m][2];\n        for (int i = 0; i < m; i++) {\n            edges[i][0] = sc.nextInt();\n            edges[i][1] = sc.nextInt();\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n4\n0 1\n1 2\n3 4\n', expected_output='2', is_hidden=False),
        TestCase(input='3\n0\n', expected_output='3', is_hidden=False),
        TestCase(input='4\n3\n0 1\n1 2\n2 3\n', expected_output='1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['number-of-islands'] = {
    "description": '# Number of Islands\n\n## Statement\nGiven an `m x n` 2D binary grid `grid` which represents a map of `1`s (land) and `0`s\n(water), return the number of islands. An island is surrounded by water and is formed\nby connecting adjacent lands horizontally or vertically. You may assume all four edges\nof the grid are all surrounded by water.\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the grid\n- Next `m` lines: each line contains `n` characters (`0` or `1`) separated by spaces\n\n## Output Format\nA single integer -- the number of islands.\n\n## Constraints\n- `1 <= m, n <= 300`\n- `grid[i][j]` is `0` or `1`.\n\n## Example\n\n**Input**\n```\n4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0\n```\n**Output**\n```\n1\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    grid = []\n    for i in range(1, m + 1):\n        grid.append(data[i].split())\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<char>> grid(m, vector<char>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> grid[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        char[][] grid = new char[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                grid[i][j] = sc.next().charAt(0);\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0\n', expected_output='1', is_hidden=False),
        TestCase(input='3 3\n1 0 1\n0 1 0\n1 0 1\n', expected_output='5', is_hidden=False),
        TestCase(input='1 1\n0\n', expected_output='0', is_hidden=True),
        TestCase(input='3 4\n1 1 1 1\n0 0 0 0\n1 1 1 1\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['pacific-atlantic-water-flow'] = {
    "description": '# Pacific Atlantic Water Flow\n\n## Statement\nThere is an `m x n` rectangular island that borders both the Pacific and Atlantic oceans.\nRain water can flow in 4 directions (up, down, left, right) from a cell to an adjacent\ncell with height equal or lower. Find all cells where water can flow to both the Pacific\nand Atlantic oceans.\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the grid\n- Next `m` lines: each line contains `n` integers (heights) separated by spaces\n\n## Output Format\nEach cell that can reach both oceans, one per line as `row col` (0-indexed), sorted\nlexicographically.\n\n## Constraints\n- `1 <= m, n <= 200`\n- `0 <= heights[r][c] <= 10^5`\n\n## Example\n\n**Input**\n```\n5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4\n```\n**Output**\n```\n0 4\n1 3\n1 4\n2 2\n3 0\n3 1\n4 0\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    heights = []\n    for i in range(1, m + 1):\n        heights.append(list(map(int, data[i].split())))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> heights(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> heights[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] heights = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                heights[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5 5\n1 2 2 3 5\n3 2 3 4 4\n2 4 5 3 1\n6 7 1 4 5\n5 1 1 2 4\n', expected_output='0 4\n1 3\n1 4\n2 2\n3 0\n3 1\n4 0', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='0 0', is_hidden=False),
        TestCase(input='2 2\n1 1\n1 1\n', expected_output='0 0\n0 1\n1 0\n1 1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['redundant-connection'] = {
    "description": '# Redundant Connection\n\n## Statement\nIn this problem, a tree is an undirected graph that is connected and has no cycles.\nYou are given a graph that started as a tree with `n` nodes labeled 1 to n, with one\nadditional edge added. The added edge has two different vertices chosen from 1 to n,\nand was not an edge that previously existed. The resulting graph has `n` edges and\n`n` vertices. Return an edge that can be removed so that the resulting graph is a\ntree of `n` nodes. If there are multiple answers, return the one with the smallest\nlabel.\n\n## Input Format\n- Line 1: integer `n` -- the number of edges (same as number of nodes)\n- Next `n` lines: each line contains two integers `a b` -- an edge\n\n## Output Format\nTwo integers `a b` -- the redundant edge to remove.\n\n## Constraints\n- `3 <= n <= 1000`\n- The edges form exactly one cycle.\n\n## Example\n\n**Input**\n```\n4\n1 2\n2 3\n3 4\n1 4\n```\n**Output**\n```\n1 4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    edges = []\n    for i in range(1, n + 1):\n        a, b = map(int, data[i].split())\n        edges.append([a, b])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<pair<int,int>> edges(n);\n    for (int i = 0; i < n; i++)\n        cin >> edges[i].first >> edges[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[][] edges = new int[n][2];\n        for (int i = 0; i < n; i++) {\n            edges[i][0] = sc.nextInt();\n            edges[i][1] = sc.nextInt();\n        }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 2\n2 3\n3 4\n1 4\n', expected_output='1 4', is_hidden=False),
        TestCase(input='5\n1 2\n2 3\n3 4\n4 5\n1 5\n', expected_output='1 5', is_hidden=False),
        TestCase(input='3\n1 2\n2 3\n1 3\n', expected_output='1 3', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['rotting-oranges'] = {
    "description": '# Rotting Oranges\n\n## Statement\nYou are given an `m x n` grid where each cell can be:\n- 0: empty cell\n- 1: fresh orange\n- 2: rotten orange\nEvery minute, any fresh orange that is 4-directionally adjacent to a rotten orange\nbecomes rotten. Return the minimum number of minutes that must elapse until no cell\nhas a fresh orange. Return -1 if it is impossible.\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the grid\n- Next `m` lines: each line contains `n` integers (0, 1, or 2) separated by spaces\n\n## Output Format\nA single integer -- the minimum minutes, or -1.\n\n## Constraints\n- `1 <= m, n <= 10`\n- `0 <= grid[i][j] <= 2`\n\n## Example\n\n**Input**\n```\n3 3\n2 1 1\n1 1 0\n0 1 1\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    grid = []\n    for i in range(1, m + 1):\n        grid.append(list(map(int, data[i].split())))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> grid(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> grid[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] grid = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                grid[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 3\n2 1 1\n1 1 0\n0 1 1\n', expected_output='4', is_hidden=False),
        TestCase(input='1 1\n2\n', expected_output='0', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='-1', is_hidden=True),
        TestCase(input='2 2\n2 1\n1 1\n', expected_output='1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['surrounded-regions'] = {
    "description": '# Surrounded Regions\n\n## Statement\nGiven an `m x n` matrix `board` containing `X` and `O`, capture all regions\nsurrounded by `X`. A region is captured by flipping all `O`s into `X`s in\nthat surrounded region. An `O` cell is not captured if it is connected to the\nborder (any `O` on the border is safe).\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the board\n- Next `m` lines: each line contains `n` characters (`X` or `O`) separated by spaces\n\n## Output Format\nThe modified board, `m` lines of `n` characters separated by spaces.\n\n## Constraints\n- `1 <= m, n <= 200`\n- `board[i][j]` is `X` or `O`.\n\n## Example\n\n**Input**\n```\n4 4\nX X X X\nX O O X\nX X O X\nX O X X\n```\n**Output**\n```\nX X X X\nX X X X\nX X X X\nX O X X\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    board = []\n    for i in range(1, m + 1):\n        board.append(data[i].split())\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<char>> board(m, vector<char>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> board[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        char[][] board = new char[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                board[i][j] = sc.next().charAt(0);\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 4\nX X X X\nX O O X\nX X O X\nX O X X\n', expected_output='X X X X\nX X X X\nX X X X\nX O X X', is_hidden=False),
        TestCase(input='1 4\nX O X O\n', expected_output='X O X O', is_hidden=False),
        TestCase(input='3 3\nO X X\nX X O\nX X X\n', expected_output='O X X\nX X O\nX X X', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['walls-and-gates'] = {
    "description": '# Walls and Gates\n\n## Statement\nYou are given an `m x n` grid with three types of rooms:\n- -1: wall\n- 0: gate\n- 2147483647 (INF): empty room\nFill each empty room with the distance to its nearest gate. If it is impossible to\nreach a gate, leave the value as INF.\n\n## Input Format\n- Line 1: integers `m n` -- the dimensions of the grid\n- Next `m` lines: each line contains `n` integers separated by spaces\n\n## Output Format\nThe modified grid, `m` lines of `n` integers separated by spaces.\n\n## Constraints\n- `1 <= m, n <= 100`\n- Values are -1, 0, or 2147483647.\n- There is at least one gate.\n\n## Example\n\n**Input**\n```\n3 3\n2147483647 -1 0\n2147483647 2147483647 -1\n2147483647 -1 2147483647\n```\n**Output**\n```\n3 -1 0\n2 2 -1\n1 -1 3\n```',
    "starter_code": {
        'python': 'import sys\n\nINF = 2147483647\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    m, n = map(int, data[0].split())\n    grid = []\n    for i in range(1, m + 1):\n        grid.append(list(map(int, data[i].split())))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nconst int INF = 2147483647;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> grid(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> grid[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static final int INF = 2147483647;\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt(), n = sc.nextInt();\n        int[][] grid = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                grid[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 3\n2147483647 -1 0\n2147483647 2147483647 -1\n2147483647 -1 2147483647\n', expected_output='3 -1 0\n2 2 -1\n1 -1 3', is_hidden=False),
        TestCase(input='1 1\n0\n', expected_output='0', is_hidden=False),
        TestCase(input='2 2\n-1 -1\n-1 -1\n', expected_output='-1 -1\n-1 -1', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['word-ladder'] = {
    "description": '# Word Ladder\n\n## Statement\nA transformation sequence from word `beginWord` to word `endWord` uses a dictionary\n`wordList`. Each step, you must change exactly one letter to another letter, and the\nresulting word must be in `wordList`. Return the number of words in the shortest\ntransformation sequence from `beginWord` to `endWord`, or 0 if no such sequence exists.\n\n## Input Format\n- Line 1: `beginWord endWord` -- the start and target words\n- Line 2: integer `k` -- the number of words in wordList\n- Next `k` lines: each line contains a word from wordList\n\n## Output Format\nA single integer -- the length of the shortest transformation sequence.\n\n## Constraints\n- `1 <= beginWord.length <= 10`\n- `beginWord.length == endWord.length`\n- `1 <= k <= 1000`\n- `beginWord`, `endWord`, and `wordList[i]` consist of lowercase English letters.\n- `beginWord != endWord`\n- All words in wordList are unique.\n\n## Example\n\n**Input**\n```\nhit cog\n6\nhot\ndot\ndog\nlot\nlog\ncog\n```\n**Output**\n```\n5\n```\nExplanation: hit -> hot -> dot -> dog -> cog (length 5).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    beginWord, endWord = data[0].split()\n    k = int(data[1])\n    wordList = [data[i + 2] for i in range(k)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string beginWord, endWord;\n    cin >> beginWord >> endWord;\n    int k;\n    cin >> k;\n    vector<string> wordList(k);\n    for (int i = 0; i < k; i++)\n        cin >> wordList[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String beginWord = sc.next(), endWord = sc.next();\n        int k = sc.nextInt();\n        String[] wordList = new String[k];\n        for (int i = 0; i < k; i++) wordList[i] = sc.next();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='hit cog\n6\nhot\ndot\ndog\nlot\nlog\ncog\n', expected_output='5', is_hidden=False),
        TestCase(input='hit cog\n3\nhot\ndot\ndog\n', expected_output='0', is_hidden=False),
        TestCase(input='a c\n2\na\nb\nc\n', expected_output='2', is_hidden=True),
        TestCase(input='red blue\n4\nted\ntex\nred\nted\n', expected_output='4', is_hidden=True),
    ],
}

# ===========================================================================
# Advanced Graphs
# ===========================================================================

NEETCODE_AUTHORING['alien-dictionary'] = {
    "description": "# Alien Dictionary\n\n## Statement\n\nThere is a new alien language that uses the English alphabet. However, the order of the letters is unknown to you.\n\nYou are given a list of strings words from the alien language's dictionary, where the strings in words are sorted lexicographically by the rules of this new language.\n\nDerive the order of letters in this language. If there is no valid output, return an empty string.\n\nIf there are multiple valid answers, return any of them.\n\n## Input Format\n- First line: integer n (number of words)\n- Next n lines: one word per line\n\n## Output Format\n- Single string (the character order)\n\n## Constraints\n- 1 <= words.length <= 100\n- 1 <= words[i].length <= 100\n- words[i] consists of only lowercase English letters\n- All the values of words are unique\n\n## Example\n\n**Input**\n```\n3\nwrt\nwrf\ner\n```\n\n**Output**\n```\nwertf\n```",
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    n = int(data[0])\n    words = [data[i + 1].strip() for i in range(n)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    cin.ignore();\n    vector<string> words(n);\n    for (int i = 0; i < n; i++) getline(cin, words[i]);\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Integer.parseInt(sc.nextLine().trim());\n        String[] words = new String[n];\n        for (int i = 0; i < n; i++) words[i] = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\nwrt\nwrf\ner\n', expected_output='wertf\n', is_hidden=False),
        TestCase(input='2\nba\nbc\n', expected_output='bac\n', is_hidden=False),
        TestCase(input='1\na\n', expected_output='a\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['cheapest-flights-within-k-stops'] = {
    "description": '# Cheapest Flights Within K Stops\n\n## Statement\n\nThere are n cities connected by some flights. You are given an array flights where flights[i] = [from_i, to_i, price_i] indicates that there is a flight from city from_i to city to_i with cost price_i.\n\nYou are also given three integers src, dst, and k, return the cheapest price from src to dst with at most k stops. If there is no such route, return -1.\n\n## Input Format\n- First line: four integers n m src dst k (cities, flights, source, destination, max stops)\n- Next m lines: three integers from to price\n\n## Output Format\n- Single integer (cheapest price or -1)\n\n## Constraints\n- 1 <= n <= 100\n- 0 <= flights.length <= n * (n - 1) / 2\n- flights[i].length == 3\n- 0 <= from_i, to_i < n\n- from_i != to_i\n- 1 <= price_i <= 10^4\n- There does not exist any sequence of flights that visits each city exactly once\n\n## Example\n\n**Input**\n```\n4 4 0 3 1\n0 1 100\n1 2 100\n2 0 100\n1 3 600\n```\n\n**Output**\n```\n700\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n, m, src, dst, k = (int(data[idx]), int(data[idx + 1]), int(data[idx + 2]),\n                         int(data[idx + 3]), int(data[idx + 4]))\n    idx += 5\n    flights = []\n    for i in range(m):\n        u, v, w = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])\n        flights.append((u, v, w))\n        idx += 3\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, m, src, dst, k;\n    cin >> n >> m >> src >> dst >> k;\n    vector<tuple<int,int,int>> flights(m);\n    for (int i = 0; i < m; i++) {\n        int u, v, w; cin >> u >> v >> w;\n        flights[i] = {u, v, w};\n    }\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), m = sc.nextInt(), src = sc.nextInt(), dst = sc.nextInt(), k = sc.nextInt();\n        int[][] flights = new int[m][3];\n        for (int i = 0; i < m; i++) { flights[i][0] = sc.nextInt(); flights[i][1] = sc.nextInt(); flights[i][2] = sc.nextInt(); }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 4 0 3 1\n0 1 100\n1 2 100\n2 0 100\n1 3 600\n', expected_output='700\n', is_hidden=False),
        TestCase(input='3 3 0 2 1\n0 1 100\n1 2 100\n0 2 500\n', expected_output='200\n', is_hidden=False),
        TestCase(input='3 1 0 2 0\n0 1 100\n', expected_output='-1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['min-cost-to-connect-all-points'] = {
    "description": '# Min Cost to Connect All Points\n\n## Statement\n\nYou are given an array points representing integer coordinates of some points on a 2D-plane, where points[i] = [xi, yi].\n\nThe cost of connecting two points [xi, yi] and [xj, yj] is the manhattan distance between them: |xi - xj| + |yi - yj|.\n\nReturn the minimum cost to make all points connected. All points are connected if there is exactly one simple path between any two points.\n\n## Input Format\n- First line: integer n\n- Next n lines: two integers x y per line\n\n## Output Format\n- Single integer (minimum cost)\n\n## Constraints\n- 1 <= points.length <= 1000\n- -10^6 <= xi, yi <= 10^6\n- All pairs (xi, yi) are distinct\n\n## Example\n\n**Input**\n```\n3\n0 0\n2 2\n3 10\n```\n\n**Output**\n```\n20\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    points = []\n    for i in range(n):\n        x, y = int(data[idx]), int(data[idx + 1])\n        points.append((x, y))\n        idx += 2\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<pair<int,int>> points(n);\n    for (int i = 0; i < n; i++) cin >> points[i].first >> points[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[][] points = new int[n][2];\n        for (int i = 0; i < n; i++) { points[i][0] = sc.nextInt(); points[i][1] = sc.nextInt(); }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n0 0\n2 2\n3 10\n', expected_output='20\n', is_hidden=False),
        TestCase(input='1\n0 0\n', expected_output='0\n', is_hidden=False),
        TestCase(input='4\n0 0\n1 1\n2 2\n3 3\n', expected_output='6\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['network-delay-time'] = {
    "description": '# Network Delay Time\n\n## Statement\n\nYou are given a network of n nodes, labeled from 1 to n. You are also given times, a list of directed edges where times[i] = (ui, vi, wi) is the time it takes for a signal to travel from node ui to node vi.\n\nWe will send a signal from a given node k. Return the minimum time it takes for all the n nodes to receive the signal. If it is impossible for all the n nodes to receive the signal, return -1.\n\n## Input Format\n- First line: three integers n m k (nodes, edges, source)\n- Next m lines: three integers u v w per line\n\n## Output Format\n- Single integer (minimum time or -1)\n\n## Constraints\n- 1 <= k <= n <= 100\n- 1 <= m <= 10^4\n- 1 <= wi <= 100\n- All the pairs (ui, vi) are unique\n\n## Example\n\n**Input**\n```\n4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 2\n```\n\n**Output**\n```\n2\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n, m, k = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])\n    idx += 3\n    edges = []\n    for i in range(m):\n        u, v, w = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])\n        edges.append((u, v, w))\n        idx += 3\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, m, k;\n    cin >> n >> m >> k;\n    vector<tuple<int,int,int>> edges(m);\n    for (int i = 0; i < m; i++) {\n        int u, v, w; cin >> u >> v >> w;\n        edges[i] = {u, v, w};\n    }\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), m = sc.nextInt(), k = sc.nextInt();\n        int[][] edges = new int[m][3];\n        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); edges[i][2] = sc.nextInt(); }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 4 2\n2 1 1\n2 3 1\n3 4 1\n1 4 2\n', expected_output='2\n', is_hidden=False),
        TestCase(input='3 2 1\n1 2 1\n2 3 1\n', expected_output='2\n', is_hidden=False),
        TestCase(input='3 1 1\n1 2 1\n', expected_output='-1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reconstruct-itinerary'] = {
    "description": '# Reconstruct Itinerary\n\n## Statement\n\nYou are given a list of airline tickets where tickets[i] = [from_i, to_i] represent the departure and arrival airports of one flight. Reconstruct the itinerary in order and return it.\n\nAll of the tickets belong to a man who departs from "JFK". Thus, the itinerary must begin with "JFK". If there are multiple valid itineraries, you should return the itinerary with the smallest lexical order.\n\n## Input Format\n- First line: integer n (number of tickets)\n- Next n lines: two strings from to\n\n## Output Format\n- Space-separated city names representing the itinerary\n\n## Constraints\n- 1 <= tickets.length <= 300\n- tickets[i].length == 2\n- from_i and to_i consist of uppercase English letters\n- There are no duplicate tickets\n- All tickets form at least one valid itinerary\n\n## Example\n\n**Input**\n```\n3\nMUC LHR\nJFK MUC\nLHR JFK\n```\n\n**Output**\n```\nJFK MUC LHR JFK\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split('\\n')\n    n = int(data[0])\n    tickets = []\n    for i in range(1, n + 1):\n        parts = data[i].split()\n        tickets.append(parts)\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<pair<string,string>> tickets(n);\n    for (int i = 0; i < n; i++) cin >> tickets[i].first >> tickets[i].second;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = Integer.parseInt(sc.nextLine().trim());\n        String[][] tickets = new String[n][2];\n        for (int i = 0; i < n; i++) { tickets[i] = sc.nextLine().split(" "); }\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\nMUC LHR\nJFK MUC\nLHR JFK\n', expected_output='JFK MUC LHR JFK\n', is_hidden=False),
        TestCase(input='4\nJFK SFO\nJFK ATL\nSFO ATL\nATL JFK\n', expected_output='JFK ATL JFK SFO ATL\n', is_hidden=False),
        TestCase(input='1\nJFK NRT\n', expected_output='JFK NRT\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['swim-in-rising-water'] = {
    "description": '# Swim in Rising Water\n\n## Statement\n\nYou are given an n x n integer matrix grid where each value grid[i][j] represents the elevation at that point (i, j).\n\nThe rain starts to fall at time t = 0, and at time t the depth of the water everywhere is t. You can swim from a square to another 4-directionally adjacent square if and only if the elevation of both squares individually are at most t. You can swim infinite distances in zero time. Of course, you must stay within the boundaries of the grid during your swim.\n\nReturn the least time until you can get to the bottom right square (n - 1, n - 1) if you start at the top left square (0, 0).\n\n## Input Format\n- First line: integer n\n- Next n lines: n integers per line (grid values)\n\n## Output Format\n- Single integer (minimum time)\n\n## Constraints\n- n == grid.length\n- n == grid[i].length\n- 1 <= n <= 50\n- 0 <= grid[i][j] < n^2\nAll values in grid are unique\n\n## Example\n\n**Input**\n```\n2\n0 2\n1 3\n```\n\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': "import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    n = int(data[idx])\n    idx += 1\n    grid = []\n    for i in range(n):\n        row = [int(data[idx + j]) for j in range(n)]\n        grid.append(row)\n        idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == '__main__':\n    main()\n",
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<vector<int>> grid(n, vector<int>(n));\n    for (int i = 0; i < n; i++)\n        for (int j = 0; j < n; j++) cin >> grid[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[][] grid = new int[n][n];\n        for (int i = 0; i < n; i++)\n            for (int j = 0; j < n; j++) grid[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2\n0 2\n1 3\n', expected_output='3\n', is_hidden=False),
        TestCase(input='3\n0 1 2\n3 4 5\n6 7 8\n', expected_output='8\n', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='0\n', is_hidden=True),
    ],
}

# ===========================================================================
# 1-D Dynamic Programming
# ===========================================================================

NEETCODE_AUTHORING['climbing-stairs'] = {
    "description": '# Climbing Stairs\n\n## Statement\nYou are climbing a staircase. It takes `n` steps to reach the top. Each time you can\nclimb 1 or 2 steps. In how many distinct ways can you climb to the top?\n\n## Input Format\n- A single integer `n`\n\n## Output Format\nA single integer -- the number of distinct ways.\n\n## Constraints\n- `1 <= n <= 45`\n\n## Example\n\n**Input**\n```\n2\n```\n**Output**\n```\n2\n```\nExplanation: 1+1, 2.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2\n', expected_output='2', is_hidden=False),
        TestCase(input='3\n', expected_output='3', is_hidden=False),
        TestCase(input='1\n', expected_output='1', is_hidden=True),
        TestCase(input='5\n', expected_output='8', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['coin-change'] = {
    "description": '# Coin Change\n\n## Statement\nYou are given an integer array `coins` representing the denominations of coins and an\ninteger `amount` representing the total amount of money. Return the fewest number of\ncoins needed to make up the amount. If it is not possible, return -1.\n\n## Input Format\n- Line 1: integer `n` -- the number of coin types\n- Line 2: `n` integers -- the coin denominations\n- Line 3: integer `amount`\n\n## Output Format\nA single integer -- the minimum number of coins, or -1.\n\n## Constraints\n- `1 <= n <= 12`\n- `1 <= coins[i] <= 2^31 - 1`\n- `0 <= amount <= 10^4`\n\n## Example\n\n**Input**\n```\n3\n1 2 5\n11\n```\n**Output**\n```\n3\n```\nExplanation: 11 = 5 + 5 + 1 (3 coins).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    coins = list(map(int, data[1].split()))\n    amount = int(data[2])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> coins(n);\n    for (int i = 0; i < n; i++)\n        cin >> coins[i];\n    int amount;\n    cin >> amount;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] coins = new int[n];\n        for (int i = 0; i < n; i++) coins[i] = sc.nextInt();\n        int amount = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 5\n11\n', expected_output='3', is_hidden=False),
        TestCase(input='1\n2\n3\n', expected_output='-1', is_hidden=False),
        TestCase(input='1\n1\n0\n', expected_output='0', is_hidden=True),
        TestCase(input='2\n1 5\n100\n', expected_output='20', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['decode-ways'] = {
    "description": '# Decode Ways\n\n## Statement\nA message consisting of letters A-Z is being encoded to numbers using the following\nmapping: A=1, B=2, ..., Z=26. Given a string `s` of digits, return the number of\nways to decode it.\n\n## Input Format\n- A single string `s` of digits\n\n## Output Format\nA single integer -- the number of ways to decode.\n\n## Constraints\n- `1 <= s.length <= 100`\n- `s` contains only digits and may contain leading zeros.\n\n## Example\n\n**Input**\n```\n226\n```\n**Output**\n```\n3\n```\nExplanation: "226" can be decoded as "BZ" (2-26), "VF" (22-6), or "BBF" (2-2-6).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    s = data[0]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='226\n', expected_output='3', is_hidden=False),
        TestCase(input='06\n', expected_output='0', is_hidden=False),
        TestCase(input='1\n', expected_output='1', is_hidden=True),
        TestCase(input='11106\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['house-robber'] = {
    "description": '# House Robber\n\n## Statement\nYou are a robber planning to rob houses along a street. Each house has a certain\namount of money stashed. The only constraint stopping you from robbing each of them\nis that adjacent houses have security systems connected -- if two adjacent houses were\nbroken into on the same night, the police are alerted. Given an array `nums`\nrepresenting the amount of money at each house, return the maximum amount you can\nrob without alerting the police.\n\n## Input Format\n- Line 1: integer `n` -- the number of houses\n- Line 2: `n` integers -- the money in each house\n\n## Output Format\nA single integer -- the maximum amount.\n\n## Constraints\n- `1 <= n <= 100`\n- `0 <= nums[i] <= 400`\n\n## Example\n\n**Input**\n```\n4\n1 2 3 1\n```\n**Output**\n```\n4\n```\nExplanation: Rob house 1 (money = 1) and house 3 (money = 3), total = 4.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    nums = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++)\n        cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 2 3 1\n', expected_output='4', is_hidden=False),
        TestCase(input='5\n2 7 9 3 1\n', expected_output='12', is_hidden=False),
        TestCase(input='1\n5\n', expected_output='5', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['house-robber-ii'] = {
    "description": '# House Robber II\n\n## Statement\nAll houses are arranged in a circle. You cannot rob adjacent houses. Given an array\n`nums` representing the amount of money at each house, return the maximum amount\nyou can rob without alerting the police.\n\n## Input Format\n- Line 1: integer `n` -- the number of houses\n- Line 2: `n` integers -- the money in each house\n\n## Output Format\nA single integer -- the maximum amount.\n\n## Constraints\n- `1 <= n <= 100`\n- `0 <= nums[i] <= 400`\n\n## Example\n\n**Input**\n```\n3\n2 3 2\n```\n**Output**\n```\n3\n```\nExplanation: You cannot rob house 0 and house 2 (adjacent in circle).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    nums = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++)\n        cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n2 3 2\n', expected_output='3', is_hidden=False),
        TestCase(input='4\n1 2 3 1\n', expected_output='4', is_hidden=False),
        TestCase(input='1\n5\n', expected_output='5', is_hidden=True),
        TestCase(input='2\n2 1\n', expected_output='2', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-increasing-subsequence'] = {
    "description": '# Longest Increasing Subsequence\n\n## Statement\nGiven an integer array `nums`, return the length of the longest strictly increasing\nsubsequence.\n\n## Input Format\n- Line 1: integer `n` -- the size of the array\n- Line 2: `n` integers\n\n## Output Format\nA single integer -- the length.\n\n## Constraints\n- `1 <= n <= 2500`\n- `-10^4 <= nums[i] <= 10^4`\n\n## Example\n\n**Input**\n```\n4\n10 9 2 5\n```\n**Output**\n```\n2\n```\nExplanation: The LIS is [2, 5] or [9, 5] (length 2).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    nums = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++)\n        cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n10 9 2 5\n', expected_output='2', is_hidden=False),
        TestCase(input='4\n3 4 -1 0\n', expected_output='3', is_hidden=False),
        TestCase(input='1\n0\n', expected_output='1', is_hidden=True),
        TestCase(input='5\n0 1 0 3 2\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-palindromic-substring'] = {
    "description": '# Longest Palindromic Substring\n\n## Statement\nGiven a string `s`, return the longest palindromic substring in `s`.\n\n## Input Format\n- A single string `s`\n\n## Output Format\nThe longest palindromic substring.\n\n## Constraints\n- `1 <= s.length <= 1000`\n- `s` consists of only digits and English letters.\n\n## Example\n\n**Input**\n```\nbabad\n```\n**Output**\n```\nbab\n```\nExplanation: "aba" is also valid.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    s = data[0]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='babad\n', expected_output='bab', is_hidden=False),
        TestCase(input='cbbd\n', expected_output='bb', is_hidden=False),
        TestCase(input='a\n', expected_output='a', is_hidden=True),
        TestCase(input='racecar\n', expected_output='racecar', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['maximum-product-subarray'] = {
    "description": '# Maximum Product Subarray\n\n## Statement\nGiven an integer array `nums`, find a subarray that has the largest product, and\nreturn the product. The answer will fit in a 32-bit integer.\n\n## Input Format\n- Line 1: integer `n` -- the size of the array\n- Line 2: `n` integers\n\n## Output Format\nA single integer -- the maximum product.\n\n## Constraints\n- `1 <= n <= 2000`\n- `-10 <= nums[i] <= 10`\n- The product of any subarray will not be in the range of `2^31`.\n\n## Example\n\n**Input**\n```\n4\n2 3 -2 4\n```\n**Output**\n```\n6\n```\nExplanation: Subarray [2, 3] has the largest product 6.',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    nums = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++)\n        cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n2 3 -2 4\n', expected_output='6', is_hidden=False),
        TestCase(input='3\n-2 0 -1\n', expected_output='0', is_hidden=False),
        TestCase(input='1\n-2\n', expected_output='-2', is_hidden=True),
        TestCase(input='5\n2 -5 -2 -4 3\n', expected_output='24', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['min-cost-climbing-stairs'] = {
    "description": '# Min Cost Climbing Stairs\n\n## Statement\nYou are given an array `cost` where `cost[i]` is the cost of the i-th step. Once you\npay the cost, you can climb one or two steps. You can start from step 0 or step 1.\nReturn the minimum cost to reach the top (index n).\n\n## Input Format\n- Line 1: integer `n` -- the number of steps\n- Line 2: `n` integers -- the costs\n\n## Output Format\nA single integer -- the minimum cost.\n\n## Constraints\n- `2 <= n <= 1000`\n- `0 <= cost[i] <= 999`\n\n## Example\n\n**Input**\n```\n3\n10 15 20\n```\n**Output**\n```\n15\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    cost = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> cost(n);\n    for (int i = 0; i < n; i++)\n        cin >> cost[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] cost = new int[n];\n        for (int i = 0; i < n; i++) cost[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n10 15 20\n', expected_output='15', is_hidden=False),
        TestCase(input='4\n1 100 1 1\n', expected_output='2', is_hidden=False),
        TestCase(input='2\n0 0\n', expected_output='0', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['palindromic-substrings'] = {
    "description": '# Palindromic Substrings\n\n## Statement\nGiven a string `s`, return the number of palindromic substrings in it. A substring\nis a contiguous sequence of characters. Single characters are palindromes.\n\n## Input Format\n- A single string `s`\n\n## Output Format\nA single integer -- the count.\n\n## Constraints\n- `1 <= s.length <= 1000`\n- `s` consists of only lowercase English letters.\n\n## Example\n\n**Input**\n```\nabc\n```\n**Output**\n```\n3\n```\nExplanation: "a", "b", "c".',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    s = data[0]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='abc\n', expected_output='3', is_hidden=False),
        TestCase(input='aaa\n', expected_output='6', is_hidden=False),
        TestCase(input='a\n', expected_output='1', is_hidden=True),
        TestCase(input='aba\n', expected_output='4', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['partition-equal-subset-sum'] = {
    "description": '# Partition Equal Subset Sum\n\n## Statement\nGiven a non-empty array of positive integers `nums`, determine if the array can be\npartitioned into two subsets such that the sum of elements in both subsets is equal.\n\n## Input Format\n- Line 1: integer `n` -- the size of the array\n- Line 2: `n` positive integers\n\n## Output Format\n`true` or `false`\n\n## Constraints\n- `1 <= n <= 200`\n- `1 <= nums[i] <= 100`\n\n## Example\n\n**Input**\n```\n4\n1 5 11 5\n```\n**Output**\n```\ntrue\n```\nExplanation: [1, 5, 5] and [11] have equal sums (11).',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    n = int(data[0])\n    nums = list(map(int, data[1].split()))\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++)\n        cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n1 5 11 5\n', expected_output='true', is_hidden=False),
        TestCase(input='3\n1 2 3\n', expected_output='false', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='false', is_hidden=True),
        TestCase(input='2\n1 1\n', expected_output='true', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['word-break'] = {
    "description": '# Word Break\n\n## Statement\nGiven a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can\nbe segmented into a space-separated sequence of one or more dictionary words.\n\n## Input Format\n- Line 1: string `s`\n- Line 2: integer `k` -- the number of words in wordDict\n- Next `k` lines: each line contains a word from wordDict\n\n## Output Format\n`true` or `false`\n\n## Constraints\n- `1 <= s.length <= 300`\n- `1 <= k <= 1000`\n- `1 <= wordDict[i].length <= 20`\n- `s` and `wordDict[i]` consist of only lowercase English letters.\n\n## Example\n\n**Input**\n```\nleetcode\n2\nleet\ncode\n```\n**Output**\n```\ntrue\n```\nExplanation: "leetcode" can be segmented as "leet code".',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().strip().split("\\n")\n    s = data[0]\n    k = int(data[1])\n    wordDict = [data[i + 2] for i in range(k)]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s;\n    cin >> s;\n    int k;\n    cin >> k;\n    vector<string> wordDict(k);\n    for (int i = 0; i < k; i++)\n        cin >> wordDict[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n        int k = Integer.parseInt(sc.nextLine().trim());\n        String[] wordDict = new String[k];\n        for (int i = 0; i < k; i++) wordDict[i] = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='leetcode\n2\nleet\ncode\n', expected_output='true', is_hidden=False),
        TestCase(input='applepen\n2\napple\npen\n', expected_output='true', is_hidden=False),
        TestCase(input='catsandog\n5\ncats\ndog\nsand\nand\ncat\n', expected_output='false', is_hidden=True),
    ],
}

# ===========================================================================
# 2-D Dynamic Programming
# ===========================================================================

NEETCODE_AUTHORING['best-time-to-buy-and-sell-stock-with-cooldown'] = {
    "description": '# Best Time to Buy and Sell Stock with Cooldown\n\n## Statement\nYou are given an array prices where prices[i] is the price of a given stock on the ith day.\n\nFind the maximum profit you can achieve. You may complete as many transactions as you like (i.e., buy one and sell one share of the stock multiple times) with the following restrictions:\n\nAfter you sell your stock, you cannot buy stock on the next day (i.e., cooldown one day).\n\nNote: You may engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).\n\n## Input Format\n- First line: an integer n (number of days).\n- Second line: n space-separated integers representing prices.\n\n## Output Format\n- A single integer representing the maximum profit.\n\n## Constraints\n- 1 <= n <= 5000\n- 0 <= prices[i] <= 1000\n\n## Example\n\n**Input**\n```\n6\n1 2 3 0 2\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    prices = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> prices(n);\n    for (int i = 0; i < n; i++) cin >> prices[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] prices = new int[n];\n        for (int i = 0; i < n; i++) prices[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n1 2 3 0 2\n', expected_output='3\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='0\n', is_hidden=False),
        TestCase(input='6\n1 2 4 1 5 7\n', expected_output='6\n', is_hidden=True),
        TestCase(input='4\n1 2 3 4\n', expected_output='3\n', is_hidden=True),
        TestCase(input='5\n5 4 3 2 1\n', expected_output='0\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['burst-balloons'] = {
    "description": '# Burst Balloons\n\n## Statement\nYou are given n balloons, indexed from 0 to n - 1. Each balloon is painted with a number on it represented by an array nums. You are asked to burst all the balloons.\n\nIf you burst the ith balloon, you will get nums[i - 1] * nums[i] * nums[i + 1] coins. If i - 1 or i + 1 goes out of bounds of the array, then treat it as if there is a balloon with a 1 painted on it.\n\nReturn the maximum coins you can collect by bursting the balloons wisely.\n\n## Input Format\n- First line: an integer n.\n- Second line: n space-separated integers.\n\n## Output Format\n- A single integer representing the maximum coins.\n\n## Constraints\n- 1 <= n <= 300\n- 0 <= nums[i] <= 100\n\n## Example\n\n**Input**\n```\n4\n3 1 5 8\n```\n**Output**\n```\n167\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n = int(data[0])\n    nums = [int(x) for x in data[1:n+1]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4\n3 1 5 8\n', expected_output='167\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='3\n1 5\n', expected_output='10\n', is_hidden=True),
        TestCase(input='5\n3 1 5 8 2\n', expected_output='243\n', is_hidden=True),
        TestCase(input='2\n4 5\n', expected_output='30\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['coin-change-ii'] = {
    "description": '# Coin Change II\n\n## Statement\nYou are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.\n\nReturn the number of combinations that make up that amount. If that amount of money cannot be made up by any combination of the coins, return 0.\n\nThe answer is guaranteed to fit into a signed 32-bit integer.\n\n## Input Format\n- First line: two integers n and amount (number of coins and target amount).\n- Second line: n space-separated integers representing coin values.\n\n## Output Format\n- A single integer representing the number of combinations.\n\n## Constraints\n- 1 <= n <= 300\n- 1 <= coins[i] <= 5000\n- 0 <= amount <= 5000\n\n## Example\n\n**Input**\n```\n4 5\n1 2 5\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, amount = int(data[0]), int(data[1])\n    coins = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, amount;\n    cin >> n >> amount;\n    vector<int> coins(n);\n    for (int i = 0; i < n; i++) cin >> coins[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int amount = sc.nextInt();\n        int[] coins = new int[n];\n        for (int i = 0; i < n; i++) coins[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='4 5\n1 2 5\n', expected_output='4\n', is_hidden=False),
        TestCase(input='2 3\n2\n', expected_output='0\n', is_hidden=False),
        TestCase(input='3 10\n10\n', expected_output='1\n', is_hidden=True),
        TestCase(input='4 325\n386 160 449 12 158 259 384 32\n', expected_output='54161\n', is_hidden=True),
        TestCase(input='1 0\n1\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['distinct-subsequences'] = {
    "description": '# Distinct Subsequences\n\n## Statement\nGiven two strings s and t, return the number of distinct subsequences of s which equals t.\n\nA subsequence of a string is a new string which is formed from the original string by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters.\n\n## Input Format\n- Two strings s and t, each on a separate line.\n\n## Output Format\n- A single integer representing the number of distinct subsequences.\n\n## Constraints\n- 1 <= s.length, t.length <= 1000\n- s and t consist of uppercase and lowercase English letters.\n\n## Example\n\n**Input**\n```\nrabbbit\nrabbit\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0].strip()\n    t = data[1].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s, t;\n    cin >> s >> t;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n        String t = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='rabbbit\nrabbit\n', expected_output='3\n', is_hidden=False),
        TestCase(input='babgbag\nbag\n', expected_output='5\n', is_hidden=False),
        TestCase(input='a\na\n', expected_output='1\n', is_hidden=True),
        TestCase(input='a\nb\n', expected_output='0\n', is_hidden=True),
        TestCase(input='aab\nab\n', expected_output='2\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['edit-distance'] = {
    "description": '# Edit Distance\n\n## Statement\nGiven two strings word1 and word2, return the minimum number of operations required to convert word1 to word2.\n\nYou have the following three operations permitted on a word:\n- Insert a character\n- Delete a character\n- Replace a character\n\n## Input Format\n- Two strings word1 and word2, each on a separate line.\n\n## Output Format\n- A single integer representing the minimum number of operations.\n\n## Constraints\n- 0 <= word1.length, word2.length <= 500\n- word1 and word2 consist of lowercase English letters.\n\n## Example\n\n**Input**\n```\nhorse\nros\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    word1 = data[0].strip()\n    word2 = data[1].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string word1, word2;\n    cin >> word1 >> word2;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String word1 = sc.nextLine().trim();\n        String word2 = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='horse\nros\n', expected_output='3\n', is_hidden=False),
        TestCase(input='intention\nexecution\n', expected_output='5\n', is_hidden=False),
        TestCase(input='a\na\n', expected_output='0\n', is_hidden=True),
        TestCase(input='a\nab\n', expected_output='1\n', is_hidden=True),
        TestCase(input='dinitrophenylhydrazine\nacetylphenylhydrazine\n', expected_output='6\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['interleaving-string'] = {
    "description": '# Interleaving String\n\n## Statement\nGiven strings s1, s2, and s3, find whether s3 is formed by an interleaving of s1 and s2.\n\nAn interleaving of two strings s1 and s2 is a configuration where s1 and s2 are divided into non-empty substrings such that:\n- s1 = s1_1 + s1_2 + ... + s1_n\n- s2 = s2_1 + s2_2 + ... + s2_m\n- |n - m| <= 1\n- The interleaving is s1_1 + s2_1 + s1_2 + s2_2 + ... or s2_1 + s1_1 + s2_2 + s1_2 + ...\n\n## Input Format\n- Three strings s1, s2, s3, each on a separate line.\n\n## Output Format\n- "true" if s3 is an interleaving of s1 and s2, "false" otherwise.\n\n## Constraints\n- 0 <= s1.length, s2.length <= 100\n- 0 <= s3.length <= 200\n- s1, s2, s3 consist of lowercase English letters.\n\n## Example\n\n**Input**\n```\naab\naxy\naaxaby\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s1 = data[0].strip()\n    s2 = data[1].strip()\n    s3 = data[2].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s1, s2, s3;\n    cin >> s1 >> s2 >> s3;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s1 = sc.nextLine().trim();\n        String s2 = sc.nextLine().trim();\n        String s3 = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='aab\naxy\naaxaby\n', expected_output='true\n', is_hidden=False),
        TestCase(input='aab\naxy\naaxabby\n', expected_output='false\n', is_hidden=False),
        TestCase(input='a\nb\nab\n', expected_output='true\n', is_hidden=True),
        TestCase(input='a\nb\nba\n', expected_output='true\n', is_hidden=True),
        TestCase(input='a\n\na\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-common-subsequence'] = {
    "description": '# Longest Common Subsequence\n\n## Statement\nGiven two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.\n\nA subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.\n\nA common subsequence of two strings is a subsequence that is common to both strings.\n\n## Input Format\n- Two strings text1 and text2, each on a separate line.\n\n## Output Format\n- A single integer representing the length of the longest common subsequence.\n\n## Constraints\n- 1 <= text1.length, text2.length <= 1000\n- text1 and text2 consist of only lowercase English characters.\n\n## Example\n\n**Input**\n```\nabcde\nace\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    text1 = data[0].strip()\n    text2 = data[1].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string text1, text2;\n    cin >> text1 >> text2;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String text1 = sc.nextLine().trim();\n        String text2 = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='abcde\nace\n', expected_output='3\n', is_hidden=False),
        TestCase(input='abc\nabc\n', expected_output='3\n', is_hidden=False),
        TestCase(input='abc\n def\n', expected_output='0\n', is_hidden=True),
        TestCase(input='ezupkr\nubmrapk\n', expected_output='0\n', is_hidden=True),
        TestCase(input='abcde\nace\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['longest-increasing-path-in-a-matrix'] = {
    "description": '# Longest Increasing Path in a Matrix\n\n## Statement\nGiven an m x n integers matrix, return the length of the longest increasing path in matrix.\n\nFrom each cell, you can either move in four directions: left, right, up, or down. You may not move diagonally or move outside the boundary (i.e., wrap-around is not allowed).\n\n## Input Format\n- First line: two integers m and n.\n- Next m lines: n space-separated integers each.\n\n## Output Format\n- A single integer representing the length of the longest increasing path.\n\n## Constraints\n- 1 <= m, n <= 200\n- 0 <= matrix[i][j] <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n3 3\n9 9 4\n6 6 8\n2 1 1\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    idx = 0\n    m, n = int(data[idx]), int(data[idx+1]); idx += 2\n    matrix = []\n    for i in range(m):\n        matrix.append([int(data[idx+j]) for j in range(n)]); idx += n\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n    vector<vector<int>> matrix(m, vector<int>(n));\n    for (int i = 0; i < m; i++)\n        for (int j = 0; j < n; j++)\n            cin >> matrix[i][j];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt();\n        int n = sc.nextInt();\n        int[][] matrix = new int[m][n];\n        for (int i = 0; i < m; i++)\n            for (int j = 0; j < n; j++)\n                matrix[i][j] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 3\n9 9 4\n6 6 8\n2 1 1\n', expected_output='4\n', is_hidden=False),
        TestCase(input='3 3\n3 4 5\n3 2 6\n2 2 1\n', expected_output='4\n', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='2 2\n1 2\n3 4\n', expected_output='3\n', is_hidden=True),
        TestCase(input='3 3\n1 10 5\n4 3 7\n2 6 8\n', expected_output='6\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['regular-expression-matching'] = {
    "description": '# Regular Expression Matching\n\n## Statement\nGiven an input string s and a pattern p, implement regular expression matching with support for "." and "*".\n\nThe matching should cover the entire input string (not partial).\n\nRules:\n- "." matches any single character.\n- "*" matches zero or more of the preceding element.\n\nThe matching should cover the entire input string.\n\n## Input Format\n- Two strings s and p, each on a separate line.\n\n## Output Format\n- "true" if p matches s, "false" otherwise.\n\n## Constraints\n- 1 <= s.length <= 20\n- 1 <= p.length <= 20\n- s contains only lowercase English letters.\n- p contains only lowercase English letters, ".", and "*".\n- It is guaranteed for each appearance of "*", there is a previous valid character to match.\n\n## Example\n\n**Input**\n```\naa\na\n```\n**Output**\n```\nfalse\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    s = data[0].strip()\n    p = data[1].strip()\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string s, p;\n    cin >> s >> p;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String s = sc.nextLine().trim();\n        String p = sc.nextLine().trim();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='aa\na\n', expected_output='false\n', is_hidden=False),
        TestCase(input='aa\na*\n', expected_output='true\n', is_hidden=False),
        TestCase(input='ab\n.*\n', expected_output='true\n', is_hidden=True),
        TestCase(input='aab\nc*a*b\n', expected_output='true\n', is_hidden=True),
        TestCase(input='mississippi\nmis*is*p*.\n', expected_output='false\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['target-sum'] = {
    "description": '# Target Sum\n\n## Statement\nYou are given an integer array nums and an integer target.\n\nYou want to build an expression out of nums by adding one of the symbols "+" or "-" before each integer in nums and then concatenate all the integers.\n\nFor example, if nums = [2, 1], you can add a "+" before 2 and a "-" before 1 and concatenate them to build the expression "+2-1".\n\nReturn the number of different expressions that you can build, which evaluates to target.\n\n## Input Format\n- First line: two integers n and target.\n- Second line: n space-separated integers.\n\n## Output Format\n- A single integer representing the number of expressions.\n\n## Constraints\n- 1 <= n <= 20\n- 0 <= nums[i] <= 1000\n- -1000 <= target <= 1000\n\n## Example\n\n**Input**\n```\n5 3\n1 1 1 1 1\n```\n**Output**\n```\n5\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    n, target = int(data[0]), int(data[1])\n    nums = [int(x) for x in data[2:n+2]]\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int n, target;\n    cin >> n >> target;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int target = sc.nextInt();\n        int[] nums = new int[n];\n        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5 3\n1 1 1 1 1\n', expected_output='5\n', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='3 -1\n1 1 1\n', expected_output='0\n', is_hidden=True),
        TestCase(input='5 -3\n1 2 3 4 5\n', expected_output='0\n', is_hidden=True),
        TestCase(input='2 0\n1 1\n', expected_output='2\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['unique-paths'] = {
    "description": '# Unique Paths\n\n## Statement\nThere is a robot on an m x n grid. The robot is initially located at the top-left corner (i.e., grid[0][0]). The robot tries to move to the bottom-right corner (i.e., grid[m-1][n-1]). The robot can only move either down or right at any point in time.\n\nGiven the two integers m and n, return the number of possible unique paths that the robot can take to reach the bottom-right corner.\n\n## Input Format\n- Two integers m and n separated by a space.\n\n## Output Format\n- A single integer representing the number of unique paths.\n\n## Constraints\n- 1 <= m, n <= 100\n\n## Example\n\n**Input**\n```\n3 7\n```\n**Output**\n```\n28\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    m, n = int(data[0]), int(data[1])\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    int m, n;\n    cin >> m >> n;\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int m = sc.nextInt();\n        int n = sc.nextInt();\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 7\n', expected_output='28\n', is_hidden=False),
        TestCase(input='3 2\n', expected_output='3\n', is_hidden=False),
        TestCase(input='7 3\n', expected_output='28\n', is_hidden=True),
        TestCase(input='1 1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='100 100\n', expected_output='22750883079422934966181954039568885395604168260154104734000\n', is_hidden=True),
    ],
}

# ===========================================================================
# Trees
# ===========================================================================

NEETCODE_AUTHORING['balanced-binary-tree'] = {
    "description": '# Balanced Binary Tree\n\n## Statement\nGiven a binary tree, determine if it is height-balanced.\n\nA height-balanced binary tree is a binary tree in which the depth of the two subtrees of every node never differs by more than one.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- "true" if the tree is balanced, "false" otherwise.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 5000].\n- -10^4 <= Node.val <= 10^4\n\n## Example\n\n**Input**\n```\n3 9 20 null null 15 7\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    if not data or data[0] == "null":\n        print("true")\n        return\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nbool isBalanced(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse and build tree, then call isBalanced\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse and build tree, then call isBalanced\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 9 20 null null 15 7\n', expected_output='true\n', is_hidden=False),
        TestCase(input='1 2 2 3 3 null null 4 4\n', expected_output='false\n', is_hidden=False),
        TestCase(input='\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1 2 3 4 5 6 null null null 7\n', expected_output='false\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['binary-tree-level-order-traversal'] = {
    "description": '# Binary Tree Level Order Traversal\n\n## Statement\nGiven the root of a binary tree, return the level order traversal of its nodes\' values. (i.e., from left to right, level by level).\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- Each level on a separate line, with values space-separated.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 2000].\n- -1000 <= Node.val <= 1000\n\n## Example\n\n**Input**\n```\n3 9 20 null null 15 7\n```\n**Output**\n```\n3\n9 20\n15 7\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nvector<vector<int>> levelOrder(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree and output level order\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree and output level order\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 9 20 null null 15 7\n', expected_output='3\n9 20\n15 7\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='\n', expected_output='', is_hidden=True),
        TestCase(input='1 2 3 4 5\n', expected_output='1\n2 3\n4 5\n', is_hidden=True),
        TestCase(input='1 2 3 null null 4 5 6\n', expected_output='1\n2 3\n4 5 6\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['binary-tree-maximum-path-sum'] = {
    "description": '# Binary Tree Maximum Path Sum\n\n## Statement\nA path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.\n\nThe path sum of a path is the sum of the node\'s values in the path.\n\nGiven the root of a binary tree, return the maximum path sum of any non-empty path.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the maximum path sum.\n\n## Constraints\n- The number of nodes in the tree is in the range [1, 3 * 10^4].\n- -1000 <= Node.val <= 1000\n\n## Example\n\n**Input**\n```\n1 2 3\n```\n**Output**\n```\n6\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nint maxPathSum(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree and find max path sum\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree and find max path sum\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3\n', expected_output='6\n', is_hidden=False),
        TestCase(input='-10 9 20 null null 15 7\n', expected_output='42\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='-3\n', expected_output='-3\n', is_hidden=True),
        TestCase(input='5 4 8 11 null 13 4 7 2 null null null 1\n', expected_output='37\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['binary-tree-right-side-view'] = {
    "description": '# Binary Tree Right Side View\n\n## Statement\nGiven the root of a binary tree, imagine yourself standing on the right side of it, return the values of the nodes you can see ordered from top to bottom.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single line of space-separated values representing the right side view.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 100].\n- -100 <= Node.val <= 100\n\n## Example\n\n**Input**\n```\n1 2 3 null 5 null 4\n```\n**Output**\n```\n1 3 4\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nvector<int> rightSideView(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree and output right side view\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree and output right side view\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 null 5 null 4\n', expected_output='1 3 4\n', is_hidden=False),
        TestCase(input='1 null 3\n', expected_output='1 3\n', is_hidden=False),
        TestCase(input='\n', expected_output='\n', is_hidden=True),
        TestCase(input='1 2 3 4\n', expected_output='1 3 4\n', is_hidden=True),
        TestCase(input='1 2 3 4 5 6 7\n', expected_output='1 3 7\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['construct-binary-tree-from-preorder-and-inorder-traversal'] = {
    "description": '# Construct Binary Tree from Preorder and Inorder Traversal\n\n## Statement\nGiven two integer arrays preorder and inorder where preorder is the preorder traversal of a binary tree and inorder is the inorder traversal of the same tree, construct and return the binary tree.\n\n## Input Format\n- First line: space-separated integers representing preorder traversal.\n- Second line: space-separated integers representing inorder traversal.\n\n## Output Format\n- A single line of space-separated values representing the constructed tree in level-order.\n\n## Constraints\n- 1 <= preorder.length <= 3000\n- inorder.length == preorder.length\n- -3000 <= preorder[i], inorder[i] <= 3000\n- All values in preorder and inorder are unique.\n\n## Example\n\n**Input**\n```\n3 9 20 15 7\n9 3 15 20 7\n```\n**Output**\n```\n3 9 20 null null 15 7\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().splitlines()\n    preorder = [int(x) for x in data[0].split()]\n    inorder = [int(x) for x in data[1].split()]\n\n    # ===== YOUR CODE HERE =====\n    root = buildTree(preorder, inorder)\n    print(" ".join(level_order_values(root)))\n\n\ndef level_order_values(root):\n    if not root:\n        return []\n    result, queue = [], deque([root])\n    while queue:\n        node = queue.popleft()\n        if node:\n            result.append(str(node.val))\n            queue.append(node.left)\n            queue.append(node.right)\n        else:\n            result.append("null")\n    while result and result[-1] == "null":\n        result.pop()\n    return result\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nTreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {\n    // ===== YOUR CODE HERE =====\n}\n\nvector<string> levelOrderValues(TreeNode* root) {\n    vector<string> result;\n    if (!root) return result;\n    queue<TreeNode*> q;\n    q.push(root);\n    while (!q.empty()) {\n        TreeNode* node = q.front(); q.pop();\n        if (node) {\n            result.push_back(to_string(node->val));\n            q.push(node->left);\n            q.push(node->right);\n        } else {\n            result.push_back("null");\n        }\n    }\n    while (!result.empty() && result.back() == "null") result.pop_back();\n    return result;\n}\n\nint main() {\n    string line1, line2;\n    getline(cin, line1);\n    getline(cin, line2);\n    // parse and build tree, then output level order\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line1 = sc.nextLine().trim();\n        String line2 = sc.nextLine().trim();\n        // parse and build tree, then output level order\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 9 20 15 7\n9 3 15 20 7\n', expected_output='3 9 20 null null 15 7\n', is_hidden=False),
        TestCase(input='-1\n-1\n', expected_output='-1\n', is_hidden=False),
        TestCase(input='1 2 3\n2 1 3\n', expected_output='1 2 null null 3\n', is_hidden=True),
        TestCase(input='1 2 4 5 3 6 7\n4 2 5 1 6 3 7\n', expected_output='1 2 3 4 5 6 7\n', is_hidden=True),
        TestCase(input='1 2 3 4\n4 3 2 1\n', expected_output='1 null 2 null 3 4\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['count-good-nodes-in-binary-tree'] = {
    "description": '# Count Good Nodes in Binary Tree\n\n## Statement\nGiven a binary tree root, a node X in the tree is named good if in the path from root to X there are no nodes with a value greater than X.\n\nReturn the number of good nodes in the binary tree.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the number of good nodes.\n\n## Constraints\n- The number of nodes in the binary tree is in the range [1, 10^5].\n- -10^4 <= Node.val <= 10^4\n\n## Example\n\n**Input**\n```\n3 1 4 3 null 1 5\n```\n**Output**\n```\n4\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nint goodNodes(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree and count good nodes\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree and count good nodes\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 1 4 3 null 1 5\n', expected_output='4\n', is_hidden=False),
        TestCase(input='3 3 null 4 2\n', expected_output='3\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='9 null 3 6 null null null 14 13 null null null 4 null null null 17 18 null 7\n', expected_output='8\n', is_hidden=True),
        TestCase(input='5 4 6 3 null null null 7\n', expected_output='4\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['diameter-of-binary-tree'] = {
    "description": '# Diameter of Binary Tree\n\n## Statement\nGiven the root of a binary tree, return the length of the diameter of the tree.\n\nThe diameter of a binary tree is the length of the longest path between any two nodes in a tree. This path may or may not pass through the root.\n\nThe length of a path between two nodes is represented by the number of edges between them.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the diameter.\n\n## Constraints\n- The number of nodes in the tree is in the range [1, 10^4].\n- -100 <= Node.val <= 100\n\n## Example\n\n**Input**\n```\n1 2 3 4 5\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nint diameterOfBinaryTree(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse and build tree, then call diameterOfBinaryTree\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse and build tree, then call diameterOfBinaryTree\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 4 5\n', expected_output='3\n', is_hidden=False),
        TestCase(input='1 2\n', expected_output='1\n', is_hidden=False),
        TestCase(input='1\n', expected_output='0\n', is_hidden=True),
        TestCase(input='1 2 3 4 5 6\n', expected_output='4\n', is_hidden=True),
        TestCase(input='1 2 3 null null 4 5 6 null 7\n', expected_output='5\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['invert-binary-tree'] = {
    "description": '# Invert Binary Tree\n\n## Statement\nGiven the root of a binary tree, invert the tree, and return its root.\n\nInverting a binary tree means swapping the left and right children of every node.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" (without quotes) to indicate a missing node.\n\n## Output Format\n- A single line of space-separated values representing the inverted tree in level-order.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 100].\n- -100 <= Node.val <= 100\n\n## Example\n\n**Input**\n```\n4 2 7 1 3 6 9\n```\n**Output**\n```\n4 7 2 9 6 3 1\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    if not data or data[0] == "null":\n        print("")\n        return\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n    inverted = invert_tree(root)\n    print(" ".join(level_order_values(inverted)))\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\ndef level_order_values(root):\n    if not root:\n        return []\n    result, queue = [], deque([root])\n    while queue:\n        node = queue.popleft()\n        if node:\n            result.append(str(node.val))\n            queue.append(node.left)\n            queue.append(node.right)\n        else:\n            result.append("null")\n    while result and result[-1] == "null":\n        result.pop()\n    return result\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nTreeNode* buildTree(vector<int>& vals) {\n    if (vals.empty() || vals[0] == -1001) return nullptr;\n    TreeNode* root = new TreeNode(vals[0]);\n    queue<TreeNode*> q;\n    q.push(root);\n    int i = 1;\n    while (!q.empty() && i < vals.size()) {\n        TreeNode* node = q.front(); q.pop();\n        if (i < vals.size() && vals[i] != -1001) {\n            node->left = new TreeNode(vals[i]);\n            q.push(node->left);\n        }\n        i++;\n        if (i < vals.size() && vals[i] != -1001) {\n            node->right = new TreeNode(vals[i]);\n            q.push(node->right);\n        }\n        i++;\n    }\n    return root;\n}\n\nvector<string> levelOrderValues(TreeNode* root) {\n    vector<string> result;\n    if (!root) return result;\n    queue<TreeNode*> q;\n    q.push(root);\n    while (!q.empty()) {\n        TreeNode* node = q.front(); q.pop();\n        if (node) {\n            result.push_back(to_string(node->val));\n            q.push(node->left);\n            q.push(node->right);\n        } else {\n            result.push_back("null");\n        }\n    }\n    while (!result.empty() && result.back() == "null") result.pop_back();\n    return result;\n}\n\nTreeNode* invertTree(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    istringstream iss(line);\n    vector<int> vals;\n    string token;\n    while (iss >> token) {\n        if (token == "null") vals.push_back(-1001);\n        else vals.push_back(stoi(token));\n    }\n    TreeNode* root = buildTree(vals);\n    TreeNode* inverted = invertTree(root);\n    auto result = levelOrderValues(inverted);\n    for (int i = 0; i < result.size(); i++) {\n        if (i) cout << " ";\n        cout << result[i];\n    }\n    cout << endl;\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String[] tokens = sc.nextLine().trim().split("\\\\s+");\n        List<Integer> vals = new ArrayList<>();\n        for (String t : tokens) {\n            if (t.equals("null")) vals.add(null);\n            else vals.add(Integer.parseInt(t));\n        }\n        TreeNode root = buildTree(vals);\n        TreeNode inverted = invertTree(root);\n        List<String> result = levelOrderValues(inverted);\n        System.out.println(String.join(" ", result));\n    }\n\n    // ===== YOUR CODE HERE =====\n}\n',
    },
    "test_cases": [
        TestCase(input='4 2 7 1 3 6 9\n', expected_output='4 7 2 9 6 3 1\n', is_hidden=False),
        TestCase(input='2 1 3\n', expected_output='2 3 1\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='\n', expected_output='\n', is_hidden=True),
        TestCase(input='1 2 3 4 5\n', expected_output='1 3 2 5 4\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['kth-smallest-element-in-a-bst'] = {
    "description": '# Kth Smallest Element in a BST\n\n## Statement\nGiven the root of a binary search tree, and an integer k, return the kth smallest value (1-indexed) of all the values of the nodes in the tree.\n\n## Input Format\n- First line: space-separated values for the BST in level-order.\n- Second line: an integer k.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the kth smallest element.\n\n## Constraints\n- The number of nodes in the tree is in the range [1, 10^4].\n- 1 <= k <= 10^4\n- -10^4 <= Node.val <= 10^4\n\n## Example\n\n**Input**\n```\n5 3 6 2 4 null null 1\n3\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().splitlines()\n    vals = [None if v == "null" else int(v) for v in data[0].split()]\n    k = int(data[1].strip())\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nint kthSmallest(TreeNode* root, int k) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse BST and find kth smallest\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse BST and find kth smallest\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5 3 6 2 4 null null 1\n3\n', expected_output='3\n', is_hidden=False),
        TestCase(input='3 1 4 null 2\n1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='5\n1\n', expected_output='5\n', is_hidden=True),
        TestCase(input='3 1 4 2\n2\n', expected_output='2\n', is_hidden=True),
        TestCase(input='2 1 3\n3\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['lowest-common-ancestor-bst'] = {
    "description": '# Lowest Common Ancestor of a Binary Search Tree\n\n## Statement\nGiven a binary search tree (BST), find the lowest common ancestor (LCA) of two given nodes in the BST.\n\nAccording to the definition of LCA on Wikipedia: "The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself)."n\n## Input Format\n- First line: space-separated values for the BST in level-order.\n- Second line: two integers p and q.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the value of the lowest common ancestor.\n\n## Constraints\n- The number of nodes in the tree is in the range [2, 10^5].\n- -10^9 <= Node.val <= 10^9\n- All Node.val are unique.\n- p != q\n- p and q will exist in the BST.\n\n## Example\n\n**Input**\n```\n6 2 8 0 4 7 9 null null 3 5\n2 8\n```\n**Output**\n```\n6\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().splitlines()\n    vals = [None if v == "null" else int(v) for v in data[0].split()]\n    p_val, q_val = int(data[1].split()[0]), int(data[1].split()[1])\n    root = build_tree(vals)\n    p = find_node(root, p_val)\n    q = find_node(root, q_val)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\ndef find_node(root, val):\n    if not root:\n        return None\n    if root.val == val:\n        return root\n    return find_node(root.left, val) or find_node(root.right, val)\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nTreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse BST and find LCA\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse BST and find LCA\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='6 2 8 0 4 7 9 null null 3 5\n2 8\n', expected_output='6\n', is_hidden=False),
        TestCase(input='6 2 8 0 4 7 9 null null 3 5\n2 4\n', expected_output='2\n', is_hidden=False),
        TestCase(input='2 1\n2 1\n', expected_output='2\n', is_hidden=True),
        TestCase(input='6 2 8 0 4 7 9 null null 3 5\n3 5\n', expected_output='4\n', is_hidden=True),
        TestCase(input='5 3 6 2 4 null null 1\n1 4\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['maximum-depth-binary-tree'] = {
    "description": '# Maximum Depth of Binary Tree\n\n## Statement\nGiven the root of a binary tree, return its maximum depth.\n\nA binary tree\'s maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single integer representing the maximum depth.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 10^4].\n- -100 <= Node.val <= 100\n\n## Example\n\n**Input**\n```\n3 9 20 null null 15 7\n```\n**Output**\n```\n3\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    if not data or data[0] == "null":\n        print(0)\n        return\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nint maxDepth(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    if (line.empty()) { cout << 0 << endl; return 0; }\n    istringstream iss(line);\n    vector<int> vals;\n    string token;\n    while (iss >> token) {\n        if (token == "null") vals.push_back(-1001);\n        else vals.push_back(stoi(token));\n    }\n    // parse and build tree, then call maxDepth\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse and build tree, then call maxDepth\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 9 20 null null 15 7\n', expected_output='3\n', is_hidden=False),
        TestCase(input='1 null 2\n', expected_output='2\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
        TestCase(input='\n', expected_output='0\n', is_hidden=True),
        TestCase(input='1 2 3 4 5 6 7\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['same-tree'] = {
    "description": '# Same Tree\n\n## Statement\nGiven the roots of two binary trees p and q, write a function to check if they are the same or not.\n\nTwo binary trees are considered the same if they are structurally identical, and the nodes have the same value.\n\n## Input Format\n- First line: space-separated values for tree p in level-order.\n- Second line: space-separated values for tree q in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- "true" if the trees are the same, "false" otherwise.\n\n## Constraints\n- The number of nodes in both trees is in the range [0, 100].\n- -10^4 <= Node.val <= 10^4\n\n## Example\n\n**Input**\n```\n1 2 3\n1 2 3\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().splitlines()\n    vals1 = [None if v == "null" else int(v) for v in data[0].split()]\n    vals2 = [None if v == "null" else int(v) for v in data[1].split()]\n    p = build_tree(vals1)\n    q = build_tree(vals2)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nbool isSameTree(TreeNode* p, TreeNode* q) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line1, line2;\n    getline(cin, line1);\n    getline(cin, line2);\n    // parse and build trees, then call isSameTree\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line1 = sc.nextLine().trim();\n        String line2 = sc.nextLine().trim();\n        // parse and build trees, then call isSameTree\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3\n1 2 3\n', expected_output='true\n', is_hidden=False),
        TestCase(input='1 2\n1 null 2\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1 2 1\n1 1 2\n', expected_output='false\n', is_hidden=True),
        TestCase(input='\n\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1\n1\n', expected_output='true\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['serialize-and-deserialize-binary-tree'] = {
    "description": '# Serialize and Deserialize Binary Tree\n\n## Statement\nSerialization is the process of converting a data structure into a sequence of bits so that it can be stored or transmitted. Once the data is stored in memory, the reverse process of reconstructing the data structure from that sequence is deserialization.\n\nGiven the root of a binary tree, design an algorithm to serialize and deserialize it. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- A single line: the serialized string followed by a newline, then the deserialized tree in level-order.\n\n## Constraints\n- The number of nodes in the tree is in the range [0, 10^4].\n- -1000 <= Node.val <= 1000\n\n## Example\n\n**Input**\n```\n1 2 3 null null 4 5\n```\n**Output**\n```\n1,2,3,null,null,4,5\n1 2 3 null null 4 5\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n    serialized = serialize(root)\n    deserialized = deserialize(serialized)\n    print(serialized)\n    print(" ".join(level_order_values(deserialized)))\n\n\ndef serialize(root):\n    # Implement this\n    pass\n\n\ndef deserialize(data):\n    # Implement this\n    pass\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\ndef level_order_values(root):\n    if not root:\n        return []\n    result, queue = [], deque([root])\n    while queue:\n        node = queue.popleft()\n        if node:\n            result.append(str(node.val))\n            queue.append(node.left)\n            queue.append(node.right)\n        else:\n            result.append("null")\n    while result and result[-1] == "null":\n        result.pop()\n    return result\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nstring serialize(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nTreeNode* deserialize(string data) {\n    // ===== YOUR CODE HERE =====\n}\n\nvector<string> levelOrderValues(TreeNode* root) {\n    vector<string> result;\n    if (!root) return result;\n    queue<TreeNode*> q;\n    q.push(root);\n    while (!q.empty()) {\n        TreeNode* node = q.front(); q.pop();\n        if (node) {\n            result.push_back(to_string(node->val));\n            q.push(node->left);\n            q.push(node->right);\n        } else {\n            result.push_back("null");\n        }\n    }\n    while (!result.empty() && result.back() == "null") result.pop_back();\n    return result;\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree, serialize, deserialize, and output\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree, serialize, deserialize, and output\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 null null 4 5\n', expected_output='1,2,3,null,null,4,5\n1 2 3 null null 4 5\n', is_hidden=False),
        TestCase(input='\n', expected_output='\n\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n1\n', is_hidden=True),
        TestCase(input='1 2\n', expected_output='1,2\n1 2\n', is_hidden=True),
        TestCase(input='1 2 3 4 5\n', expected_output='1,2,3,4,5\n1 2 3 4 5\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['subtree-of-another-tree'] = {
    "description": '# Subtree of Another Tree\n\n## Statement\nGiven the roots of two binary trees root and subRoot, return true if there is a subtree of root with the same structure and node values as subRoot and false otherwise.\n\nA subtree of a binary tree is a tree that consists of a node in root and all of this node\'s descendants. A tree is also considered a subtree of itself.\n\n## Input Format\n- First line: space-separated values for root in level-order.\n- Second line: space-separated values for subRoot in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- "true" if subRoot is a subtree of root, "false" otherwise.\n\n## Constraints\n- The number of nodes in root is in the range [1, 2000].\n- The number of nodes in subRoot is in the range [1, 1000].\n- -10^4 <= Node.val <= 10^4\n\n## Example\n\n**Input**\n```\n3 4 5 1 2\n4 1 2\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().splitlines()\n    vals1 = [None if v == "null" else int(v) for v in data[0].split()]\n    vals2 = [None if v == "null" else int(v) for v in data[1].split()]\n    root = build_tree(vals1)\n    subRoot = build_tree(vals2)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nbool isSubtree(TreeNode* root, TreeNode* subRoot) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line1, line2;\n    getline(cin, line1);\n    getline(cin, line2);\n    // parse and build trees, then call isSubtree\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line1 = sc.nextLine().trim();\n        String line2 = sc.nextLine().trim();\n        // parse and build trees, then call isSubtree\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 4 5 1 2\n4 1 2\n', expected_output='true\n', is_hidden=False),
        TestCase(input='3 4 5 1 2 null null null null 0\n4 1 2\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1 1\n1\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1 2 3 4 5\n2 4 5\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1 2 3\n2 3\n', expected_output='false\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['validate-binary-search-tree'] = {
    "description": '# Validate Binary Search Tree\n\n## Statement\nGiven the root of a binary tree, determine if it is a valid binary search tree (BST).\n\nA valid BST is defined as follows:\n- The left subtree of a node contains only nodes with keys less than the node\'s key.\n- The right subtree of a node contains only nodes with keys greater than the node\'s key.\n- Both the left and right subtrees must also be binary search trees.\n\n## Input Format\n- A single line of space-separated values representing the binary tree in level-order.\n- Use "null" to indicate a missing node.\n\n## Output Format\n- "true" if the tree is a valid BST, "false" otherwise.\n\n## Constraints\n- The number of nodes in the tree is in the range [1, 10^4].\n- -2^31 <= Node.val <= 2^31 - 1\n\n## Example\n\n**Input**\n```\n2 1 3\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\nfrom collections import deque\n\n\ndef main():\n    data = sys.stdin.read().strip().split()\n    vals = [None if v == "null" else int(v) for v in data]\n    root = build_tree(vals)\n\n    # ===== YOUR CODE HERE =====\n\n\ndef build_tree(vals):\n    if not vals or vals[0] is None:\n        return None\n    root = TreeNode(vals[0])\n    q = deque([root])\n    i = 1\n    while q and i < len(vals):\n        node = q.popleft()\n        if i < len(vals) and vals[i] is not None:\n            node.left = TreeNode(vals[i])\n            q.append(node.left)\n        i += 1\n        if i < len(vals) and vals[i] is not None:\n            node.right = TreeNode(vals[i])\n            q.append(node.right)\n        i += 1\n    return root\n\n\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nstruct TreeNode {\n    int val;\n    TreeNode *left, *right;\n    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}\n};\n\nbool isValidBST(TreeNode* root) {\n    // ===== YOUR CODE HERE =====\n}\n\nint main() {\n    string line;\n    getline(cin, line);\n    // parse tree and validate BST\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    static class TreeNode {\n        int val;\n        TreeNode left, right;\n        TreeNode(int v) { val = v; }\n    }\n\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String line = sc.nextLine().trim();\n        // parse tree and validate BST\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2 1 3\n', expected_output='true\n', is_hidden=False),
        TestCase(input='5 1 4 null null 3 6\n', expected_output='false\n', is_hidden=False),
        TestCase(input='1\n', expected_output='true\n', is_hidden=True),
        TestCase(input='1 1\n', expected_output='false\n', is_hidden=True),
        TestCase(input='5 4 6 null null 3 7\n', expected_output='false\n', is_hidden=True),
    ],
}

# ===========================================================================
# Linked List
# ===========================================================================

NEETCODE_AUTHORING['add-two-numbers'] = {
    "description": '# Add Two Numbers\n\n## Statement\nYou are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.\n\n## Input Format\n- First line: integer `n1` (length of list1)\n- Second line: `n1` space-separated integers (list1)\n- Third line: integer `n2` (length of list2)\n- Fourth line: `n2` space-separated integers (list2)\n\n## Output Format\n- Space-separated values of the sum linked list\n\n## Constraints\n- 1 <= n1, n2 <= 100\n- 0 <= Node.val <= 9\n- Lists represent numbers in reverse order\n\n## Example\n\n**Input**\n```\n3\n2 4 3\n3\n5 6 4\n```\n**Output**\n```\n7 0 8\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n2 4 3\n3\n5 6 4\n', expected_output='7 0 8\n', is_hidden=False),
        TestCase(input='1\n0\n1\n0\n', expected_output='0\n', is_hidden=False),
        TestCase(input='2\n9 9\n1\n1\n', expected_output='0 0 1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['copy-list-with-random-pointer'] = {
    "description": '# Copy List with Random Pointer\n\n## Statement\nA linked list of length n is given such that each node contains an additional random pointer, which could point to any node in the list, or null. Construct a deep copy of the list.\n\n## Input Format\n- First line: space-separated values representing the node values\n- Second line: space-separated random indices (-1 for null, 0-based index into original list)\n\n## Output Format\n- Space-separated values of the copied linked list (the copy has the same structure)\n\n## Constraints\n- 0 <= n <= 1000\n- -10000 <= Node.val <= 10000\n- Node.random is null or points to a node in the list\n\n## Example\n\n**Input**\n```\n7 13 11 10 1\n1 2 3 -1 0\n```\n**Output**\n```\n7 13 11 10 1\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='7 13 11 10 1\n1 2 3 -1 0\n', expected_output='7 13 11 10 1\n', is_hidden=False),
        TestCase(input='1 2\n1 -1\n', expected_output='1 2\n', is_hidden=False),
        TestCase(input='3\n-1\n', expected_output='3\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['find-the-duplicate-number'] = {
    "description": '# Find the Duplicate Number\n\n## Statement\nGiven an array of integers `nums` containing n + 1 integers where each integer is in the range [1, n] inclusive. There is only one repeated number in nums, return this repeated number. You must solve the problem without modifying the array and using constant extra space.\n\n## Input Format\n- First line: integer `n + 1` (size of array)\n- Second line: `n + 1` space-separated integers\n\n## Output Format\n- The duplicate number\n\n## Constraints\n- 1 <= n <= 10^5\n- nums.length == n + 1\n- 1 <= nums[i] <= n\n- All integers in nums are repeated exactly once except one\n\n## Example\n\n**Input**\n```\n5\n1 3 4 2 2\n```\n**Output**\n```\n2\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='5\n1 3 4 2 2\n', expected_output='2\n', is_hidden=False),
        TestCase(input='2\n1 1\n', expected_output='1\n', is_hidden=False),
        TestCase(input='6\n1 4 4 3 2 4\n', expected_output='4\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['linked-list-cycle'] = {
    "description": '# Linked List Cycle\n\n## Statement\nGiven head, the head of a linked list, determine if the linked list has a cycle in it. There is a cycle if some node in the list can be reached again by continuously following the next pointer. The input `pos` is used to denote the index (0-based) where the tail connects to. If pos is -1, there is no cycle.\n\n## Input Format\n- First line: space-separated values representing the linked list values\n- Second line: integer `pos` (index where tail connects, -1 if no cycle)\n\n## Output Format\n- `true` if there is a cycle, `false` otherwise\n\n## Constraints\n- 0 <= number of nodes <= 10^4\n- -10^5 <= Node.val <= 10^5\n- pos is -1 or a valid index\n\n## Example\n\n**Input**\n```\n3 2 0 -4\n1\n```\n**Output**\n```\ntrue\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3 2 0 -4\n1\n', expected_output='true\n', is_hidden=False),
        TestCase(input='1 2\n0\n', expected_output='true\n', is_hidden=False),
        TestCase(input='1\n-1\n', expected_output='false\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['lru-cache'] = {
    "description": '# LRU Cache\n\n## Statement\nDesign a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement the LRUCache class with `get(key)` and `put(key, value)` methods. Both operations must run in O(1) average time complexity.\n\n## Input Format\n- First line: integer `capacity`\n- Second line: integer `number of operations`\n- Next lines: operations, one per line:\n  - `get key` - get the value of key, return -1 if not found\n  - `put key value` - insert or update key-value pair\n\n## Output Format\n- For each `get` operation, output the value (or -1) on a separate line\n\n## Constraints\n- 1 <= capacity <= 3000\n- 0 <= key <= 10^4\n- 0 <= value <= 10^5\n- At most 2 * 10^5 calls to get and put\n\n## Example\n\n**Input**\n```\n2\n6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3\n```\n**Output**\n```\n1\n-1\n3\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='2\n6\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3\n', expected_output='1\n-1\n3\n', is_hidden=False),
        TestCase(input='1\n2\nput 2 1\nget 2\n', expected_output='1\n', is_hidden=False),
        TestCase(input='2\n5\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\n', expected_output='1\n-1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['merge-k-sorted-lists'] = {
    "description": '# Merge K Sorted Lists\n\n## Statement\nYou are given an array of `k` linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked list and return it.\n\n## Input Format\n- First line: integer `k` (number of lists)\n- For each list:\n  - First line: integer `n` (length of list)\n  - Second line: `n` space-separated integers\n\n## Output Format\n- Space-separated values of the merged sorted linked list\n\n## Constraints\n- 1 <= k <= 10^4\n- 0 <= lists[i].length <= 500\n- -10^4 <= lists[i][j] <= 10^4\n- Each list is sorted in ascending order\n\n## Example\n\n**Input**\n```\n3\n2\n1 4\n3\n2 5 3\n2\n6 0\n```\n**Output**\n```\n0 1 2 3 4 5 6\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n2\n1 4\n3\n2 5 3\n2\n6 0\n', expected_output='0 1 2 3 4 5 6\n', is_hidden=False),
        TestCase(input='1\n3\n1 2 3\n', expected_output='1 2 3\n', is_hidden=False),
        TestCase(input='2\n0\n\n1\n1\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['merge-two-sorted-lists'] = {
    "description": '# Merge Two Sorted Lists\n\n## Statement\nYou are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the head of the merged linked list.\n\n## Input Format\n- First line: integer `n1` (length of list1)\n- Second line: `n1` space-separated integers (list1)\n- Third line: integer `n2` (length of list2)\n- Fourth line: `n2` space-separated integers (list2)\n\n## Output Format\n- Space-separated values of the merged linked list\n\n## Constraints\n- 0 <= n1, n2 <= 50\n- -100 <= Node.val <= 100\n- Both lists are sorted in non-decreasing order\n\n## Example\n\n**Input**\n```\n3\n1 2 4\n3\n1 3 4\n```\n**Output**\n```\n1 1 2 3 4 4\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='3\n1 2 4\n3\n1 3 4\n', expected_output='1 1 2 3 4 4\n', is_hidden=False),
        TestCase(input='0\n\n0\n\n', expected_output='\n', is_hidden=False),
        TestCase(input='1\n1\n0\n\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['remove-nth-node-from-end-of-list'] = {
    "description": '# Remove Nth Node From End of List\n\n## Statement\nGiven the head of a linked list, remove the nth node from the end of the list and return its head.\n\n## Input Format\n- First line: space-separated values representing the linked list\n- Second line: integer `n` (index from end, 1-based)\n\n## Output Format\n- Space-separated values of the remaining linked list\n\n## Constraints\n- 1 <= number of nodes <= 30\n- 0 <= Node.val <= 100\n- 1 <= n <= size of list\n\n## Example\n\n**Input**\n```\n1 2 3 4 5\n2\n```\n**Output**\n```\n1 2 3 5\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 4 5\n2\n', expected_output='1 2 3 5\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='\n', is_hidden=False),
        TestCase(input='1 2\n1\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reorder-list'] = {
    "description": "# Reorder List\n\n## Statement\nYou are given the head of a singly linked-list. The list can be represented as: L0 -> L1 -> ... -> Ln-1 -> Ln. Reorder the list to be on the following form: L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ... You may not modify the values in the list's nodes. Only nodes themselves may be changed.\n\n## Input Format\n- Space-separated values representing the linked list\n\n## Output Format\n- Space-separated values of the reordered linked list\n\n## Constraints\n- 1 <= number of nodes <= 5 * 10^4\n- -1000 <= Node.val <= 1000\n\n## Example\n\n**Input**\n```\n1 2 3 4\n```\n**Output**\n```\n1 4 2 3\n```",
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 4\n', expected_output='1 4 2 3\n', is_hidden=False),
        TestCase(input='1 2 3 4 5\n', expected_output='1 5 2 4 3\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reverse-linked-list'] = {
    "description": '# Reverse Linked List\n\n## Statement\nGiven the head of a singly linked list, reverse the list, and return the reversed list.\n\n## Input Format\n- Space-separated values representing the linked list\n\n## Output Format\n- Space-separated values of the reversed linked list\n\n## Constraints\n- 0 <= number of nodes <= 5000\n- -5000 <= Node.val <= 5000\n\n## Example\n\n**Input**\n```\n1 2 3 4 5\n```\n**Output**\n```\n5 4 3 2 1\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().split()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 4 5\n', expected_output='5 4 3 2 1\n', is_hidden=False),
        TestCase(input='1 2\n', expected_output='2 1\n', is_hidden=False),
        TestCase(input='1\n', expected_output='1\n', is_hidden=True),
    ],
}

NEETCODE_AUTHORING['reverse-nodes-in-k-group'] = {
    "description": '# Reverse Nodes in k-Group\n\n## Statement\nGiven the head of a linked list, reverse the nodes of the list k at a time, and return the modified list. k is a positive integer and is less than or equal to the length of the linked list. If the number of nodes is not a multiple of k, the left-out nodes at the end should remain in their original order.\n\n## Input Format\n- First line: space-separated values representing the linked list\n- Second line: integer `k`\n\n## Output Format\n- Space-separated values of the modified linked list\n\n## Constraints\n- 1 <= k <= number of nodes <= 5000\n- 0 <= Node.val <= 1000\n\n## Example\n\n**Input**\n```\n1 2 3 4 5\n2\n```\n**Output**\n```\n2 1 4 3 5\n```',
    "starter_code": {
        'python': 'import sys\n\n\ndef main():\n    data = sys.stdin.read().splitlines()\n    # parse\n\n    # ===== YOUR CODE HERE =====\n\n\nif __name__ == "__main__":\n    main()\n',
        'cpp': '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // parse\n\n    // ===== YOUR CODE HERE =====\n\n    return 0;\n}\n',
        'java': 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // parse\n\n        // ===== YOUR CODE HERE =====\n    }\n}\n',
    },
    "test_cases": [
        TestCase(input='1 2 3 4 5\n2\n', expected_output='2 1 4 3 5\n', is_hidden=False),
        TestCase(input='1 2 3 4 5\n3\n', expected_output='3 2 1 4 5\n', is_hidden=False),
        TestCase(input='1\n1\n', expected_output='1\n', is_hidden=True),
    ],
}
