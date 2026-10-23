"""Authored solution ladders, keyed by problem slug.

Ordered cheapest approach first, so the reader climbs from the brute force
they would write under pressure to the one an interviewer wants. Each rung
carries its own complexity; ``trace_key`` points at the visualizer registry
entry that animates that rung, and is left off when no trace exists yet.

Kept in its own module (rather than spread across ``data_*.py``) so the
ladders can be reviewed, extended and re-seeded without touching the
statement/case authoring files.
"""

from app.seeds.schema import ApproachSeed

APPROACHES: dict[str, list[ApproachSeed]] = {
    "two-sum": [
        ApproachSeed(
            name="Brute force pairs",
            idea=(
                "Check every pair (i, j) and return the first one that sums to "
                "target. The honest first draft when you are still reading the "
                "problem."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
            tradeoff="No extra memory, but it dies on large inputs.",
        ),
        ApproachSeed(
            name="Sort + two pointers",
            idea=(
                "Sort the values, then walk a low/high pair inward, moving the "
                "pointer that makes the sum too small or too large."
            ),
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            tradeoff=(
                "Sorting costs more than hashing and destroys the original "
                "indices, so you must carry them along."
            ),
        ),
        ApproachSeed(
            name="One-pass hash map",
            idea=(
                "Walk the array once. Before inserting nums[i], check whether "
                "target - nums[i] has already been seen; if so the pair is found "
                "in a single pass."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff=(
                "Trades linear memory for linear time, and returns the indices "
                "untouched — the shape the problem asks for."
            ),
            trace_key="two-sum",
        ),
    ],
    "two-sum-ii-input-array-is-sorted": [
        ApproachSeed(
            name="Binary search the complement",
            idea=(
                "For each index i, binary search the rest of the sorted array "
                "for target - nums[i]. The sort is already paid for, so this "
                "needs no extra structure."
            ),
            time_complexity="O(n log n)",
            space_complexity="O(1)",
            tradeoff="Simple to reason about, but it re-scans a shrinking tail.",
        ),
        ApproachSeed(
            name="Two pointers from the ends",
            idea=(
                "Start with the smallest and largest values. If the sum is too "
                "small move the low pointer up; if too large move the high "
                "pointer down. The answer, if it exists, is never skipped."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "Only works because the input is sorted and 1-indexed — reuse "
                "the ordering instead of rebuilding it."
            ),
            trace_key="two-sum-ii-input-array-is-sorted",
        ),
    ],
    "3sum": [
        ApproachSeed(
            name="Triple loop over distinct triples",
            idea=(
                "Enumerate every i < j < k, collect the triples summing to zero "
                "and deduplicate them at the end."
            ),
            time_complexity="O(n³)",
            space_complexity="O(k)",
            tradeoff="Correct but unusable past tiny inputs; dedup is fiddly.",
        ),
        ApproachSeed(
            name="Hash set per element",
            idea=(
                "Fix one element, then solve the remaining two-sum with a set, "
                "skipping duplicate values of the fixed element."
            ),
            time_complexity="O(n²)",
            space_complexity="O(n)",
            tradeoff=(
                "Beats the triple loop, but deduplicating triples correctly is "
                "easier to get wrong than with sorted pointers."
            ),
        ),
        ApproachSeed(
            name="Sort + two pointers",
            idea=(
                "Sort first. For each anchor i, run the two-pointer scan on the "
                "suffix; skip repeated anchors and repeated lows so each triple "
                "is emitted exactly once."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
            tradeoff=(
                "Same asymptotics as the set version with no hash overhead, and "
                "dedup falls out of the sorted order."
            ),
            trace_key="3sum",
        ),
    ],
    "container-with-most-water": [
        ApproachSeed(
            name="Every pair of walls",
            idea=(
                "Compute min(h[i], h[j]) * (j - i) for all i < j and keep the "
                "largest area."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
            tradeoff="The baseline that makes the greedy argument necessary.",
        ),
        ApproachSeed(
            name="Two pointers, move the shorter wall",
            idea=(
                "Hold the widest pair first. The shorter wall can never be part "
                "of a better container with any inner wall, so move it inward; "
                "each step shrinks the width, so the max area is found in one pass."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "Needs the exchange argument to justify — but it is the answer, "
                "with no extra memory."
            ),
            trace_key="container-with-most-water",
        ),
    ],
    "move-zeroes": [
        ApproachSeed(
            name="Copy the non-zeros out",
            idea=(
                "Build a fresh array of non-zero values, then pad it with zeros "
                "and copy back."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff="Easy to read; fails the in-place / no-copy follow-up.",
        ),
        ApproachSeed(
            name="Write index + zero fill",
            idea=(
                "Keep a write pointer for the next non-zero, overwrite forward, "
                "then zero-fill the tail."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "In place, but it writes each surviving element once and the "
                "zeros a second time."
            ),
        ),
        ApproachSeed(
            name="One-pass swap with the reader",
            idea=(
                "Walk a reader i and a write pointer j. On every non-zero, swap "
                "nums[i] into slot j and advance j — zeros drift to the back "
                "with one write per element."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "Preserves relative order and touches each element at most once; "
                "the standard trick worth memorising."
            ),
            trace_key="move-zeroes",
        ),
    ],
    "best-time-to-buy-and-sell-stock": [
        ApproachSeed(
            name="Try every buy/sell day",
            idea=(
                "For each buy day, scan forward for the best later sell day and "
                "keep the maximum profit."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
        ),
        ApproachSeed(
            name="Track the minimum so far",
            idea=(
                "Sweep once, remembering the cheapest price seen so far; at each "
                "day the best profit ending there is today's price minus that "
                "minimum."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "The whole problem collapses to two running values — the pattern "
                "that generalises to the stock-series follow-ups."
            ),
            trace_key="best-time-to-buy-and-sell-stock",
        ),
    ],
    "longest-substring-without-repeating-characters": [
        ApproachSeed(
            name="Check every substring",
            idea=(
                "For each start, extend the end while characters stay unique, "
                "and track the longest window that survived."
            ),
            time_complexity="O(n²)",
            space_complexity="O(min(n, Σ))",
            tradeoff="Fine for short strings, but re-checks characters.",
        ),
        ApproachSeed(
            name="Sliding window with a set",
            idea=(
                "Grow the window on the right; when a repeat appears, shrink from "
                "the left until it is gone. The window is always repeat-free."
            ),
            time_complexity="O(n)",
            space_complexity="O(min(n, Σ))",
            tradeoff=(
                "Each character enters and leaves the window once, so the two "
                "nested loops are still linear overall."
            ),
            trace_key="longest-substring-without-repeating-characters",
        ),
        ApproachSeed(
            name="Sliding window with last-seen index",
            idea=(
                "Store each character's most recent index and jump the left edge "
                "straight past a repeat instead of stepping it one at a time."
            ),
            time_complexity="O(n)",
            space_complexity="O(min(n, Σ))",
            tradeoff=(
                "Same asymptotics as the set version with a smaller constant, but "
                "the left-edge jump is the easy part to get wrong."
            ),
        ),
    ],
    "valid-parentheses": [
        ApproachSeed(
            name="Repeatedly strip matched pairs",
            idea=(
                "Delete every occurrence of () [] {} until nothing changes; the "
                "string is valid only if it ends up empty."
            ),
            time_complexity="O(n²)",
            space_complexity="O(n)",
            tradeoff="No stack needed, but each pass rescans the whole string.",
        ),
        ApproachSeed(
            name="Stack of open brackets",
            idea=(
                "Push openers; on a closer, the top of the stack must be its "
                "partner. Valid exactly when every closer matched and the stack "
                "ends empty."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff=(
                "Single pass, and the empty-stack check catches both an early "
                "closer and an unclosed opener."
            ),
            trace_key="valid-parentheses",
        ),
    ],
    "min-stack": [
        ApproachSeed(
            name="Scan for the minimum on demand",
            idea=(
                "Store plain values; getMin walks the whole stack each call."
            ),
            time_complexity="O(1) push/pop, O(n) getMin",
            space_complexity="O(n)",
            tradeoff="Perfectly correct, but getMin is not the O(1) the API promises.",
        ),
        ApproachSeed(
            name="Stack of (value, running min) pairs",
            idea=(
                "Push each value together with the minimum of the stack below it, "
                "so the current minimum is always the top pair's second field."
            ),
            time_complexity="O(1) for every operation",
            space_complexity="O(n)",
            tradeoff=(
                "Honest and simple, at the cost of storing a second number per "
                "element — the version to write in an interview."
            ),
            trace_key="min-stack",
        ),
    ],
    "evaluate-reverse-polish-notation": [
        ApproachSeed(
            name="Recursive expression tree",
            idea=(
                "Parse the token list into an expression tree and evaluate it "
                "bottom-up."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff="Illustrates the structure, but it is a lot of machinery for a flat list.",
        ),
        ApproachSeed(
            name="Operand stack",
            idea=(
                "Push numbers; on an operator pop the two most recent operands, "
                "apply, and push the result. The stack is the expression tree "
                "flattened."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff=(
                "One pass, no recursion, and the operand order (right, then left) "
                "is the only detail to be careful about."
            ),
            trace_key="evaluate-reverse-polish-notation",
        ),
    ],
    "daily-temperatures": [
        ApproachSeed(
            name="Scan forward for each day",
            idea=(
                "For every day, walk right until a warmer temperature appears; "
                "0 if none does."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
            tradeoff="Obvious, but quadratic on a falling-then-flat series.",
        ),
        ApproachSeed(
            name="Monotonic stack of waiting days",
            idea=(
                "Keep indices of days still awaiting a warmer reading, in "
                "decreasing temperature order. A new temperature pops every "
                "cooler day on top and stamps its wait as the index difference."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tradeoff=(
                "Each day is pushed and popped at most once; the monotonic stack "
                "is the reusable idea behind the whole next-greater family."
            ),
            trace_key="daily-temperatures",
        ),
    ],
    "binary-search": [
        ApproachSeed(
            name="Linear scan",
            idea="Walk the array left to right and return the first match.",
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff="Correct for any array, and the reason the sorted precondition matters.",
        ),
        ApproachSeed(
            name="Halve the search space",
            idea=(
                "Probe the middle: equal means done, otherwise discard the half "
                "that cannot contain the target. The interval halves every step."
            ),
            time_complexity="O(log n)",
            space_complexity="O(1)",
            tradeoff=(
                "The boundary arithmetic (low <= high, mid + 1 / mid - 1) is where "
                "the off-by-ones live — prefer the half-open form to keep it safe."
            ),
            trace_key="binary-search",
        ),
        ApproachSeed(
            name="Lower-bound (bisect) form",
            idea=(
                "Search for the leftmost index whose value is >= target, then "
                "confirm equality. No special-casing of the found branch."
            ),
            time_complexity="O(log n)",
            space_complexity="O(1)",
            tradeoff=(
                "Uniform, loop-invariant-friendly, and the version that "
                "generalises to first/last-occurrence problems."
            ),
        ),
    ],
    "permutation-in-string": [
        ApproachSeed(
            name="Sort and compare every window",
            idea=(
                "For each window of len(s1), sort its characters and compare with "
                "the sorted s1."
            ),
            time_complexity="O(n · k log k)",
            space_complexity="O(k)",
        ),
        ApproachSeed(
            name="Fixed-size window with frequency counts",
            idea=(
                "Slide a window of len(s1) and maintain a 26-slot count "
                "difference, tracking how many letters are still out of balance; "
                "zero means the window is a permutation."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "The fixed-window-with-mismatch-counter trick — reuse it for "
                "anagram and substring-coverage problems."
            ),
            trace_key="permutation-in-string",
        ),
    ],
    "longest-repeating-character-replacement": [
        ApproachSeed(
            name="Try every window and replacement budget",
            idea=(
                "For each window, the cost to make it uniform is "
                "len - max_frequency; test all windows."
            ),
            time_complexity="O(n²)",
            space_complexity="O(1)",
        ),
        ApproachSeed(
            name="Sliding window with a max-frequency high-water mark",
            idea=(
                "Grow right and record frequencies. When window - max_freq exceeds "
                "k, slide left. The window never shrinks, so its final size is the "
                "best valid answer."
            ),
            time_complexity="O(n)",
            space_complexity="O(1)",
            tradeoff=(
                "Keeping the max-frequency mark as a running maximum (rather than "
                "recomputing it) is the subtle part that keeps this linear."
            ),
            trace_key="longest-repeating-character-replacement",
        ),
    ],
}
