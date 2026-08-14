# Medium — Longest Common Subsequence

**Source**: LeetCode #1143
**Pattern**: Dynamic Programming — 2D (Grid / Two Sequences)
**Difficulty**: Medium

## Problem Statement
Given two strings `text1` and `text2`, return the length of their longest common subsequence. If there is no common subsequence, return `0`.

A **subsequence** of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, `"ace"` is a subsequence of `"abcde"`.

A **common subsequence** of two strings is a subsequence that is common to both strings.

## Constraints
- `1 <= text1.length, text2.length <= 1000`
- `text1` and `text2` consist of only lowercase English characters.

## Examples
1. Input: `text1 = "abcde", text2 = "ace"` -> Output: `3`
   Explanation: The longest common subsequence is `"ace"`, which has length 3.
2. Input: `text1 = "abc", text2 = "abc"` -> Output: `3`
   Explanation: The longest common subsequence is `"abc"`, which has length 3 (the whole string).
3. Input: `text1 = "abc", text2 = "def"` -> Output: `0`
   Explanation: There is no common subsequence between the two strings.

## Intuition — Why This Pattern
**Brute force**: For each pair of positions `(i, j)` in `text1` and `text2`, we could try every possible way of choosing/skipping characters — this is naturally expressed as a recursion: either the two current characters match (and we recurse on both strings shortened by one) or they don't (and we try skipping a character from either string). Without memoization this branches into up to `2^(m+n)` calls, since the same `(i, j)` state is revisited by many different decision paths.

**What's inefficient**: The recursion `lcs(i, j)` — "the LCS length of `text1[i:]` and `text2[j:]`" — depends only on the pair `(i, j)`, not on how we arrived there. Yet brute force recomputes the same `(i, j)` state repeatedly. Classic overlapping-subproblems + optimal-substructure signature -> DP.

**Insight**: Since we have **two sequences** being compared index-by-index, we use a 2D DP table indexed by one position in each string. Define:

`dp[i][j]` = length of the longest common subsequence of `text1[0:i]` and `text2[0:j]` (the first `i` characters of `text1` and first `j` characters of `text2`).

If the characters `text1[i-1]` and `text2[j-1]` match, they can both be part of the LCS, so we extend the LCS found without those two characters: `dp[i][j] = dp[i-1][j-1] + 1`. If they don't match, the best LCS either drops the last character of `text1` or the last character of `text2` (whichever gives a longer result): `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.

## Approach
1. Let `m = len(text1)`, `n = len(text2)`. Create a `(m+1) x (n+1)` table `dp`, where `dp[i][j]` represents the LCS length using the first `i` characters of `text1` and the first `j` characters of `text2`.
2. Base case: `dp[0][j] = 0` for all `j`, and `dp[i][0] = 0` for all `i` (an empty prefix has LCS length 0 with anything).
3. For `i` from `1` to `m`, and for `j` from `1` to `n`:
   - If `text1[i-1] == text2[j-1]`: `dp[i][j] = dp[i-1][j-1] + 1`
   - Else: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`
4. The answer is `dp[m][n]`.
5. (Space optimization) Since row `i` only depends on row `i-1` (and the current row being filled left to right), the table can be compressed to two 1D rows of length `n+1`.

## Dry Run
Example: `text1 = "abcde"`, `text2 = "ace"` (`m = 5`, `n = 3`). Expected output: `3`.

Build a `(6 x 4)` table, rows indexed 0..5 for `text1 = a b c d e`, columns indexed 0..3 for `text2 = a c e`. Row 0 and column 0 are all zero.

```
        ""  a  c  e
    ""   0  0  0  0
    a    0  1  1  1
    b    0  1  1  1
    c    0  1  2  2
    d    0  1  2  2
    e    0  1  2  3
```

Trace key cells:
- `dp[1][1]` (text1[0]='a', text2[0]='a') -> match -> `dp[0][0] + 1 = 1`.
- `dp[1][2]` (text1[0]='a', text2[1]='c') -> no match -> `max(dp[0][2], dp[1][1]) = max(0, 1) = 1`.
- `dp[3][2]` (text1[2]='c', text2[1]='c') -> match -> `dp[2][1] + 1 = 1 + 1 = 2`.
- `dp[5][3]` (text1[4]='e', text2[2]='e') -> match -> `dp[4][2] + 1 = 2 + 1 = 3`.

Final answer: `dp[5][3] = 3`, matching the expected LCS `"ace"`.

## Solution (Python 3)
```python
def longest_common_subsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    # dp[i][j] = LCS length of text1[:i] and text2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


if __name__ == "__main__":
    print(longest_common_subsequence("abcde", "ace"))  # Expected: 3
    print(longest_common_subsequence("abc", "abc"))    # Expected: 3
    print(longest_common_subsequence("abc", "def"))    # Expected: 0
```

## Complexity Analysis
- Time: O(m * n) — one pass filling every cell of the table once.
- Space: O(m * n) for the full table, reducible to O(min(m, n)) with the rolling-row optimization.

## Key Takeaways
- This is the archetypal "two sequences" 2D DP: `dp[i][j]` depends on `dp[i-1][j-1]`, `dp[i-1][j]`, `dp[i][j-1]` — the three neighbors forming an "L" shape above/left of the current cell.
- Common mistake: off-by-one errors between the DP table indices (`1`-based, representing prefix lengths) and the string indices (`0`-based, so `text1[i-1]` not `text1[i]`).
- Many string-comparison DP problems (Edit Distance, Distinct Subsequences, Interleaving String) reuse this exact table shape with a different recurrence at each cell.
- Related/variant problems to try next: **Edit Distance** (LeetCode #72, same table shape but recurrence models insert/delete/replace operations) and **Longest Common Substring** (a variant requiring contiguity, where a mismatch resets `dp[i][j]` to 0 instead of taking a max).
