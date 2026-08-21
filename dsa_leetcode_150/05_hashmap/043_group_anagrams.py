"""
LeetCode Top Interview 150 — #43 (LeetCode #49)
Group Anagrams
Category: Hashmap | Difficulty: Medium

Problem
-------
Given an array of strings `strs`, group the anagrams together. You can return the answer in any
order.

Constraints
-----------
- 1 <= strs.length <= 10^4
- 0 <= strs[i].length <= 100
- strs[i] consists of lowercase English letters.

Examples
--------
Example 1:
    Input: strs = ["eat","tea","tan","ate","nat","bat"]
    Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
    Explanation: groups may be returned in any order, and the strings within a group may be in
    any order too.

Example 2:
    Input: strs = [""]
    Output: [[""]]

Example 3:
    Input: strs = ["a"]
    Output: [["a"]]

Intuition
---------
This is Valid Anagram scaled up to n strings: instead of checking one pair, we need to bucket all
strings so that anagrams land in the same bucket. The brute-force way is to compare every string
against every other string pairwise (using the sorted-string or Counter equality check from Valid
Anagram) and union them into groups — O(n^2) comparisons, each itself costing string-comparison
time. The key realization: anagrams share a canonical "signature" — their sorted character
sequence is identical. So instead of comparing pairs, compute each string's sorted form once and
use it as a hashmap key; every string with the same signature automatically lands in the same
bucket. This turns O(n^2) pairwise comparisons into a single O(n) pass with O(k log k) work per
string (k = string length) to compute its signature.
"""

from collections import defaultdict
from typing import List


# ============================================================
# Approach 1: Brute Force (pairwise comparison + union into groups)
# ============================================================
# Idea: for each string, scan existing groups; if it's an anagram of that
# group's representative (compared via sorted equality), add it there;
# otherwise start a new group.
# Time:  O(n^2 * k log k) — n strings, up to n groups scanned per string,
#        each comparison sorts two strings of length up to k
# Space: O(n*k) — the output groups plus sorted-string temporaries
def solve_brute_force(strs: List[str]) -> List[List[str]]:
    groups: List[List[str]] = []
    for s in strs:
        placed = False
        for group in groups:
            if sorted(group[0]) == sorted(s):
                group.append(s)
                placed = True
                break
        if not placed:
            groups.append([s])
    return groups


# ============================================================
# Approach 2: Optimal (hashmap keyed by sorted-string signature)
# ============================================================
# Idea: every anagram of a given string shares the same sorted-character
# signature. Use that signature as a hashmap key and bucket strings in one
# linear pass — no pairwise comparisons needed.
# Dry run: strs=["eat","tea","tan","ate","nat","bat"]
#   "eat" -> key "aet" -> buckets={"aet":["eat"]}
#   "tea" -> key "aet" -> buckets={"aet":["eat","tea"]}
#   "tan" -> key "ant" -> buckets={"aet":[...], "ant":["tan"]}
#   "ate" -> key "aet" -> appended
#   "nat" -> key "ant" -> appended
#   "bat" -> key "abt" -> new bucket
#   result: [["eat","tea","ate"], ["tan","nat"], ["bat"]]  (order may vary)
# Time:  O(n * k log k) — n strings, each sorted in O(k log k)
# Space: O(n*k) — the hashmap of buckets holds every input string once
def solve_optimal(strs: List[str]) -> List[List[str]]:
    buckets = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        buckets[key].append(s)
    return list(buckets.values())


# ============================================================
# Approach 3: Best (hashmap keyed by character-count signature)
# ============================================================
# Idea: avoid sorting entirely. Since the alphabet is fixed (lowercase
# English letters), represent each string's signature as a 26-length tuple
# of character counts — computing it is O(k) instead of O(k log k) for a
# sort, and tuples are hashable so they work directly as dict keys.
# Time:  O(n*k) — n strings, O(k) to build each count tuple (k <= 100 here)
# Space: O(n*k) — buckets hold every input string, plus O(26) per key
def solve_best(strs: List[str]) -> List[List[str]]:
    buckets = defaultdict(list)
    for s in strs:
        counts = [0] * 26
        for ch in s:
            counts[ord(ch) - ord("a")] += 1
        buckets[tuple(counts)].append(s)
    return list(buckets.values())


# ============================================================
# Key Takeaways
# ============================================================
# - Grouping-by-property problems are almost always "compute a canonical
#   signature, then bucket by that signature in a hashmap" — this replaces
#   O(n^2) pairwise comparisons with a single O(n) pass.
# - Common mistake: using an unsorted/unnormalized string (or the wrong
#   signature) as the bucket key — the signature must be identical for all
#   anagrams and only for anagrams (e.g. sorted string, or a fixed-length
#   count tuple for a bounded alphabet).
# - Count-tuple signatures beat sorting when the alphabet is small and
#   fixed, since building the tuple is O(k) instead of O(k log k) — the same
#   trade-off as Valid Anagram's sort-vs-count comparison, generalized to
#   n-way grouping.
# - Related/variant problems to try next: Valid Anagram, Find All Anagrams
#   in a String, Group Shifted Strings.


if __name__ == "__main__":
    tests = [
        ((["eat", "tea", "tan", "ate", "nat", "bat"],),
         [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]),
        (([""],), [[""]]),
        ((["a"],), [["a"]]),
        ((["abc", "bca", "cab", "xyz"],), [["abc", "bca", "cab"], ["xyz"]]),
    ]

    def normalize(groups: List[List[str]]) -> List[List[str]]:
        # Order of groups and order within groups is unspecified by the
        # problem, so sort both levels before comparing to expected output.
        return sorted(sorted(group) for group in groups)

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if normalize(result) == normalize(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:55s} -> {result!r}  [{status}]")
