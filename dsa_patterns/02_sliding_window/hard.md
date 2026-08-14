# Hard — Minimum Window Substring

**Source**: LeetCode #76
**Pattern**: Sliding Window
**Difficulty**: Hard

## Problem Statement
Given two strings `s` and `t` of lengths `m` and `n` respectively, return the minimum-length substring of `s` such that every character in `t` (including duplicates) is included in the substring. If there is no such substring, return the empty string `""`.

The test cases are generated such that the answer, when it exists, is unique.

## Constraints
- `1 <= s.length, t.length <= 10^5`
- `s` and `t` consist of uppercase and lowercase English letters.
- The answer is guaranteed to be unique when a valid substring exists.

## Examples
**Example 1**
Input: `s = "ADOBECODEBANC"`, `t = "ABC"`
Output: `"BANC"`
Explanation: The substring `"BANC"` contains 'A', 'B', and 'C' from string `t`, and it is the shortest such substring in `s`.

**Example 2**
Input: `s = "a"`, `t = "a"`
Output: `"a"`
Explanation: The entire string `s` is the minimum window.

**Example 3**
Input: `s = "a"`, `t = "aa"`
Output: `""`
Explanation: Both characters of `t` ('a' and 'a') have to be included in the window, but `s` only has one 'a'. No valid window exists.

## Intuition — Why This Pattern
**Brute force**: for every pair of indices `(i, j)` with `i <= j`, check whether `s[i:j+1]` contains all characters of `t` with the required multiplicities, tracking the shortest valid one. Checking a single substring's character counts against `t`'s requirement costs O(n) (or O(alphabet) with counting), and there are O(m^2) substrings, giving roughly O(m^2 * n) — far too slow for m, n up to 10^5.

The twist versus the medium problem in this pattern (Longest Substring Without Repeating Characters): now we need a window that satisfies a **coverage** condition (contains at least as many of each required character as `t` needs) rather than an **exclusion** condition (no duplicates), and we want the *minimum* length that satisfies it, not the maximum.

