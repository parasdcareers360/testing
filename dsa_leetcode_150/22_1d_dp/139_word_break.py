"""
LeetCode Top Interview 150 — #139 (LeetCode #139)
Word Break
Category: 1D DP | Difficulty: Medium

Problem
-------
Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented
into a space-separated sequence of one or more dictionary words.

Note that the same word in `wordDict` may be reused multiple times in the segmentation.

Constraints
-----------
- 1 <= s.length <= 300
- 1 <= wordDict.length <= 1000
- 1 <= wordDict[i].length <= 20
- s and wordDict[i] consist of only lowercase English letters
- All the strings of wordDict are unique

Examples
--------
Example 1:
    Input: s = "leetcode", wordDict = ["leet","code"]
    Output: true
    Explanation: "leetcode" can be segmented as "leet code".

Example 2:
    Input: s = "applepenapple", wordDict = ["apple","pen"]
    Output: true
    Explanation: "apple pen apple". Note that "apple" is reused.

Example 3:
    Input: s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]
    Output: false

Intuition
---------
The brute-force instinct is to try every prefix of `s` as a candidate first word and recurse on
the remainder — correct, but the same suffix of `s` gets re-attempted from many different
recursion paths (e.g. "og" gets re-checked whether we arrived there via "cats+and" or "cat+sand"),
so the naive recursion is exponential. The fix is to notice there are only `len(s)+1` distinct
suffixes total, so caching "can this suffix be segmented?" per starting index turns it into
O(n^2) top-down DP. Flipping the same idea bottom-up gives the classic formulation: let
dp[i] = "can s[0:i] be fully segmented using dictionary words?" dp[i] is true if there's some cut
point j < i where dp[j] is true AND s[j:i] is itself a dictionary word — dp[0] = true (empty
prefix) is the seed.
"""

from typing import List
from functools import lru_cache


# ============================================================
# Approach 1: Brute Force (plain recursion)
# ============================================================
# Idea: try every prefix of the remaining string as a word; if it's in the
# dictionary, recurse on what's left.
# Time:  O(2^n) worst case — each position can branch into many recursive
#        calls with no memory of repeated suffixes
# Space: O(n) — recursion stack depth
def solve_brute_force(s: str, wordDict: List[str]) -> bool:
    words = set(wordDict)

    def can_break(start: int) -> bool:
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in words and can_break(end):
                return True
        return False

    return can_break(0)


# ============================================================
# Approach 2: Better (recursion + memoization, top-down DP)
# ============================================================
# Idea: cache can_break(start) — there are only n+1 distinct starting
# indices, so each is resolved once no matter how many paths reach it.
# Time:  O(n^2) — n starting indices, each trying up to n end points
# Space: O(n) — cache + recursion stack
def solve_memo(s: str, wordDict: List[str]) -> bool:
    words = set(wordDict)
    n = len(s)

    @lru_cache(maxsize=None)
    def can_break(start: int) -> bool:
        if start == n:
            return True
        for end in range(start + 1, n + 1):
            if s[start:end] in words and can_break(end):
                return True
        return False

    result = can_break(0)
    can_break.cache_clear()
    return result


# ============================================================
# Approach 3: Optimal (iterative tabulation, bottom-up DP)
# ============================================================
# Idea: dp[i] = True means s[0:i] can be fully segmented. Build left to
# right; for each i, look back at every possible cut point j and check
# dp[j] (prefix already breakable) and s[j:i] is a dictionary word.
# Dry run: s="leetcode", wordDict={"leet","code"}
#   dp[0]=True (empty prefix)
#   i=4: j=0, dp[0]=True, s[0:4]="leet" in words -> dp[4]=True
#   i=8: j=4, dp[4]=True, s[4:8]="code" in words -> dp[8]=True
#   dp[8]=True -> whole string breakable
# Time:  O(n^2) — n end points, each scanning up to n cut points
# Space: O(n) — the dp array (+ O(sum of word lengths) for the word set)
def solve_optimal(s: str, wordDict: List[str]) -> bool:
    words = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]


# ============================================================
# Key Takeaways
# ============================================================
# - "Can prefix/suffix i be built?" is a classic 1D DP shape: dp[i] depends
#   on some dp[j] for j < i plus a local check (here, dictionary
#   membership of the substring between j and i).
# - Common mistake: forgetting dp[0] = True (the empty string is trivially
#   "breakable"), which is the seed every other dp[i] ultimately traces
#   back to.
# - Related/variant problems to try next: Word Break II (return all
#   segmentations), Concatenated Words, Palindrome Partitioning.


if __name__ == "__main__":
    tests = [
        (("leetcode", ["leet", "code"]), True),
        (("applepenapple", ["apple", "pen"]), True),
        (("catsandog", ["cats", "dog", "sand", "and", "cat"]), False),
        (("a", ["a"]), True),
        (("a", ["b"]), False),
        (("aaaaaaa", ["aaaa", "aaa"]), True),
        (("cars", ["car", "ca", "rs"]), True),
    ]

    approaches = [solve_brute_force, solve_memo, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:55s} -> {result!r}  [{status}]")
