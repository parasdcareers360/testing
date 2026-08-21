"""
LeetCode Top Interview 150 — #145 (LeetCode #5)
Longest Palindromic Substring
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given a string `s`, return the longest palindromic substring of `s`.

Constraints
-----------
- 1 <= s.length <= 1000
- s consists of only digits and English letters.

Examples
--------
Example 1:
    Input: s = "babad"
    Output: "bab"
    Explanation: "aba" is also a valid answer.

Example 2:
    Input: s = "cbbd"
    Output: "bb"

Intuition
---------
The brute force checks every one of the O(n^2) substrings and tests each for being a palindrome
in O(n) time, for O(n^3) total — wasteful because "is s[i..j] a palindrome" overlaps heavily with
"is s[i+1..j-1] a palindrome". That overlap is exactly what DP exploits: s[i..j] is a palindrome
iff s[i] == s[j] AND s[i+1..j-1] is a palindrome (or the inner substring has length <= 1). Filling
a 2D table dp[i][j] by increasing substring length turns each check into O(1), for O(n^2) total.
The best approach flips the question around: instead of asking "is this substring a palindrome?"
for every (i, j) pair, pick every possible *center* (there are 2n-1 of them, including between
characters for even-length palindromes) and expand outward while the two sides match. This does
the same O(n^2) worst-case work but needs no O(n^2) table at all — O(1) extra space — and in
practice terminates early on non-matching centers, which is why it's the approach most interviewers
and production code prefer despite sharing the same asymptotic time bound as the DP table.
"""


# ============================================================
# Approach 1: Brute Force (check every substring)
# ============================================================
# Idea: for every (i, j) pair, slice out s[i:j+1] and check if it reads the
# same forwards and backwards; track the longest one found.
# Time:  O(n^3) — O(n^2) substrings, O(n) to check each
# Space: O(1) extra (ignoring the substring slices themselves)
def solve_brute_force(s: str) -> str:
    n = len(s)
    best = s[0:1]
    for i in range(n):
        for j in range(i, n):
            candidate = s[i:j + 1]
            if candidate == candidate[::-1] and len(candidate) > len(best):
                best = candidate
    return best


# ============================================================
# Approach 2: Better (2D DP table)
# ============================================================
# Idea: dp[i][j] = True iff s[i..j] is a palindrome. Base cases: every
# single character (length 1) is a palindrome, and dp[i][i+1] depends only
# on s[i] == s[i+1]. Fill by increasing substring length so dp[i+1][j-1]
# (a shorter, already-known substring) is always ready when needed.
# Time:  O(n^2) — n^2 table entries, O(1) work each
# Space: O(n^2) — the dp table
def solve_dp_table(s: str) -> str:
    n = len(s)
    if n < 2:
        return s
    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 1
    for i in range(n):
        dp[i][i] = True

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] != s[j]:
                continue
            if length == 2 or dp[i + 1][j - 1]:
                dp[i][j] = True
                if length > max_len:
                    start, max_len = i, length
    return s[start:start + max_len]


# ============================================================
# Approach 3: Best (expand around center)
# ============================================================
# Idea: every palindrome has a center — either a single character (odd
# length) or the gap between two characters (even length). Try all 2n-1
# centers, expanding left/right while the characters match, and keep the
# longest span found. No auxiliary table needed at all.
# Dry run: s="babad"
#   center i=0 ('b'): expands to "b" (len 1)
#   center i=1 ('a'): expands to "bab" (len 3, matches s[0]==s[2]=='b')
#   center i=2 ('b'): expands to "aba" (len 3) - tie, first found ("bab") kept
#   center i=3 ('a'): expands to "ada"? s[2..4]="bad"[2]='b' no -> "a" (len1)... (etc)
#   best remains "bab" (len 3)
# Time:  O(n^2) worst case (e.g. "aaaa...a"), but expansions stop early on
#        mismatches in practice
# Space: O(1) extra — no table, just index bookkeeping
def solve_best(s: str) -> str:
    if len(s) < 2:
        return s

    def expand(left: int, right: int) -> tuple:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        # loop overshoots by one on both sides; the valid palindrome is (left+1, right-1)
        return left + 1, right - 1

    start, end = 0, 0
    for center in range(len(s)):
        l1, r1 = expand(center, center)      # odd-length palindrome centered at `center`
        if r1 - l1 > end - start:
            start, end = l1, r1
        l2, r2 = expand(center, center + 1)  # even-length palindrome centered between chars
        if r2 - l2 > end - start:
            start, end = l2, r2
    return s[start:end + 1]


# ============================================================
# Key Takeaways
# ============================================================
# - "Is s[i..j] a palindrome" reduces to "does s[i]==s[j] and is s[i+1..j-1]
#   a palindrome" — the same shrink-the-interval overlap that drives most
#   substring/subsequence DP problems.
# - Expand-around-center matches the DP table's O(n^2) worst-case time but
#   drops the O(n^2) space to O(1), and is usually faster in practice since
#   most centers terminate expansion almost immediately — that's why it's
#   generally preferred over building the full DP table.
# - Common mistake: forgetting even-length palindromes (centers *between*
#   characters, not just *on* a character) — "bb" has no single-character
#   center.
# - Related/variant problems to try next: Palindromic Substrings (count
#   instead of longest), Longest Palindromic Subsequence, Palindrome
#   Partitioning.


if __name__ == "__main__":
    tests = [
        (("babad",), {"bab", "aba"}),
        (("cbbd",), {"bb"}),
        (("a",), {"a"}),
        (("ac",), {"a", "c"}),
        (("forgeeksskeegfor",), {"geeksskeeg"}),
        (("aaaa",), {"aaaa"}),
    ]

    approaches = [solve_brute_force, solve_dp_table, solve_best]
    for args, expected_set in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result in expected_set else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:25s} -> {result!r:20s}  [{status}]")
