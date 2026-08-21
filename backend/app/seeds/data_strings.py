from app.seeds.data_arrays import starters

STRINGS = [
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "difficulty": "EASY",
        "topic": "STRING",
        "description": """# Valid Anagram

## Statement
Given two lowercase strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise. An anagram uses every character of `s` exactly once, rearranged.

## Input Format
- Line 1: string `s`
- Line 2: string `t`

## Output Format
`true` or `false` (lowercase).

## Constraints
- `1 <= s.length == t.length <= 5 * 10^4`
- Both strings contain only lowercase English letters.

## Example

**Input**
```
anagram
nagaram
```
**Output**
```
true
```
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
    string s, t;
    cin >> s >> t;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();
        String t = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "anagram\nnagaram\n", "expected_output": "true", "is_hidden": False},
            {"input": "rat\ncar\n", "expected_output": "false", "is_hidden": False},
            {"input": "a\nab\n", "expected_output": "false", "is_hidden": True},
            {"input": "aa\naa\n", "expected_output": "true", "is_hidden": True},
            {"input": "abcba\nabcbc\n", "expected_output": "false", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Palindrome",
        "slug": "valid-palindrome",
        "difficulty": "EASY",
        "topic": "STRING",
        "description": """# Valid Palindrome

## Statement
A phrase is a palindrome if, after converting all uppercase letters to lowercase and removing all non-alphanumeric characters, it reads the same forward and backward.

Given a line of text `s`, output `true` if it is a palindrome, otherwise `false`.

## Input Format
- Line 1: the text `s` (may contain letters, digits, spaces and punctuation)

## Output Format
`true` or `false` (lowercase).

## Constraints
- `1 <= s.length <= 2 * 10^5`

## Example

**Input**
```
A man, a plan, a canal: Panama
```
**Output**
```
true
```

Explanation: after filtering -> `"amanaplanacanalpanama"`.
""",
        "starter_code": starters(
            py="""import sys


def main():
    s = input()

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string line;
    getline(cin, line);

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "A man, a plan, a canal: Panama\n", "expected_output": "true", "is_hidden": False},
            {"input": "race a car\n", "expected_output": "false", "is_hidden": False},
            {"input": " \n", "expected_output": "true", "is_hidden": True},
            {"input": "0P\n", "expected_output": "false", "is_hidden": True},
            {"input": "12321\n", "expected_output": "true", "is_hidden": True},
        ],
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "difficulty": "MEDIUM",
        "topic": "STRING",
        "description": """# Longest Substring Without Repeating Characters

## Statement
Given a string `s`, find the length of the longest substring that contains no repeated characters. Target an O(n) sliding-window solution.

## Input Format
- Line 1: string `s`

## Output Format
A single integer — the length found.

## Constraints
- `0 <= s.length <= 5 * 10^4`
- `s` consists of printable ASCII characters.

## Example

**Input**
```
pwwkew
```
**Output**
```
3
```

Explanation: `"wke"` has length 3; note `"pwke"` is a subsequence, not a substring.
""",
        "starter_code": starters(
            py="""import sys


def main():
    s = input()

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    getline(cin, s);

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.nextLine();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "abcabcbb\n", "expected_output": "3", "is_hidden": False},
            {"input": "bbbbb\n", "expected_output": "1", "is_hidden": False},
            {"input": "pwwkew\n", "expected_output": "3", "is_hidden": True},
            {"input": "\n", "expected_output": "0", "is_hidden": True},
            {"input": "dvdf\n", "expected_output": "3", "is_hidden": True},
            {"input": "abba\n", "expected_output": "2", "is_hidden": True},
        ],
    },
    {
        "title": "Group Anagrams",
        "slug": "group-anagrams",
        "difficulty": "MEDIUM",
        "topic": "STRING",
        "description": """# Group Anagrams

## Statement
Given `n` strings, group the anagrams together. Anagrams contain exactly the same characters with the same frequencies.

To keep judging deterministic, output rules are strict:
- Sort the words inside each group alphabetically.
- Sort the groups by comparing their first word.
- Print each group on its own line, words separated by single spaces.

## Input Format
- Line 1: integer `n`
- Line 2: `n` space-separated words

## Output Format
One group per line as described above.

## Constraints
- `1 <= n <= 10^4`
- Each word is 1..100 lowercase letters.
- Every word belongs to exactly one group.

## Example

**Input**
```
6
eat tea tan ate nat bat
```
**Output**
```
ate eat tea
bat
nat tan
```
""",
        "starter_code": starters(
            py="""import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    words = data[1:n + 1]

    # ===== YOUR CODE HERE =====


if __name__ == "__main__":
    main()
""",
            cpp="""#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<string> words(n);
    for (auto& w : words) cin >> w;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        String[] words = new String[n];
        for (int i = 0; i < n; i++) words[i] = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "6\neat tea tan ate nat bat\n", "expected_output": "ate eat tea\nbat\nnat tan", "is_hidden": False},
            {"input": "1\nsolo\n", "expected_output": "solo", "is_hidden": False},
            {"input": "2\nab ba\n", "expected_output": "ab ba", "is_hidden": True},
            {"input": "4\nlisten silent enlist google\n", "expected_output": "enlist listen silent\ngoogle", "is_hidden": True},
            {"input": "3\nabc cab bca\n", "expected_output": "abc bca cab", "is_hidden": True},
        ],
    },
    {
        "title": "Minimum Window Substring",
        "slug": "minimum-window-substring",
        "difficulty": "HARD",
        "topic": "STRING",
        "description": """# Minimum Window Substring

## Statement
Given two strings `s` and `t`, return the minimum-length substring of `s` that contains every character of `t` **including multiplicity**. If no such substring exists, output nothing (empty line).

If several minimum windows exist, output any one of them — the judge accepts any correct answer of minimal length... but to keep automated comparison simple, tests guarantee a **unique** answer whenever one exists.

## Input Format
- Line 1: string `s`
- Line 2: string `t`

## Output Format
The minimum window substring (possibly empty).

## Constraints
- `1 <= s.length <= 10^5`
- `1 <= t.length <= 10^4`
- Uppercase/lowercase are distinct characters.

## Example

**Input**
```
ADOBECODEBANC
ABC
```
**Output**
```
BANC
```
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
    string s, t;
    cin >> s >> t;

    // ===== YOUR CODE HERE =====

    return 0;
}
""",
            java="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();
        String t = sc.next();

        // ===== YOUR CODE HERE =====
    }
}
""",
        ),
        "test_cases": [
            {"input": "ADOBECODEBANC\nABC\n", "expected_output": "BANC", "is_hidden": False},
            {"input": "a\na\n", "expected_output": "a", "is_hidden": False},
            {"input": "a\naa\n", "expected_output": "", "is_hidden": True},
            {"input": "aa\naa\n", "expected_output": "aa", "is_hidden": True},
            {"input": "zeusazoth\nsz\n", "expected_output": "saz", "is_hidden": True},
        ],
    },
]
