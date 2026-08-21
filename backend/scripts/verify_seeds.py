import io
import sys
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from itertools import zip_longest
from math import comb
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.seeds import PROBLEMS


def normalize(text):
    if text is None:
        return ""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def tf(flag):
    return "true" if flag else "false"


def tokens():
    return sys.stdin.read().split()


class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None


def build_tree(tok):
    if not tok or tok[0] == "null":
        return None
    root = TreeNode(int(tok[0]))
    q = deque([root])
    i = 1
    while q and i < len(tok):
        node = q.popleft()
        if i < len(tok):
            v = tok[i]
            i += 1
            if v != "null":
                node.left = TreeNode(int(v))
                q.append(node.left)
        if i < len(tok):
            v = tok[i]
            i += 1
            if v != "null":
                node.right = TreeNode(int(v))
                q.append(node.right)
    return root


def serialize_level_order(root):
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
        else:
            out.append(str(node.val))
            q.append(node.left)
            q.append(node.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def two_sum():
    d = tokens()
    n = int(d[0])
    nums = [int(x) for x in d[1 : n + 1]]
    target = int(d[n + 1])
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            print(seen[target - v], i)
            return
        seen[v] = i


def move_zeroes():
    d = tokens()
    n = int(d[0])
    nums = [int(x) for x in d[1 : n + 1]]
    kept = [x for x in nums if x != 0]
    print(*(kept + [0] * (n - len(kept))))


def maximum_subarray():
    d = tokens()
    nums = [int(x) for x in d[1 : int(d[0]) + 1]]
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    print(best)


def subarray_sum_equals_k():
    d = tokens()
    nums = [int(x) for x in d[1 : int(d[0]) + 1]]
    k = int(d[int(d[0]) + 1])
    count = pref = 0
    seen = {0: 1}
    for x in nums:
        pref += x
        count += seen.get(pref - k, 0)
        seen[pref] = seen.get(pref, 0) + 1
    print(count)


def product_of_array_except_self():
    d = tokens()
    nums = [int(x) for x in d[1 : int(d[0]) + 1]]
    res = [1] * len(nums)
    pre = 1
    for i, v in enumerate(nums):
        res[i] = pre
        pre *= v
    suf = 1
    for i in range(len(nums) - 1, -1, -1):
        res[i] *= suf
        suf *= nums[i]
    print(*res)


def first_missing_positive():
    d = tokens()
    present = {int(x) for x in d[1 : int(d[0]) + 1]}
    i = 1
    while i in present:
        i += 1
    print(i)


def valid_anagram():
    lines = sys.stdin.read().splitlines()
    print(tf(sorted(lines[0]) == sorted(lines[1])))


def valid_palindrome():
    line = sys.stdin.read().splitlines()[0] if sys.stdin else ""
    cleaned = [c.lower() for c in line if c.isalnum()]
    print(tf(cleaned == cleaned[::-1]))


def longest_substring_without_repeating_characters():
    line = sys.stdin.read().splitlines()[0] if sys.stdin else ""
    last = {}
    left = 0
    best = 0
    for right, ch in enumerate(line):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    print(best)


def group_anagrams():
    d = tokens()
    words = d[1 : int(d[0]) + 1]
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    ordered = [sorted(g) for g in groups.values()]
    ordered.sort(key=lambda g: g[0])
    for g in ordered:
        print(" ".join(g))


def minimum_window_substring():
    lines = sys.stdin.read().splitlines()
    s, t = lines[0], lines[1]
    need = Counter(t)
    window = {}
    formed = 0
    left = 0
    best_len = float("inf")
    best = ""
    for right, ch in enumerate(s):
        if ch in need:
            window[ch] = window.get(ch, 0) + 1
            if window[ch] == need[ch]:
                formed += 1
        while formed == len(need):
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best = s[left : right + 1]
            lc = s[left]
            if lc in need:
                window[lc] -= 1
                if window[lc] < need[lc]:
                    formed -= 1
            left += 1
    print(best)


def reverse_linked_list():
    d = tokens()
    values = [int(x) for x in d[1 : int(d[0]) + 1]]
    print(*reversed(values))


def middle_of_the_linked_list():
    d = tokens()
    values = [int(x) for x in d[1 : int(d[0]) + 1]]
    print(values[len(values) // 2])


def linked_list_cycle():
    d = tokens()
    pos = int(d[-1])
    print(tf(pos != -1))


def merge_two_sorted_lists():
    d = tokens()
    n = int(d[0])
    a = [int(x) for x in d[1 : n + 1]]
    m = int(d[n + 1])
    b = [int(x) for x in d[n + 2 : n + 2 + m]]
    merged = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    merged.extend(a[i:])
    merged.extend(b[j:])
    print(*merged)


def valid_parentheses():
    s = sys.stdin.readline().strip()
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    ok = True
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs.get(ch):
            ok = False
            break
    print(tf(ok and not stack))


def next_greater_element():
    d = tokens()
    nums = [int(x) for x in d[1 : int(d[0]) + 1]]
    res = [-1] * len(nums)
    stack = []
    for i, v in enumerate(nums):
        while stack and nums[stack[-1]] < v:
            res[stack.pop()] = v
        stack.append(i)
    print(*res)


def daily_temperatures():
    d = tokens()
    temps = [int(x) for x in d[1 : int(d[0]) + 1]]
    res = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j
        stack.append(i)
    print(*res)


def sliding_window_maximum():
    d = tokens()
    n, k = int(d[0]), int(d[1])
    nums = [int(x) for x in d[2 : n + 2]]
    dq = deque()
    out = []
    for i, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    print(*out)


def maximum_depth_binary_tree():
    def depth(node):
        if node is None:
            return 0
        return 1 + max(depth(node.left), depth(node.right))

    print(depth(build_tree(tokens())))


def invert_binary_tree():
    def invert(node):
        if node is None:
            return None
        node.left, node.right = invert(node.right), invert(node.left)
        return node

    root = build_tree(tokens())
    print(serialize_level_order(invert(root)))


def lowest_common_ancestor_bst():
    d = tokens()
    p, q = int(d[-2]), int(d[-1])
    node = build_tree(d[:-2])
    while True:
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            break
    print(node.val)


def validate_binary_search_tree():
    def check(node, lo, hi):
        if node is None:
            return True
        if lo is not None and node.val <= lo:
            return False
        if hi is not None and node.val >= hi:
            return False
        return check(node.left, lo, node.val) and check(node.right, node.val, hi)

    print(tf(check(build_tree(tokens()), None, None)))


def binary_tree_level_order_traversal():
    root = build_tree(tokens())
    levels = []
    current = [root] if root else []
    while current:
        levels.append([str(n.val) for n in current])
        nxt = []
        for n in current:
            if n.left:
                nxt.append(n.left)
            if n.right:
                nxt.append(n.right)
        current = nxt
    for level in levels:
        print(" ".join(level))


def diameter_of_binary_tree():
    best = 0

    def depth(node):
        nonlocal best
        if node is None:
            return 0
        l = depth(node.left)
        r = depth(node.right)
        best = max(best, l + r)
        return max(l, r) + 1

    depth(build_tree(tokens()))
    print(best)


def flood_fill():
    d = tokens()
    idx = 0
    r, c = int(d[idx]), int(d[idx + 1])
    idx += 2
    grid = [[int(d[idx + r_i * c + c_i]) for c_i in range(c)] for r_i in range(r)]
    idx += r * c
    sr, sc, color = int(d[idx]), int(d[idx + 1]), int(d[idx + 2])
    orig = grid[sr][sc]
    if orig != color:
        q = deque([(sr, sc)])
        grid[sr][sc] = color
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < r and 0 <= ny < c and grid[nx][ny] == orig:
                    grid[nx][ny] = color
                    q.append((nx, ny))
    for row in grid:
        print(*row)


def number_of_islands():
    d = tokens()
    r, c = int(d[0]), int(d[1])
    grid = [list(d[2 + i]) for i in range(r)]
    seen = [[False] * c for _ in range(r)]
    count = 0
    for i in range(r):
        for j in range(c):
            if grid[i][j] == "1" and not seen[i][j]:
                count += 1
                q = deque([(i, j)])
                seen[i][j] = True
                while q:
                    x, y = q.popleft()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < r
                            and 0 <= ny < c
                            and grid[nx][ny] == "1"
                            and not seen[nx][ny]
                        ):
                            seen[nx][ny] = True
                            q.append((nx, ny))
    print(count)


def course_schedule():
    d = tokens()
    v, e = int(d[0]), int(d[1])
    adj = defaultdict(list)
    indeg = [0] * v
    idx = 2
    for _ in range(e):
        a, b = int(d[idx]), int(d[idx + 1])
        idx += 2
        adj[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(v) if indeg[i] == 0)
    taken = 0
    while q:
        node = q.popleft()
        taken += 1
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    print(tf(taken == v))


def climbing_stairs():
    n = int(sys.stdin.read())
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    print(b)


def unique_paths():
    m, n = map(int, tokens())
    print(comb(m + n - 2, m - 1))


def coin_change():
    lines = sys.stdin.read().splitlines()
    coins = [int(x) for x in lines[0].split()]
    amount = int(lines[1])
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a and dp[a - coin] + 1 < dp[a]:
                dp[a] = dp[a - coin] + 1
    print(dp[amount] if dp[amount] != INF else -1)


def longest_increasing_subsequence():
    import bisect

    d = tokens()
    nums = [int(x) for x in d[1 : int(d[0]) + 1]]
    tails = []
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    print(len(tails))


def word_break():
    d = tokens()
    s = d[0]
    words = set(d[2 : 2 + int(d[1])])
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    print(tf(dp[len(s)]))


def edit_distance():
    lines = sys.stdin.read().splitlines()
    a, b = lines[0], lines[1]
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    print(prev[-1])


REFS = {
    "two-sum": two_sum,
    "move-zeroes": move_zeroes,
    "maximum-subarray": maximum_subarray,
    "subarray-sum-equals-k": subarray_sum_equals_k,
    "product-of-array-except-self": product_of_array_except_self,
    "first-missing-positive": first_missing_positive,
    "valid-anagram": valid_anagram,
    "valid-palindrome": valid_palindrome,
    "longest-substring-without-repeating-characters": longest_substring_without_repeating_characters,
    "group-anagrams": group_anagrams,
    "minimum-window-substring": minimum_window_substring,
    "reverse-linked-list": reverse_linked_list,
    "middle-of-the-linked-list": middle_of_the_linked_list,
    "linked-list-cycle": linked_list_cycle,
    "merge-two-sorted-lists": merge_two_sorted_lists,
    "valid-parentheses": valid_parentheses,
    "next-greater-element": next_greater_element,
    "daily-temperatures": daily_temperatures,
    "sliding-window-maximum": sliding_window_maximum,
    "maximum-depth-binary-tree": maximum_depth_binary_tree,
    "invert-binary-tree": invert_binary_tree,
    "lowest-common-ancestor-bst": lowest_common_ancestor_bst,
    "validate-binary-search-tree": validate_binary_search_tree,
    "binary-tree-level-order-traversal": binary_tree_level_order_traversal,
    "diameter-of-binary-tree": diameter_of_binary_tree,
    "flood-fill": flood_fill,
    "number-of-islands": number_of_islands,
    "course-schedule": course_schedule,
    "climbing-stairs": climbing_stairs,
    "unique-paths": unique_paths,
    "coin-change": coin_change,
    "longest-increasing-subsequence": longest_increasing_subsequence,
    "word-break": word_break,
    "edit-distance": edit_distance,
}


def run_reference(func, stdin_text):
    buffer = io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin_text)
    try:
        with redirect_stdout(buffer):
            func()
    finally:
        sys.stdin = old_stdin
    return normalize(buffer.getvalue())


def main():
    failures = []
    checked = 0
    missing_refs = []

    for problem in PROBLEMS:
        slug = problem["slug"]
        ref = REFS.get(slug)
        if ref is None:
            missing_refs.append(slug)
            continue
        for index, case in enumerate(problem["test_cases"]):
            checked += 1
            try:
                actual = run_reference(ref, case["input"])
            except Exception as exc:
                failures.append((slug, index, f"reference crashed: {exc!r}"))
                continue
            expected = normalize(case["expected_output"])
            if actual != expected:
                failures.append(
                    (
                        slug,
                        index,
                        f"\n    input:    {case['input']!r}"
                        f"\n    expected: {expected!r}"
                        f"\n    actual:   {actual!r}",
                    )
                )

    print(f"Checked {checked} test cases across {len(PROBLEMS)} problems")
    if missing_refs:
        print(f"[WARN] No reference solution for: {', '.join(missing_refs)}")
    if failures:
        print(f"[FAIL] {len(failures)} mismatches:")
        for slug, index, detail in failures:
            print(f"  - {slug} case #{index}:{detail}")
        raise SystemExit(1)
    print("[OK] All expected outputs verified")


if __name__ == "__main__":
    main()
