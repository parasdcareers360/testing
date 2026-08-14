# Easy — Longest Palindromic Substring

**Source**: LeetCode #5
**Pattern**: Dynamic Programming — Interval / Range
**Difficulty**: Easy

## Problem Statement
Given a string `s`, return the longest substring of `s` that is a palindrome (reads the same forwards and backwards). A substring must be made of contiguous characters.

If there are multiple longest palindromic substrings, return any one of them.

## Constraints
- `1 <= s.length <= 1000`
- `s` consists of only digits and English letters.

## Examples
1. Input: `s = "babad"` -> Output: `"bab"` (or `"aba"`, both are valid answers of length 3)
   Explanation: Both `"bab"` and `"aba"` are palindromic substrings of length 3, and no longer palindrome exists.
2. Input: `s = "cbbd"` -> Output: `"bb"`
   Explanation: `"bb"` is a palindrome of length 2; no palindromic substring of length 3 or more exists.

## Intuition — Why This Pattern
**Brute force**: Check every possible substring `s[i:j+1]` (there are `O(n^2)` of them) for being a palindrome, which itself takes `O(n)` per check by comparing characters from both ends inward. Total: `O(n^3)`.

**What's inefficient**: Whether `s[i:j+1]` is a palindrome depends entirely on whether `s[i] == s[j]` **and** whether the *inner* substring `s[i+1:j]` is itself a palindrome. Brute force re-checks that inner substring's palindrome status from scratch every time it's needed as part of a larger check, instead of reusing a previously computed answer.

**Insight — the state**: This is the signature setup for interval/range DP: define

`dp[i][j]` = `True` if the substring `s[i..j]` (inclusive on both ends) is a palindrome, else `False`.

The recurrence builds from **smaller ranges up to larger ranges**: a range `[i, j]` is a palindrome exactly when its two endpoints match (`s[i] == s[j]`) and the strictly smaller inner range `[i+1, j-1]` is also a palindrome (or the inner range is empty/single-character, which is always trivially a palindrome). This "combine smaller intervals into a verdict about a bigger interval" structure is exactly what defines interval DP, distinguishing it from the two-index-into-two-different-sequences shape of 2D grid DP.

## Approach
1. Let `n = len(s)`. Create a 2D boolean table `dp` of size `n x n`, where `dp[i][j]` means "`s[i..j]` is a palindrome."
2. Base cases:
   - Every single character is a palindrome: `dp[i][i] = True` for all `i`.
   - Two consecutive equal characters form a palindrome: `dp[i][i+1] = True` if `s[i] == s[i+1]`.
3. Build up by increasing substring length `L` from `3` to `n`:
   For each starting index `i` (with ending index `j = i + L - 1` still within bounds):
   `dp[i][j] = True` if `s[i] == s[j]` **and** `dp[i+1][j-1]` is `True`.
4. Track the best `(start, length)` seen whenever `dp[i][j]` becomes `True` and `j - i + 1` exceeds the current best length.
5. Return `s[best_start : best_start + best_length]`.

## Dry Run
Example: `s = "babad"` (`n = 5`, indices 0..4: b=0, a=1, b=2, a=3, d=4). Expected output: `"bab"` (length 3, starting at index 0).

**Base cases (length 1)**: `dp[0][0]=dp[1][1]=dp[2][2]=dp[3][3]=dp[4][4] = True`. Best so far: length 1, e.g. `"b"`.

**Length 2**: check each adjacent pair:
- `dp[0][1]`: s[0]='b', s[1]='a' -> not equal -> False
- `dp[1][2]`: s[1]='a', s[2]='b' -> not equal -> False
- `dp[2][3]`: s[2]='b', s[3]='a' -> not equal -> False
- `dp[3][4]`: s[3]='a', s[4]='d' -> not equal -> False

No length-2 palindromes found. Best remains length 1.

**Length 3**: for each `i`, `j = i+2`, check `s[i]==s[j]` and `dp[i+1][j-1]` (a single character, always True):
- `dp[0][2]`: s[0]='b', s[2]='b' -> equal, and `dp[1][1]=True` -> `dp[0][2] = True`. Substring `s[0:3] = "bab"`. New best: length 3, `"bab"`.
- `dp[1][3]`: s[1]='a', s[3]='a' -> equal, and `dp[2][2]=True` -> `dp[1][3] = True`. Substring `s[1:4] = "aba"`. Length 3 tie — since we only update on strictly greater length, we keep `"bab"` (found first).
- `dp[2][4]`: s[2]='b', s[4]='d' -> not equal -> False.

**Length 4**: `dp[0][3]`: s[0]='b', s[3]='a' -> not equal -> False. `dp[1][4]`: s[1]='a', s[4]='d' -> not equal -> False.

**Length 5**: `dp[0][4]`: s[0]='b', s[4]='d' -> not equal -> False.

Final best: length 3, starting at index 0 -> `"bab"`. Matches expected output.

## Solution (Python 3)
```python
def longest_palindromic_substring(s: str) -> str:
    n = len(s)
    if n == 0:
        return ""

    dp = [[False] * n for _ in range(n)]
    best_start, best_len = 0, 1

    # length 1: every single character is a palindrome
    for i in range(n):
        dp[i][i] = True

    # length 2
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            if 2 > best_len:
                best_start, best_len = i, 2

    # length 3 and up, building from smaller ranges
    for length in range(3, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                if length > best_len:
                    best_start, best_len = i, length

    return s[best_start: best_start + best_len]


if __name__ == "__main__":
    print(longest_palindromic_substring("babad"))  # Expected: "bab" (or "aba")
    print(longest_palindromic_substring("cbbd"))    # Expected: "bb"
```

## Complexity Analysis
- Time: O(n^2) — the table has `n^2` cells, each filled in O(1).
- Space: O(n^2) for the DP table (can be reduced to O(n) by only keeping the previous two diagonals, but the full table is clearer for beginners).

## Key Takeaways
- Interval DP always iterates by **increasing range length**, because `dp[i][j]` depends on the strictly smaller sub-range `dp[i+1][j-1]`, which must already be finalized.
- Common mistake: iterating `i` and `j` in plain nested loops (`for i in range(n): for j in range(n)`) without ordering by length — this reads `dp[i+1][j-1]` before it has been computed, producing wrong answers.
- The base cases for length-1 and length-2 ranges must be handled explicitly since the general recurrence's "inner range" `dp[i+1][j-1]` doesn't make sense (or is out of bounds) for ranges that small.
- Related/variant problems to try next: **Longest Palindromic Subsequence** (LeetCode #516, same interval-DP shape but allows skipping non-matching characters instead of requiring contiguity) and **Palindromic Substrings** (LeetCode #647, counts *all* palindromic substrings using the same `dp[i][j]` table instead of tracking just the longest).
