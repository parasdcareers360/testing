"""
LeetCode Top Interview 150 — #106 (LeetCode #22)
Generate Parentheses
Category: Backtracking | Difficulty: Medium

Problem
-------
Given `n` pairs of parentheses, generate all combinations of well-formed (balanced) parentheses
strings that can be made using exactly `n` open and `n` close parentheses. Return the answer as a
list of strings, in any order.

Constraints
-----------
- 1 <= n <= 8

Examples
--------
Example 1:
    Input: n = 3
    Output: ["((()))","(()())","(())()","()(())","()()()"]

Example 2:
    Input: n = 1
    Output: ["()"]

Intuition
---------
The brute force is to generate every string of length 2n over the alphabet {'(', ')'} — there are
2^(2n) of them — and filter to the ones that are balanced. That wastes enormous effort building
strings that are doomed from the very first few characters (e.g. starting with three closing
parens can never recover). Backtracking fixes this by building the string left to right and only
ever placing a character that *cannot* already break balance: place '(' whenever we still have
opens left to use, and place ')' only when doing so wouldn't create more closes than opens so far
(i.e. `close_count < open_count`). This one pruning rule guarantees every path we ever fully
explore is a valid combination, so no filtering step is needed at the end at all.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (generate all 2^(2n) strings, filter valid ones)
# ============================================================
# Idea: build every length-2n string over {'(', ')'} via full binary
# recursion, then check each for balance (running count never negative,
# ending at zero). Simple but explores exponentially many dead strings that
# are already broken partway through.
# Time:  O(2^(2n) * n) — 2^(2n) strings, O(n) to validate each
# Space: O(n) recursion depth per string, output aside
def solve_brute_force(n: int) -> List[str]:
    result: List[str] = []
    total = 2 * n

    def is_valid(s: str) -> bool:
        balance = 0
        for ch in s:
            balance += 1 if ch == "(" else -1
            if balance < 0:
                return False
        return balance == 0

    def build(path: List[str]) -> None:
        if len(path) == total:
            candidate = "".join(path)
            if is_valid(candidate):
                result.append(candidate)
            return
        for ch in "()":
            path.append(ch)
            build(path)
            path.pop()

    build([])
    return result


# ============================================================
# Approach 2: Optimal (backtracking with open/close counters, no filtering)
# ============================================================
# Idea: track how many '(' and ')' have been used so far. Only recurse on
# '(' if open_count < n (opens remain), and only recurse on ')' if
# close_count < open_count (closing wouldn't exceed opens placed so far).
# Every complete path built this way is automatically balanced, so there is
# no post-hoc validity check at all.
# Dry run: n=2
#   "" -> place '(' -> "(" (open=1,close=0)
#     -> place '(' -> "((" (open=2,close=0)
#       -> can't open (open==n); place ')' -> "(()" (close=1<open=2 ok)
#         -> place ')' -> "(())" len=4 -> record "(())"
#     -> place ')' -> "()" (close=1<open=1? no, 1<1 false... wait close<open
#        uses close=0<open=1 before placing) -> "()" (open=1,close=1)
#       -> place '(' -> "()(" (open=2,close=1) -> place ')' -> "()()" -> record
#   result: ["(())", "()()"]
# Time:  O(4^n / sqrt(n)) — bounded by the nth Catalan number (the count of
#        valid strings itself), each built in O(n) — no wasted dead branches
# Space: O(n) recursion depth
def solve_optimal(n: int) -> List[str]:
    result: List[str] = []
    path: List[str] = []

    def backtrack(open_count: int, close_count: int) -> None:
        if len(path) == 2 * n:
            result.append("".join(path))
            return
        if open_count < n:
            path.append("(")
            backtrack(open_count + 1, close_count)
            path.pop()
        if close_count < open_count:
            path.append(")")
            backtrack(open_count, close_count + 1)
            path.pop()

    backtrack(0, 0)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - The core backtracking pattern here is "prune using a cheap local
#   invariant" (close_count < open_count) instead of "generate then check a
#   global property" — whenever a partial solution can be proven doomed
#   early, check it before recursing, not after the fact.
# - Common mistake: allowing ')' whenever close_count < n instead of
#   close_count < open_count — that lets closes get ahead of opens and
#   produces invalid strings like ")(" mixed into otherwise-valid output.
# - Related/variant problems to try next: Valid Parentheses, Remove Invalid
#   Parentheses, Longest Valid Parentheses.


if __name__ == "__main__":
    def normalize(strings):
        return sorted(strings)

    tests = [
        ((1,), ["()"]),
        ((2,), ["(())", "()()"]),
        ((3,), ["((()))", "(()())", "(())()", "()(())", "()()()"]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:10s} -> {result!r}  [{status}]")
