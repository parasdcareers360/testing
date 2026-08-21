"""
LeetCode Top Interview 150 — #33 (LeetCode #76)
Minimum Window Substring
Category: Sliding Window | Difficulty: Hard

Problem
-------
Given two strings `s` and `t`, return the minimum-length substring of `s` such that every
character in `t` (including duplicates) is present in that substring. If there is no such
substring, return the empty string "".

The testcases are generated such that the answer is unique (when one exists).

Constraints
-----------
- 1 <= s.length, t.length <= 10^5
- s and t consist of uppercase and lowercase English letters.

Examples
--------
Example 1:
    Input: s = "ADOBECODEBANC", t = "ABC"
    Output: "BANC"
    Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C' from t.

Example 2:
    Input: s = "a", t = "a"
    Output: "a"

Example 3:
    Input: s = "a", t = "aa"
    Output: ""
    Explanation: Both 'a's from t must be included in the window. Since s only has one 'a',
    there is no valid window.

Intuition
---------
The brute force tries every substring of `s` and checks whether it contains all of `t`'s
characters (with correct multiplicity) — O(n^2) substrings, each check costing up to O(m), so
roughly O(n^2 * m). The insight that unlocks a linear pass: as the right edge of a candidate
window moves rightward, "does this window satisfy t?" only ever flips from false to true one way —
once satisfied by adding characters, removing characters (shrinking from the left) can only make
it stop being satisfied, never start being satisfied. That's the sliding-window precondition: grow
`right` until the window covers `t` completely, then greedily shrink `left` as far as possible
while it's still covering `t`, recording the shortest window seen. To check "covers t" in O(1)
per step instead of re-scanning, keep a running count of how many of `t`'s *distinct required
characters* are currently fully satisfied in the window, updated incrementally as each character
enters or leaves.
"""

from typing import Dict
from collections import Counter


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every substring of s, check via a fresh Counter comparison
# whether it contains all characters of t with sufficient multiplicity,
# and keep the shortest that qualifies.
# Time:  O(n^2 * m) — n^2 substrings, O(m) counter comparison each
# Space: O(m) for the target/window counters
def solve_brute_force(s: str, t: str) -> str:
    if not s or not t or len(t) > len(s):
        return ""

    target = Counter(t)
    n = len(s)
    best_start, best_len = -1, n + 1

    for start in range(n):
        window: Counter = Counter()
        for end in range(start, n):
            window[s[end]] += 1
            length = end - start + 1
            if length >= len(t) and length < best_len:
                # Only bother with the full containment check once the
                # window is at least as long as t (a cheap early filter).
                if all(window[c] >= cnt for c, cnt in target.items()):
                    best_start, best_len = start, length
                    break  # longer windows from this start can't beat this

    return "" if best_start == -1 else s[best_start:best_start + best_len]


# ============================================================
# Approach 2: Optimal (sliding window with a "satisfied count")
# ============================================================
# Idea: maintain window_count for characters currently in the window, and
# `satisfied` = number of distinct characters in `target` whose required
# count is currently met or exceeded. Grow `right`; whenever adding a
# character causes its count to exactly reach target's requirement,
# increment `satisfied`. Once satisfied == len(target), shrink `left`
# greedily (recording the window length each time it's still fully
# satisfied) until removing the leftmost character would break coverage.
# Dry run: s="ADOBECODEBANC", t="ABC", target={A:1,B:1,C:1}
#   right scans to right=5 ('C' at "ADOBEC") -> window has A,B,C all >=1
#     satisfied=3=len(target) -> shrink: left=0 'A' count1==req1, removing
#     drops satisfied -> can't shrink -> record window [0:6)="ADOBEC" len6
#   right continues... right=9 ('B' in "ADOBECODEB") window now has
#     A,B(2),C,D,E,O -> satisfied still 3 -> shrink left:
#     left=0 'A' count1==req -> removing breaks it -> stop, but wait 'A'
#     is still needed so we can't remove it while satisfied must hold;
#     actual shrink only proceeds past characters that are NOT the
#     bottleneck (e.g. extra 'B' or unrelated chars) -- here left stays at
#     the first 'A' until a later 'A' enters the window (right=10).
#   right=10 'A' -> window "ADOBECODEBA", now two A's -> shrink left:
#     remove s[0]='A' (count 2->1, still >=1, satisfied stays 3) -> left=1
#     remove s[1]='D' (not in target, no effect) -> left=2
#     remove s[2]='O' (not in target) -> left=3
#     remove s[3]='B' (count 2->1, still >=1) -> left=4
#     remove s[4]='E' (not in target) -> left=5
#     remove s[5]='C' (count 1->0, now <1) -> satisfied drops to 2 -> stop
#     window recorded before this last removal: s[5:11) = "CODEBA" len6
#   right=11 'N' (not in target, satisfied unaffected, still 2 -> no shrink)
#   right=12 'C' -> window has C again -> satisfied=3 -> shrink left:
#     left=5 'C'? no left is now 6 (from previous stop at left=5 meaning
#     window starts at 5) -- shrinking removes s[6]='O'(no effect) left=7,
#     s[7]='D'(no effect) left=8, s[8]='E'(no effect) left=9,
#     s[9]='B'(count1->0,<1) satisfied drops -> stop
#     window recorded before that removal: s[9:13) = "BANC" len4
#   final answer: shortest recorded = "BANC" (len 4)
# Time:  O(n + m) — right and left each move forward at most n times total
# Space: O(m) for target/window counters (bounded by alphabet size)
def solve_optimal(s: str, t: str) -> str:
    if not s or not t or len(t) > len(s):
        return ""

    target: Dict[str, int] = Counter(t)
    required_distinct = len(target)
    window_count: Dict[str, int] = {}
    satisfied = 0

    best_start, best_len = -1, len(s) + 1
    left = 0

    for right, ch in enumerate(s):
        window_count[ch] = window_count.get(ch, 0) + 1
        if ch in target and window_count[ch] == target[ch]:
            satisfied += 1

        while satisfied == required_distinct:
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1

            left_ch = s[left]
            window_count[left_ch] -= 1
            if left_ch in target and window_count[left_ch] < target[left_ch]:
                satisfied -= 1
            left += 1

    return "" if best_start == -1 else s[best_start:best_start + best_len]


# ============================================================
# Key Takeaways
# ============================================================
# - Track a single integer "how many distinct required characters are
#   currently satisfied" instead of re-checking full containment on every
#   step -- this turns an O(m) check into an O(1) increment/decrement.
# - Common mistake: comparing window_count[ch] >= target[ch] to decide
#   satisfaction after every change instead of only reacting to the
#   specific character that just changed -- that silently reintroduces an
#   O(m) or O(alphabet) cost per step and defeats the point of the trick.
# - Related/variant problems to try next: Longest Substring Without
#   Repeating Characters, Minimum Size Subarray Sum, Find All Anagrams in
#   a String.


if __name__ == "__main__":
    tests = [
        (("ADOBECODEBANC", "ABC"), "BANC"),
        (("a", "a"), "a"),
        (("a", "aa"), ""),
        (("ab", "b"), "b"),
        (("ab", "a"), "a"),
        (("bba", "ab"), "ba"),
        (("aa", "aa"), "aa"),
        (("", "a"), ""),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")
