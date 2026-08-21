"""
LeetCode Top Interview 150 — #21 (LeetCode #151)
Reverse Words in a String
Category: Array / String | Difficulty: Medium

Problem
-------
Given an input string `s`, reverse the order of the words. A word is defined as a sequence of
non-space characters. The words in `s` will be separated by at least one space.

Return a string of the words in reverse order, joined by a single space. The returned string
should only have a single space separating the words; it should not contain any leading or
trailing spaces, even if the input has extra spaces between/around words.

Constraints
-----------
- 1 <= s.length <= 10^4
- s contains English letters, digits, and spaces ' '
- There is at least one word in s

Examples
--------
Example 1:
    Input: s = "the sky is blue"
    Output: "blue is sky the"

Example 2:
    Input: s = "  hello world  "
    Output: "world hello"
    Explanation: Leading and trailing spaces are removed from the reversed string.

Example 3:
    Input: s = "a good   example"
    Output: "example good a"
    Explanation: Multiple spaces between words are reduced to a single space in the output.

Intuition
---------
The straightforward way is to split on whitespace (which already collapses runs of spaces and
strips leading/trailing ones), reverse the resulting list of words, and join with single spaces —
that's O(n) and essentially the "intended" solution in a language like Python where split/join are
built-ins, so there's no meaningfully slower brute force to contrast it with here. What's actually
interesting is the follow-up constraint LeetCode poses (solve it in-place with O(1) extra space,
as you would in C): reverse the *entire* character array first, which flips the word order but
also reverses each individual word's letters; then walk through and reverse each word's letters
back to their original order in a second pass. That two-reversal trick — reverse the whole, then
reverse the parts — achieves the word-order reversal without ever allocating a list of substrings.
"""

from typing import List


# ============================================================
# Approach 1: Split, reverse, join
# ============================================================
# Idea: str.split() with no argument splits on runs of whitespace and
# discards empty tokens (handling extra/leading/trailing spaces for free);
# reverse that list and join with single spaces.
# Time:  O(n) — split, reverse, and join are each linear
# Space: O(n) — the list of words and the output string
def solve_split_join(s: str) -> str:
    words = s.split()
    return " ".join(reversed(words))


# ============================================================
# Approach 2: Optimal (reverse-the-whole-then-reverse-each-word, O(1) extra
# space over a mutable character array — the classic in-place C-style trick)
# ============================================================
# Idea: (1) strip and collapse whitespace into a list of characters with
# single separators, (2) reverse the whole array so word order flips (but
# each word's letters are now backward), (3) walk the array and reverse
# each word's letters back to normal in place.
# Dry run: s="the sky is blue"
#   chars (collapsed) = ['t','h','e',' ','s','k','y',' ','i','s',' ','b','l','u','e']
#   reverse whole: "eulb si yks eht" (word order flipped, letters backward)
#   reverse each word's letters back:
#     "eulb" -> "blue", "si" -> "is", "yks" -> "sky", "eht" -> "the"
#   result: "blue is sky the"
# Time:  O(n) — each character touched a constant number of times
# Space: O(n) for the mutable char list itself (true O(1) *extra* space
#        beyond the output, matching the spirit of the in-place follow-up;
#        Python strings are immutable so a list stand-in is required)
def solve_optimal(s: str) -> str:
    # Step 1: build a char list with words separated by exactly one space,
    # no leading/trailing spaces (equivalent to trimming in place in C).
    chars = list(" ".join(s.split()))
    n = len(chars)

    def reverse_range(lo: int, hi: int) -> None:
        while lo < hi:
            chars[lo], chars[hi] = chars[hi], chars[lo]
            lo += 1
            hi -= 1

    # Step 2: reverse the entire array -> word order flips, letters backward.
    reverse_range(0, n - 1)

    # Step 3: reverse each word's letters back to normal.
    start = 0
    for i in range(n + 1):
        if i == n or chars[i] == " ":
            reverse_range(start, i - 1)
            start = i + 1

    return "".join(chars)


# ============================================================
# Key Takeaways
# ============================================================
# - "Reverse the whole, then reverse the parts" is a general in-place
#   trick for reordering fixed-size chunks (words, digit groups, rotated
#   array segments) without extra space, since the whole-array reversal
#   over-corrects each chunk's internal order and the second pass fixes it.
# - Common mistake: forgetting to collapse multiple spaces / trim
#   leading-trailing spaces before (or as part of) reversing, which leaves
#   extra spaces in the final output.
# - Related/variant problems to try next: Rotate Array (same reverse-thrice
#   trick), Reverse String, Reverse Words in a String III (reverse letters
#   within words but keep word order).


if __name__ == "__main__":
    tests = [
        (("the sky is blue",), "blue is sky the"),
        (("  hello world  ",), "world hello"),
        (("a good   example",), "example good a"),
        (("  Bob    Loves  Alice   ",), "Alice Loves Bob"),
        (("Alice does not even like bob",), "bob like even not does Alice"),
        (("a",), "a"),
    ]

    approaches = [solve_split_join, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
