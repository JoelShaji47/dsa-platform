from app.seeds.data_arrays import starters

LINKED_STACK = [
    {
        "title": "Reverse Linked List",
        "slug": "reverse-linked-list",
        "difficulty": "EASY",
        "topic": "LINKED_LIST",
        "description": """# Reverse Linked List

## Statement
Given the head of a singly linked list of `n` nodes, reverse the list and print its values in order. Try the iterative O(n) O(1) approach; the recursive version is also accepted.

The input gives the node values in order — build the list first (done for you in the starter code).

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers — node values head to tail

## Output Format
`n` space-separated integers — values after reversal.

## Constraints
- `1 <= n <= 10^4`
- `-10^3 <= val <= 10^3`

## Example 1

**Input**
```
5
1 2 3 4 5
```
**Output**
```
5 4 3 2 1
```

Explanation: Reversing 1 -> 2 -> 3 -> 4 -> 5 produces 5 -> 4 -> 3 -> 2 -> 1.

## Example 2

**Input**
```
1
42
```
**Output**
```
42
```

Explanation: A single-node list still reverses to itself, 42.
""",
        "starter_code": starters(
            py="""import sys


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_array(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    values = [int(x) for x in data[1:n + 1]]
    head = build_list(values)

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v) : val(v), next(nullptr) {}
};

int main() {
    int n;
    cin >> n;
    ListNode dummy(0);
    ListNode* tail = &dummy;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        tail->next = new ListNode(x);
        tail = tail->next;
    }
    ListNode* head = dummy.next;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v) { val = v; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ListNode dummy = new ListNode(0), tail = dummy;
        for (int i = 0; i < n; i++) {
            tail.next = new ListNode(sc.nextInt());
            tail = tail.next;
        }
        ListNode head = dummy.next;

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "5\n1 2 3 4 5\n", "expected_output": "5 4 3 2 1", "is_hidden": False},
            {"input": "1\n42\n", "expected_output": "42", "is_hidden": False},
            {"input": "2\n7 -7\n", "expected_output": "-7 7", "is_hidden": False},
            {"input": "6\n1 1 2 2 3 3\n", "expected_output": "3 3 2 2 1 1", "is_hidden": True},
        ],
    },
    {
        "title": "Middle of the Linked List",
        "slug": "middle-of-the-linked-list",
        "pattern_key": "linked-list",
        "difficulty": "EASY",
        "topic": "LINKED_LIST",
        "description": """# Middle of the Linked List

## Statement
Given the head of a singly linked list, return the middle node's value. If there are two middle nodes, return the **second** one.

Aim for the two-pointer (slow/fast) single-pass technique.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
A single integer — the middle node's value.

## Constraints
- `1 <= n <= 10^4`

## Example 1

**Input**
```
5
1 2 3 4 5
```
**Output**
```
3
```

Explanation: With five nodes, the middle node is the third one, value 3.

## Example 2

**Input**
```
6
1 2 3 4 5 6
```
**Output**
```
4
```

Explanation: With six nodes, the second middle node is the fourth one, value 4.
""",
        "starter_code": starters(
            py="""import sys


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    values = [int(x) for x in data[1:n + 1]]
    head = build_list(values)

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v) : val(v), next(nullptr) {}
};

int main() {
    int n;
    cin >> n;
    ListNode dummy(0);
    ListNode* tail = &dummy;
    for (int i = 0; i < n; i++) {
        tail->next = new ListNode(0);
        cin >> tail->next->val;
        tail = tail->next;
    }
    ListNode* head = dummy.next;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v) { val = v; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ListNode dummy = new ListNode(0), tail = dummy;
        for (int i = 0; i < n; i++) {
            tail.next = new ListNode(sc.nextInt());
            tail = tail.next;
        }
        ListNode head = dummy.next;

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "5\n1 2 3 4 5\n", "expected_output": "3", "is_hidden": False},
            {"input": "6\n1 2 3 4 5 6\n", "expected_output": "4", "is_hidden": False},
            {"input": "1\n9\n", "expected_output": "9", "is_hidden": False},
            {"input": "2\n8 9\n", "expected_output": "9", "is_hidden": True},
            {"input": "7\n11 22 33 44 55 66 77\n", "expected_output": "44", "is_hidden": True},
        ],
    },
    {
        "title": "Linked List Cycle",
        "slug": "linked-list-cycle",
        "difficulty": "EASY",
        "topic": "LINKED_LIST",
        "description": """# Linked List Cycle

## Statement
Given a linked list where the tail may connect back to an earlier node (forming a cycle), determine whether a cycle exists. Target O(1) memory with Floyd's tortoise-and-hare.

The list is described by its values plus `pos`: the index (0-based) that the tail connects to, or `-1` if there is no cycle. The starter code builds the structure for you.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers — node values head to tail
- Line 3: integer `pos` — tail connection index (`-1` = no cycle)

## Output Format
`true` if a cycle exists, otherwise `false`.

## Constraints
- `1 <= n <= 10^4`
- `-1 <= pos < n`

## Example 1

**Input**
```
4
3 2 0 -4
1
```
**Output**
```
true
```

Explanation: tail (-4) connects back to node at index 1.

## Example 2

**Input**
```
2
1 2
0
```
**Output**
```
true
```

Explanation: The list 1 -> 2 points back to node 0, so a cycle exists.
""",
        "starter_code": starters(
            py="""import sys


class ListNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None


def build_list(values, pos):
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos != -1:
        nodes[-1].next = nodes[pos]
    return nodes[0]


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    values = [int(x) for x in data[1:n + 1]]
    pos = int(data[n + 1])
    head = build_list(values, pos)

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v) : val(v), next(nullptr) {}
};

int main() {
    int n;
    cin >> n;
    vector<ListNode*> nodes(n);
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        nodes[i] = new ListNode(x);
        if (i) nodes[i - 1]->next = nodes[i];
    }
    int pos;
    cin >> pos;
    if (pos != -1 && n > 0) nodes[n - 1]->next = nodes[pos];
    ListNode* head = n > 0 ? nodes[0] : nullptr;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v) { val = v; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ListNode[] nodes = new ListNode[n];
        for (int i = 0; i < n; i++) {
            nodes[i] = new ListNode(sc.nextInt());
            if (i > 0) nodes[i - 1].next = nodes[i];
        }
        int pos = sc.nextInt();
        if (pos != -1) nodes[n - 1].next = nodes[pos];
        ListNode head = nodes[0];

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "4\n3 2 0 -4\n1\n", "expected_output": "true", "is_hidden": False},
            {"input": "2\n1 2\n0\n", "expected_output": "true", "is_hidden": False},
            {"input": "1\n1\n-1\n", "expected_output": "false", "is_hidden": False},
            {"input": "5\n10 20 30 40 50\n4\n", "expected_output": "true", "is_hidden": True},
            {"input": "3\n5 6 7\n-1\n", "expected_output": "false", "is_hidden": True},
        ],
    },
    {
        "title": "Merge Two Sorted Lists",
        "slug": "merge-two-sorted-lists",
        "difficulty": "EASY",
        "topic": "LINKED_LIST",
        "description": """# Merge Two Sorted Lists

## Statement
You are given two sorted linked lists in non-decreasing order. Merge them into one sorted list by splicing together their nodes (no new values, just relinking). Print the merged values.

## Input Format
- Line 1: integer `n` — length of list A
- Line 2: `n` space-separated integers — list A (non-decreasing)
- Line 3: integer `m` — length of list B
- Line 4: `m` space-separated integers — list B (non-decreasing)

## Output Format
`n + m` space-separated integers — the merged sorted list.

## Constraints
- `0 <= n, m <= 10^4`
- Each list is given in non-decreasing order.

## Example 1

**Input**
```
3
1 2 4
3
1 3 4
```
**Output**
```
1 1 2 3 4 4
```

Explanation: Interleaving the two sorted lists gives 1 1 2 3 4 4.

## Example 2

**Input**
```
0

2
1 2
```
**Output**
```
1 2
```

Explanation: An empty first list merges to just the remaining list 1 2.
""",
        "starter_code": starters(
            py="""import sys


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_array(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = build_list([int(x) for x in data[1:n + 1]])
    m = int(data[n + 1])
    b = build_list([int(x) for x in data[n + 2:n + 2 + m]])

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v) : val(v), next(nullptr) {}
};

int main() {
    int n;
    cin >> n;
    ListNode dummyA(0), dummyB(0);
    ListNode* ta = &dummyA;
    for (int i = 0; i < n; i++) {
        ta->next = new ListNode(0);
        cin >> ta->next->val;
        ta = ta->next;
    }
    int m;
    cin >> m;
    ListNode* tb = &dummyB;
    for (int i = 0; i < m; i++) {
        tb->next = new ListNode(0);
        cin >> tb->next->val;
        tb = tb->next;
    }
    ListNode* a = dummyA.next;
    ListNode* b = dummyB.next;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int v) { val = v; }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ListNode da = new ListNode(0), ta = da;
        for (int i = 0; i < n; i++) { ta.next = new ListNode(sc.nextInt()); ta = ta.next; }
        int m = sc.nextInt();
        ListNode db = new ListNode(0), tb = db;
        for (int i = 0; i < m; i++) { tb.next = new ListNode(sc.nextInt()); tb = tb.next; }
        ListNode a = da.next, b = db.next;

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "3\n1 2 4\n3\n1 3 4\n", "expected_output": "1 1 2 3 4 4", "is_hidden": False},
            {"input": "0\n\n2\n1 2\n", "expected_output": "1 2", "is_hidden": False},
            {"input": "2\n5 7\n2\n5 9\n", "expected_output": "5 5 7 9", "is_hidden": False},
            {"input": "3\n-9 -2 0\n1\n3\n", "expected_output": "-9 -2 0 3", "is_hidden": True},
            {"input": "0\n\n0\n\n", "expected_output": "", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": "EASY",
        "topic": "STACK",
        "description": """# Valid Parentheses

## Statement
Given a string containing only the characters `(`, `)`, `{`, `}`, `[`, `]`, determine whether it is valid. A string is valid when every opening bracket is closed by the same type in the correct nested order.

Solve with a stack.

## Input Format
- Line 1: the bracket string `s`

## Output Format
`true` or `false` (lowercase).

## Constraints
- `1 <= s.length <= 10^4`
- `s` contains only bracket characters.

## Example 1

**Input**
```
()[]{}
```
**Output**
```
true
```

Explanation: Each opening bracket is closed by its matching partner in the right order.

## Example 2

**Input**
```
([)]
```
**Output**
```
false
```

Explanation: The brackets are interlaced (([)]), so the match is invalid.
""",
        "starter_code": starters(
            py="""import sys


def main():
    s = input().strip()

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "()[]{}\n", "expected_output": "true", "is_hidden": False},
            {"input": "([)]\n", "expected_output": "false", "is_hidden": False},
            {"input": "{[]}\n", "expected_output": "true", "is_hidden": False},
            {"input": "(]\n", "expected_output": "false", "is_hidden": True},
            {"input": "((((()))))\n", "expected_output": "true", "is_hidden": True},
            {"input": "(\n", "expected_output": "false", "is_hidden": True},
        ],
    },
    {
        "title": "Next Greater Element",
        "slug": "next-greater-element",
        "pattern_key": "stack",
        "difficulty": "MEDIUM",
        "topic": "STACK",
        "description": """# Next Greater Element

## Statement
For each element in the array, find the first element to its **right** that is strictly greater than it. If none exists, output `-1` for that position. The classic monotonic-stack problem — target O(n).

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers

## Output Format
`n` space-separated integers — next greater values.

## Constraints
- `1 <= n <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Example 1

**Input**
```
4
4 5 2 25
```
**Output**
```
5 25 25 -1
```

Explanation: The next larger element to the right: 4->5, 5->25, 2->25, and 25 has none (-1).

## Example 2

**Input**
```
4
13 7 6 12
```
**Output**
```
-1 12 12 -1
```

Explanation: 13, 7 and 6 all find 12 to their right; 12 has no larger element after it.
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
            {"input": "4\n4 5 2 25\n", "expected_output": "5 25 25 -1", "is_hidden": False},
            {"input": "4\n13 7 6 12\n", "expected_output": "-1 12 12 -1", "is_hidden": False},
            {"input": "1\n3\n", "expected_output": "-1", "is_hidden": False},
            {"input": "5\n1 2 3 4 5\n", "expected_output": "2 3 4 5 -1", "is_hidden": True},
            {"input": "5\n5 4 3 2 1\n", "expected_output": "-1 -1 -1 -1 -1", "is_hidden": True},
        ],
    },
    {
        "title": "Daily Temperatures",
        "slug": "daily-temperatures",
        "difficulty": "MEDIUM",
        "topic": "STACK",
        "description": """# Daily Temperatures

## Statement
Given daily temperatures `temps`, return an array `answer` where `answer[i]` is the number of days you have to wait after day `i` to get a warmer temperature. If no future warmer day exists, `answer[i] == 0`.

Monotonic stack gives an elegant O(n).

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated integers (30..100)

## Output Format
`n` space-separated integers.

## Constraints
- `1 <= n <= 10^5`
- `30 <= temps[i] <= 100`

## Example 1

**Input**
```
8
73 74 75 71 69 72 76 73
```
**Output**
```
1 1 4 2 1 1 0 0
```

Explanation: Each entry records the days until a warmer temperature: 73 waits 1 day, 69 waits 2 (reaches 72), and the last two never see a warmer day.

## Example 2

**Input**
```
4
30 40 50 60
```
**Output**
```
1 1 1 0
```

Explanation: Every day is warmer than the previous, so each value waits 1 day except the last, which waits 0.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    temps = [int(x) for x in data[1:n + 1]]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> temps(n);
    for (auto& x : temps) cin >> x;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] temps = new int[n];
        for (int i = 0; i < n; i++) temps[i] = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "8\n73 74 75 71 69 72 76 73\n", "expected_output": "1 1 4 2 1 1 0 0", "is_hidden": False},
            {"input": "4\n30 40 50 60\n", "expected_output": "1 1 1 0", "is_hidden": False},
            {"input": "3\n60 60 60\n", "expected_output": "0 0 0", "is_hidden": False},
            {"input": "5\n70 69 68 67 80\n", "expected_output": "4 3 2 1 0", "is_hidden": True},
        ],
    },
    {
        "title": "Sliding Window Maximum",
        "slug": "sliding-window-maximum",
        "difficulty": "HARD",
        "topic": "QUEUE",
        "description": """# Sliding Window Maximum

## Statement
You are given an array `nums` and a window size `k`. A window slides from left to right across the array one position at a time; there are exactly `n - k + 1` windows. Print the maximum of each window.

The expected optimal solution uses a monotonic deque for O(n).

## Input Format
- Line 1: integers `n k`
- Line 2: `n` space-separated integers

## Output Format
`n - k + 1` space-separated integers — window maxima.

## Constraints
- `1 <= k <= n <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Example 1

**Input**
```
8 3
1 3 -1 -3 5 3 6 7
```
**Output**
```
3 3 5 5 6 7
```

Explanation: Sliding a size-3 window across the array yields maxima [3, 3, 5, 5, 6, 7].

## Example 2

**Input**
```
1 1
9
```
**Output**
```
9
```

Explanation: A window of size 1 always contains just the single element, 9.
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    nums = [int(x) for x in data[2:n + 2]]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
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
        int n = sc.nextInt(), k = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "8 3\n1 3 -1 -3 5 3 6 7\n", "expected_output": "3 3 5 5 6 7", "is_hidden": False},
            {"input": "1 1\n9\n", "expected_output": "9", "is_hidden": False},
            {"input": "5 2\n2 1 5 1 3\n", "expected_output": "2 5 5 3", "is_hidden": False},
            {"input": "4 4\n1 2 3 4\n", "expected_output": "4", "is_hidden": True},
            {"input": "6 2\n9 8 7 6 5 4\n", "expected_output": "9 8 7 6 5", "is_hidden": True},
        ],
    },
]
