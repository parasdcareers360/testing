"""
LeetCode Top Interview 150 — #42 (LeetCode #242)
Valid Anagram
Category: Hashmap | Difficulty: Easy

Problem
-------
Given two strings `s` and `t`, return True if `t` is an anagram of `s`, and False otherwise.

An anagram is a word or phrase formed by rearranging the letters of a different word or phrase,
typically using all the original letters exactly once.

Constraints
-----------
- 1 <= s.length, t.length <= 5 * 10^4
- s and t consist of lowercase English letters.

Follow-up: What if the inputs contain Unicode characters? How would you adapt your solution to
such a case?

Examples
--------
Example 1:
    Input: s = "anagram", t = "nagaram"
    Output: true

Example 2:
    Input: s = "rat", t = "car"
    Output: false

Intuition
---------
An anagram check is fundamentally "do these two multisets of characters match?" The most direct
brute-force expression of that is to sort both strings and compare — if they're anagrams, their
sorted forms are character-for-character identical. This costs O(n log n) because of the sort, but
it's dead simple and correct. We can do better: since order doesn't matter, we don't need to sort
at all — just count the frequency of each character in one string and subtract by walking the
other. If every count lands exactly at zero, the multisets matched. This drops the cost to O(n),
trading the sort for a linear counting pass, since counting is asymptotically cheaper than sorting.
"""

from collections import Counter


# ============================================================
# Approach 1: Brute Force (sort and compare)
# ============================================================
# Idea: two strings are anagrams iff their sorted character sequences are
# identical.
# Time:  O(n log n) — dominated by sorting both strings
# Space: O(n) — sorted() returns new lists
def solve_brute_force(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return sorted(s) == sorted(t)


# ============================================================
# Approach 2: Optimal (hashmap / Counter of letter frequencies)
# ============================================================
# Idea: count characters in s, then decrement while scanning t. If any
# decrement drives a count negative, or a leftover count remains nonzero,
# the strings aren't anagrams. Counter equality after subtraction (or a
# direct Counter(s) == Counter(t)) captures this in one line.
# Dry run: s="anagram", t="nagaram"
#   counts(s) = {a:3, n:1, g:1, r:1, m:1}
#   subtract counts(t) letter by letter -> every count returns to 0
#   all zero -> True
# Time:  O(n) — one pass to build each Counter, O(1) average per lookup
# Space: O(k) — k = number of distinct characters (bounded by alphabet size)
def solve_optimal(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)


# ============================================================
# Key Takeaways
# ============================================================
# - "Anagram" == "same character multiset" — recognize this and reach for
#   frequency counting (hashmap or fixed-size array) instead of sorting
#   whenever performance matters, since counting is O(n) vs. sorting's
#   O(n log n).
# - Common mistake: forgetting the length check before comparing — without
#   it, a shorter string could still coincidentally "fit inside" counts.
#   (Counter equality actually handles this correctly on its own since
#   leftover nonzero counts would differ, but the explicit check is a cheap
#   early exit and communicates intent.)
# - For the Unicode follow-up: a fixed 26-slot array only works for
#   lowercase English letters; Unicode needs a hashmap (dict/Counter) since
#   the character space is far too large for a fixed array — which is
#   exactly what solve_optimal already uses, making it Unicode-safe as-is.
# - Related/variant problems to try next: Group Anagrams, Ransom Note, Find
#   All Anagrams in a String.


if __name__ == "__main__":
    tests = [
        (("anagram", "nagaram"), True),
        (("rat", "car"), False),
        (("a", "ab"), False),
        (("", ""), True),
        (("aacc", "ccac"), False),
        (("listen", "silent"), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")
