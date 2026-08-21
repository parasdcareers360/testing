"""
LeetCode Top Interview 150 — #40 (LeetCode #205)
Isomorphic Strings
Category: Hashmap | Difficulty: Easy

Problem
-------
Given two strings `s` and `t`, determine if they are isomorphic.

Two strings `s` and `t` are isomorphic if the characters in `s` can be replaced to get `t`.

All occurrences of a character must be replaced with another character while preserving the
order of characters. No two characters may map to the same character, but a character may map
to itself.

Constraints
-----------
- 1 <= s.length <= 5 * 10^4
- t.length == s.length
- s and t consist of any valid ASCII character.

Examples
--------
Example 1:
    Input: s = "egg", t = "add"
    Output: true
    Explanation: e->a, g->d (both g's map to the same d)

Example 2:
    Input: s = "foo", t = "bar"
    Output: false
    Explanation: the two o's in "foo" would both need to map to 'a' then 'r' — inconsistent.

Example 3:
    Input: s = "paper", t = "title"
    Output: true

Intuition
---------
A tempting shortcut is "just check if the pattern of repeated positions matches" by brute-force
comparing, for every index, whether all earlier positions with the same character in `s` line up
with the same character in `t` (and vice versa) — this works but costs O(n^2) since each index
triggers a fresh scan of everything before it. The real requirement is a **bijection**: every
character in `s` must map to exactly one character in `t`, and that mapping must be reversible
(no two different `s`-characters may collide onto the same `t`-character). Two hashmaps — one
tracking `s -> t` and one tracking `t -> s` — let us verify both directions of the bijection in a
single linear pass: at each position, either the mapping already exists and must agree, or it
doesn't exist yet and we can create it, but only if the reverse mapping is also free.
"""

from typing import Dict


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: for every index i, the "signature" of character s[i] within s (the
# most recent earlier index with the same char, or -1) must match the
# signature of t[i] within t. Checked naively by scanning backward each time.
# Time:  O(n^2) — for each index, scan back through all prior indices
# Space: O(1) extra (excluding input)
def solve_brute_force(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    n = len(s)
    for i in range(n):
        # last index j < i where s[j] == s[i]
        s_prev = -1
        for j in range(i - 1, -1, -1):
            if s[j] == s[i]:
                s_prev = j
                break
        t_prev = -1
        for j in range(i - 1, -1, -1):
            if t[j] == t[i]:
                t_prev = j
                break
        if s_prev != t_prev:
            return False
    return True


# ============================================================
# Approach 2: Optimal (two hashmaps for a bijective mapping)
# ============================================================
# Idea: maintain s_to_t and t_to_s. At each position, if s[i] is already
# mapped, it must map to t[i]; if t[i] is already mapped, it must map back
# to s[i]; otherwise create both mappings fresh. This enforces the mapping
# is a true one-to-one bijection in a single pass.
# Dry run: s="egg", t="add"
#   i=0: 'e'->'a' new, 'a'->'e' new. maps: {e:a}, {a:e}
#   i=1: 'g'->'d' new, 'd'->'g' new. maps: {e:a,g:d}, {a:e,d:g}
#   i=2: 'g' already maps to 'd', t[2]='d' matches -> ok
#   all consistent -> True
# Time:  O(n) — one pass, O(1) hashmap operations
# Space: O(k) — k = number of distinct characters (bounded by alphabet size)
def solve_optimal(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False

    s_to_t: Dict[str, str] = {}
    t_to_s: Dict[str, str] = {}

    for cs, ct in zip(s, t):
        if cs in s_to_t:
            if s_to_t[cs] != ct:
                return False
        elif ct in t_to_s:
            # ct is already claimed by a different source character
            return False
        else:
            s_to_t[cs] = ct
            t_to_s[ct] = cs

    return True


# ============================================================
# Key Takeaways
# ============================================================
# - "Isomorphic" problems are really bijection-checking problems: a single
#   one-way hashmap is a trap (it misses collisions where two different
#   source characters map to the same target character) — you need to
#   verify both directions.
# - Common mistake: only building s->t and forgetting to also guard against
#   two different s-characters mapping onto the same t-character.
# - Related/variant problems to try next: Word Pattern, Word Pattern II,
#   Isomorphic Strings variants with custom alphabets.


if __name__ == "__main__":
    tests = [
        (("egg", "add"), True),
        (("foo", "bar"), False),
        (("paper", "title"), True),
        (("badc", "baba"), False),
        (("ab", "aa"), False),
        (("a", "a"), True),
        (("", ""), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:30s} -> {result!r}  [{status}]")
