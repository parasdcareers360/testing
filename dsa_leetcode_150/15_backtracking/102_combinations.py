"""
LeetCode Top Interview 150 — #102 (LeetCode #77)
Combinations
Category: Backtracking | Difficulty: Medium

Problem
-------
Given two integers `n` and `k`, return all possible combinations of `k` numbers chosen from the
range [1, n], in any order. Each combination is a distinct set of numbers (order within a
combination doesn't matter, and no number repeats within a combination).

Constraints
-----------
- 1 <= n <= 20
- 1 <= k <= n

Examples
--------
Example 1:
    Input: n = 4, k = 2
    Output: [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]

Example 2:
    Input: n = 1, k = 1
    Output: [[1]]

Intuition
---------
The brute-force route is to generate every k-length combination via `itertools.combinations` (or
equivalently, enumerate all subsets of {1..n} and keep those of size k) — correct, but treating
combination-generation as a black box misses the general technique. Backtracking builds each
combination incrementally: maintain a `start` pointer so we only ever consider numbers `>= start`,
which guarantees we never revisit a number and never produce the same combination twice in a
different order (this is what turns "permutation-style" DFS into "combination-style" DFS). The key
optimization on top of plain backtracking is **pruning**: if the numbers remaining from `start` to
`n` aren't even enough to fill out the rest of the combination, that branch can never succeed, so
we cut it immediately instead of wasting time exploring it.
"""

from typing import List
from itertools import combinations as itertools_combinations


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: use itertools.combinations to enumerate every k-subset of [1, n]
# directly — a correct, direct restatement of "all size-k subsets".
# Time:  O(C(n,k) * k) to build and materialize all combinations
# Space: O(C(n,k) * k) for the output
def solve_brute_force(n: int, k: int) -> List[List[int]]:
    return [list(c) for c in itertools_combinations(range(1, n + 1), k)]


# ============================================================
# Approach 2: Optimal (backtracking with pruning)
# ============================================================
# Idea: DFS with a `start` index so candidates only move forward (avoids
# duplicate/reordered combinations). Prune branches where there aren't
# enough remaining numbers (n - candidate + 1) to complete the combination
# to length k.
# Dry run: n=4, k=2
#   path=[] start=1 need=2
#     choose 1 -> path=[1] start=2 need=1
#       choose 2 -> path=[1,2] len==k -> record [1,2]; pop
#       choose 3 -> record [1,3]; pop
#       choose 4 -> record [1,4]; pop
#     pop 1 -> choose 2 -> path=[2] start=3 -> record [2,3],[2,4]
#     choose 3 -> path=[3] start=4 -> record [3,4]
#     choose 4 -> path=[4] start=5 -> need 1 more but nothing left -> pruned (loop doesn't even start)
#   result: [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
# Time:  O(C(n,k) * k) — pruning avoids wasted work but output size still dominates
# Space: O(k) recursion depth/path, excluding output
def solve_optimal(n: int, k: int) -> List[List[int]]:
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int) -> None:
        if len(path) == k:
            result.append(path[:])
            return
        needed = k - len(path)
        # Prune: candidate..n must contain at least `needed` numbers.
        for candidate in range(start, n - needed + 2):
            path.append(candidate)
            backtrack(candidate + 1)
            path.pop()

    backtrack(1)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - The `start` pointer is what distinguishes "combination" DFS from
#   "permutation" DFS: always moving forward means each subset is only
#   ever generated once, in one canonical (increasing) order.
# - Common mistake: bounding the loop with plain `range(start, n + 1)`
#   instead of pruning with `n - needed + 2` — still correct, just slower,
#   since it explores branches that can never reach length k.
# - Related/variant problems to try next: Combination Sum, Permutations,
#   Subsets.


if __name__ == "__main__":
    def normalize(combos):
        return sorted(sorted(c) for c in combos)

    tests = [
        ((4, 2), [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]),
        ((1, 1), [[1]]),
        ((3, 3), [[1, 2, 3]]),
        ((5, 1), [[1], [2], [3], [4], [5]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")
