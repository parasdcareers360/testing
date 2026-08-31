"""
Dynamic Programming — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.

Every shape below follows the same 5-step derivation from concept.md:
state -> transition -> base case -> extraction point -> top-down or bottom-up.
"""

from functools import lru_cache
from typing import List


# ---------------------------------------------------------------------------
# Shape 1: 1D DP, top-down memoization (fibonacci / climbing stairs family)
# ---------------------------------------------------------------------------
def climb_stairs_top_down(n: int) -> int:
    """dp[i] = number of ways to reach step i, taking 1 or 2 steps at a time."""

    @lru_cache(maxsize=None)
    def ways(i: int) -> int:
        if i <= 1:
            return 1
        return ways(i - 1) + ways(i - 2)

    return ways(n)


# ---------------------------------------------------------------------------
# Shape 2: 1D DP, bottom-up tabulation (same recurrence as Shape 1)
# ---------------------------------------------------------------------------
def climb_stairs_bottom_up(n: int) -> int:
    if n <= 1:
        return 1
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


# ---------------------------------------------------------------------------
# Shape 3: 1D DP with O(1) rolling-variable space optimization (house robber family)
# ---------------------------------------------------------------------------
def house_robber(nums: List[int]) -> int:
    """dp[i] = max money robbable from nums[0..i], house i optionally robbed."""
    rob_prev2 = rob_prev1 = 0
    for x in nums:
        rob_prev2, rob_prev1 = rob_prev1, max(rob_prev1, rob_prev2 + x)
    return rob_prev1


# ---------------------------------------------------------------------------
# Shape 4: 2D DP, grid paths (unique paths family)
# ---------------------------------------------------------------------------
def unique_paths(m: int, n: int) -> int:
    """dp[r][c] = number of paths from (0,0) to (r,c) moving only right or down."""
    dp = [[1] * n for _ in range(m)]
    for r in range(1, m):
        for c in range(1, n):
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[m - 1][n - 1]


# ---------------------------------------------------------------------------
# Shape 5: 2D DP, two-string comparison (edit distance / LCS family)
# ---------------------------------------------------------------------------
def edit_distance(word1: str, word2: str) -> int:
    """dp[i][j] = min edits to turn word1[:i] into word2[:j]."""
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def longest_common_subsequence(text1: str, text2: str) -> int:
    """dp[i][j] = length of LCS of text1[:i] and text2[:j] -- same grid shape as edit_distance."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


# ---------------------------------------------------------------------------
# Shape 6: 0/1 knapsack -- iterate capacity DESCENDING (each item used at most once)
# ---------------------------------------------------------------------------
def knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]


# ---------------------------------------------------------------------------
# Shape 7: unbounded knapsack -- iterate capacity ASCENDING (unlimited reuse per item)
# ---------------------------------------------------------------------------
def coin_change_min_coins(coins: List[int], amount: int) -> int:
    """dp[a] = min coins to make amount a; unbounded because each coin is reusable."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1


if __name__ == "__main__":
    # Shape 1 & 2: top-down and bottom-up agree (equivalence check)
    for n in [0, 1, 2, 5, 10]:
        assert climb_stairs_top_down(n) == climb_stairs_bottom_up(n)
    assert climb_stairs_bottom_up(5) == 8

    # Shape 3
    assert house_robber([1, 2, 3, 1]) == 4
    assert house_robber([2, 7, 9, 3, 1]) == 12
    assert house_robber([]) == 0

    # Shape 4
    assert unique_paths(3, 7) == 28
    assert unique_paths(1, 1) == 1

    # Shape 5
    assert edit_distance("horse", "ros") == 3
    assert edit_distance("intention", "execution") == 5
    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "abc") == 3

    # Shape 6
    assert knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9

    # Shape 7
    assert coin_change_min_coins([1, 2, 5], 11) == 3
    assert coin_change_min_coins([2], 3) == -1

    print("All template shapes verified.")
