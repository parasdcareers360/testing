"""
LeetCode Top Interview 150 — #147 (LeetCode #72)
Edit Distance
Category: Multidimensional DP | Difficulty: Medium

Problem
-------
Given two strings `word1` and `word2`, return the minimum number of operations required to
convert `word1` to `word2`.

You have the following three operations permitted on a word:
- Insert a character
- Delete a character
- Replace a character

Constraints
-----------
- 0 <= word1.length, word2.length <= 500
- word1 and word2 consist of lowercase English letters.

Examples
--------
Example 1:
    Input: word1 = "horse", word2 = "ros"
    Output: 3
    Explanation: horse -> rorse (replace 'h' with 'r')
                 rorse -> rose (remove 'r')
                 rose -> ros (remove 'e')

Example 2:
    Input: word1 = "intention", word2 = "execution"
    Output: 5

Intuition
---------
Brute-force recursion compares word1[i:] to word2[j:] character by character: if the leading
characters match, advance both pointers for free; otherwise try all three operations (insert,
delete, replace) and take 1 + the best of the three resulting subproblems. This branches into up
to 3 recursive calls per mismatched position, exponential in the worst case, but the number of
*distinct* (i, j) subproblems is only len(word1)*len(word2), so memoizing on (i, j) makes it
polynomial. Bottom-up: dp[i][j] = edit distance between word1[0:i] and word2[0:j]. Base cases are
turning an empty prefix into the other prefix, which costs exactly its length in insertions (or
deletions) — dp[i][0] = i, dp[0][j] = j. Otherwise dp[i][j] = dp[i-1][j-1] if the characters match
(no operation needed), else 1 + min(dp[i-1][j] [delete from word1], dp[i][j-1] [insert into
word1], dp[i-1][j-1] [replace]). As with the other grid DPs, row i only needs row i-1 and the
current row's own left neighbor, so it compresses to a single rolling 1D array.
"""


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: compare word1[i:] vs word2[j:]; if chars match, advance both for
# free; otherwise try insert/delete/replace and take 1 + best of the three.
# Time:  O(3^(m+n)) — up to 3-way branching at each mismatched position
# Space: O(m+n) — recursion stack depth
def solve_brute_force(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)

    def helper(i: int, j: int) -> int:
        if i == m:
            return n - j          # insert the rest of word2
        if j == n:
            return m - i          # delete the rest of word1
        if word1[i] == word2[j]:
            return helper(i + 1, j + 1)
        insert_op = helper(i, j + 1)
        delete_op = helper(i + 1, j)
        replace_op = helper(i + 1, j + 1)
        return 1 + min(insert_op, delete_op, replace_op)

    return helper(0, 0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache helper(i, j) — only (m+1)*(n+1) distinct states exist, but
# plain recursion revisits many of them via different operation sequences.
# Time:  O(m*n)
# Space: O(m*n) — memo table + recursion stack
def solve_memo(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    memo = {}

    def helper(i: int, j: int) -> int:
        if i == m:
            return n - j
        if j == n:
            return m - i
        if (i, j) in memo:
            return memo[(i, j)]
        if word1[i] == word2[j]:
            result = helper(i + 1, j + 1)
        else:
            result = 1 + min(helper(i, j + 1), helper(i + 1, j), helper(i + 1, j + 1))
        memo[(i, j)] = result
        return result

    return helper(0, 0)


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[i][j] = edit distance between word1[0:i] and word2[0:j]. First
# row/column are the "convert from/to empty string" base cases (pure
# insert/delete chains); everywhere else, matching chars carry the
# diagonal value forward for free, mismatches cost 1 + best neighbor.
# Dry run: word1="horse", word2="ros" (answer 3)
#   dp[0] = [0,1,2,3]                      (build "ros" from "")
#   dp[1] ('h'): [1,1,2,3]                 (h vs r,o,s all mismatch except base)
#   dp[2] ('o'): [2,2,1,2]                 (word1[1]='o'==word2[1]='o' -> diagonal)
#   dp[3] ('r'): [3,2,2,2]
#   dp[4] ('s'): [4,3,3,2]
#   dp[5] ('e'): [5,4,4,3]
#   final dp[5][3] = 3
# Time:  O(m*n)
# Space: O(m*n) — the dp table
def solve_optimal(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


# ============================================================
# Approach 4: Best (O(n)-space rolling 1D array)
# ============================================================
# Idea: dp[i][j] only depends on dp[i-1][j] (above), dp[i][j-1] (left, just
# computed this row), and dp[i-1][j-1] (diagonal) — keep one rolling array
# plus a single scalar to remember the diagonal before it's overwritten.
# Time:  O(m*n)
# Space: O(n) — one rolling row instead of the full (m+1)x(n+1) table
def solve_best(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))  # row 0: converting "" -> word2[0:j] costs j inserts

    for i in range(1, m + 1):
        prev_diag = dp[0]      # dp[i-1][0], the diagonal for j=1
        dp[0] = i               # dp[i][0]: converting word1[0:i] -> "" costs i deletes
        for j in range(1, n + 1):
            temp = dp[j]        # save dp[i-1][j] before overwriting (becomes next diagonal)
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev_diag
            else:
                dp[j] = 1 + min(dp[j], dp[j - 1], prev_diag)
            prev_diag = temp
    return dp[n]


# ============================================================
# Key Takeaways
# ============================================================
# - Edit Distance is the canonical "two-string alignment" DP: matching
#   characters glide along the diagonal for free, mismatches cost 1 plus
#   the cheapest of insert/delete/replace neighbors.
# - Common mistake: mixing up which neighbor corresponds to which
#   operation — dp[i-1][j] is delete-from-word1, dp[i][j-1] is
#   insert-into-word1, dp[i-1][j-1] is replace; getting them backwards
#   still often passes small tests by symmetry but fails on asymmetric
#   inputs.
# - Related/variant problems to try next: Longest Common Subsequence,
#   Delete Operation for Two Strings, One Edit Distance.


if __name__ == "__main__":
    tests = [
        (("horse", "ros"), 3),
        (("intention", "execution"), 5),
        (("", ""), 0),
        (("", "abc"), 3),
        (("abc", ""), 3),
        (("abc", "abc"), 0),
        (("a", "b"), 1),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")
