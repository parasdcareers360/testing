# Hard — Distinct Subsequences

**Source**: LeetCode #115
**Pattern**: Dynamic Programming — 2D (Grid / Two Sequences)
**Difficulty**: Hard

## Problem Statement
Given two strings `s` and `t`, return the number of distinct subsequences of `s` which equal `t`.

The test cases are generated so that the answer fits in a 32-bit integer.

A subsequence of a string is a new string formed from the original string by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters (i.e., `"ACE"` is a subsequence of `"ABCDE"` while `"AEC"` is not).

## Constraints
- `1 <= s.length, t.length <= 1000`
- `s` and `t` consist of English letters.

## Examples
1. Input: `s = "rabbbit", t = "rabbit"` -> Output: `3`
   Explanation: There are 3 ways to remove characters from `s` (removing exactly one of the three `b`'s in `"rabbbit"`, keeping two) so that the remaining string equals `"rabbit"`: `ra**b**b_bit -> rabbit` picking b's at different positions gives 3 distinct index-choices, all producing `"rabbit"`.
2. Input: `s = "babgbag", t = "bag"` -> Output: `5`
   Explanation: There are 5 distinct index-subsequences of `s` that spell out `"bag"`.

## Intuition — Why This Pattern
**Brute force**: Recursively decide, for each character of `s`, whether to "use" it to match the current character of `t` or skip it, backtracking over all `2^|s|` subsets of `s` and checking whether each equals `t`. This is astronomically slow and also re-derives the same `(i, j)` — "how many ways to match `t[j:]` using `s[i:]`" — state over and over.

**What's inefficient**: The sub-problem "number of ways to form `t[j:]` from `s[i:]`" depends only on the pair of remaining suffixes `(i, j)`, never on the specific characters already consumed. Since `s` and `t` are the two sequences being compared position by position, this is exactly the shape of a two-sequence 2D DP problem — but unlike LCS (which takes a `max`), here we need to **sum** over choices, because we're counting distinct ways, not just checking feasibility or optimizing one quantity.

**Insight — the state**: Define `dp[i][j]` = number of distinct subsequences of `s[0:i]` (the first `i` characters of `s`) that equal `t[0:j]` (the first `j` characters of `t`).

- If `s[i-1] == t[j-1]`, the last character of `s`'s prefix can either be **used** to match the last character of `t`'s prefix (contributing `dp[i-1][j-1]` ways), or **ignored** entirely (contributing `dp[i-1][j]` ways, i.e., still trying to match all of `t[0:j]` using only `s[0:i-1]`). Both are valid, so we **add** them: `dp[i][j] = dp[i-1][j-1] + dp[i-1][j]`.
- If `s[i-1] != t[j-1]`, we cannot use `s[i-1]` to match `t[j-1]`, so the only option is to ignore it: `dp[i][j] = dp[i-1][j]`.

This "hard" twist relative to standard 2D grid/two-sequence DP (like LCS) is that the recurrence **counts** (sums branches) rather than optimizes (takes max/min), and the base case `dp[i][0] = 1` (there is exactly one way to form the empty string — delete everything) is easy to get wrong.

## Approach
1. Let `m = len(s)`, `n = len(t)`. If `n > m`, the answer is immediately `0` (can't form a longer string as a subsequence of a shorter one) — optional early exit, the DP handles it correctly anyway.
2. Create a `(m+1) x (n+1)` table `dp` where `dp[i][j]` = number of ways `s[0:i]` produces `t[0:j]` as a subsequence.
3. Base cases:
   - `dp[i][0] = 1` for all `i` from `0` to `m` (the empty target string can always be formed exactly one way — by deleting everything).
   - `dp[0][j] = 0` for all `j` from `1` to `n` (a non-empty target can never be formed from an empty source).
4. Fill the table for `i` from `1` to `m`, `j` from `1` to `n`:
   - If `s[i-1] == t[j-1]`: `dp[i][j] = dp[i-1][j-1] + dp[i-1][j]`
   - Else: `dp[i][j] = dp[i-1][j]`
5. Return `dp[m][n]`.
6. (Space optimization) Since row `i` only depends on row `i-1`, roll the table down to a single 1D array of length `n+1`, iterating `j` from high to low within each row so `dp[j-1]` (needed as the *old*, row-`i-1` value) isn't overwritten before use — this mirrors the 0/1 knapsack "iterate backwards" trick.

## Dry Run
Example: `s = "rabbbit"`, `t = "rabbit"` (`m = 7`, `n = 6`). Expected output: `3`.

Index `s`: r(1) a(2) b(3) b(4) b(5) i(6) t(7)
Index `t`: r(1) a(2) b(3) b(4) i(5) t(6)

Row 0 (`i=0`): `[1, 0, 0, 0, 0, 0, 0]` (dp[0][0]=1, rest 0).

Build row by row (columns j=0..6 correspond to t-prefixes "", r, ra, rab, rabb, rabbi, rabbit):

```
i=0 ("")     : 1 0 0 0 0 0 0
i=1 ("r")    : 1 1 0 0 0 0 0
i=2 ("ra")   : 1 1 1 0 0 0 0
i=3 ("rab")  : 1 1 1 1 0 0 0
i=4 ("rabb") : 1 1 1 2 1 0 0
i=5 ("rabbb"): 1 1 1 3 3 0 0
i=6 ("rabbbi"):1 1 1 3 3 3 0
i=7 ("rabbbit"):1 1 1 3 3 3 3
```

Key transitions:
- Row `i=4` ("rabb"), `s[3]='b'` matches `t[3]='b'` (j=4, "rabb"): `dp[4][4] = dp[3][3] + dp[3][4] = 1 + 0 = 1`. Also `dp[4][3]`("rab") : `s[3]='b'` matches `t[2]='b'`(j=3): `dp[4][3] = dp[3][2] + dp[3][3] = 1+1=2`.
- Row `i=5` ("rabbb"), `s[4]='b'` matches `t[3]='b'`(j=4): `dp[5][4] = dp[4][3] + dp[4][4] = 2 + 1 = 3`.
- Row `i=6` ("rabbbi"), `s[5]='i'` matches `t[4]='i'`(j=5): `dp[6][5] = dp[5][4] + dp[5][5] = 3 + 0 = 3`.
- Row `i=7` ("rabbbit"), `s[6]='t'` matches `t[5]='t'`(j=6): `dp[7][6] = dp[6][5] + dp[6][6] = 3 + 0 = 3`.

Final answer: `dp[7][6] = 3`, matching the expected output.

## Solution (Python 3)
```python
def num_distinct(s: str, t: str) -> int:
    m, n = len(s), len(t)
    if n > m:
        return 0

    # dp[i][j] = number of ways s[:i] forms t[:j] as a subsequence
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = 1  # empty target: exactly one way (delete everything)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j]

    return dp[m][n]


if __name__ == "__main__":
    print(num_distinct("rabbbit", "rabbit"))  # Expected: 3
    print(num_distinct("babgbag", "bag"))     # Expected: 5
```

## Complexity Analysis
- Time: O(m * n) — every cell of the table is computed exactly once with O(1) work.
- Space: O(m * n) for the full table; reducible to O(n) with a rolling 1D array (iterating `j` from `n` down to `1` per row).

## Key Takeaways
- The key generalization from LCS-style problems: when a problem asks "how many ways" instead of "what's the best/longest", the recurrence **sums** the branches (`dp[i-1][j-1] + dp[i-1][j]`) instead of taking `max`/`min` — same table shape, different combination operator.
- Common mistake: setting `dp[0][j] = 1` for all `j` (copying the "one way to reach empty" base case to the wrong axis) — only `dp[i][0]` should be 1; `dp[0][j>0]` must be 0.
- Watch for integer overflow in other languages (not an issue in Python, but the LeetCode constraints call it out because the count can grow combinatorially large).
- Related/variant problems to try next: **Interleaving String** (LeetCode #97, two-sequence 2D DP with a boolean "can we build this interleaving" recurrence) and **Edit Distance** (LeetCode #72, same table shape, minimizing operation count instead of counting subsequences).
