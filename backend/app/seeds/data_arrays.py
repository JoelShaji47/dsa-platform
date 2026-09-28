PY = "python"
CPP = "cpp"
JAVA = "java"


def starters(py: str, cpp: str, java: str) -> dict:
    return {PY: py, CPP: cpp, JAVA: java}


ARRAY_PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "EASY",
        "topic": "ARRAY",
        "description": """# Two Sum

## Statement
Given an array of `n` integers `nums` and an integer `target`, return the **indices** of the two numbers such that they add up to `target`.

Each input has exactly one solution, and you may not use the same element twice. Return the indices in ascending order (`i < j`).

## Input Format
- Line 1: integer `n` — the size of the array
- Line 2: `n` space-separated integers — the array `nums`
- Line 3: integer `target`

## Output Format
Two space-separated integers `i j` with `i < j`.

## Constraints
- `2 <= n <= 10^4`
- `-10^9 <= nums[i], target <= 10^9`
- Exactly one valid answer exists.

## Example 1

**Input**
```
4
2 7 11 15
9
```
**Output**
```
0 1
```

Explanation: `nums[0] + nums[1] == 9`.

## Example 2

**Input**
```
3
3 2 4
6
```
**Output**
```
1 2
```

Explanation: nums[1] + nums[2] == 3 + 2 == 6, so the indices are 1 2.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n + 1]]
    target = int(data[n + 1])

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
    long long target;
    cin >> target;

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
        long target = sc.nextLong();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "4\n2 7 11 15\n9\n", "expected_output": "0 1", "is_hidden": False},
            {"input": "3\n3 2 4\n6\n", "expected_output": "1 2", "is_hidden": False},
            {"input": "2\n3 3\n6\n", "expected_output": "0 1", "is_hidden": False},
            {"input": "5\n-3 4 3 90 0\n0\n", "expected_output": "0 2", "is_hidden": True},
            {"input": "6\n-10 7 19 15 -4 12\n22\n", "expected_output": "1 3", "is_hidden": True},
        ],
    },
    {
        "title": "Move Zeroes",
        "slug": "move-zeroes",
        "pattern_key": "two-pointers",
        "difficulty": "EASY",
        "topic": "ARRAY",
        "description": """# Move Zeroes

## Statement
Given an array `nums`, move all `0`s to the end of it while maintaining the relative order of the non-zero elements. The operation must be done conceptually in-place; print the resulting array.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
The transformed array as `n` space-separated integers.

## Constraints
- `1 <= n <= 10^4`
- `-10^9 <= nums[i] <= 10^9`

## Example 1

**Input**
```
5
0 1 0 3 12
```
**Output**
```
1 3 12 0 0
```

Explanation: Moving all zeroes to the end preserves the order [1, 3, 12].

## Example 2

**Input**
```
1
0
```
**Output**
```
0
```

Explanation: A single zero stays in place as the whole array.
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
            {"input": "5\n0 1 0 3 12\n", "expected_output": "1 3 12 0 0", "is_hidden": False},
            {"input": "1\n0\n", "expected_output": "0", "is_hidden": False},
            {"input": "4\n0 0 0 0\n", "expected_output": "0 0 0 0", "is_hidden": False},
            {"input": "5\n1 2 3 4 5\n", "expected_output": "1 2 3 4 5", "is_hidden": True},
            {"input": "6\n4 0 -1 0 3 0\n", "expected_output": "4 -1 3 0 0 0", "is_hidden": True},
        ],
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": "MEDIUM",
        "topic": "ARRAY",
        "description": """# Maximum Subarray

## Statement
Given an integer array `nums`, find the contiguous subarray (containing at least one number) which has the largest sum, and return that sum. Aim for an O(n) solution (Kadane's algorithm).

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
A single integer — the maximum subarray sum.

## Constraints
- `1 <= n <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Example 1

**Input**
```
9
-2 1 -3 4 -1 2 1 -5 4
```
**Output**
```
6
```

Explanation: subarray `[4, -1, 2, 1]` has the largest sum `6`.

## Example 2

**Input**
```
1
-5
```
**Output**
```
-5
```

Explanation: The whole array is a single value, so the best subarray is that value, -5.
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
            {"input": "9\n-2 1 -3 4 -1 2 1 -5 4\n", "expected_output": "6", "is_hidden": False},
            {"input": "1\n-5\n", "expected_output": "-5", "is_hidden": False},
            {"input": "5\n5 4 -1 7 8\n", "expected_output": "23", "is_hidden": False},
            {"input": "2\n-1 -2\n", "expected_output": "-1", "is_hidden": True},
            {"input": "8\n-2 -3 4 -1 -2 1 5 -3\n", "expected_output": "7", "is_hidden": True},
        ],
    },
    {
        "title": "Subarray Sum Equals K",
        "slug": "subarray-sum-equals-k",
        "pattern_key": "arrays-hashing",
        "difficulty": "MEDIUM",
        "topic": "ARRAY",
        "description": """# Subarray Sum Equals K

