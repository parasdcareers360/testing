# Easy — Implement strStr()

**Source**: LeetCode #28 (Find the Index of the First Occurrence in a String)
**Pattern**: String Matching (KMP)
**Difficulty**: Easy

## Problem Statement
Given two strings `haystack` and `needle`, return the index of the first occurrence of `needle` in `haystack`, or `-1` if `needle` is not part of `haystack`.

## Constraints
- `1 <= haystack.length, needle.length <= 10^4`
- `haystack` and `needle` consist of only lowercase English characters.

## Examples
**Example 1**
Input: `haystack = "sadbutsad"`, `needle = "sad"`
Output: `0`
Explanation: `"sad"` occurs starting at index 0 and again at index 6, but the first occurrence's index is `0`.

**Example 2**
Input: `haystack = "leetcode"`, `needle = "leeto"`
Output: `-1`
Explanation: `"leeto"` does not appear as a substring of `"leetcode"` (it matches `"leet"` then fails on `o` vs `c`).

## Intuition — Why This Pattern
The brute-force approach tries every starting position `i` in `haystack` and, for each one, compares up to `len(needle)` characters to see if they match. That's `O(n*m)` time where `n = len(haystack)`, `m = len(needle)`. For `n, m` up to `10^4` this is `10^8` in the worst case (e.g. `haystack = "aaaa...a"`, `needle = "aaa...b"`) — borderline, and exactly the kind of pathological case string-matching algorithms are designed to eliminate entirely.

The inefficiency: when a match attempt fails partway through (say after matching `k` characters of `needle`), brute force throws away all that information and restarts the next attempt from scratch at `i+1`, re-comparing characters it has effectively already seen.

The Knuth-Morris-Pratt (KMP) insight: precompute, for the `needle` alone, a **failure function** (a.k.a. LPS array — "Longest proper Prefix which is also a Suffix") that tells you, the moment a mismatch occurs at some position `j` in `needle`, exactly how far back in `needle` you can jump to *without* re-scanning `haystack` — because the prefix of `needle` you already matched has internal structure that guarantees a partial re-match is possible. This lets you scan `haystack` left-to-right exactly once, achieving `O(n + m)` total time.

## Approach
1. **Handle trivial case**: if `needle` is empty, return `0` (not needed here since `needle.length >= 1`, but a common real-world guard).
2. **Build the LPS array** for `needle` (length `m`):
   - `lps[0] = 0`.
   - Maintain `length = 0` (length of the current matched prefix-suffix) and iterate `i` from `1` to `m-1`:
     - While `length > 0` and `needle[i] != needle[length]`, fall back: `length = lps[length - 1]`.
     - If `needle[i] == needle[length]`, increment `length`.
     - Set `lps[i] = length`.
3. **Scan `haystack`** with two pointers: `i` (haystack index) and `j` (needle index, starts at 0):
   - While `i < n`:
     - If `haystack[i] == needle[j]`: increment both `i` and `j`.
       - If `j == m`, a full match ends at `i - 1`; return `i - m` (start index).
     - Else if `j > 0`: fall back `j = lps[j - 1]` (do **not** advance `i`).
     - Else (`j == 0` and mismatch): advance `i` only.
4. If the loop finishes without `j` ever reaching `m`, return `-1`.

## Dry Run
Input: `haystack = "sadbutsad"`, `needle = "sad"`

**Build LPS for `"sad"`**:
- `lps[0] = 0`.
- `i=1`: `needle[1]='a'` vs `needle[length=0]='s'` → mismatch, `length` stays 0 → `lps[1] = 0`.
- `i=2`: `needle[2]='d'` vs `needle[length=0]='s'` → mismatch → `lps[2] = 0`.
- `lps = [0, 0, 0]`.

**Scan `haystack`** (`i` over haystack, `j` over needle):
| i | haystack[i] | j | needle[j] | action |
|---|---|---|---|---|
| 0 | s | 0 | s | match → i=1, j=1 |
| 1 | a | 1 | a | match → i=2, j=2 |
| 2 | d | 2 | d | match → i=3, j=3 → j==m=3 → **found!** |

Return `i - m = 3 - 3 = 0`. ✅ matches Example 1.

## Solution (Python 3)
```python
def build_lps(pattern: str) -> list:
    m = len(pattern)
    lps = [0] * m
    length = 0
    for i in range(1, m):
        while length > 0 and pattern[i] != pattern[length]:
            length = lps[length - 1]
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    return lps


def str_str(haystack: str, needle: str) -> int:
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0

    lps = build_lps(needle)
    i = j = 0
    while i < n:
        if haystack[i] == needle[j]:
            i += 1
            j += 1
            if j == m:
                return i - m
        elif j > 0:
            j = lps[j - 1]
        else:
            i += 1

    return -1


if __name__ == "__main__":
    print(str_str("sadbutsad", "sad"))    # Expected: 0
    print(str_str("leetcode", "leeto"))   # Expected: -1
    print(str_str("aaaaa", "bba"))        # Expected: -1
    print(str_str("mississippi", "issip"))# Expected: 4
```

## Complexity Analysis
- Time: `O(n + m)` — `O(m)` to build the LPS array, `O(n)` to scan `haystack` once (each character is visited a bounded number of times due to the failure-function fallback).
- Space: `O(m)` for the LPS array.

## Key Takeaways
- The LPS/failure array is the reusable core of KMP — once you can build it correctly, it powers substring search, "shortest palindrome," and "longest happy prefix" problems alike.
- Common mistake: advancing `i` when falling back `j` — only fall back `j`; `i` only advances on a match or when `j` is already `0` and a mismatch occurs.
- `i` never needs to move backward in `haystack` — that "never rescan haystack" property is exactly what gives KMP its linear time guarantee over brute force's quadratic worst case.
- Related/variant problems to try next: **Repeated Substring Pattern** (LC 459), **Shortest Palindrome** (LC 214).
