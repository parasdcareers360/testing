"""
LeetCode Top Interview 150 — #146 (LeetCode #97)
Interleaving String
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given strings `s1`, `s2`, and `s3`, find whether `s3` is formed by an interleaving of `s1` and
`s2`.

An interleaving of two strings `s` and `t` is a configuration where `s` and `t` are divided into
`n` and `m` substrings respectively, such that:
- s = s_1 + s_2 + ... + s_n
- t = t_1 + t_2 + ... + t_m
- |n - m| <= 1
- The interleaving is s_1 + t_1 + s_2 + t_2 + ... or t_1 + s_1 + t_2 + s_2 + ...

Note: a + b is the concatenation of strings a and b.

Constraints
-----------
- 0 <= s1.length, s2.length <= 100
- 0 <= s3.length <= 200
- s1, s2, and s3 consist of lowercase English letters.

Examples
--------
Example 1:
    Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"
    Output: true

Example 2:
    Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"
    Output: false

Intuition
---------
The key realization: interleaving preserves relative order within each source string, so at any
point in building s3 we've consumed some prefix of s1 (length i) and some prefix of s2 (length j),
with i + j characters of s3 placed so far — the *specific* characters used don't matter, only how
many. That collapses the state space to just (i, j) pairs. Brute-force recursion tries "take the
next char from s1" or "take the next char from s2" at every step and backtracks — correct but
exponential since many different choice sequences land on the same (i, j). Memoizing on (i, j)
fixes that. Bottom-up: dp[i][j] = True iff s3[0:i+j] can be built from s1[0:i] and s2[0:j], which
holds iff (s1[i-1] matches and dp[i-1][j] was True) OR (s2[j-1] matches and dp[i][j-1] was True).
As with the grid-DP problems, row i only depends on row i-1 and the current row's own left
neighbor, so the table compresses to a single rolling 1D array of size len(s2)+1.
"""


# ============================================================
# Approach 1: Brute Force (plain recursion / backtracking)
# ============================================================
# Idea: at each step, try consuming the next char from s1 (if it matches
# the next char of s3) or from s2 (if it matches), recursing on the rest.
# Time:  O(2^(m+n)) — up to two branches at each of m+n steps
# Space: O(m+n) — recursion stack depth
def solve_brute_force(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False

    def helper(i: int, j: int) -> bool:
        if i == m and j == n:
            return True
        k = i + j
        take_s1 = i < m and s1[i] == s3[k] and helper(i + 1, j)
        take_s2 = j < n and s2[j] == s3[k] and helper(i, j + 1)
        return take_s1 or take_s2

    return helper(0, 0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache helper(i, j) — only (m+1)*(n+1) distinct states exist, but
# plain recursion revisits many of them via different interleavings.
# Time:  O(m*n)
# Space: O(m*n) — memo table + recursion stack
def solve_memo(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    memo = {}

    def helper(i: int, j: int) -> bool:
        if i == m and j == n:
            return True
        if (i, j) in memo:
            return memo[(i, j)]
        k = i + j
        take_s1 = i < m and s1[i] == s3[k] and helper(i + 1, j)
        take_s2 = j < n and s2[j] == s3[k] and helper(i, j + 1)
        result = take_s1 or take_s2
        memo[(i, j)] = result
        return result

    return helper(0, 0)


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[i][j] = True iff s3[0:i+j] is an interleaving of s1[0:i] and
# s2[0:j]. dp[0][0] = True (empty + empty = empty). dp[i][j] is reachable
# from dp[i-1][j] (consuming s1[i-1]) or dp[i][j-1] (consuming s2[j-1]),
# whichever's matching character lines up with s3[i+j-1].
# Dry run: s1="aa", s2="ab", s3="aaab" (True)
#   dp[0][0]=T
#   dp[1][0]: s1[0]='a'==s3[0]='a' & dp[0][0] -> T
#   dp[2][0]: s1[1]='a'==s3[1]='a' & dp[1][0] -> T
#   dp[0][1]: s2[0]='a'==s3[0]='a' & dp[0][0] -> T
#   dp[1][1]: s1[0]='a'==s3[1]='a'&dp[0][1]=T -> T  (or s2 branch)
#   dp[2][1]: s1[1]='a'==s3[2]='a'&dp[1][1]=T -> T
#   dp[2][2]: s2[1]='b'==s3[3]='b'&dp[2][1]=T -> T
#   final dp[2][2] = True
# Time:  O(m*n)
# Space: O(m*n) — the dp table
def solve_optimal(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False

    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 and j == 0:
                continue
            from_s1 = i > 0 and s1[i - 1] == s3[i + j - 1] and dp[i - 1][j]
            from_s2 = j > 0 and s2[j - 1] == s3[i + j - 1] and dp[i][j - 1]
            dp[i][j] = from_s1 or from_s2
    return dp[m][n]


# ============================================================
# Approach 4: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: dp[i][j] only depends on dp[i-1][j] (the value directly above,
# still in dp[j] before this row overwrites it) and dp[i][j-1] (the value
# directly to the left, dp[j-1], already updated this row) — one rolling
# array of size n+1, processed left-to-right row by row, is enough.
# Time:  O(m*n)
# Space: O(n) — one rolling row instead of the full (m+1)x(n+1) table
def solve_best(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False

    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, n + 1):
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]

    for i in range(1, m + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            from_s1 = s1[i - 1] == s3[i + j - 1] and dp[j]        # dp[j] still row i-1
            from_s2 = s2[j - 1] == s3[i + j - 1] and dp[j - 1]    # dp[j-1] already row i
            dp[j] = from_s1 or from_s2
    return dp[n]


# ============================================================
# Key Takeaways
# ============================================================
# - The whole trick is realizing the state only needs "how many characters
#   consumed from each source" (i, j), not which specific characters — that
#   collapses an apparent string-matching problem into a 2D grid DP.
# - Common mistake: forgetting the O(1) early exit when len(s1) + len(s2)
#   != len(s3) — without it you either crash on an out-of-range index or
#   waste time on an impossible case.
# - Related/variant problems to try next: Edit Distance, Distinct
#   Subsequences, Longest Common Subsequence.


if __name__ == "__main__":
    tests = [
        (("aabcc", "dbbca", "aadbbcbcac"), True),
        (("aabcc", "dbbca", "aadbbbaccc"), False),
        (("", "", ""), True),
        (("", "b", "b"), True),
        (("a", "", "b"), False),
        (("aa", "ab", "aaab"), True),
        (("abc", "abc", "aabbcc"), True),
        (("abc", "abc", "abcabd"), False),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
