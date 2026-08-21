"""
LeetCode Top Interview 150 — #39 (LeetCode #383)
Ransom Note
Category: Hashmap | Difficulty: Easy

Problem
-------
Given two strings `ransomNote` and `magazine`, return True if `ransomNote` can be constructed by
using the letters from `magazine` and False otherwise.

Each letter in `magazine` can only be used once in `ransomNote`.

Constraints
-----------
- 1 <= ransomNote.length, magazine.length <= 10^5
- ransomNote and magazine consist of lowercase English letters.

Examples
--------
Example 1:
    Input: ransomNote = "a", magazine = "b"
    Output: false

Example 2:
    Input: ransomNote = "aa", magazine = "ab"
    Output: false

Example 3:
    Input: ransomNote = "aa", magazine = "aab"
    Output: true

Intuition
---------
The brute-force instinct is to treat this like a matching problem: for every letter needed in
`ransomNote`, scan `magazine` for an unused occurrence and "cross it off" by removing it from a
mutable copy. That works but is O(n*m) in the worst case because each removal is itself an O(m)
scan. The insight that unlocks the optimal solution is that order never matters here — only
*counts* matter: can `magazine` supply at least as many of each letter as `ransomNote` demands?
Counting the letters of `magazine` once with a hashmap (or a fixed 26-slot array, since the
alphabet is small and lowercase-only) turns the whole problem into a single linear pass with O(1)
lookups, no scanning-and-removing required.
"""

from collections import Counter


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for each character needed, search magazine for it and remove the
# first occurrence found (simulating "using up" that letter).
# Time:  O(n*m) — n = len(ransomNote), m = len(magazine); each removal scans
# Space: O(m) — mutable copy of magazine
def solve_brute_force(ransomNote: str, magazine: str) -> bool:
    available = list(magazine)
    for ch in ransomNote:
        if ch in available:
            available.remove(ch)
        else:
            return False
    return True


# ============================================================
# Approach 2: Optimal (hashmap / Counter of letter frequencies)
# ============================================================
# Idea: count every letter available in magazine, then walk ransomNote and
# decrement counts; if any count would go negative (or the letter is
# missing), magazine can't supply enough. Counter subtraction handles this
# cleanly via a single comparison at the end.
# Dry run: ransomNote="aa", magazine="aab"
#   magazine_counts = {a:2, b:1}
#   need a: count 2 -> 1 (ok)
#   need a: count 1 -> 0 (ok)
#   loop finishes without shortfall -> True
# Time:  O(n + m) — one pass to count magazine, one pass to check ransomNote
# Space: O(1) — at most 26 letters in the counter
def solve_optimal(ransomNote: str, magazine: str) -> bool:
    available = Counter(magazine)
    for ch in ransomNote:
        if available[ch] <= 0:
            return False
        available[ch] -= 1
    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a problem is really about "do I have enough of each item", stop
#   thinking about scanning/removing and count frequencies with a hashmap
#   (or fixed-size array for a small known alphabet) instead.
# - Common mistake: using `magazine.count(ch)` inside the loop over
#   ransomNote — that recomputes the count from scratch every time and
#   degrades back to O(n*m).
# - Related/variant problems to try next: Valid Anagram, Find the Difference,
#   First Unique Character in a String.


if __name__ == "__main__":
    tests = [
        (("a", "b"), False),
        (("aa", "ab"), False),
        (("aa", "aab"), True),
        (("", "abc"), True),
        (("abc", ""), False),
        (("aab", "baa"), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")
