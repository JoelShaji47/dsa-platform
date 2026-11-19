# Function Mode Roadmap — NeetCode 150 Priority

## Current state
- **251** solvable problems (have starter_code + test_cases)
- **1** with function mode: `two-sum`
- **148** NeetCode 150 problems need function mode (out of 149 total NC150)

## Pattern (from two-sum)
Each problem needs two new fields in its seed entry:

| Field | Purpose |
|---|---|
| `function_starter[lang]` | The `solve()` stub user sees in the editor |
| `function_driver[lang]` | `prefix` (parses stdin → args) + `suffix` (calls solve(), prints output) |

The grader wraps `prefix + user_code + suffix` and sends to Judge0.

## Priority batches

### Batch 1 — Easy Array/Hashing (10 problems)
These are the most practiced NC150 problems. Each has python/cpp/java starters.

1. valid-anagram — `solve(s: str, t: str) -> bool`
2. valid-palindrome — `solve(s: str) -> bool`
3. contains-duplicate — `solve(nums: list[int]) -> bool`
4. happy-number — `solve(n: int) -> bool`
5. plus-one — `solve(digits: list[int]) -> list[int]`
6. missing-number — `solve(nums: list[int]) -> int`
7. single-number — `solve(nums: list[int]) -> int`
8. reverse-integer — `solve(x: int) -> int`
9. best-time-to-buy-and-sell-stock — `solve(prices: list[int]) -> int`
10. climbing-stairs — `solve(n: int) -> int`

### Batch 2 — Medium Array/Hashing (10 problems)
11. two-sum (done)
12. maximum-subarray — `solve(nums: list[int]) -> int`
13. product-of-array-except-self — `solve(nums: list[int]) -> list[int]`
14. group-anagrams — `solve(strs: list[str]) -> list[list[str]]`
15. longest-substring-without-repeating-characters — `solve(s: str) -> int`
16. top-k-frequent-elements — `solve(nums: list[int], k: int) -> list[int]`
17. encode-and-decode-strings — `solve(strs: list[str]) -> list[str]`
18. longest-consecutive-sequence — `solve(nums: list[int]) -> int`
19. 3sum — `solve(nums: list[int]) -> list[list[int]]`
20. container-with-most-water — `solve(height: list[int]) -> int`

### Batch 3 — Easy/Medium Linked List & Tree (20 problems)
21-30: reverse-linked-list, linked-list-cycle, merge-two-sorted-lists, valid-parentheses, etc.
31-40: maximum-depth-binary-tree, invert-binary-tree, validate-binary-search-tree, binary-tree-level-order-traversal, diameter-of-binary-tree, same-tree, subtree-of-another-tree, etc.

### Batch 4 — Remaining NC150 (98 problems)
All remaining Medium/Hard problems across DP, Graph, Matrix, Heap, Interval, etc.

## Files to edit
- `backend/app/seeds/data_authored.py` — source of truth for authored problems
- `backend/app/seeds/data_arrays.py` — some authored array problems
- Other `data_*.py` files as needed based on where each slug lives

## Verification after each batch
```bash
cd backend
.venv/bin/python scripts/check_starters.py   # all starters compile
.venv/bin/python scripts/verify_seeds.py      # test cases pass against reference
```
