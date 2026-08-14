# Medium — Repeated Substring Pattern

**Source**: LeetCode #459
**Pattern**: String Matching (KMP Failure Function)
**Difficulty**: Medium

## Problem Statement
Given a string `s`, determine if it can be constructed by taking a substring of it and appending multiple copies of that substring together to form the entirety of `s`. In other words, decide whether `s` is a repetition of some smaller (or equal) block of characters, repeated two or more times.

Return `True` if such a substring exists, `False` otherwise.

## Constraints
- `1 <= s.length <= 10^4`
- `s` consists of lowercase English letters only.

## Examples
**Example 1**
Input: `s = "abab"`
Output: `True`
Explanation: `"abab"` is `"ab"` repeated 2 times.

**Example 2**
Input: `s = "aba"`
Output: `False`
Explanation: No substring shorter than `"aba"` itself, repeated an integer number of times, reconstructs `"aba"` (`"a"` repeated 3 times gives `"aaa"`, not `"aba"`; `"ab"`/`"ba"` don't divide evenly or match).

**Example 3**
Input: `s = "abcabcabcabc"`
Output: `True`
Explanation: `"abc"` repeated 4 times (or `"abcabc"` repeated 2 times) reconstructs `s`.

## Intuition — Why This Pattern
The brute-force approach tries every possible block length `L` that divides `len(s)` evenly (there are `O(d(n))` divisors, but naively you might just try every `L` from `1` to `n/2`), and for each candidate `L` checks whether repeating `s[0:L]` exactly `n/L` times reproduces `s` — an `O(n)` check per candidate, giving roughly `O(n^2 / d)` overall. That's acceptable for `n <= 10^4` but doesn't generalize and misses the elegant one-pass insight this pattern is built around; it also requires explicitly enumerating divisors.

The twist that makes this a step up from plain substring search: there's no "needle" given at all — we must discover *whether some repeating block exists* using structural self-information about `s`, not compare `s` against a separate pattern. This is exactly what the KMP failure function (LPS array) captures for free: `lps[n-1]` tells you the length of the longest proper prefix of `s` that is also a suffix of `s`. If `s` is built from a repeating block of length `L`, then everything except the very first block is simultaneously a prefix (the tail end of `s`, shifted) and a suffix (also the tail end) — this forces `lps[n-1] = n - L`, i.e., `L = n - lps[n-1]`.

So instead of trying every candidate length, run the LPS-array builder **once** over the whole string `s` against itself, read off `lps[n-1]`, derive the one candidate period `L = n - lps[n-1]`, and check two conditions: `L` must be a proper divisor of `n` (`L < n` and `n % L == 0`) — if both hold, `s` is exactly `s[0:L]` repeated `n/L` times.

## Approach
1. Compute `n = len(s)`. If `n == 1`, return `False` immediately (a single character can't be "multiple copies" of anything shorter).
2. Build the LPS/failure array for `s` treated as its own pattern (same algorithm as in KMP's preprocessing step):
   - `lps[0] = 0`; maintain `length = 0`.
   - For `i` from `1` to `n-1`: while `length > 0` and `s[i] != s[length]`, set `length = lps[length-1]`; if `s[i] == s[length]`, increment `length`; set `lps[i] = length`.
3. Read `candidate_period = n - lps[n-1]`.
4. Return `True` if `candidate_period < n` and `n % candidate_period == 0`; otherwise return `False`.
   - `candidate_period < n` rules out the degenerate case where `lps[n-1] == 0` (no nontrivial prefix-suffix overlap at all, meaning the only "period" candidate would be the whole string itself — not a repetition of anything *smaller*).
   - `n % candidate_period == 0` ensures the block actually tiles `s` evenly (an integer number of full copies), not just partially.

## Dry Run
Input: `s = "abcabcabcabc"` (n = 12)

**Build LPS**:
- `lps[0] = 0`.
- `i=1`: `s[1]='b'` vs `s[0]='a'` → mismatch → `lps[1]=0`.
- `i=2`: `s[2]='c'` vs `s[0]='a'` → mismatch → `lps[2]=0`.
- `i=3`: `s[3]='a'` vs `s[0]='a'` → match, `length=1` → `lps[3]=1`.
- `i=4`: `s[4]='b'` vs `s[1]='b'` → match, `length=2` → `lps[4]=2`.
- `i=5`: `s[5]='c'` vs `s[2]='c'` → match, `length=3` → `lps[5]=3`.
- `i=6`: `s[6]='a'` vs `s[3]='a'` → match, `length=4` → `lps[6]=4`.
- `i=7`: `s[7]='b'` vs `s[4]='b'` → match, `length=5` → `lps[7]=5`.
- `i=8`: `s[8]='c'` vs `s[5]='c'` → match, `length=6` → `lps[8]=6`.
- `i=9`: `s[9]='a'` vs `s[6]='a'` → match, `length=7` → `lps[9]=7`.
- `i=10`: `s[10]='b'` vs `s[7]='b'` → match, `length=8` → `lps[10]=8`.
- `i=11`: `s[11]='c'` vs `s[8]='c'` → match, `length=9` → `lps[11]=9`.

Final `lps = [0,0,0,1,2,3,4,5,6,7,8,9]`, so `lps[n-1] = lps[11] = 9`.

**Derive period**: `candidate_period = n - lps[11] = 12 - 9 = 3`.

**Check**: `candidate_period (3) < n (12)` ✅, and `n % candidate_period = 12 % 3 = 0` ✅ → return `True`. Indeed `s[0:3] = "abc"` repeated `12/3 = 4` times reconstructs `s`. ✅ matches Example 3.

**Contrast with `s = "aba"`** (n=3): LPS build gives `lps = [0,0,1]` (`s[2]='a'` matches `s[0]='a'`, so `length=1`). `candidate_period = 3 - 1 = 2`. Check: `2 < 3` ✅ but `3 % 2 = 1 != 0` ❌ → return `False`. ✅ matches Example 2.

## Solution (Python 3)
```python
def build_lps(pattern: str) -> list:
    n = len(pattern)
    lps = [0] * n
    length = 0
    for i in range(1, n):
        while length > 0 and pattern[i] != pattern[length]:
            length = lps[length - 1]
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    return lps


def repeated_substring_pattern(s: str) -> bool:
    n = len(s)
    if n <= 1:
        return False

    lps = build_lps(s)
    candidate_period = n - lps[n - 1]

    return candidate_period < n and n % candidate_period == 0


if __name__ == "__main__":
    print(repeated_substring_pattern("abab"))           # Expected: True
    print(repeated_substring_pattern("aba"))            # Expected: False
    print(repeated_substring_pattern("abcabcabcabc"))   # Expected: True
    print(repeated_substring_pattern("a"))              # Expected: False
```

## Complexity Analysis
- Time: `O(n)` — building the LPS array over the string of length `n` is linear (the standard KMP amortized-analysis argument: `length` can only increase up to `n` times total across the whole loop, and each fallback strictly decreases it, so the total work is bounded by `O(n)`).
- Space: `O(n)` for the LPS array.

## Key Takeaways
- `lps[n-1]` (the failure function evaluated at the very last character) encodes deep global structure about the whole string's self-overlap — many "does this string have property X" problems (periodicity, borders, shortest rotation) reduce to reading this one value instead of searching explicitly.
- Common mistake: forgetting the `candidate_period < n` guard — without it, a string with zero self-overlap (`lps[n-1] == 0`) would incorrectly compute `candidate_period = n` and then trivially pass `n % n == 0`, wrongly reporting a string as "repeated" when it isn't built from anything smaller.
- The same LPS array reused here is *exactly* the one used for substring search (Implement strStr()) — building it is a completely reusable subroutine.
- Related/variant problems to try next: **Longest Happy Prefix** (LC 1392, literally returns `s[:lps[n-1]]`), **Shortest Palindrome** (LC 214, LPS on a concatenated string).
