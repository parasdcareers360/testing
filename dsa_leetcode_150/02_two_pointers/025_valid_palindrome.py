"""
LeetCode Top Interview 150 — #25 (LeetCode #125)
Valid Palindrome
Category: Two Pointers | Difficulty: Easy

Problem
-------
Given a string `s`, determine whether it is a palindrome after these transformations:
convert all uppercase letters to lowercase, and remove all non-alphanumeric characters.
An empty string (after filtering) is considered a valid palindrome.

Return `True` if `s` is a palindrome under these rules, otherwise `False`.

Constraints
-----------
- 1 <= s.length <= 2 * 10^5
- `s` consists only of printable ASCII characters.

Examples
--------
Example 1:
    Input: s = "A man, a plan, a canal: Panama"
    Output: True
    Explanation: "amanaplanacanalpanama" is a palindrome.

Example 2:
    Input: s = "race a car"
    Output: False
    Explanation: "raceacar" is not a palindrome.

Example 3:
    Input: s = " "
    Output: True
    Explanation: After filtering, the string is empty, which counts as a palindrome.

Intuition
---------
The brute-force approach is to actually build the cleaned string (lowercase, alnum-only) and
compare it to its own reverse — simple, correct, but it allocates two extra strings when we
don't need to. The insight that gets us to O(1) extra space is that we never need the cleaned
string materialized at all: we can walk two pointers inward from both ends of the *original*
string, skipping over non-alphanumeric characters on the fly, and compare characters
(case-insensitively) directly. The moment a mismatch is found we can stop early, and if the
pointers cross without a mismatch, it's a palindrome.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (build cleaned string, compare to reverse)
# ============================================================
# Idea: filter to lowercase alnum characters into a new string, then check
# that string equals its reverse.
# Time:  O(n) — one pass to filter, one to reverse/compare
# Space: O(n) — the cleaned string (and its reverse)
def solve_brute_force(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]


# ============================================================
# Approach 2: Optimal (two pointers, in place, no extra string)
# ============================================================
# Idea: pointers `left` and `right` start at the two ends of the original
# string. Advance `left` forward / `right` backward past any non-alphanumeric
# characters, then compare the lowercase versions of s[left] and s[right].
# Mismatch -> not a palindrome; pointers cross -> confirmed palindrome.
# Dry run: s = "A man, a plan, a canal: Panama"
#   left=0('A') right=29('a') -> 'a'=='a' -> left=1, right=28
#   left=1(' ') skip -> left=2('m') right=28('m') -> match -> left=3, right=27
#   ... continues matching through the whole string ...
#   left and right meet/cross in the middle -> True
# Time:  O(n) — each character visited at most once across both pointers
# Space: O(1) — no auxiliary string, only two index pointers
def solve_optimal(s: str) -> bool:
    left, right = 0, len(s) - 1

    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Two pointers converging from both ends is the classic pattern for
#   palindrome checks — it avoids materializing a cleaned/reversed copy.
# - Common mistake: forgetting the `left < right` guard inside the inner
#   skip-loops, which can let a pointer run past the other and read out of
#   bounds (or falsely "match" past the crossing point).
# - Related/variant problems to try next: Valid Palindrome II (one deletion
#   allowed), Palindrome Linked List, Longest Palindromic Substring.


if __name__ == "__main__":
    tests: List[tuple] = [
        (("A man, a plan, a canal: Panama",), True),
        (("race a car",), False),
        ((" ",), True),
        ((".,",), True),
        (("0P",), False),
        (("ab_ca",), False),
        (("a.",), True),
        (("Was it a car or a cat I saw?",), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")
