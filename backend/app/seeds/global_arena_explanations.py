"""Hand-authored example explanations for the global two-example arena rule.

Keyed by problem slug. "ex2" is required for every solvable problem (its
description is rewritten to show Example 1 + Example 2). "ex1" is optional
and only used when the stored description lacks an Explanation line for its
Example 1 (about 118 problems); statements that already explain Example 1
keep their original wording.
"""

EXPLANATIONS: dict[str, dict[str, str]] = {
    "maximum-subarray": {
        "ex2": "The whole array is a single value, so the best subarray is that value, -5.",
    },
    "valid-anagram": {
        "ex1": "Both words use the same letters in the same counts, so they are anagrams.",
        "ex2": "\"rat\" and \"car\" do not use the same letters in the same counts, so they are not anagrams.",
    },
    "reverse-linked-list": {
        "ex1": "Reversing 1 -> 2 -> 3 -> 4 -> 5 produces 5 -> 4 -> 3 -> 2 -> 1.",
        "ex2": "A single-node list still reverses to itself, 42.",
    },
    "maximum-depth-binary-tree": {
        "ex1": "The longest root-to-leaf path is 3 -> 9 -> 20 -> 15 (or 7), which is 3 nodes deep.",
        "ex2": "1 -> 2 has depth 2: the tree is two nodes tall.",
    },
    "daily-temperatures": {
        "ex1": "Each entry records the days until a warmer temperature: 73 waits 1 day, 69 waits 2 (reaches 72), and the last two never see a warmer day.",
        "ex2": "Every day is warmer than the previous, so each value waits 1 day except the last, which waits 0.",
    },
    "diameter-of-binary-tree": {
        "ex2": "The tree 1 -> 2 has just two nodes, so the longest path between nodes uses a single edge.",
    },
    "binary-tree-level-order-traversal": {
        "ex1": "Traversed level by level: row \"3\", row \"9 20\", then row \"15 7\".",
        "ex2": "A single node forms one level containing just 1.",
    },
    "lowest-common-ancestor-bst": {
        "ex1": "6 sits between 2 and 8 in BST order, so the lowest common ancestor of nodes 2 and 8 is 6.",
        "ex2": "Node 2 is an ancestor of itself and of 4, so the lowest common ancestor is 2.",
    },
    "linked-list-cycle": {
        "ex2": "The list 1 -> 2 points back to node 0, so a cycle exists.",
    },
    "climbing-stairs": {
        "ex2": "There are 8 distinct ways to climb 5 steps using 1- and 2-step moves.",
    },
    "edit-distance": {
        "ex2": "Transforming \"intention\" into \"execution\" needs 5 edits (delete i, substitute n/e, etc.).",
    },
    "group-anagrams": {
        "ex1": "Words with the same sorted letters group together: the \"ate/eat/tea\" group, then \"bat\", then \"nat/tan\".",
        "ex2": "A single word forms its own group by itself, \"solo\".",
    },
    "unique-paths": {
        "ex1": "A 3x7 grid has C(8, 2) = 28 distinct downward/rightward routes from top-left to bottom-right.",
        "ex2": "A 3x2 grid has exactly 3 paths: DDR, DRD, and RDD.",
    },
    "coin-change": {
        "ex2": "11 cannot be formed from coin 2 alone, so no combination works and the answer is -1.",
    },
    "course-schedule": {
        "ex2": "Course 1 depends only on course 0, which has no prerequisites, so every course can be completed.",
    },
    "first-missing-positive": {
        "ex1": "1 and 3 appear but 2 is the smallest positive integer missing from [3, 4, -1, 1].",
        "ex2": "[1, 2, 0] already contains all positive numbers up to 2, so 3 is the missing one.",
    },
    "sliding-window-maximum": {
        "ex1": "Sliding a size-3 window across the array yields maxima [3, 3, 5, 5, 6, 7].",
        "ex2": "A window of size 1 always contains just the single element, 9.",
    },
    "move-zeroes": {
        "ex1": "Moving all zeroes to the end preserves the order [1, 3, 12].",
        "ex2": "A single zero stays in place as the whole array.",
    },
    "number-of-islands": {
        "ex1": "All four connected 1s form one island.",
        "ex2": "Three separate clusters of 1s exist: one of four, one of one (via the diagonal 1), and one of two.",
    },
    "minimum-window-substring": {
        "ex1": "The shortest substring of ADOBECODEBANC containing A, B and C is BANC.",
        "ex2": "The window is simply \"a\", the only possible substring.",
    },
    "flood-fill": {
        "ex1": "Starting at (1,1), the connected region of 1s is recolored to 2, stopping at the 0s.",
        "ex2": "A single 0 recolored to 0 is an identity fill.",
    },
    "validate-binary-search-tree": {
        "ex2": "Every node respects the BST invariant: 1 < 2 < 3.",
    },
    "subarray-sum-equals-k": {
        "ex2": "Two contiguous windows sum to 3: [3] and [1, 2].",
    },
    "product-of-array-except-self": {
        "ex1": "Multiplying the other elements: [2*3*4, 1*3*4, 1*2*4, 1*2*3] = [24, 12, 8, 6].",
        "ex2": "Every product touches the zero, so all entries are 0 except position 2, which is 3*3 = 9.",
    },
    "longest-increasing-subsequence": {
        "ex2": "Using every other element gives [0, 1, 3] or [0, 1, 2, 3]; the longest strictly increasing subsequence has length 4.",
    },
    "valid-palindrome": {
        "ex2": "After removing punctuation and case, \"raceacar\" reads backward as \"racacecar\", so it is not a palindrome.",
    },
    "invert-binary-tree": {
        "ex1": "Every node's children are swapped: 4 2 7 becomes 4 7 2, and left-right mirrored all the way down.",
        "ex2": "Swapping the two children of the root gives 2 3 1.",
    },
    "valid-parentheses": {
        "ex1": "Each opening bracket is closed by its matching partner in the right order.",
        "ex2": "The brackets are interlaced (([)]), so the match is invalid.",
    },
    "middle-of-the-linked-list": {
        "ex1": "With five nodes, the middle node is the third one, value 3.",
        "ex2": "With six nodes, the second middle node is the fourth one, value 4.",
    },
    "word-break": {
        "ex2": "No segmentation of \"catsandog\" uses only the dictionary; the \"sand\"/\"dog\" split out of order never tiles the word.",
    },
    "longest-substring-without-repeating-characters": {
        "ex1": "The longest substring without a repeating character in \"abcabcbb\" is \"abc\", length 3.",
        "ex2": "Every character is the same, so the longest window without repeats is a single character.",
    },
    "merge-two-sorted-lists": {
        "ex1": "Interleaving the two sorted lists gives 1 1 2 3 4 4.",
        "ex2": "An empty first list merges to just the remaining list 1 2.",
    },
    "two-sum": {
        "ex2": "nums[1] + nums[2] == 3 + 2 == 6, so the indices are 1 2.",
    },
    "next-greater-element": {
        "ex1": "The next larger element to the right: 4->5, 5->25, 2->25, and 25 has none (-1).",
        "ex2": "13, 7 and 6 all find 12 to their right; 12 has no larger element after it.",
    },
    "contains-duplicate": {
        "ex2": "All four values are distinct, so there is no duplicate.",
    },
    "top-k-frequent-elements": {
        "ex1": "1 appears 3 times and 2 appears twice, so the two most frequent values are 1 2.",
        "ex2": "With one element, the only value, 1, is also the most frequent.",
    },
    "valid-sudoku": {
        "ex1": "Every row, column, and 3x3 box contains each digit 1-9 at most once.",
        "ex2": "The first column repeats 8, so the board is invalid.",
    },
    "remove-nth-node-from-end-of-list": {
        "ex1": "Removing the second node from the end (value 4) leaves 1 2 3 5.",
        "ex2": "Removing the only node leaves an empty list.",
    },
    "encode-and-decode-strings": {
        "ex1": "Encode then decode returns the original three strings, including the embedded #.",
        "ex2": "The round trip preserves \"leet\", \"code\" and \"love\" unchanged.",
    },
    "longest-consecutive-sequence": {
        "ex2": "Neither 0 nor 3 is consecutive to the other, so the longest run is length 1.",
    },
    "word-search-ii": {
        "ex2": "\"ab\" can be traced through the top row of the 2x2 board.",
    },
    "two-sum-ii-input-array-is-sorted": {
        "ex2": "3 + 3 == 6 using 1-based indices 1 and 2.",
    },
    "3sum": {
        "ex2": "The only triple summing to 0 is 0 + 0 + 0.",
    },
    "container-with-most-water": {
        "ex2": "Two bars of height 1 hold at most 1*1 = 1 unit between them.",
    },
    "trapping-rain-water": {
        "ex2": "Water collects in the dips between the taller bars, totaling 9 units.",
    },
    "best-time-to-buy-and-sell-stock": {
        "ex1": "Buying at 1 and selling at 6 yields the maximum profit 5, achieved between days 2 and 6.",
        "ex2": "The price only falls, so no profitable trade exists and the answer is 0.",
    },
    "longest-repeating-character-replacement": {
        "ex1": "With one replacement, a window of 4 A's (or B's) fits inside AABABBA.",
        "ex2": "Two replacements turn ABAB into four characters all equal.",
    },
    "permutation-in-string": {
        "ex1": "\"ab\" appears in \"eidbaooo\" as the contiguous \"ba\".",
        "ex2": "Neither \"ab\" nor \"ba\" appears contiguously in \"eidboaoo\".",
    },
    "min-stack": {
        "ex1": "After the pushes the min is -3; popping leaves min -3 again, and the top is -2.",
        "ex2": "The only pushed values leave min 1, top 2, and after pop the remaining min is still 1.",
    },
    "evaluate-reverse-polish-notation": {
        "ex1": "(2 + 1) * 3 = 9.",
        "ex2": "4 + (13 / 5) = 4 + 2 = 6.",
    },
    "generate-parentheses": {
        "ex2": "The only valid string of one pair is \"()\".",
    },
    "implement-trie-prefix-tree": {
        "ex2": "search \"world\" returns false because the word was never inserted, while startsWith \"hel\" returns true since \"hello\" is stored and shares that prefix.",
    },
"car-fleet": {
        "ex1": "Sorted by starting position, the faster cars ahead pull the trailing cars into them, and exactly two fleets arrive at the destination.",
        "ex2": "Every car travels the same speed from a different starting position, so none can ever catch the car ahead: 5 separate fleets.",
    },
    "largest-rectangle-in-histogram": {
        "ex1": "A height-2 rectangle spanning five bars gives the maximum area 10.",
        "ex2": "Three equal bars of height 2 form a 2x3 rectangle with area 6.",
    },
    "binary-search": {
        "ex1": "9 is at index 4 of the sorted array.",
        "ex2": "2 is not in the array, so the search returns -1.",
    },
    "search-a-2d-matrix": {
        "ex1": "3 lies in the first row between 1 and 7.",
        "ex2": "13 falls between 7 and 10, which is a gap, and is not present in the matrix.",
    },
    "koko-eating-bananas": {
        "ex1": "Eating 4 bananas/hour clears [3,6,7,11] in 1+2+2+3 = 8 hours.",
        "ex2": "Only 30 bananas/hour finishes the largest pile within 7 hours; any slower pile exceeds 7 hours.",
    },
    "find-minimum-in-rotated-sorted-array": {
        "ex1": "The array was rotated around 0, which is the smallest element.",
        "ex2": "Rotating [1,2,3,4,5] left once puts the minimum 1 at the end.",
    },
    "search-in-rotated-sorted-array": {
        "ex2": "0 sits at index 4 after the rotation.",
    },
    "time-based-key-value-store": {
        "ex1": "get foo 1 returns \"bar\" (its value at time 1); after set foo bar2 4, reads at 4 and 5 return \"bar2\".",
        "ex2": "The latest value at each timestamp: b at 1, then c at 2 and beyond.",
    },
    "median-of-two-sorted-arrays": {
        "ex1": "Merging gives [1,2,3,3,4,5]; the middle two 3 and 3 average to 3.0.",
        "ex2": "Merging gives [1,2,2,3,4]; the two middle values 2 and 3 average to 2.5.",
    },
    "reorder-list": {
        "ex1": "L0, Ln, L1, Ln-1 ... = 1 4 2 3.",
        "ex2": "With an odd-length list, the order becomes 1 5 2 4 3.",
    },
    "copy-list-with-random-pointer": {
        "ex1": "The deep copy keeps values 7 13 11 10 1 in the same order, and random pointers hang off the same structure.",
        "ex2": "The copy of a two-node list preserves values 1 2 in order.",
    },
    "add-two-numbers": {
        "ex1": "342 + 465 = 807, digits stored head-first as 7 0 8.",
        "ex2": "0 + 0 = 0.",
    },
    "find-the-duplicate-number": {
        "ex1": "2 appears twice while all other values appear once.",
        "ex2": "1 appears twice in [1, 1].",
    },
    "lru-cache": {
        "ex1": "get 1 returns 1; inserting 3 evicts the least-recently-used key 2, so get 2 is -1; get 3 is 3.",
        "ex2": "With capacity 1, get 2 returns the stored value 1.",
    },
    "merge-k-sorted-lists": {
        "ex1": "Merging the three sorted lists produces the fully sorted 0 1 2 3 4 5 6.",
        "ex2": "A single list merges unchanged: 1 2 3.",
    },
    "reverse-nodes-in-k-group": {
        "ex1": "Groups of two reverse within themselves: 2 1, 4 3, and the leftover 5 stays.",
        "ex2": "Groups of three reverse the first triple and leave 4 5 in place: 3 2 1 4 5.",
    },
    "design-add-and-search-words-data-structure": {
        "ex2": "Both \"a\" and \".\" match only the single inserted word \"a\"; \"..\" needs two characters, so it fails.",
    },
    "balanced-binary-tree": {
        "ex1": "Every subtree differs in height by at most 1.",
        "ex2": "The left subtree 2 2 3 3 4 4 hangs two levels deeper than the right, so the tree is unbalanced.",
    },
    "same-tree": {
        "ex1": "Both trees have 1 2 3 in identical positions, so they are structurally equal.",
        "ex2": "The second tree's 2 attaches on the right instead of the left, so the trees differ.",
    },
    "subtree-of-another-tree": {
        "ex1": "The four-node tree 4 1 2 appears as the left subtree of the larger tree.",
        "ex2": "The candidate subtree has an extra node 0 that the main tree lacks, so it does not match.",
    },
    "binary-tree-right-side-view": {
        "ex1": "The rightmost node of each level is 1, then 3, then 4.",
        "ex2": "Levels hold 1 and 3, so the right side sees 1 3.",
    },
    "count-good-nodes-in-binary-tree": {
        "ex1": "3, 3, 4 and 5 are all >= every ancestor on their path, so four good nodes.",
        "ex2": "Every node on each root-to-leaf path is >= its ancestors (3, 3, 4), giving three good nodes.",
    },
    "kth-smallest-element-in-a-bst": {
        "ex1": "The in-order traversal is 1 2 3 4 5 6; the 3rd value is 3.",
        "ex2": "The smallest value in the tree is 1.",
    },
    "construct-binary-tree-from-preorder-and-inorder-traversal": {
        "ex1": "Preorder root 3 splits inorder into left {9} and right {15 20 7}, producing the given level-order.",
        "ex2": "A single node -1 reconstructs to just -1.",
    },
    "binary-tree-maximum-path-sum": {
        "ex1": "The path 2 -> 1 -> 3 sums to 6.",
        "ex2": "The best path runs 15 -> 20 -> 7 (or 9) for a total of 42.",
    },
    "serialize-and-deserialize-binary-tree": {
        "ex1": "In-order (or level-order preorder) serialization reproduces 1 2 3 null null 4 5 after deserialize.",
        "ex2": "An empty tree serializes to an empty representation and back.",
    },
    "kth-largest-element-in-a-stream": {
        "ex1": "With k=3 the stream's current 3rd largest is 4 after inserting 3, 3 and 5.",
        "ex2": "The only element is 2, so it is the 1st largest.",
    },
    "last-stone-weight": {
        "ex1": "Smashing the heaviest stones repeatedly leaves nothing (0).",
        "ex2": "Smashing weights 2,7,4,1,8,1 ends with one stone of weight 1.",
    },
    "k-closest-points-to-origin": {
        "ex1": "(-2,2) and (2,-2) tie at distance sqrt(8), the two closest to the origin.",
        "ex2": "(0,1) and (0,-1) are both distance 1, and the closest is (0,1).",
    },
    "kth-largest-element-in-an-array": {
        "ex1": "Sorted descending [6,5,4,3,2,1], the 2nd largest is 5.",
        "ex2": "The only element 1 is also the kth largest.",
    },
    "task-scheduler": {
        "ex1": "AAABBB with cooldown 2 needs 8 slots: A B _ A B _ A B.",
        "ex2": "A single task with no cooldown runs in 1 unit.",
    },
    "design-twitter": {
        "ex1": "User 1 sees their own tweet 5, then after following 2 also sees 6 5, and after unfollowing only 5.",
        "ex2": "A user's own two tweets are returned newest first: 2 1.",
    },
    "find-median-from-data-stream": {
        "ex1": "Median after each insertion of 1..5: 1.0, 1.5, 2.0, 2.5, 3.0.",
        "ex2": "Insert 2 (median 2.0), then 1 (middle 2 and 1 -> 1.5), then 3 (median 2.0).",
    },
    "subsets": {
        "ex1": "All 8 subsets of {1,2,3}, one per line.",
        "ex2": "The subsets of a single element are the empty set and {0}.",
    },
    "combination-sum": {
        "ex1": "Combinations of [2,3,6,7] summing to 7 are 2+2+3 and 7.",
        "ex2": "From [2,3,5], 8 = 2+2+2+2, 2+3+3 or 3+5.",
    },
    "permutations": {
        "ex1": "All 3! = 6 orderings of 1 2 3.",
        "ex2": "The single value 1 has one permutation.",
    },
    "subsets-ii": {
        "ex1": "With duplicates, only unique subsets are listed (8 rows), skipping repeated copies.",
        "ex2": "The distinct subsets of {0,1} are the empty set, {0}, {1} and {0,1}.",
    },
    "combination-sum-ii": {
        "ex1": "Unique sets of candidates from [2,5,2,1,2] summing to 8 are 1+2+5 and 2+2+2.",
        "ex2": "Only 1 alone reaches the target 1 (2 exceeds it), giving a single combination.",
    },
    "word-search": {
        "ex1": "ABCCED can be traced through adjacent cells of the board.",
        "ex2": "AB appears down the first column.",
    },
    "palindrome-partitioning": {
        "ex1": "\"aab\" splits as \"a\" \"a\" \"b\" or the palindrome \"aa\" plus \"b\".",
        "ex2": "A single character is already a palindrome.",
    },
    "letter-combinations-of-a-phone-number": {
        "ex1": "Mapping 2 and 3 yields nine pairs: ad, ae, af, bd, be, bf, cd, ce, cf.",
        "ex2": "Digit 2 maps to the three letters a, b, c.",
    },
    "n-queens": {
        "ex1": "Two mirror solutions place four non-attacking queens on a 4x4 board.",
        "ex2": "One queen on a 1x1 board is trivially valid.",
    },
    "clone-graph": {
        "ex2": "A deep copy of the single node graph is a single node with the same value.",
    },
    "max-area-of-island": {
        "ex1": "The only island is a connected block of four 1s.",
        "ex2": "The ring of 1s encloses 8 cells, the maximum island area.",
    },
    "pacific-atlantic-water-flow": {
        "ex1": "Cells that drain to both oceans are at the listed intersections of reachable sets.",
        "ex2": "The single cell (0,0) drains to both oceans.",
    },
    "surrounded-regions": {
        "ex1": "Only O's not touching the border and fully enclosed get flipped to X.",
        "ex2": "All O's touch the border, so none are flipped.",
    },
    "rotting-oranges": {
        "ex1": "Rotting spreads for 4 minutes until every fresh orange is infected.",
        "ex2": "With only a rotten orange, no time passes (0).",
    },
    "walls-and-gates": {
        "ex1": "Distance to the nearest gate for each empty room: 3, then 2 2, then 1 and 3.",
        "ex2": "The gate itself has distance 0.",
    },
    "course-schedule-ii": {
        "ex1": "A valid order of courses 0..3 following prerequisites is 0 1 2 3.",
        "ex2": "The prerequisites form a cycle, so no ordering exists.",
    },
    "redundant-connection": {
        "ex1": "Adding 1-4 closes a cycle; removing that edge restores a tree.",
        "ex2": "The edge 1-5 is the one that creates the cycle in the 5-node graph.",
    },
    "number-of-connected-components-in-an-undirected-graph": {
        "ex1": "Edges connect 0-1-2 and 3-4 into two components.",
        "ex2": "With no edges, each node is its own component: 3.",
    },
    "reconstruct-itinerary": {
        "ex1": "Starting at JFK, the valid itinerary is JFK -> MUC -> LHR -> JFK.",
        "ex2": "Lexicographically smallest itinerary is JFK -> ATL -> JFK -> SFO -> ATL.",
    },
    "min-cost-to-connect-all-points": {
        "ex1": "The minimum spanning tree of the three points links them for 20 total Manhattan distance.",
        "ex2": "A single point needs no connections: cost 0.",
    },
    "network-delay-time": {
        "ex1": "Signals from 2 reach node 1 and 3 in 1, and node 4 in 2 — max delay 2.",
        "ex2": "The chain 1 -> 2 -> 3 costs 2 to reach the farthest node.",
    },
    "swim-in-rising-water": {
        "ex1": "The path through the 2x2 grid never crosses above elevation 3.",
        "ex2": "Reaching the bottom-right requires climbing to elevation 8 (checked first or last), the max along the diagonal path.",
    },
    "alien-dictionary": {
        "ex1": "From wrt < wrf and wrt < er, the letters impose the order w e r t f.",
        "ex2": "ba before bc means a precedes c, giving order b a c.",
    },
    "cheapest-flights-within-k-stops": {
        "ex1": "The cheapest route 0 -> 1 -> 2 -> 3 costs 700 with 2 stops (k=1 allows 2 edges: 100+100+600).",
        "ex2": "Direct 0 -> 2 costs 500 but 0 -> 1 -> 2 costs only 200 within 1 stop, so 200 is chosen.",
    },
    "min-cost-climbing-stairs": {
        "ex1": "Pay 15 once by stepping straight onto the top from cost[1].",
        "ex2": "Take costs 1 (index 0), then 1 (index 2), to climb for 2 total.",
    },
    "reverse-bits": {
        "ex1": "Bit-reversing 00000010100101000001111010011101 (43261596) gives 964176192.",
        "ex2": "Reversing 11111111111111111111111111111101 yields 3221225471.",
    },
    "partition-equal-subset-sum": {
        "ex2": "Total 6 is even, but no subset sums to 3, so partitioning is impossible.",
    },
    "longest-common-subsequence": {
        "ex1": "The common subsequence \"ace\" has length 3.",
        "ex2": "Both strings are identical, so every character matches: length 3.",
    },
    "best-time-to-buy-and-sell-stock-with-cooldown": {
        "ex1": "Buy at 1, sell at 3, then buy at 0 and sell at 2, honoring the cooldown for a profit of 3.",
        "ex2": "A single day leaves no room for a trade: 0.",
    },
    "coin-change-ii": {
        "ex1": "Coins {1,2,5} make 5 in 4 ways: 5, 2+2+1, 2+1+1+1, 1+1+1+1+1.",
        "ex2": "Coin 2 cannot build amount 3 with any number of 2s, so the count is 0.",
    },
    "target-sum": {
        "ex1": "Five sign assignments make [1,1,1,1,1] sum to 3.",
        "ex2": "The single 1 reaches target 1 with one assignment (+1).",
    },
    "interleaving-string": {
        "ex1": "aaxaby can be written by interleaving aab and axy in order.",
        "ex2": "aaxabby requires an extra 'b' that wastes characters, so it is not a valid interleaving.",
    },
    "longest-increasing-path-in-a-matrix": {
        "ex1": "The longest strictly increasing path (2-6-9 or 6-9 or 1-2-6-9) has length 4.",
        "ex2": "The diagonal 3-4-5-6 gives four strictly increasing steps.",
    },
    "distinct-subsequences": {
        "ex1": "Three ways to delete letters from rabbbit to get rabbit.",
        "ex2": "bag appears as a subsequence of babgbag in 5 ways.",
    },
    "burst-balloons": {
        "ex1": "Bursting in the optimal order yields 167 points.",
        "ex2": "A single balloon earns its own value, 1.",
    },
    "regular-expression-matching": {
        "ex1": "\"a\" matches exactly one character, so it cannot match the two a's.",
        "ex2": "\"a*\" can repeat the a twice, matching the whole string.",
    },
    "jump-game": {
        "ex1": "Each index can reach the end: 2 -> 4 directly.",
        "ex2": "Position 3 contains a 0 with no way around, so the end is unreachable.",
    },
    "jump-game-ii": {
        "ex1": "Two jumps reach the end: 2 -> 4.",
        "ex2": "The minimal jumps are still 2 (e.g., index 0 -> 1 -> 4).",
    },
    "gas-station": {
        "ex1": "Starting at station 1 lets the car complete the circular loop.",
        "ex2": "Total gas (9) is less than total cost (10), so no station works: -1.",
    },
    "hand-of-straights": {
        "ex1": "The nine cards split into three runs of exactly 3 consecutive values \u2014 (1,2,3), (2,3,4) and (6,7,8) \u2014 so the answer is true.",
        "ex2": "[1,2,3,4,5,6] splits into the three runs 1-2, 3-4, 5-6 of size 2.",
    },
"merge-triplets-to-form-target-triplet": {
        "ex1": "The triplet (1,8,4) exceeds the target's middle value (8 > 7), so it is set aside; merging (2,5,3) and (1,7,5) elementwise gives exactly (2,7,5).",
        "ex2": "Merging the two triplets elementwise yields (2,5,5), which can never match the target (2,7,5).",
    },
    "partition-labels": {
        "ex1": "Each letter appears in only one part: \"ababcbaca\", \"defegde\" and \"hijhklij\", with lengths 9, 7 and 8.",
        "ex2": "No two positions share a letter, so every character forms its own part of length 1.",
    },
    "valid-parenthesis-string": {
        "ex1": "The star acts as the closing bracket, pairing \"( )\" to make \"(*)\" balanced.",
        "ex2": "The star can act as an opening bracket, yielding an even number of pairs for \"(*))\" so the string stays balanced.",
    },
    "insert-interval": {
        "ex1": "The existing intervals merge into [1,9]; the inserted interval [10,15] starts after it and is appended unchanged.",
        "ex2": "There are no existing intervals, so the inserted interval [2,5] becomes the full result.",
    },
    "merge-intervals": {
        "ex1": "[1,3] and [2,6] overlap and merge into [1,6], while [8,10] and [15,18] stay as-is.",
        "ex2": "[1,4] and [4,5] touch at 4, so they merge into the single interval [1,5].",
    },
    "non-overlapping-intervals": {
        "ex1": "Removing just [1,3] leaves [1,2], [2,3] and [3,4], which do not overlap.",
        "ex2": "The two identical intervals overlap, so exactly one must be removed.",
    },
    "meeting-rooms": {
        "ex1": "The [0,30] meeting overlaps both [5,10] and [15,20], so no single room fits all three.",
        "ex2": "The [2,4] meeting ends before [7,10] begins, so one room suffices.",
    },
    "meeting-rooms-ii": {
        "ex1": "[5,10] and [15,20] fit inside [0,30], so two meeting rooms are enough and needed.",
        "ex2": "The [2,4] and [7,10] meetings never overlap, so one room covers both.",
    },
    "rotate-image": {
        "ex1": "Each cell moves to (row, col) = (col, n-1-row), rotating the matrix 90 degrees into rows 7 4 1, 8 5 2, 9 6 3.",
        "ex2": "A 1x1 matrix is unchanged when rotated.",
    },
    "spiral-matrix": {
        "ex1": "Walking the border clockwise gives 1 2 3 6 9 8 7 4, then the inner cell 5.",
        "ex2": "A single row is just read left to right: 1 2 3 4.",
    },
    "set-matrix-zeroes": {
        "ex1": "The 0 at (1,1) zeros its entire row and column, leaving 1 in the four untouched corners.",
        "ex2": "The zeros at column 0 in both rows propagate down the whole first column, and the zero in row 0 blanks that row.",
    },
    "happy-number": {
        "ex1": "19 then 82 then 68 then 100 then 1: the sum of squared digits reaches 1, so 19 is happy.",
        "ex2": "2 goes to 4 to 16 to 37 to 58 to 89 to 145 to 42 to 20 to 4, entering a cycle that never reaches 1.",
    },
    "plus-one": {
        "ex1": "Adding 1 to the last digit 3 carries no further: 123 + 1 = 124.",
        "ex2": "The last digit 1 becomes 2 with no carry: 4321 + 1 = 4322.",
    },
    "powx-n": {
        "ex1": "2.0 raised to the 10th power is 1024.0.",
        "ex2": "2.1 multiplied by itself three times is 9.261.",
    },
    "multiply-strings": {
        "ex1": "2 times 3 is 6.",
        "ex2": "123 times 456 computes to 56088.",
    },
    "detect-squares": {
        "ex1": "The added points complete exactly one square anchored at the queried (3,10), and the later query for (1,2) also matches one square.",
        "ex2": "After adding (0,0), (0,1) and (1,1), the queried corner (0,0) closes exactly one square.",
    },
    "single-number": {
        "ex1": "Every value pairs up except 4, which appears exactly once.",
        "ex2": "With a single element it is trivially the number that appears once.",
    },
    "number-of-1-bits": {
        "ex1": "11 in binary is 1011, which has three set bits.",
        "ex2": "128 in binary is 10000000, which has exactly one set bit.",
    },
    "counting-bits": {
        "ex1": "From 0 to 5 the set-bit counts are 0, 1, 1, 2, 1, 2 (binary 0,1,10,11,100,101).",
        "ex2": "For n = 0 the only count is 0.",
    },
    "missing-number": {
        "ex1": "The numbers 0, 1 and 3 are present, so 2 is the one missing from [0, n].",
        "ex2": "Only 0 is present, so 1 is the missing number.",
    },
    "sum-of-two-integers": {
        "ex1": "1 plus 2 sums to 3.",
        "ex2": "2 plus 3 sums to 5.",
    },
    "reverse-integer": {
        "ex1": "Reversing 123 gives 321.",
        "ex2": "Reversing -123 keeps the sign, giving -321.",
    },
    "graph-valid-tree": {
        "ex1": "Four edges join all five nodes with no cycles, so the graph is a tree.",
        "ex2": "The four edges on four nodes form the cycle 0-1-2-3-0, so it is not a tree.",
    },
    "word-ladder": {
        "ex1": "hit ? hot ? dot ? dog ? cog transforms one letter at a time in 4 steps, so the shortest sequence has length 5.",
        "ex2": "Without \"cog\" in the word list (or a path to it), no transformation reaches the target, so 0 is returned.",
    },
    "house-robber": {
        "ex1": "Robbing houses 1 and 3 (values 1 and 3) yields 4, more than any adjacent run.",
        "ex2": "Robbing houses 1, 3 and 5 (2 + 9 + 1 = 12) is the legal maximum under the no-adjacent rule.",
    },
    "house-robber-ii": {
        "ex1": "The first and last houses are adjacent on the circle, so only the middle house (3) can be robbed.",
        "ex2": "Robbing houses 0 and 2 (1 + 3 = 4) beats robbing just 3 or the two end houses which are adjacent.",
    },
    "longest-palindromic-substring": {
        "ex1": "Both \"bab\" and \"aba\" are palindromic substrings of length 3; the first found, \"bab\", is returned.",
        "ex2": "The substring \"bb\" is the longest palindromic segment of \"cbbd\".",
    },
    "palindromic-substrings": {
        "ex1": "Each single letter is a palindrome: a, b, c count as 3.",
        "ex2": "\"aaa\" contains 3 single-letter plus 2 double-letter (\"aa\", \"aa\") plus 1 triple-letter palindromes, totaling 6.",
    },
    "decode-ways": {
        "ex1": "226 decodes as 2-2-6, 22-6 or 2-26, which is 3 distinct ways.",
        "ex2": "06 cannot start with 0 (only 0 is not a valid letter code, and 06 has a leading zero), so 0 ways.",
    },
    "maximum-product-subarray": {
        "ex1": "The subarray [2,3] has the largest product, 6.",
        "ex2": "The single element 0 gives the largest product here because negatives multiply to positives but never exceed 0 alone.",
    },
    "longest-consecutive-sequence": {
        "ex1": "The numbers 1, 2, 3 and 4 form the longest consecutive run, length 4; 100 and 200 are isolated.",
        "ex2": "0 and 3 are not consecutive to each other, so the longest run is a single element, length 1.",
    },
    "generate-parentheses": {
        "ex1": "For three pairs there are exactly five valid combinations: ((())), (()()), (())(), ()(()) and ()()().",
        "ex2": "With one pair there is only the single combination ().",
    },
    "search-in-rotated-sorted-array": {
        "ex1": "3 does not appear in 4 5 6 7 0 1 2, so the answer is -1.",
        "ex2": "The target 0 sits at index 4 of 4 5 6 7 0 1 2, so the answer is 4.",
    },
}