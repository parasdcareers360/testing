"""
LeetCode Top Interview 150 — #101 (LeetCode #17)
Letter Combinations of a Phone Number
Category: Backtracking | Difficulty: Medium

Problem
-------
Given a string `digits` containing digits from 2-9 inclusive, return all possible letter
combinations that the number could represent, in any order. The mapping of digits to letters is
the same as on a telephone keypad:

    2 -> abc   3 -> def   4 -> ghi   5 -> jkl
    6 -> mno   7 -> pqrs  8 -> tuv   9 -> wxyz

If `digits` is empty, return an empty list.

Constraints
-----------
- 0 <= digits.length <= 4
- digits[i] is a digit in the range ['2', '9']

Examples
--------
Example 1:
    Input: digits = "23"
    Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]

Example 2:
    Input: digits = ""
    Output: []

Example 3:
    Input: digits = "2"
    Output: ["a","b","c"]

Intuition
---------
Each digit contributes a small, independent set of letter choices, and the final answer is
exactly the Cartesian product of those choice-sets. The brute-force way to build a Cartesian
product is `itertools.product` (or manually folding one digit's letters into every partial string
built so far) — correct and simple, but it doesn't generalize to problems where later choices
depend on earlier ones. Backtracking builds the same product one character at a time via DFS:
pick a letter for the current digit, append it to the path, recurse into the next digit, then
undo (pop) before trying the next letter. Since `digits.length <= 4`, the total output size is
tiny (at most 4^4 = 256), so every approach here runs essentially instantly — the point of this
problem is the *pattern* (DFS + path + undo), which is the backbone of every backtracking problem
that follows.
"""

from typing import List
from itertools import product


DIGIT_TO_LETTERS = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


# ============================================================
# Approach 1: Brute Force (Cartesian product)
# ============================================================
# Idea: look up each digit's letters, then take the Cartesian product of
# all the letter-sets and join each tuple into a string. This is the most
# direct translation of "answer = product of independent choice sets".
# Time:  O(3^m * 4^n * L) where m/n = digits mapping to 3/4 letters, L = digits length (output size)
# Space: O(L) per combination, output-size dominated
def solve_brute_force(digits: str) -> List[str]:
    if not digits:
        return []
    letter_groups = [DIGIT_TO_LETTERS[d] for d in digits]
    return ["".join(combo) for combo in product(*letter_groups)]


# ============================================================
# Approach 2: Optimal (backtracking / DFS)
# ============================================================
# Idea: DFS over digit positions. At each position, try every letter the
# current digit maps to, append it to a shared "path" buffer, recurse to
# the next digit, then pop the letter off before trying the next one
# (the "undo" step that makes this backtracking rather than plain
# recursion). A complete path (len(path) == len(digits)) is one answer.
# Dry run: digits = "23"
#   path=[] idx=0 digit='2' letters="abc"
#     try 'a' -> path=['a'] idx=1 digit='3' letters="def"
#       try 'd' -> path=['a','d'] idx=2 == len -> record "ad"; pop 'd'
#       try 'e' -> record "ae"; pop 'e'
#       try 'f' -> record "af"; pop 'f'
#     pop 'a' -> try 'b' -> produces "bd","be","bf" ... -> try 'c' -> "cd","ce","cf"
#   result: ["ad","ae","af","bd","be","bf","cd","ce","cf"]
# Time:  O(3^m * 4^n * L) — same output-bound complexity as brute force
# Space: O(L) recursion depth + path buffer, excluding output
def solve_optimal(digits: str) -> List[str]:
    if not digits:
        return []

    result: List[str] = []
    path: List[str] = []

    def backtrack(idx: int) -> None:
        if idx == len(digits):
            result.append("".join(path))
            return
        for letter in DIGIT_TO_LETTERS[digits[idx]]:
            path.append(letter)          # choose
            backtrack(idx + 1)           # explore
            path.pop()                   # un-choose (backtrack)

    backtrack(0)
    return result


# ============================================================
# Key Takeaways
# ============================================================
# - The core backtracking skeleton: choose -> recurse -> un-choose. The
#   shared mutable `path` list plus explicit pop is more memory-efficient
#   than passing/copying a new string at every level.
# - Common mistake: forgetting the `path.pop()` undo step, which silently
#   corrupts every subsequent branch's path with leftover letters.
# - Related/variant problems to try next: Combinations, Permutations,
#   Generate Parentheses (all DFS-with-undo over a small search space).


if __name__ == "__main__":
    tests = [
        (("23",), ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]),
        (("",), []),
        (("2",), ["a", "b", "c"]),
        (("9",), ["w", "x", "y", "z"]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if sorted(result) == sorted(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")
