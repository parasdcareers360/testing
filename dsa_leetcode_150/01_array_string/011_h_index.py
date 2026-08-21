"""
LeetCode Top Interview 150 — #11 (LeetCode #274)
H-Index
Category: Array / String | Difficulty: Medium

Problem
-------
Given an array of integers `citations` where `citations[i]` is the number of citations a
researcher received for their `i`-th paper, return the researcher's h-index.

The h-index is defined as: the maximum value `h` such that the researcher has published at least
`h` papers that have each been cited at least `h` times (and the remaining papers have no more
than `h` citations each).

Constraints
-----------
- n == citations.length
- 1 <= n <= 5000
- 0 <= citations[i] <= 1000

Examples
--------
Example 1:
    Input: citations = [3,0,6,1,5]
    Output: 3
    Explanation: The researcher has 5 papers with [3,0,6,1,5] citations. Sorted descending:
                 [6,5,3,1,0]. Three papers have >= 3 citations each (6, 5, 3), and the h-index
                 cannot be 4 because only 2 papers (6, 5) have >= 4 citations. So h = 3.

Example 2:
    Input: citations = [1,3,1]
    Output: 1

Intuition
---------
The definition of h-index is really a search over candidate values of h — "does this value of h
work?" — so the brute force just tries every candidate h from n down to 0 and checks, for each,
whether at least h papers have >= h citations, taking the first (largest) h that works; each check
costs a full scan, so this is O(n^2). The key structural fact is that h-index only depends on the
*relative order* of citation counts, not their raw values — so sorting once (descending) lets us
answer with a single linear scan: walk the sorted list and stop at the first position where the
citation count drops below the 1-indexed rank (paper count so far), since beyond that point no
paper can sustain "h papers with >= h citations" for a larger h. Sorting costs O(n log n), which
we can shave down to O(n) using counting sort: since a citation count of n or more is functionally
equivalent to exactly n citations for this problem (an h-index can never exceed n, the total
number of papers), we can bucket citations into n+1 buckets and derive h directly, no comparison
sort required.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (try every candidate h)
# ============================================================
# Idea: for each candidate h from n down to 0, count how many papers have
# >= h citations; the first h (largest) for which that count is >= h is
# the answer. Each candidate requires a full scan of citations.
# Time:  O(n^2)
# Space: O(1)
def solve_brute_force(citations: List[int]) -> int:
    n = len(citations)
    for h in range(n, -1, -1):
        count = sum(1 for c in citations if c >= h)
        if count >= h:
            return h
    return 0


# ============================================================
# Approach 2: Better (sort then scan)
# ============================================================
# Idea: sort citations descending. Walk the sorted list; at position i
# (0-indexed), we're asking "do the first i+1 papers all have at least
# i+1 citations?" i.e. is citations[i] >= i+1. The answer is the largest
# such i+1; scanning stops at the first violation.
# Time:  O(n log n) — dominated by the sort
# Space: O(n) or O(log n) depending on sort implementation
def solve_better(citations: List[int]) -> int:
    sorted_desc = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(sorted_desc):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h


# ============================================================
# Approach 3: Best / Alternate Optimal (counting sort / bucket)
# ============================================================
# Idea: h-index can never exceed n (there are only n papers), so any
# citation count >= n is interchangeable with exactly n for this problem.
# Bucket each paper's citation count (capped at n) into buckets[0..n],
# then scan from the top bucket down, accumulating a running count of
# "papers with at least this many citations" -- the first bucket value h
# where that running total >= h is the h-index.
# Dry run: citations = [3,0,6,1,5], n=5
#   6 is capped to 5, so buckets by citation count:
#   buckets = [1,1,0,1,0,2]  (index 0:1, 1:1, 3:1, 5:2 -- from both 5 and capped 6)
#   scan h=5..0, running total of papers with >= h citations:
#     h=5: total=0+buckets[5]=2 -> 2>=5? no
#     h=4: total=2+buckets[4]=2 -> 2>=4? no
#     h=3: total=2+buckets[3]=3 -> 3>=3? yes -> return 3
# Time:  O(n)
# Space: O(n) — the bucket array
def solve_best(citations: List[int]) -> int:
    n = len(citations)
    buckets = [0] * (n + 1)
    for c in citations:
        buckets[min(c, n)] += 1

    total = 0
    for h in range(n, -1, -1):
        total += buckets[h]
        if total >= h:
            return h
    return 0


# ============================================================
# Key Takeaways
# ============================================================
# - H-index is fundamentally a "find the largest threshold h that a
#   sorted-by-rank sequence still satisfies" problem — sorting (or
#   bucketing, when values are bounded) turns an O(n^2) definition-check
#   into a single linear scan.
# - Common mistake: comparing citations[i] >= i (0-indexed) instead of
#   citations[i] >= i + 1 (rank is 1-indexed: "i+1 papers so far").
# - Related/variant problems to try next: H-Index II (citations already
#   sorted -> binary search for O(log n)), Kth Largest Element, Meeting
#   Rooms II (also solved via counting/bucket-style scans).


if __name__ == "__main__":
    tests = [
        (([3, 0, 6, 1, 5],), 3),
        (([1, 3, 1],), 1),
        (([0],), 0),
        (([0, 0, 0],), 0),
        (([100],), 1),
        (([1, 2, 3, 4, 5],), 3),
        (([25, 8, 5, 3, 3],), 3),
    ]

    approaches = [solve_brute_force, solve_better, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
