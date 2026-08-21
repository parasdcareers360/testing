"""
LeetCode Top Interview 150 — #19 (LeetCode #58)
Length of Last Word
Category: Array / String | Difficulty: Easy

Problem
-------
Given a string `s` consisting of words and spaces, return the length of the last word in the
string. A word is a maximal substring consisting of non-space characters only.

Constraints
-----------
- 1 <= s.length <= 10^4
- s consists of only English letters and spaces ' '
- There is at least one word in s

Examples
--------
Example 1:
    Input: s = "Hello World"
    Output: 5
    Explanation: The last word is "World" with length 5.

Example 2:
    Input: s = "   fly me   to   the moon  "
    Output: 4
    Explanation: The last word is "moon" with length 4.

Example 3:
    Input: s = "luffy is still joyboy"
    Output: 6
    Explanation: The last word is "joyboy" with length 6.

Intuition
---------
The most direct approach is to use the language's built-in split-on-whitespace, which already
collapses runs of spaces and drops empty tokens, then take the length of the last element. That's
effectively O(n) already and there's no slower "brute force" alternative worth contrasting it
against — splitting the whole string is the natural first idea, not a naive one. The refinement
worth showing is doing it *without* allocating a list of every word: walk the string backward from
the end, first skipping any trailing spaces to find where the last word ends, then counting
characters backward until hitting a space (or the start of the string) to find where it begins.
This never scans past the last word, uses O(1) extra space, and in the worst case (no trailing
spaces) still only touches each relevant character once.
"""


# ============================================================
# Approach 1: Split on whitespace
# ============================================================
# Idea: Python's str.split() with no argument already splits on runs of
# whitespace and discards empty strings, so the last word is simply the
# last element of the resulting list.
# Time:  O(n) — split scans the whole string once
# Space: O(n) — the list of all words
def solve_split(s: str) -> int:
    words = s.split()
    return len(words[-1])


# ============================================================
# Approach 2: Optimal (backward scan, no splitting)
# ============================================================
# Idea: walk an index from the end of the string backward. First skip any
# trailing spaces. Then count characters until the next space (or the
# start of the string) — that count is the length of the last word.
# Dry run: s="   fly me   to   the moon  "
#   skip trailing spaces: index lands on 'n' of "moon"
#   count backward over "moon" (4 chars) until hitting the space before it
#   result: 4
# Time:  O(k) where k is the distance from the end to the start of the last
#        word — never scans past it, so it's often much less than O(n)
# Space: O(1)
def solve_optimal(s: str) -> int:
    i = len(s) - 1

    # Skip trailing spaces to find the end of the last word.
    while i >= 0 and s[i] == " ":
        i -= 1

    length = 0
    while i >= 0 and s[i] != " ":
        length += 1
        i -= 1

    return length


# ============================================================
# Key Takeaways
# ============================================================
# - When you only need information about the *end* of a sequence, scanning
#   backward from the end can avoid processing (or allocating) the whole
#   sequence, unlike a forward split/scan that touches everything.
# - Common mistake: forgetting to skip trailing spaces before counting,
#   which would incorrectly return 0 for inputs like "Hello World  ".
# - Related/variant problems to try next: Reverse Words in a String, Valid
#   Palindrome, Longest Common Prefix.


if __name__ == "__main__":
    tests = [
        (("Hello World",), 5),
        (("   fly me   to   the moon  ",), 4),
        (("luffy is still joyboy",), 6),
        (("a",), 1),
        (("   a   ",), 1),
        (("day",), 3),
    ]

    approaches = [solve_split, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
