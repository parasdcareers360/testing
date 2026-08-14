# Hard — Shortest Palindrome

**Source**: LeetCode #214
**Pattern**: String Matching (KMP Failure Function)
**Difficulty**: Hard

## Problem Statement
You are given a string `s`. You may add characters **only in front of** `s` (you cannot add characters anywhere else, and you cannot remove or reorder any existing character). Convert `s` into a palindrome by performing this front-insertion, using as few added characters as possible, and return the resulting shortest palindrome string.

## Constraints
- `0 <= s.length <= 5 * 10^4`
- `s` consists of lowercase English letters only.

## Examples
**Example 1**
Input: `s = "aacecaaa"`
Output: `"aaacecaaa"`
Explanation: The longest prefix of `s` that is already a palindrome is `"aacecaa"` (length 7). The one leftover trailing character is `"a"`; reversing it gives `"a"`, which is prepended to `s` to get `"a" + "aacecaaa" = "aaacecaaa"`, a palindrome, using the minimum possible number of added characters (1).

**Example 2**
Input: `s = "abcd"`
Output: `"dcbabcd"`
Explanation: The longest palindromic prefix of `"abcd"` is just `"a"` (length 1). The remaining suffix `"bcd"`, reversed, is `"dcb"`; prepending it gives `"dcb" + "abcd" = "dcbabcd"`, which reads the same forwards and backwards.

## Intuition — Why This Pattern
The brute-force approach tries, for every possible cut point starting from the longest: is `s[0:k]` (the whole string, then `s[0:n-1]`, then `s[0:n-2]`, ...) a palindrome? The largest `k` for which `s[0:k]` is a palindrome tells you the longest palindromic **prefix**; everything after that prefix (`s[k:]`) must be mirrored and prepended, since it's the part with no palindromic partner already in front of it. Checking "is `s[0:k]` a palindrome" naively costs `O(k)`, and you may need to check up to `O(n)` candidate values of `k`, giving `O(n^2)` overall — too slow for `n` up to `5*10^4` (`2.5*10^9` operations).

