# Medium — Longest Substring Without Repeating Characters

**Source**: LeetCode #3
**Pattern**: Sliding Window
**Difficulty**: Medium

## Problem Statement
Given a string `s`, find the length of the longest substring without repeating characters. A substring is a contiguous sequence of characters within the string.

## Constraints
- `0 <= s.length <= 5 * 10^4`
- `s` consists of English letters, digits, symbols, and spaces (i.e., any printable ASCII / Unicode character may appear).

## Examples
**Example 1**
Input: `s = "abcabcbb"`
Output: `3`
Explanation: The answer is `"abc"`, with a length of 3. Note that `"bca"` and `"cab"` are also valid answers of length 3, but no substring of length 4 or more is repeat-free.

**Example 2**
Input: `s = "bbbbb"`
Output: `1`
Explanation: The answer is `"b"`, with a length of 1.

**Example 3**
Input: `s = "pwwkew"`
Output: `3`
Explanation: The answer is `"wke"`, with a length of 3. Note that `"pwke"` is a subsequence, not a substring (it's not contiguous), so it doesn't count.

## Intuition — Why This Pattern
Unlike the easy version of this pattern, the window size here is **not fixed** — we don't know in advance how long the longest repeat-free substring is. This is the key twist: instead of always sliding by exactly one element on both ends, we need to **expand** the window greedily and **shrink** it only when a duplicate is detected.

**Brute force**: for every possible starting index `i`, extend `j` as far right as possible while all characters in `s[i:j+1]` are unique, tracking the max length found. This is O(n^2) (or O(n^3) if you re-check uniqueness from scratch each time using a set rebuilt every iteration) because for each of the n starting points we may re-scan up to n characters.

The waste: when we move the start of the window from `i` to `i+1`, most of the characters between the old start and the new "first valid position" don't need to be re-examined from scratch — we already know their positions from the previous scan.

The Sliding Window insight: maintain a window `[left, right]` and a hash map of `character -> last seen index`. Expand `right` one character at a time. Whenever the incoming character `s[right]` was already seen **inside the current window** (i.e., its last-seen index is `>= left`), jump `left` forward to one past that duplicate's last position — no need to shrink one-by-one, we can jump directly. This way each character is visited a bounded number of times, giving O(n) total time.

## Approach
1. Initialize `left = 0`, `max_length = 0`, and an empty hash map `last_seen` (maps character → most recent index at which it appeared).
2. For `right` in `0` to `len(s) - 1`:
   a. Let `c = s[right]`.
   b. If `c` is in `last_seen` **and** `last_seen[c] >= left` (meaning the previous occurrence of `c` is still inside the current window):
      - Move `left = last_seen[c] + 1` (shrink the window to just past the duplicate).
   c. Update `last_seen[c] = right`.
   d. Update `max_length = max(max_length, right - left + 1)`.
3. Return `max_length`.

## Dry Run
Input: `s = "pwwkew"`

| right | c | in last_seen & >= left? | left before | left after | last_seen update | window | length | max_length |
|-------|---|---------------------------|-------------|------------|-------------------|--------|--------|------------|
| 0 | 'p' | no | 0 | 0 | {p:0} | "p" | 1 | 1 |
| 1 | 'w' | no | 0 | 0 | {p:0,w:1} | "pw" | 2 | 2 |
| 2 | 'w' | yes (last_seen['w']=1 >= 0) | 0 | 2 (=1+1) | {p:0,w:2} | "w" | 1 | 2 |
| 3 | 'k' | no | 2 | 2 | {..,k:3} | "wk" | 2 | 2 |
| 4 | 'e' | no | 2 | 2 | {..,e:4} | "wke" | 3 | 3 |
| 5 | 'w' | yes (last_seen['w']=2 >= 2) | 2 | 3 (=2+1) | {..,w:5} | "kew" | 3 | 3 |

Final `max_length = 3`, matching the expected output (`"wke"` or `"kew"`, both length 3).

## Solution (Python 3)
```python
def length_of_longest_substring(s: str) -> int:
    last_seen = {}
    left = 0
    max_length = 0

    for right, c in enumerate(s):
        if c in last_seen and last_seen[c] >= left:
            left = last_seen[c] + 1
        last_seen[c] = right
        max_length = max(max_length, right - left + 1)

    return max_length


if __name__ == "__main__":
    print(length_of_longest_substring("abcabcbb"))  # Expected: 3
    print(length_of_longest_substring("bbbbb"))     # Expected: 1
    print(length_of_longest_substring("pwwkew"))    # Expected: 3
    print(length_of_longest_substring(""))          # Expected: 0
```

## Complexity Analysis
- Time: O(n) — `right` advances exactly once per iteration through the whole string, and `left` only ever moves forward (never backward), so both pointers together make at most O(n) total moves.
- Space: O(min(n, alphabet_size)) — the hash map stores at most one entry per distinct character encountered, bounded by the size of the character set.

## Key Takeaways
- This is the canonical **variable-size** sliding window: expand `right` every iteration unconditionally, and shrink/jump `left` only when the window becomes invalid (here: contains a duplicate).
- Common mistake: shrinking `left` one step at a time in a `while` loop even when a direct jump (`left = last_seen[c] + 1`) is possible and correct — the jump is what makes this O(n) instead of O(n) with a worse constant, and forgetting the `>= left` check (only counting duplicates *inside* the current window) is a classic bug that causes `left` to jump backward incorrectly.
- Related/variant problems to try next: **Longest Repeating Character Replacement**, **Minimum Window Substring** (see the hard problem in this pattern), **Permutation in String**.
