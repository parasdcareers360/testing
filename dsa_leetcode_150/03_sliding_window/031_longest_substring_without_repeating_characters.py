"""
LeetCode Top Interview 150 — #31 (LeetCode #3)
Longest Substring Without Repeating Characters
Category: Sliding Window | Difficulty: Medium

Problem
-------
Given a string `s`, find the length of the longest substring without duplicate characters.

Constraints
-----------
- 0 <= s.length <= 5 * 10^4
- s consists of English letters, digits, symbols and spaces.

Examples
--------
Example 1:
    Input: s = "abcabcbb"
    Output: 3
    Explanation: The answer is "abc", with the length of 3.

Example 2:
    Input: s = "bbbbb"
    Output: 1
    Explanation: The answer is "b", with the length of 1.

Example 3:
    Input: s = "pwwkew"
    Output: 3
    Explanation: The answer is "wke", with the length of 3. Note "pwke" is a subsequence, not a
    substring.

Intuition
---------
The brute force checks every substring and verifies it has no duplicate characters, which is
O(n^3) (O(n^2) substrings, O(n) each to check via a set). The key realization: if a window
`s[left:right]` already has no repeats, and we extend to `s[right]`, only one thing can go wrong —
`s[right]` might already appear somewhere in the current window. If it does, the window is only
valid again once `left` moves past that earlier occurrence; everything before that occurrence is
now unusable as a starting point (any window starting there would still contain the duplicate).
So instead of resetting `left` back to `right` and rescanning, jump `left` directly to one past the
duplicate's last known position — a hashmap of "last seen index per character" makes that jump
O(1), giving an O(n) single pass where each pointer only moves forward.
"""

from typing import Dict


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: check every substring for duplicate characters using a set, keep
# the longest one that passes.
# Time:  O(n^3)   Space: O(min(n, charset)) for the per-substring set
def solve_brute_force(s: str) -> int:
    n = len(s)
    best = 0
    for start in range(n):
        seen = set()
        for end in range(start, n):
            if s[end] in seen:
                break
            seen.add(s[end])
            best = max(best, end - start + 1)
    return best


# ============================================================
# Approach 2: Better (sliding window with a set, shrink one at a time)
# ============================================================
# Idea: maintain a window with a set of characters currently inside it.
# Extend right; if the new character is already in the window, shrink from
# the left one step at a time (removing from the set) until it isn't.
# Distinct from Optimal because it doesn't jump `left` directly -- it
# discovers the duplicate is gone only by repeatedly stepping, which is
# still O(n) amortized but does more bookkeeping per removal.
# Time:  O(n) amortized   Space: O(min(n, charset))
def solve_better(s: str) -> int:
    window = set()
    left = 0
    best = 0
    for right, ch in enumerate(s):
        while ch in window:
            window.remove(s[left])
            left += 1
        window.add(ch)
        best = max(best, right - left + 1)
    return best


# ============================================================
# Approach 3: Optimal (sliding window with last-seen-index hashmap)
# ============================================================
# Idea: track the most recent index at which each character was seen. When
# extending to s[right], if that character was last seen at an index >=
# left (i.e. inside the current window), jump `left` directly to one past
# that index instead of shrinking step by step. `left` only ever moves
# forward, so total work is O(n).
# Dry run: s = "pwwkew"
#   right=0 'p' last_seen={} -> window[0:1] "p", best=1, last_seen={p:0}
#   right=1 'w' not in window -> window[0:2] "pw", best=2, last_seen={p:0,w:1}
#   right=2 'w' last_seen[w]=1 >= left(0) -> left=2; window[2:3] "w",
#            best stays 2, last_seen={p:0,w:2}
#   right=3 'k' new -> window[2:4] "wk", best=2, last_seen+={k:3}
#   right=4 'e' new -> window[2:5] "wke", best=3, last_seen+={e:4}
#   right=5 'w' last_seen[w]=2 < left(2)? equal -> left=3; window[3:6] "kew",
#            best stays 3
#   final best = 3
# Time:  O(n) — each index visited once by right, left moves monotonically
# Space: O(min(n, charset)) for the last-seen map
def solve_optimal(s: str) -> int:
    last_seen: Dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best


# ============================================================
# Key Takeaways
# ============================================================
# - A "last seen index" hashmap turns a shrink-one-step-at-a-time sliding
#   window into a direct jump, avoiding redundant work when a duplicate is
#   far from the window's left edge.
# - Common mistake: forgetting the `>= left` guard when jumping `left` --
#   without it, a stale last-seen index from before the current window can
#   incorrectly move `left` backward, shrinking the window in the wrong
#   direction (or corrupting the length calculation).
# - Related/variant problems to try next: Minimum Window Substring, Longest
#   Substring with At Most K Distinct Characters, Longest Repeating
#   Character Replacement.


if __name__ == "__main__":
    tests = [
        (("abcabcbb",), 3),
        (("bbbbb",), 1),
        (("pwwkew",), 3),
        (("",), 0),
        ((" ",), 1),
        (("au",), 2),
        (("dvdf",), 3),
        (("abba",), 2),
        (("tmmzuxt",), 5),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