The key realization that elevates this beyond a simple two-pointer palindrome check: **finding the longest palindromic prefix of `s` is equivalent to finding the longest prefix of `s` that is also a suffix of `reverse(s)`** — because a string `p` is simultaneously a prefix of `s` and equal to its own reverse exactly when `p` (read from `s`'s front) lines up with `p` reversed (read from `reverse(s)`'s back). That "longest prefix of X that is also a suffix of Y" phrasing is *precisely* what the KMP failure function computes — just build it over the concatenation `s + separator + reverse(s)` (the separator, a character not in the alphabet, prevents the failure function from "seeing across" and falsely matching parts of `s` against parts of `reverse(s)` that shouldn't align at the boundary).

So instead of testing candidate prefixes one at a time, run the LPS-array construction **once** over `combined = s + '#' + reverse(s)`, and read the answer directly off the **last** entry of that array: `lps[-1]` is exactly the length of the longest palindromic prefix of `s`. Everything after that point in `s` gets reversed and prepended. This is the same LPS machinery as "Implement strStr()" and "Repeated Substring Pattern," but applied to a cleverly constructed combined string rather than to `s` directly — the "combine two strings around a separator, then run KMP's preprocessing once" trick is what makes this a hard-tier application of the pattern.

## Approach
1. Handle the trivial case: if `s` is empty or already a palindrome (or has length `<= 1`), return `s` unchanged (0 characters needed) — the general algorithm below also naturally produces this, but it's worth noting as a base case.
2. Compute `rev = reverse(s)`.
3. Build `combined = s + '#' + rev`, using `'#'` (or any character guaranteed absent from `s`) as a separator to block false overlaps across the `s` / `rev` boundary.
4. Build the LPS/failure array for `combined` using the standard KMP preprocessing routine.
5. Let `longest_pal_prefix_len = lps[len(combined) - 1]` — the length of the longest prefix of `combined` that is also a suffix of `combined`, which (thanks to the separator) equals the longest palindromic prefix of `s`.
6. Compute `remainder = s[longest_pal_prefix_len:]` — the suffix of `s` that lies *outside* the palindromic prefix and therefore has no mirror already present.
7. Return `reverse(remainder) + s` — this prepends exactly the missing mirror characters, producing the shortest possible palindrome achievable by front-insertion only.

## Dry Run
Input: `s = "abcd"` (Example 2, chosen for a compact trace)

**Step 1**: `rev = reverse("abcd") = "dcba"`.

**Step 2**: `combined = "abcd" + "#" + "dcba" = "abcd#dcba"` (length 9, indices 0-8: `a b c d # d c b a`).

**Step 3 — build LPS for `combined`** (`length` = running matched prefix length):
| i | combined[i] | comparing to combined[length] | result | lps[i] |
|---|---|---|---|---|
| 0 | a | (base case) | lps[0]=0 | 0 |
| 1 | b | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 2 | c | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 3 | d | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 4 | # | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 5 | d | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 6 | c | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 7 | b | length=0, combined[0]='a' → mismatch | length stays 0 | 0 |
| 8 | a | length=0, combined[0]='a' → **match!** length→1 | | 1 |

Final `lps = [0,0,0,0,0,0,0,0,1]`, so `lps[8] = 1`.

**Step 4**: `longest_pal_prefix_len = 1` → the longest palindromic prefix of `"abcd"` is `"a"` (just the first character — correct, since `"ab"`, `"abc"`, `"abcd"` are none of them palindromes).

**Step 5**: `remainder = s[1:] = "bcd"`.

**Step 6**: `reverse(remainder) = "dcb"`. Return `"dcb" + "abcd" = "dcbabcd"`. ✅ matches Example 2's expected output.

(Sanity check on Example 1 mentally: `s="aacecaaa"`, the longest palindromic prefix is `"aacecaa"` (length 7, itself a palindrome), leaving `remainder = "a"`, so the answer is `reverse("a") + s = "a" + "aacecaaa" = "aaacecaaa"`, matching Example 1.)

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


def shortest_palindrome(s: str) -> str:
    if len(s) <= 1:
        return s

    rev = s[::-1]
    combined = s + '#' + rev
    lps = build_lps(combined)

    longest_pal_prefix_len = lps[-1]
    remainder = s[longest_pal_prefix_len:]

    return remainder[::-1] + s


if __name__ == "__main__":
    print(shortest_palindrome("aacecaaa"))  # Expected: "aaacecaaa"
    print(shortest_palindrome("abcd"))      # Expected: "dcbabcd"
    print(shortest_palindrome(""))          # Expected: ""
    print(shortest_palindrome("a"))         # Expected: "a"
    print(shortest_palindrome("racecar"))   # Expected: "racecar" (already a palindrome)
```

## Complexity Analysis
- Time: `O(n)`, where `n = len(s)`. Building `rev` and `combined` is `O(n)`; building the LPS array over a string of length `2n+1` is linear in its length, i.e., `O(n)`.
- Space: `O(n)` for `rev`, `combined`, and the `lps` array.

## Key Takeaways
- "Longest prefix of A that is also a suffix of B" is a general reduction target — whenever a problem can be rephrased that way, concatenating `A + separator + B` and running one LPS-array build solves it in linear time.
- The separator character is not cosmetic — omitting it (or using a separator that might actually appear in the input) can let the failure function falsely "see through" the boundary and produce a wrong (too-large) prefix-suffix length. Always use a sentinel character guaranteed not to occur in the alphabet.
- Only `lps[-1]` (the very last entry) is needed here — the rest of the array is scaffolding, not the answer itself. It's easy to mistakenly look at `max(lps)` instead, which is a different (and wrong) quantity.
- Related/variant problems to try next: **Longest Happy Prefix** (LC 1392, same LPS-over-`s` idea without the reverse-concatenation trick), **Repeated Substring Pattern** (LC 459, another "read the answer off `lps[-1]`" problem).
