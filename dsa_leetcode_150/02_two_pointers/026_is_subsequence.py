"""
LeetCode Top Interview 150 — #26 (LeetCode #392)
Is Subsequence
Category: Two Pointers | Difficulty: Easy

Problem
-------
Given two strings `s` and `t`, determine whether `s` is a subsequence of `t`.

A subsequence is formed by deleting some (possibly zero) characters from a string without
disturbing the relative order of the remaining characters (e.g. "ace" is a subsequence of
"abcde" but "aec" is not).

Return `True` if `s` is a subsequence of `t`, otherwise `False`.

Constraints
-----------
- 0 <= s.length <= 100
- 0 <= t.length <= 10^4
- `s` and `t` consist only of lowercase English letters.

Follow-up: Suppose there are lots of incoming `s` strings (say billions), all checked against
the same `t`. How would you change your code to handle this efficiently?

Examples
--------
Example 1:
    Input: s = "abc", t = "ahbgdc"
    Output: True

Example 2:
    Input: s = "axc", t = "ahbgdc"
    Output: False

Intuition
---------
A brute-force way to check "can s be carved out of t in order" is recursive backtracking: try to
match s[0] against t starting at every possible position, then recurse on the rest — correct but
exponential in the worst case since it can re-explore overlapping choices. The key realization is
that matching a subsequence greedily is always safe: whenever the current characters of s and t
match, there is never a reason to "save" that match for later — taking it earliest only leaves
more of t available for the rest of s. That greedy two-pointer scan is linear. The follow-up
(checking many different `s` against the same fixed `t`) motivates a different, precomputation-
based approach: build a table of "next occurrence of each letter from position i in t", turning
each subsequent query into O(len(s) * 26) or better via binary search over per-letter position
lists — worthwhile when `t` is queried many times but wasteful for a single one-off check.
"""

from typing import List
from collections import defaultdict
from bisect import bisect_left


# ============================================================
# Approach 1: Brute Force (recursive backtracking)
# ============================================================
# Idea: recursively try to match s[i] at every position j in t going
# forward; if matched, recurse on (i+1, j+1), else try (i, j+1). Correct
# but re-explores the "skip this char of t" branch even when a greedy
# match would already work, making it exponential in the worst case.
# Time:  O(2^n) worst case (n = len(t)) without memoization
# Space: O(n) recursion depth
def solve_brute_force(s: str, t: str) -> bool:
    def helper(i: int, j: int) -> bool:
        if i == len(s):
            return True
        if j == len(t):
            return False
        if s[i] == t[j]:
            # Try consuming this match, but also allow skipping it (in case
            # a later occurrence of the same letter leads to a full match) —
            # this branching is what makes it exponential.
            if helper(i + 1, j + 1):
                return True
        return helper(i, j + 1)

    return helper(0, 0)


# ============================================================
# Approach 2: Optimal (greedy two pointers)
# ============================================================
# Idea: walk pointer i over s and j over t simultaneously. Whenever
# s[i] == t[j], advance i (we "used" that character of s); always advance
# j. If i reaches len(s), every character of s was matched in order.
# Dry run: s = "abc", t = "ahbgdc"
#   i=0('a') j=0('a') -> match -> i=1, j=1
#   i=1('b') j=1('h') -> no match -> j=2
#   i=1('b') j=2('b') -> match -> i=2, j=3
#   i=2('c') j=3('g') -> no match -> j=4
#   i=2('c') j=4('d') -> no match -> j=5
#   i=2('c') j=5('c') -> match -> i=3, j=6
#   i == len(s)=3 -> True
# Time:  O(len(t)) — single pass through t
# Space: O(1)
def solve_optimal(s: str, t: str) -> bool:
    i = 0
    for j in range(len(t)):
        if i < len(s) and s[i] == t[j]:
            i += 1
    return i == len(s)


# ============================================================
# Approach 3: Best (precompute per-letter positions + binary search,
# for the "many s queries against the same t" follow-up)
# ============================================================
# Idea: build, once, a map from each letter to the sorted list of indices
# where it occurs in t. For each character of s, binary-search (bisect) for
# the smallest position in that letter's list that is strictly greater than
# the last matched position. This turns each query into O(len(s) * log n)
# instead of O(len(t)), which wins big when t is fixed and queried
# repeatedly (the brute/optimal approaches above re-scan t every time).
# Time:  O(n) one-time preprocessing (n = len(t)) + O(m log n) per query (m = len(s))
# Space: O(n) for the position map
def solve_best(s: str, t: str) -> bool:
    positions = defaultdict(list)
    for idx, ch in enumerate(t):
        positions[ch].append(idx)

    search_from = -1
    for ch in s:
        candidates = positions.get(ch)
        if not candidates:
            return False
        pos = bisect_left(candidates, search_from + 1)
        if pos == len(candidates):
            return False
        search_from = candidates[pos]

    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Greedy two pointers work for subsequence matching because matching a
#   character as early as possible never hurts future matches — a classic
#   "exchange argument" greedy proof.
# - Common mistake: trying to also advance the s-pointer on a mismatch (it
#   must only advance on a match), or forgetting the bounds check on i
#   before comparing s[i] to t[j].
# - Related/variant problems to try next: Number of Matching Subsequences,
#   Longest Common Subsequence, Edit Distance.


if __name__ == "__main__":
    tests: List[tuple] = [
        (("abc", "ahbgdc"), True),
        (("axc", "ahbgdc"), False),
        (("", "ahbgdc"), True),
        (("abc", ""), False),
        (("", ""), True),
        (("b", "abc"), True),
        (("acb", "ahbgdc"), False),
        (("aaaaaa", "aaaaaaaaaa"), True),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
