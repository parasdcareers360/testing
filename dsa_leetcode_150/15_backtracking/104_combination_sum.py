"""
LeetCode Top Interview 150 — #104 (LeetCode #39)
Combination Sum
Category: Backtracking | Difficulty: Medium

Problem
-------
Given an array of distinct integers `candidates` and a target integer `target`, return a list of
all unique combinations of `candidates` where the chosen numbers sum to `target`. The same number
may be chosen from `candidates` an unlimited number of times. Two combinations are unique if the
frequency of at least one of the chosen numbers is different. Return the combinations in any
order.

Constraints
-----------
- 1 <= candidates.length <= 30
- 2 <= candidates[i] <= 40
- All elements of candidates are distinct.
- 1 <= target <= 40

Examples
--------
Example 1:
    Input: candidates = [2,3,6,7], target = 7
    Output: [[2,2,3],[7]]

Example 2:
    Input: candidates = [2,3,5], target = 8
    Output: [[2,2,2,2],[2,3,3],[3,5]]

Example 3:
    Input: candidates = [2], target = 1
    Output: []

Intuition
---------
Because each candidate can be reused any number of times, the brute-force way to think about it is
"generate all multisets of candidates up to some bounded length and keep the ones that sum to
target" — but there's no natural finite bound on length without already knowing which numbers sum
to target, so a true brute force must cap the count of each candidate (target // candidate) and
enumerate the resulting bounded Cartesian product, filtering by sum. That's wasteful and awkward.
Backtracking instead builds sums incrementally with a running `remaining` budget: at each step,
try each candidate `>= start_index` (allowing repeats by *not* advancing the index when we reuse
the same candidate, but never looking backward, which prevents `[2,3]` and `[3,2]` both appearing).
Two prunes make this efficient: stop trying a candidate once it exceeds what's left to reach
target, and (with sorted candidates) break out of the loop entirely once a candidate exceeds the
remaining budget, since every later candidate is even bigger.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (bounded repetition + filter)
# ============================================================
# Idea: for each candidate, the maximum number of times it could appear in
# any valid combination is target // candidate. Enumerate the Cartesian
# product of "how many times each candidate is used" (0..max_count for
# each), keep combinations whose weighted sum equals target. Correct but
# explores many dead sum totals that backtracking prunes early.
# Time:  O(prod(target/candidates[i] + 1) * n) — exponential, much worse than backtracking's
#        effective search-space pruning
# Space: O(n) per combination check, plus output
def solve_brute_force(candidates: List[int], target: int) -> List[List[int]]:
    n = len(candidates)
    max_counts = [target // c for c in candidates]
    result: List[List[int]] = []

    def build(idx: int, counts: List[int], remaining: int) -> None:
        if idx == n:
            if remaining == 0:
                combo = []
                for c, cnt in zip(candidates, counts):
                    combo.extend([c] * cnt)
                if combo:  # empty combo only valid if target == 0, which can't happen (target >= 1)
                    result.append(combo)
            return
        for cnt in range(max_counts[idx] + 1):
            used = cnt * candidates[idx]
            if used > remaining:
                break
            counts.append(cnt)
            build(idx + 1, counts, remaining - used)
            counts.pop()

    build(0, [], target)
    return result


# ============================================================
# Approach 2: Optimal (backtracking with pruning, index doesn't advance on reuse)
# ============================================================
# Idea: DFS with a running `remaining` target. At index `start`, either
# skip candidates[start] entirely (move to start+1) or take it and recurse
# with the SAME start (since it can be reused) and a reduced remaining.
# Sorting candidates first lets us break early once candidates[i] > remaining,
# since every subsequent candidate is only larger.
# Dry run: candidates=[2,3,6,7] (sorted), target=7
#   start=0 remaining=7: take 2 -> path=[2] remaining=5
#     take 2 -> path=[2,2] remaining=3
#       take 2 -> path=[2,2,2] remaining=1 -> take 3? 3>1 break -> dead end
#       take 3 -> path=[2,2,3] remaining=0 -> record [2,2,3]; pop
#     take 6? 6>... continue exploring other branches similarly
#   eventually also finds path=[7] remaining=0 -> record [7]
#   result: [[2,2,3],[7]]
# Time:  O(2^target) worst case (still exponential — this problem is inherently
#        combinatorial), but pruning cuts off entire subtrees once remaining < 0
# Space: O(target / min(candidates)) recursion depth, excluding output
def solve_optimal(candidates: List[int], target: int) -> List[List[int]]:
    candidates = sorted(candidates)
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break  # sorted: every candidate from here on is also too big
            path.append(c)
            backtrack(i, remaining - c)  # same i: c may be reused
            path.pop()

    backtrack(0, target)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - "Unlimited reuse" combinations are handled by recursing with the SAME
#   start index (not start+1) when a candidate is taken — that permits
#   repeats while the forward-only index still prevents reordered
#   duplicates like both [2,3] and [3,2].
# - Common mistake: sorting candidates but forgetting the early `break`
#   (using `continue` instead) — still correct, just loses the pruning
#   speedup that sorting was meant to enable.
# - Related/variant problems to try next: Combinations, Combination Sum II
#   (each candidate usable once, array has duplicates), Combination Sum III.


if __name__ == "__main__":
    def normalize(combos):
        return sorted(sorted(c) for c in combos)

    tests = [
        (([2, 3, 6, 7], 7), [[2, 2, 3], [7]]),
        (([2, 3, 5], 8), [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
        (([2], 1), []),
        (([3, 5], 8), [[3, 5]]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")
