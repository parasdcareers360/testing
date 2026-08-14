# Medium — Longest Palindromic Subsequence

**Source**: LeetCode #516
**Pattern**: Dynamic Programming — Interval / Range
**Difficulty**: Medium

## Problem Statement
Given a string `s`, find the length of the longest palindromic **subsequence** in `s`.

A subsequence is a sequence that can be derived from the original string by deleting some (possibly zero) characters without disturbing the relative order of the remaining characters. Unlike a substring, a subsequence does not need to be contiguous.

## Constraints
- `1 <= s.length <= 1000`
- `s` consists only of lowercase English letters.

## Examples
1. Input: `s = "bbbab"` -> Output: `4`
   Explanation: One possible longest palindromic subsequence is `"bbbb"` (drop the 'a'), which has length 4.
2. Input: `s = "cbbd"` -> Output: `2`
   Explanation: One possible longest palindromic subsequence is `"bb"`, which has length 2.

## Intuition — Why This Pattern
**Brute force**: Enumerate all `2^n` subsequences of `s`, check which ones are palindromes, and track the longest. Completely infeasible for `n` up to 1000.

**What's inefficient**: Whether the best palindromic subsequence within a range `[i, j]` uses both endpoints, one endpoint, or neither only depends on the *range* `[i, j]` itself and its smaller sub-ranges — not on how we happened to explore it. Just like the "easy" substring version, this has overlapping sub-ranges, but now with an added twist.

**The twist vs. the easy (substring) version**: In the substring problem, `dp[i][j]` was a boolean ("is this exact range a palindrome"), and characters had to be *contiguous* and *both* match at the endpoints to extend the answer. Here, since we allow skipping characters (a true subsequence, not a substring), `dp[i][j]` must instead be a **length** (an optimization value, not a yes/no), and at each step we have **three options** instead of a strict boolean check: use both endpoints if they match, or drop the left endpoint, or drop the right endpoint — taking whichever gives the longer result. This turns the recurrence from a simple boolean propagation into a genuine max-based interval DP.

**State**: `dp[i][j]` = length of the longest palindromic subsequence within `s[i..j]` (inclusive).

- If `s[i] == s[j]`: both endpoints can be included in the palindrome, wrapping around whatever palindromic subsequence exists strictly inside: `dp[i][j] = dp[i+1][j-1] + 2` (the `+2` accounts for matching `s[i]` and `s[j]`; if `i+1 > j-1` — i.e., the range had length 1 or 2 — treat `dp[i+1][j-1]` as `0`).
- If `s[i] != s[j]`: we cannot use both endpoints together, so the best is the better of dropping the left character or dropping the right character: `dp[i][j] = max(dp[i+1][j], dp[i][j-1])`.

## Approach
1. Let `n = len(s)`. Create a 2D table `dp` of size `n x n`, where `dp[i][j]` = longest palindromic subsequence length within `s[i..j]`.
2. Base case: every single character is a palindrome of length 1: `dp[i][i] = 1` for all `i`.
3. Build up by increasing range length `L` from `2` to `n`. For each starting index `i` with ending index `j = i + L - 1`:
   - If `s[i] == s[j]`:
     `dp[i][j] = (dp[i+1][j-1] if i+1 <= j-1 else 0) + 2`
   - Else:
     `dp[i][j] = max(dp[i+1][j], dp[i][j-1])`
4. Return `dp[0][n-1]`.

As with all interval DP, ranges must be processed strictly in order of increasing length, because `dp[i][j]` reads from smaller ranges `dp[i+1][j-1]`, `dp[i+1][j]`, `dp[i][j-1]` — all of which must already be finalized.

## Dry Run
Example: `s = "bbbab"` (`n = 5`, indices: b=0, b=1, b=2, a=3, b=4). Expected output: `4`.

**Base case (length 1)**: `dp[i][i] = 1` for all `i` (0..4).

**Length 2**:
- `dp[0][1]`: s[0]='b', s[1]='b' -> equal -> `dp[0][1] = 0 + 2 = 2` (inner range empty since i+1=1 > j-1=0).
- `dp[1][2]`: s[1]='b', s[2]='b' -> equal -> `dp[1][2] = 2`.
- `dp[2][3]`: s[2]='b', s[3]='a' -> not equal -> `dp[2][3] = max(dp[3][3], dp[2][2]) = max(1,1) = 1`.
- `dp[3][4]`: s[3]='a', s[4]='b' -> not equal -> `dp[3][4] = max(dp[4][4], dp[3][3]) = max(1,1) = 1`.

**Length 3**:
- `dp[0][2]`: s[0]='b', s[2]='b' -> equal -> `dp[0][2] = dp[1][1] + 2 = 1 + 2 = 3`.
- `dp[1][3]`: s[1]='b', s[3]='a' -> not equal -> `dp[1][3] = max(dp[2][3], dp[1][2]) = max(1, 2) = 2`.
- `dp[2][4]`: s[2]='b', s[4]='b' -> equal -> `dp[2][4] = dp[3][3] + 2 = 1 + 2 = 3`.

**Length 4**:
- `dp[0][3]`: s[0]='b', s[3]='a' -> not equal -> `dp[0][3] = max(dp[1][3], dp[0][2]) = max(2, 3) = 3`.
- `dp[1][4]`: s[1]='b', s[4]='b' -> equal -> `dp[1][4] = dp[2][3] + 2 = 1 + 2 = 3`.

**Length 5**:
- `dp[0][4]`: s[0]='b', s[4]='b' -> equal -> `dp[0][4] = dp[1][3] + 2 = 2 + 2 = 4`.

Final answer: `dp[0][4] = 4`, matching expected output. (This corresponds to the subsequence `"bbbb"` — positions 0,1,2,4.)

## Solution (Python 3)
```python
def longest_palindromic_subsequence(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0

    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = 1

    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                inner = dp[i + 1][j - 1] if i + 1 <= j - 1 else 0
                dp[i][j] = inner + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])

    return dp[0][n - 1]


if __name__ == "__main__":
    print(longest_palindromic_subsequence("bbbab"))  # Expected: 4
    print(longest_palindromic_subsequence("cbbd"))    # Expected: 2
```

## Complexity Analysis
- Time: O(n^2) — the table has `n^2` cells, each filled in O(1) work.
- Space: O(n^2) for the DP table (can be reduced to O(n) with careful diagonal-order iteration, but the full table is clearer pedagogically).

## Key Takeaways
- The key generalization from the substring version: when characters can be *skipped* (true subsequence) rather than required to be contiguous, the DP state becomes a **length to maximize** with three candidate transitions, not a boolean propagated from one fixed rule.
- Common mistake: forgetting to guard the `i+1 > j-1` case (ranges of length 1 or 2) when computing `dp[i+1][j-1]` — this would index into an invalid or wrongly-ordered range if not handled (e.g., accessing `dp[i+1][j-1]` when `i+1 > j-1` should conceptually be treated as `0`, not skipped or errored).
- This problem is equivalent to computing the Longest Common Subsequence between `s` and its reverse — `LCS(s, reverse(s))` — which is a common alternate implementation and a useful sanity check.
- Related/variant problems to try next: **Minimum Insertions to Make a String Palindrome** (LeetCode #1312, `n - longest_palindromic_subsequence(s)`) and **Longest Palindromic Substring** (LeetCode #5, the easier boolean/contiguous variant of this same interval-DP idea).