The Sliding Window insight still applies, just steered differently: expand the window (`right` pointer) to *gather* characters until the window becomes "valid" (fully covers `t`'s requirements). Once valid, instead of stopping, try to **shrink from the left** as much as possible while remaining valid — every time we shrink, we might find a new minimum window. When shrinking breaks validity, resume expanding `right`. This "expand until valid, then shrink until invalid, repeat" pattern lets every character be visited a bounded number of times (added once when `right` passes it, removed at most once when `left` passes it), giving O(m + n) time — versus the brute force's near-quadratic blowup.

We track how many *distinct* required characters currently have their full required count satisfied (`formed`), compared against how many distinct characters `t` requires (`required`). The window is valid exactly when `formed == required`.

## Approach
1. If `t` is longer than `s`, return `""` immediately (impossible).
2. Build a frequency map `need` of characters in `t` (character → required count). Let `required = len(need)` (number of *distinct* characters that must be satisfied).
3. Initialize `left = 0`, `formed = 0` (count of distinct characters currently fully satisfied), and a frequency map `window_counts` for characters currently in the window.
4. Initialize `best_len = infinity`, `best_left = 0`, `best_right = 0` (to record the best window found).
5. For `right` in `0` to `len(s) - 1`:
   a. Let `c = s[right]`; increment `window_counts[c]`.
   b. If `c` is in `need` and `window_counts[c] == need[c]`, increment `formed` (this character just became fully satisfied).
   c. While `formed == required` (window is currently valid):
      - If `right - left + 1 < best_len`, update `best_len = right - left + 1`, `best_left = left`, `best_right = right`.
      - Let `d = s[left]`; decrement `window_counts[d]`.
      - If `d` is in `need` and `window_counts[d] < need[d]`, decrement `formed` (this character is no longer fully satisfied — window about to become invalid).
      - Increment `left` (shrink the window).
6. If `best_len` is still infinity, return `""`; otherwise return `s[best_left:best_right+1]`.

## Dry Run
Input: `s = "ADOBECODEBANC"`, `t = "ABC"`

`need = {A:1, B:1, C:1}`, `required = 3`.

Expanding `right` from 0, tracking window and `formed`:
- right=0 ('A'): window_counts={A:1}; A hits need → formed=1. Not valid (formed<required).
- right=1 ('D'): window_counts={A:1,D:1}. Not valid.
- right=2 ('O'): window_counts={A:1,D:1,O:1}. Not valid.
- right=3 ('B'): window_counts adds B:1 → B hits need → formed=2. Not valid.
- right=4 ('E'): adds E:1. Not valid.
- right=5 ('C'): adds C:1 → C hits need → formed=3. **Valid!** Window = s[0:6] = "ADOBEC", length 6.
  - Shrink: best_len=6, best="ADOBEC". Remove s[left=0]='A': window_counts[A]=0 < need[A]=1 → formed=2. left=1. Now formed<required, stop shrinking.
- right=6 ('O'): adds O (already there, now 2). Not valid.
- right=7 ('D'): adds D (now 2). Not valid.
- right=8 ('E'): adds E (now 2). Not valid.
- right=9 ('B'): adds B (now 2, already satisfied — no change to formed, stays satisfied). Not valid (still missing A which we removed).
- right=10 ('A'): adds A back → window_counts[A]=1 == need[A] → formed=3. **Valid!** Window = s[1:11] = "DOBECODEBA", length 10.
  - Shrink: current window length 10 > best_len 6, don't update best. Remove s[left=1]='D' (not in need) → left=2.
  - Still valid (formed still 3, since 'D' removal doesn't affect need-tracking). Window = s[2:11], length 9. 9 > 6, don't update. Remove s[left=2]='O' (not in need) → left=3.
  - Still valid. Window = s[3:11] = "BECODEBA", length 8. Remove s[left=3]='B': window_counts[B]=1, still >= need[B]=1 → formed stays 3 (only decrements formed if it drops *below* need). left=4.
  - Still valid. Window = s[4:11]="ECODEBA", length 7. Remove s[left=4]='E' (not in need) → left=5.
  - Still valid. Window=s[5:11]="CODEBA", length 6. Not < 6, don't update (tie doesn't replace). Remove s[left=5]='C': window_counts[C]=0 < need[C]=1 → formed=2. left=6. Stop shrinking (formed<required).
- right=11 ('N'): adds N. Not valid.
- right=12 ('C'): adds C back → window_counts[C]=1==need[C] → formed=3. **Valid!** Window = s[6:13] = "ODEBANC", length 7. 7 > 6, don't update best.
  - Shrink: remove s[left=6]='O' (not in need) → left=7. Window=s[7:13]="DEBANC", length 6. Not <6. Remove s[left=7]='D' (not in need) → left=8. Window=s[8:13]="EBANC", length 5. **5 < 6 → update best_len=5, best="EBANC"**... 

Wait — let's double check: is "EBANC" actually valid (contains A, B, C)? E-B-A-N-C: yes contains B, A, C. So best becomes length 5, "EBANC" at this point. Continue shrinking: remove s[left=8]='E' (not in need) → left=9. Window=s[9:13]="BANC", length 4. **4 < 5 → update best_len=4, best="BANC"**. Remove s[left=9]='B': window_counts[B]=0 < need[B]=1 → formed=2. left=10. Stop shrinking.

Loop ends (right reaches end of string, index 12 = len(s)-1).

Final best window: `"BANC"`, length 4 — matches the expected output.

(This dry run shows exactly why the algorithm is correct: it never misses a shorter valid window because it greedily shrinks every time the window is valid, checking the length at every valid state.)

## Solution (Python 3)
```python
from collections import Counter


def min_window(s: str, t: str) -> str:
    if not s or not t or len(t) > len(s):
        return ""

    need = Counter(t)
    required = len(need)

    window_counts = {}
    formed = 0
    left = 0
    best_len = float("inf")
    best_left, best_right = 0, 0

    for right, c in enumerate(s):
        window_counts[c] = window_counts.get(c, 0) + 1
        if c in need and window_counts[c] == need[c]:
            formed += 1

        while formed == required:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_left, best_right = left, right

            d = s[left]
            window_counts[d] -= 1
            if d in need and window_counts[d] < need[d]:
                formed -= 1
            left += 1

    if best_len == float("inf"):
        return ""
    return s[best_left:best_right + 1]


if __name__ == "__main__":
    print(min_window("ADOBECODEBANC", "ABC"))  # Expected: "BANC"
    print(min_window("a", "a"))                 # Expected: "a"
    print(min_window("a", "aa"))                # Expected: ""
```

## Complexity Analysis
- Time: O(m + n) — building `need` from `t` costs O(n); the main loop over `s` has `right` advancing m times, and `left` can advance at most m times total across the entire run (it never resets backward), so both pointers together do O(m) work; each step does O(1) hash map operations.
- Space: O(n + k) where k is the number of distinct characters in the window — bounded by the alphabet size (at most 52 for upper/lowercase English letters), so effectively O(1) extra space beyond the `need` map which is O(distinct chars in t).

## Key Takeaways
- This problem demonstrates the "expand to make valid, then shrink to minimize while it stays valid" variant of sliding window — contrasted with "expand and shrink only to stay valid" from the medium problem. Recognizing which of these two shrink strategies a problem needs is the key skill this pattern builds.
- Common mistakes: decrementing `formed` whenever a required character is removed (should only decrement when the count *drops below* the required amount, since a character can appear in the window with count higher than required without breaking validity); forgetting the tie-breaking rule (`<` not `<=`) which affects picking the leftmost minimal window when there are multiple windows of equal minimal length — the problem guarantees uniqueness so this specific edge case won't arise in valid test cases, but is worth understanding.
- Related/variant problems to try next: **Permutation in String**, **Longest Repeating Character Replacement**, **Sliding Window Maximum** (uses a monotonic deque instead, pattern #29).
