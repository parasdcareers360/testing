"""
LeetCode Top Interview 150 — #23 (LeetCode #28)
Find the Index of the First Occurrence in a String
Category: Array / String | Difficulty: Easy

Problem
-------
Given two strings `haystack` and `needle`, return the index of the first occurrence of `needle`
in `haystack`, or -1 if `needle` is not part of `haystack`.

(This is essentially implementing `str.find()` / `strstr()` from scratch.)

Constraints
-----------
- 1 <= haystack.length, needle.length <= 10^4
- haystack and needle consist of only lowercase English characters.

Examples
--------
Example 1:
    Input: haystack = "sadbutsad", needle = "sad"
    Output: 0
    Explanation: "sad" occurs at index 0 and index 6, but the first occurrence is at index 0.

Example 2:
    Input: haystack = "leetcode", needle = "leeto"
    Output: -1
    Explanation: "leeto" does not occur in "leetcode".

Intuition
---------
The most direct approach is the naive substring check: try every starting offset `i` in
`haystack`, and at each one compare up to `len(needle)` characters against `needle`. This is
O(n*m) in the worst case (e.g. haystack = "aaaa...a", needle = "aaa...ab") because a mismatch near
the end of a long needle forces us to fall all the way back and retry from the very next offset,
throwing away everything we learned about the partial match. The Knuth-Morris-Pratt (KMP)
algorithm fixes exactly this waste: it precomputes, for the needle itself, a "failure function"
(a.k.a. the longest-proper-prefix-that-is-also-a-suffix table, or LPS table) that tells us, upon a
mismatch, exactly how far we can safely slide the needle forward without re-comparing characters
we already know match — because the needle's own internal structure tells us what prefix could
still be in play. This lets KMP scan `haystack` in a single O(n+m) pass, never backtracking the
haystack pointer. It's a genuinely different algorithmic idea (preprocessing the pattern to avoid
redundant comparisons), not just a cosmetic tweak of the naive check, so it earns its place as a
distinct "best" approach rather than a padded 4th approach.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (naive substring check per offset)
# ============================================================
# Idea: try every starting index in haystack; at each one, compare
# characters one by one against needle until a mismatch or a full match.
# Time:  O(n*m) worst case (n = len(haystack), m = len(needle))
# Space: O(1)
def solve_brute_force(haystack: str, needle: str) -> int:
    n, m = len(haystack), len(needle)
    for i in range(n - m + 1):
        j = 0
        while j < m and haystack[i + j] == needle[j]:
            j += 1
        if j == m:
            return i
    return -1


# ============================================================
# Approach 2: Best (Knuth-Morris-Pratt, KMP)
# ============================================================
# Idea: precompute needle's LPS (longest-proper-prefix-that-is-also-suffix)
# table so that on a mismatch we know exactly how far the needle can slide
# without re-checking characters already confirmed to match — the haystack
# pointer then never needs to move backward.
# Dry run: needle="aab" -> lps = [0,1,0]
#   (lps[0]=0 always; lps[1]: prefix "a" vs suffix "a" of "aa" -> match len 1;
#    lps[2]: "aab" has no proper prefix==suffix -> 0)
#   haystack="aaab", needle="aab":
#     i=0 j=0 'a'=='a' -> i=1,j=1
#     i=1 j=1 'a'=='a' -> i=2,j=2
#     i=2 j=2 'a'!='b' -> mismatch, j>0 so j=lps[1]=1 (don't move i back)
#     i=2 j=1 'a'=='a' -> i=3,j=2
#     i=3 j=2 'b'=='b' -> i=4,j=3=len(needle) -> match found at i-j=1
# Time:  O(n+m) — O(m) to build the LPS table, O(n) to scan haystack once
# Space: O(m) — the LPS table
def solve_best(haystack: str, needle: str) -> int:
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0
    if m > n:
        return -1

    # Build the LPS (failure function) table for needle.
    lps = [0] * m
    length = 0  # length of the current matching proper prefix/suffix
    k = 1
    while k < m:
        if needle[k] == needle[length]:
            length += 1
            lps[k] = length
            k += 1
        elif length > 0:
            length = lps[length - 1]
        else:
            lps[k] = 0
            k += 1

    # Scan haystack using the LPS table to skip redundant comparisons.
    i = j = 0
    while i < n:
        if haystack[i] == needle[j]:
            i += 1
            j += 1
            if j == m:
                return i - j
        elif j > 0:
            j = lps[j - 1]
        else:
            i += 1
    return -1


# ============================================================
# Key Takeaways
# ============================================================
# - The naive O(n*m) scan re-derives information it already had after every
#   mismatch; KMP's core trick is preprocessing the pattern so a mismatch
#   tells you exactly how far to slide forward instead of restarting.
# - Common mistake: in the LPS table build, forgetting that on a mismatch
#   you fall back via `length = lps[length - 1]` (not reset to 0 directly)
#   so partial progress from an earlier prefix isn't thrown away needlessly.
# - Related/variant problems to try next: Shortest Palindrome (also uses
#   KMP's LPS table), Repeated Substring Pattern, Longest Happy Prefix.


if __name__ == "__main__":
    tests = [
        (("sadbutsad", "sad"), 0),
        (("leetcode", "leeto"), -1),
        (("hello", "ll"), 2),
        (("a", "a"), 0),
        (("mississippi", "issip"), 4),
        (("aaaaa", "bba"), -1),
        (("aaa", "aaaa"), -1),
        (("abc", ""), 0),
    ]

    approaches = [solve_brute_force, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