## Statement
Given an integer array `nums` and an integer `k`, return the total number of contiguous subarrays whose elements sum exactly to `k`.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers
- Line 3: integer `k`

## Output Format
A single integer — the count of qualifying subarrays.

## Constraints
- `1 <= n <= 10^5`
- `-10^4 <= nums[i], k <= 10^4`

## Example 1

**Input**
```
3
1 1 1
2
```
**Output**
```
2
```

Explanation: subarrays `[1,1]` (indices 0-1) and `[1,1]` (indices 1-2).

## Example 2

**Input**
```
3
1 2 3
3
```
**Output**
```
2
```

Explanation: Two contiguous windows sum to 3: [3] and [1, 2].
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = [int(x) for x in data[1:n + 1]]
    k = int(data[n + 1])

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
    int k;
    cin >> k;

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
        int k = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "3\n1 1 1\n2\n", "expected_output": "2", "is_hidden": False},
            {"input": "3\n1 2 3\n3\n", "expected_output": "2", "is_hidden": False},
            {"input": "8\n3 4 7 2 -3 1 4 2\n7\n", "expected_output": "4", "is_hidden": False},
            {"input": "3\n1 -1 0\n0\n", "expected_output": "3", "is_hidden": True},
            {"input": "5\n0 0 0 0 0\n0\n", "expected_output": "15", "is_hidden": True},
        ],
    },
    {
        "title": "Product of Array Except Self",
        "slug": "product-of-array-except-self",
        "difficulty": "MEDIUM",
        "topic": "ARRAY",
        "description": """# Product of Array Except Self

## Statement
Given an integer array `nums`, return an array `answer` such that `answer[i]` equals the product of all elements of `nums` except `nums[i]`.

You must write an algorithm that runs in O(n) time and **without using division**.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
`n` space-separated integers — the answer array.

## Constraints
- `2 <= n <= 10^5`
- `-30 <= nums[i] <= 30`
- The product of any prefix or suffix fits in a 32-bit integer.

## Example 1

**Input**
```
4
1 2 3 4
```
**Output**
```
24 12 8 6
```

Explanation: Multiplying the other elements: [2*3*4, 1*3*4, 1*2*4, 1*2*3] = [24, 12, 8, 6].

## Example 2

**Input**
```
5
-1 1 0 -3 3
```
**Output**
```
0 0 9 0 0
```

Explanation: Every product touches the zero, so all entries are 0 except position 2, which is 3*3 = 9.
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
            {"input": "4\n1 2 3 4\n", "expected_output": "24 12 8 6", "is_hidden": False},
            {"input": "5\n-1 1 0 -3 3\n", "expected_output": "0 0 9 0 0", "is_hidden": False},
            {"input": "3\n0 0 5\n", "expected_output": "0 0 0", "is_hidden": False},
            {"input": "2\n7 3\n", "expected_output": "3 7", "is_hidden": True},
            {"input": "4\n2 -2 2 -2\n", "expected_output": "8 -8 8 -8", "is_hidden": True},
        ],
    },
    {
        "title": "First Missing Positive",
        "slug": "first-missing-positive",
        "pattern_key": "arrays-hashing",
        "difficulty": "HARD",
        "topic": "ARRAY",
        "description": """# First Missing Positive

## Statement
Given an unsorted integer array `nums`, return the smallest positive integer that does **not** appear in it.

The ideal solution runs in O(n) time using O(1) extra space, though O(n) space solutions are accepted within limits.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
A single integer — the smallest missing positive.

## Constraints
- `1 <= n <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

## Example 1

**Input**
```
4
3 4 -1 1
```
**Output**
```
2
```

Explanation: 1 and 3 appear but 2 is the smallest positive integer missing from [3, 4, -1, 1].

## Example 2

**Input**
```
3
1 2 0
```
**Output**
```
3
```

Explanation: [1, 2, 0] already contains all positive numbers up to 2, so 3 is the missing one.
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
            {"input": "4\n3 4 -1 1\n", "expected_output": "2", "is_hidden": False},
            {"input": "3\n1 2 0\n", "expected_output": "3", "is_hidden": False},
            {"input": "3\n7 8 9\n", "expected_output": "1", "is_hidden": False},
            {"input": "5\n1 2 3 4 5\n", "expected_output": "6", "is_hidden": True},
            {"input": "2\n-5 -3\n", "expected_output": "1", "is_hidden": True},
        ],
    },
]
