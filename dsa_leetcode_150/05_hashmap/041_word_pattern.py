"""
LeetCode Top Interview 150 — #41 (LeetCode #290)
Word Pattern
Category: Hashmap | Difficulty: Easy

Problem
-------
Given a `pattern` and a string `s`, find if `s` follows the same pattern.

Here "follow" means a full bijective mapping between a letter in `pattern` and a non-empty word
in `s` (split by single spaces): every letter maps to exactly one word, every word maps back to
exactly one letter, and no two letters may map to the same word.

Constraints
-----------
- 1 <= pattern.length <= 300
- pattern contains only lowercase English letters.
- 1 <= s.length <= 3000
- s contains only lowercase English letters and spaces ' '.
- s does not contain any leading or trailing spaces.
- All the words in s are separated by a single space.

Examples
--------
Example 1:
    Input: pattern = "abba", s = "dog cat cat dog"
    Output: true

Example 2:
    Input: pattern = "abba", s = "dog cat cat fish"
    Output: false

Example 3:
    Input: pattern = "aaaa", s = "dog cat cat dog"
    Output: false

Intuition
---------
This is the same bijection idea as Isomorphic Strings, just one level up: instead of mapping
character-to-character, we map character-to-word. The naive approach still works — for each
position, check whether the pattern-letter seen so far always paired with the same word, scanning
back over prior positions — but that's O(n^2) in the number of tokens. Since a letter can only map
to one word and a word can only map to one letter, we again need two hashmaps (letter->word and
word->letter) walked in a single pass over the split words, plus an upfront length check: if the
word count doesn't match the pattern length, it's an automatic mismatch.
"""

from typing import Dict


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: split s into words; lengths must match pattern. For each index i,
# find the most recent earlier index j where pattern[j] == pattern[i] and
# compare it against the most recent earlier index where words[j] == words[i].
# Time:  O(n^2) — n = number of tokens, each index scans backward
# Space: O(n) — the split word list
def solve_brute_force(pattern: str, s: str) -> bool:
    words = s.split(" ")
    if len(pattern) != len(words):
        return False
    n = len(pattern)
    for i in range(n):
        p_prev = -1
        for j in range(i - 1, -1, -1):
            if pattern[j] == pattern[i]:
                p_prev = j
                break
        w_prev = -1
        for j in range(i - 1, -1, -1):
            if words[j] == words[i]:
                w_prev = j
                break
        if p_prev != w_prev:
            return False
    return True


# ============================================================
# Approach 2: Optimal (two hashmaps for a bijective mapping)
# ============================================================
# Idea: mirror Isomorphic Strings — maintain letter->word and word->letter
# maps and verify consistency in both directions in one linear pass.
# Dry run: pattern="abba", s="dog cat cat dog"
#   words = [dog, cat, cat, dog]
#   i=0: a->dog new, dog->a new
#   i=1: b->cat new, cat->b new
#   i=2: b already -> cat, matches words[2]='cat' -> ok
#   i=3: a already -> dog, matches words[3]='dog' -> ok
#   all consistent -> True
# Time:  O(n) — n = number of tokens (word comparisons are O(1) amortized
#        via hashing, ignoring word length)
# Space: O(n) — the split word list plus two hashmaps of distinct entries
def solve_optimal(pattern: str, s: str) -> bool:
    words = s.split(" ")
    if len(pattern) != len(words):
        return False

    char_to_word: Dict[str, str] = {}
    word_to_char: Dict[str, str] = {}

    for ch, word in zip(pattern, words):
        if ch in char_to_word:
            if char_to_word[ch] != word:
                return False
        elif word in word_to_char:
            return False
        else:
            char_to_word[ch] = word
            word_to_char[word] = ch

    return True


# ============================================================
# Key Takeaways
# ============================================================
# - Same bijection pattern as Isomorphic Strings, just with words instead of
#   characters as one side of the mapping — recognizing the shared shape
#   means the same two-hashmap technique transfers directly.
# - Common mistake: forgetting the upfront length check (pattern length vs.
#   word count) — without it, zip() silently truncates to the shorter
#   sequence and can produce a false positive.
# - Related/variant problems to try next: Isomorphic Strings, Word Pattern
#   II (backtracking version without a fixed split), Word Break.


if __name__ == "__main__":
    tests = [
        (("abba", "dog cat cat dog"), True),
        (("abba", "dog cat cat fish"), False),
        (("aaaa", "dog cat cat dog"), False),
        (("abba", "dog dog dog dog"), False),
        (("a", "dog"), True),
        (("ab", "dog dog"), False),
        (("abc", "dog cat fish"), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
