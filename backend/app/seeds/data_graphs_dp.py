from app.seeds.data_arrays import starters

GRAPHS_DP = [
    {
        "title": "Flood Fill",
        "slug": "flood-fill",
        "pattern_key": "graphs",
        "difficulty": "EASY",
        "topic": "GRAPH",
        "description": """# Flood Fill

## Statement
You are given an image as a 2D grid of integers, a starting pixel `(sr, sc)` and a replacement color. Perform a flood fill: change the color of the starting pixel **and every 4-directionally connected pixel sharing its original color**, then print the resulting image.

## Input Format
- Line 1: integers `R C` (grid dimensions)
- Next `R` lines: `C` space-separated integers per row
- Last line: integers `sr sc newColor`

## Output Format
The filled grid — one row per line, values separated by spaces.

## Constraints
- `1 <= R, C <= 50`
- `0 <= image[i][j], newColor <= 10^5`
- `0 <= sr < R`, `0 <= sc < C`

## Example 1

**Input**
```
3 3
1 1 1
1 1 0
1 0 1
1 1 2
```
**Output**
```
2 2 2
2 2 0
2 0 1
```

Explanation: Starting at (1,1), the connected region of 1s is recolored to 2, stopping at the 0s.

## Example 2

**Input**
```
1 1
0
0 0 0
```
**Output**
```
0
```

Explanation: A single 0 recolored to 0 is an identity fill.
""",
        "starter_code": starters(
            py="""import sys
sys.setrecursionlimit(10000)


def main():
    data = sys.stdin.read().split()
    idx = 0
    r, c = int(data[idx]), int(data[idx + 1])
    idx += 2
    image = []
    for _ in range(r):
        image.append([int(x) for x in data[idx:idx + c]])
        idx += c
    sr, scc, color = int(data[idx]), int(data[idx + 1]), int(data[idx + 2])

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int r, c;
    cin >> r >> c;
    vector<vector<int>> image(r, vector<int>(c));
    for (auto& row : image)
        for (auto& x : row) cin >> x;
    int sr, scc, color;
    cin >> sr >> scc >> color;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt(), c = sc.nextInt();
        int[][] image = new int[r][c];
        for (int[] row : image)
            for (int j = 0; j < c; j++) row[j] = sc.nextInt();
        int sr = sc.nextInt(), scc = sc.nextInt(), color = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "3 3\n1 1 1\n1 1 0\n1 0 1\n1 1 2\n", "expected_output": "2 2 2\n2 2 0\n2 0 1", "is_hidden": False},
            {"input": "1 1\n0\n0 0 0\n", "expected_output": "0", "is_hidden": False},
            {"input": "2 2\n1 2\n2 1\n0 0 3\n", "expected_output": "3 2\n2 1", "is_hidden": False},
            {"input": "3 2\n5 5\n5 7\n7 7\n2 0 9\n", "expected_output": "5 5\n5 9\n9 9", "is_hidden": True},
            {"input": "1 4\n8 8 8 8\n0 3 1\n", "expected_output": "1 1 1 1", "is_hidden": True},
        ],
    },
    {
        "title": "Number of Islands",
        "slug": "number-of-islands",
        "difficulty": "MEDIUM",
        "topic": "GRAPH",
        "description": """# Number of Islands

## Statement
You are given a binary grid where `'1'` is land and `'0'` is water. An **island** is a maximal group of land cells connected 4-directionally (all surrounding cells are water; the grid's edges are coastline). Count the islands.

## Input Format
- Line 1: integers `R C`
- Next `R` lines: a string of `C` characters, each `0` or `1`

## Output Format
A single integer — the number of islands.

## Constraints
- `1 <= R, C <= 300`

## Example 1

**Input**
```
4 5
11110
11010
11000
00000
```
**Output**
```
1
```

Explanation: All four connected 1s form one island.

## Example 2

**Input**
```
4 5
11000
11000
00100
00011
```
**Output**
```
3
```

Explanation: Three separate clusters of 1s exist: one of four, one of one (via the diagonal 1), and one of two.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    r, c = int(data[0]), int(data[1])
    grid = [list(data[2 + i]) for i in range(r)]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int r, c;
    cin >> r >> c;
    vector<vector<char>> grid(r, vector<char>(c));
    for (auto& row : grid)
        for (auto& ch : row) cin >> ch;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int r = sc.nextInt(), c = sc.nextInt();
        char[][] grid = new char[r][];
        for (int i = 0; i < r; i++) grid[i] = sc.next().toCharArray();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "4 5\n11110\n11010\n11000\n00000\n", "expected_output": "1", "is_hidden": False},
            {"input": "4 5\n11000\n11000\n00100\n00011\n", "expected_output": "3", "is_hidden": False},
            {"input": "1 1\n0\n", "expected_output": "0", "is_hidden": False},
            {"input": "1 5\n10101\n", "expected_output": "3", "is_hidden": True},
            {"input": "3 3\n111\n101\n111\n", "expected_output": "1", "is_hidden": True},
        ],
    },
    {
        "title": "Course Schedule",
        "slug": "course-schedule",
        "difficulty": "MEDIUM",
        "topic": "GRAPH",
        "description": """# Course Schedule

## Statement
There are `V` courses numbered `0..V-1` and `E` prerequisite pairs. A pair `a b` means you must take course `b` before course `a`. Determine whether it is possible to finish all courses — i.e., whether the prerequisite graph has no cycle.

This is cycle detection on a directed graph (Kahn's BFS by in-degree or DFS coloring both work).

## Input Format
- Line 1: integers `V E`
- Next `E` lines: two integers `a b` meaning `b` must be taken before `a`

## Output Format
`true` if all courses can be finished, otherwise `false`.

## Constraints
- `1 <= V <= 2000`
- `0 <= E <= 5000`
- No duplicate pairs.

## Example 1

**Input**
```
2 2
1 0
0 1
```
**Output**
```
false
```

Explanation: courses 0 and 1 require each other.

## Example 2

**Input**
```
2 1
1 0
```
**Output**
```
true
```

Explanation: Course 1 depends only on course 0, which has no prerequisites, so every course can be completed.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    v, e = int(data[0]), int(data[1])
    edges = []
    idx = 2
    for _ in range(e):
        edges.append((int(data[idx]), int(data[idx + 1])))
        idx += 2

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int v, e;
    cin >> v >> e;
    vector<pair<int,int>> edges(e);
    for (auto& [a, b] : edges) cin >> a >> b;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int v = sc.nextInt(), e = sc.nextInt();
        int[][] edges = new int[e][2];
        for (int[] p : edges) { p[0] = sc.nextInt(); p[1] = sc.nextInt(); }

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "2 2\n1 0\n0 1\n", "expected_output": "false", "is_hidden": False},
            {"input": "2 1\n1 0\n", "expected_output": "true", "is_hidden": False},
            {"input": "4 4\n1 0\n2 1\n3 2\n0 3\n", "expected_output": "false", "is_hidden": False},
            {"input": "3 0\n", "expected_output": "true", "is_hidden": True},
            {"input": "5 4\n1 0\n2 0\n3 1\n4 3\n", "expected_output": "true", "is_hidden": True},
        ],
    },
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "difficulty": "EASY",
        "topic": "DP",
        "description": """# Climbing Stairs

## Statement
You are climbing a staircase with `n` steps. Each move you may climb **1 or 2 steps**. In how many distinct ways can you reach the top?

## Input Format
- Line 1: integer `n`

## Output Format
A single integer — the number of distinct ways.

## Constraints
- `1 <= n <= 45`

## Example 1

**Input**
```
3
```
**Output**
```
3
```

Explanation: `1+1+1`, `1+2`, `2+1`.

## Example 2

**Input**
```
5
```
**Output**
```
8
```

Explanation: There are 8 distinct ways to climb 5 steps using 1- and 2-step moves.
""",
        "starter_code": starters(
            py="""import sys


def main():
    n = int(input())

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "3\n", "expected_output": "3", "is_hidden": False},
            {"input": "5\n", "expected_output": "8", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "2\n", "expected_output": "2", "is_hidden": True},
            {"input": "45\n", "expected_output": "1836311903", "is_hidden": True},
        ],
    },
    {
        "title": "Unique Paths",
        "slug": "unique-paths",
        "difficulty": "MEDIUM",
        "topic": "DP",
        "description": """# Unique Paths

## Statement
A robot starts at the top-left corner of an `m x n` grid and wants to reach the bottom-right corner. It may only move **right** or **down**. Count the number of unique paths.

## Input Format
- Line 1: integers `m n`

## Output Format
A single integer — the number of unique paths.

## Constraints
- `1 <= m, n <= 100`
- The answer fits in a 32-bit integer... barely for the extremes; a 64-bit intermediate is safer.

## Example 1

**Input**
```
3 7
```
**Output**
```
28
```

Explanation: A 3x7 grid has C(8, 2) = 28 distinct downward/rightward routes from top-left to bottom-right.

## Example 2

**Input**
```
3 2
```
**Output**
```
3
```

Explanation: A 3x2 grid has exactly 3 paths: DDR, DRD, and RDD.
""",
        "starter_code": starters(
            py="""import sys


def main():
    m, n = map(int, input().split())

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int m, n;
    cin >> m >> n;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int m = sc.nextInt(), n = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "3 7\n", "expected_output": "28", "is_hidden": False},
            {"input": "3 2\n", "expected_output": "3", "is_hidden": False},
            {"input": "1 1\n", "expected_output": "1", "is_hidden": False},
            {"input": "1 10\n", "expected_output": "1", "is_hidden": True},
            {"input": "23 12\n", "expected_output": "193536720", "is_hidden": True},
        ],
    },
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "difficulty": "MEDIUM",
        "topic": "DP",
        "description": """# Coin Change

## Statement
You are given coin denominations (unlimited supply of each) and a target amount. Return the **fewest number of coins** needed to make up the amount, or `-1` if it is impossible.

## Input Format
- Line 1: space-separated coin denominations
- Line 2: integer `amount`

## Output Format
A single integer — minimum coins, or `-1`.

## Constraints
- `1 <= number of denominations <= 12`
- `1 <= coin <= 2^31 - 1`
- `0 <= amount <= 10^4`

## Example 1

**Input**
```
1 2 5
11
```
**Output**
```
3
```

Explanation: `5 + 5 + 1`.

## Example 2

**Input**
```
2
3
```
**Output**
```
-1
```

Explanation: 11 cannot be formed from coin 2 alone, so no combination works and the answer is -1.
""",
        "starter_code": starters(
            py="""import sys


def main():
    lines = sys.stdin.read().splitlines()
    coins = [int(x) for x in lines[0].split()]
    amount = int(lines[1])

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string line;
    getline(cin, line);
    vector<int> coins;
    istringstream iss(line);
    int x;
    while (iss >> x) coins.push_back(x);
    int amount;
    cin >> amount;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String[] parts = sc.nextLine().trim().split("\\\\s+");
        int[] coins = new int[parts.length];
        for (int i = 0; i < parts.length; i++) coins[i] = Integer.parseInt(parts[i]);
        int amount = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "1 2 5\n11\n", "expected_output": "3", "is_hidden": False},
            {"input": "2\n3\n", "expected_output": "-1", "is_hidden": False},
            {"input": "1\n0\n", "expected_output": "0", "is_hidden": False},
            {"input": "1 2147483647\n2\n", "expected_output": "2", "is_hidden": True},
            {"input": "186 419 83 408\n6249\n", "expected_output": "20", "is_hidden": True},
        ],
    },
    {
        "title": "Longest Increasing Subsequence",
        "slug": "longest-increasing-subsequence",
        "difficulty": "MEDIUM",
        "topic": "DP",
        "description": """# Longest Increasing Subsequence

## Statement
Given an integer array `nums`, return the length of the longest **strictly increasing** subsequence. The O(n²) DP is a fine first pass; the O(n log n) patience-sorting approach is the stretch goal.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
A single integer — LIS length.

## Constraints
- `1 <= n <= 2500`
- `-10^4 <= nums[i] <= 10^4`

## Example 1

**Input**
```
8
10 9 2 5 3 7 101 18
```
**Output**
```
4
```

Explanation: `[2, 3, 7, 101]` (other lengths of 4 exist).

## Example 2

**Input**
```
6
0 1 0 3 2 3
```
**Output**
```
4
```

Explanation: Using every other element gives [0, 1, 3] or [0, 1, 2, 3]; the longest strictly increasing subsequence has length 4.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n + 1]]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> nums(n);
    for (auto& x : nums) cin >> x;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "8\n10 9 2 5 3 7 101 18\n", "expected_output": "4", "is_hidden": False},
            {"input": "6\n0 1 0 3 2 3\n", "expected_output": "4", "is_hidden": False},
            {"input": "1\n7\n", "expected_output": "1", "is_hidden": False},
            {"input": "4\n7 7 7 7\n", "expected_output": "1", "is_hidden": True},
            {"input": "6\n1 3 6 7 9 4\n", "expected_output": "5", "is_hidden": True},
        ],
    },
    {
        "title": "Word Break",
        "slug": "word-break",
        "difficulty": "MEDIUM",
        "topic": "DP",
        "description": """# Word Break

## Statement
Given a string `s` and a dictionary of words, determine whether `s` can be segmented into a space-separated sequence of one or more dictionary words. Words from the dictionary may be reused any number of times.

## Input Format
- Line 1: string `s` (lowercase letters)
- Line 2: integer `k`
- Line 3: `k` space-separated dictionary words

## Output Format
`true` or `false` (lowercase).

## Constraints
- `1 <= s.length <= 300`
- `1 <= k <= 20`
- Dictionary words are 1..20 lowercase letters and unique.

## Example 1

**Input**
```
applepenapple
2
apple pen
```
**Output**
```
true
```

Explanation: `"apple pen apple"`.

## Example 2

**Input**
```
catsandog
5
cats dog sand and cat
```
**Output**
```
false
```

Explanation: No segmentation of "catsandog" uses only the dictionary; the "sand"/"dog" split out of order never tiles the word.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    s = data[0]
    k = int(data[1])
    words = data[2:2 + k]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    int k;
    cin >> s >> k;
    vector<string> words(k);
    for (auto& w : words) cin >> w;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();
        int k = sc.nextInt();
        String[] words = new String[k];
        for (int i = 0; i < k; i++) words[i] = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "applepenapple\n2\napple pen\n", "expected_output": "true", "is_hidden": False},
            {"input": "catsandog\n5\ncats dog sand and cat\n", "expected_output": "false", "is_hidden": False},
            {"input": "aaaaaaa\n2\naaaa aaa\n", "expected_output": "true", "is_hidden": False},
            {"input": "abcd\n3\na abc b\n", "expected_output": "false", "is_hidden": True},
            {"input": "goalspecial\n2\ngoal special\n", "expected_output": "true", "is_hidden": True},
        ],
    },
    {
        "title": "Edit Distance",
        "slug": "edit-distance",
        "difficulty": "HARD",
        "topic": "DP",
        "description": """# Edit Distance

## Statement
Given two strings `word1` and `word2`, return the minimum number of operations to convert `word1` into `word2`, where an operation is one of: **insert** a character, **delete** a character, or **replace** a character. The classic 2-D DP table problem.

## Input Format
- Line 1: string `word1`
- Line 2: string `word2`

## Output Format
A single integer — the minimum edit distance.

## Constraints
- `0 <= word1.length, word2.length <= 500`

## Example 1

**Input**
```
horse
ros
```
**Output**
```
3
```

Explanation: horse -> rorse (replace h) -> rose (delete r) -> ros (delete e).

## Example 2

**Input**
```
intention
execution
```
**Output**
```
5
```

Explanation: Transforming "intention" into "execution" needs 5 edits (delete i, substitute n/e, etc.).
""",
        "starter_code": starters(
            py="""import sys


def main():
    lines = sys.stdin.read().splitlines()

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string a, b;
    cin >> a >> b;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String a = sc.next();
        String b = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "horse\nros\n", "expected_output": "3", "is_hidden": False},
            {"input": "intention\nexecution\n", "expected_output": "5", "is_hidden": False},
            {"input": "\n\n", "expected_output": "0", "is_hidden": False},
            {"input": "abc\nabc\n", "expected_output": "0", "is_hidden": True},
            {"input": "a\n\n", "expected_output": "1", "is_hidden": True},
            {"input": "algorithm\naltruistic\n", "expected_output": "6", "is_hidden": True},
        ],
    },
]






