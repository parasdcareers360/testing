"""
LeetCode Top Interview 150 — #20 (LeetCode #14)
Longest Common Prefix
Category: Array / String | Difficulty: Easy

Problem
-------
Write a function to find the longest common prefix string amongst an array of strings. If there
is no common prefix, return an empty string "".

Constraints
-----------
- 1 <= strs.length <= 200
- 0 <= strs[i].length <= 200
- strs[i] consists of only lowercase English letters (if it is non-empty)

Examples
--------
Example 1:
    Input: strs = ["flower","flow","flight"]
    Output: "fl"

Example 2:
    Input: strs = ["dog","racecar","car"]
    Output: ""
    Explanation: There is no common prefix among the input strings.

Intuition
---------
The naive way is to compare character-by-character across *all* strings at once: walk a column
index from 0 upward, and at each column check whether every string has the same character there,
stopping at the first mismatch (or the first string that's too short). That's already close to
optimal — O(S) where S is the total number of characters — so the real alternative worth showing
is a different strategy entirely: horizontal scanning, where you start with the first string as
the candidate prefix and repeatedly shrink it (chopping off its last character) until it's a
prefix of the next string, then the next, and so on. This reframes the problem as "reduce a
candidate until it fits" rather than "grow a shared column," and in the worst case (strings share
almost nothing) it can shrink the candidate to "" very quickly rather than checking every string
at every column.
"""

from typing import List


# ============================================================
# Approach 1: Vertical scanning (column by column)
# ============================================================
# Idea: treat strs[0] as a guide; for each character position i in strs[0],
# check that every other string also has that same character at position i.
# Stop at the first mismatch or the first string too short to have index i.
# Time:  O(S) where S is the total number of characters across all strings
#        in the worst case (all strings identical) — but stops early on
#        the first mismatching column
# Space: O(1) extra (excluding the output string)
def solve_vertical(strs: List[str]) -> str:
    if not strs:
        return ""

    for i, ch in enumerate(strs[0]):
        for s in strs[1:]:
            if i >= len(s) or s[i] != ch:
                return strs[0][:i]

    return strs[0]


# ============================================================
# Approach 2: Horizontal scanning (shrink a candidate prefix)
# ============================================================
# Idea: start with prefix = strs[0]. For each subsequent string, shrink the
# prefix from the right (one character at a time) until it's actually a
# prefix of that string. If the prefix ever empties out, no common prefix
# exists at all.
# Dry run: strs=["flower","flow","flight"]
#   prefix="flower"
#   check against "flow": "flower" not a prefix of "flow" -> shrink to
#     "flowe" -> "flow" -> now "flow" is a prefix of "flow" -> prefix="flow"
#   check against "flight": "flow" not a prefix of "flight" -> shrink to
#     "flo" -> "fl" -> "fl" is a prefix of "flight" -> prefix="fl"
#   result: "fl"
# Time:  O(S) worst case, but often much less — each shrink step is O(1)
#        amortized against the characters being discarded
# Space: O(1) extra (excluding the output string)
def solve_optimal(strs: List[str]) -> str:
    if not strs:
        return ""

    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""

    return prefix


# ============================================================
# Key Takeaways
# ============================================================
# - "Longest common prefix" problems can be attacked either by growing a
#   shared column across all strings (vertical) or by shrinking a candidate
#   until it fits every string (horizontal) — both are O(S) worst case, but
#   horizontal scanning short-circuits faster when an early string kills
#   most of the candidate immediately.
# - Common mistake: not handling an empty input list, or not guarding
#   against index-out-of-range when a string is shorter than the current
#   prefix candidate.
# - Related/variant problems to try next: Longest Common Subsequence,
#   Implement Trie (Prefix Tree), Longest Word in Dictionary.


if __name__ == "__main__":
    tests = [
        ((["flower", "flow", "flight"],), "fl"),
        ((["dog", "racecar", "car"],), ""),
        ((["single"],), "single"),
        ((["", "b"],), ""),
        ((["abc", "abc", "abc"],), "abc"),
        ((["ab", "a"],), "a"),
    ]

    approaches = [solve_vertical, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
