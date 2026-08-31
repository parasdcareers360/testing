"""
Sliding Window — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from collections import Counter
from typing import Dict, List


# ---------------------------------------------------------------------------
# Shape 1: fixed-size window
# ---------------------------------------------------------------------------
def max_sum_fixed_window_template(nums: List[int], k: int) -> int:
    if len(nums) < k:
        raise ValueError("window size larger than input")
    window_sum = sum(nums[:k])
    best = window_sum
    for right in range(k, len(nums)):
        window_sum += nums[right] - nums[right - k]
        best = max(best, window_sum)
    return best


# ---------------------------------------------------------------------------
# Shape 2: variable-size window, expand-and-jump-left-on-invalid ("longest substring/subarray")
# ---------------------------------------------------------------------------
def longest_no_repeat_template(s: str) -> int:
    last_seen: Dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best


# ---------------------------------------------------------------------------
# Shape 3: variable-size window, shrink-until-invalid ("shortest subarray satisfying X")
# ---------------------------------------------------------------------------
def min_subarray_len_template(target: int, nums: List[int]) -> int:
    left = 0
    total = 0
    best = len(nums) + 1
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return best if best <= len(nums) else 0


# ---------------------------------------------------------------------------
# Shape 4: frequency-matching window ("smallest window containing all of t")
# ---------------------------------------------------------------------------
def min_window_substring_template(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)
    left = 0
    best_len, best_left = float("inf"), 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_len, best_left = right - left + 1, left
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return "" if best_len == float("inf") else s[best_left:best_left + best_len]


if __name__ == "__main__":
    assert max_sum_fixed_window_template([2, 1, 5, 1, 3, 2], 3) == 9  # [5,1,3]
    assert max_sum_fixed_window_template([1, 1, 1, 1], 2) == 2

    assert longest_no_repeat_template("abcabcbb") == 3
    assert longest_no_repeat_template("bbbbb") == 1
    assert longest_no_repeat_template("") == 0

    assert min_subarray_len_template(7, [2, 3, 1, 2, 4, 3]) == 2  # [4,3]
    assert min_subarray_len_template(100, [1, 2, 3]) == 0  # impossible

    assert min_window_substring_template("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window_substring_template("a", "aa") == ""

    print("All template shapes verified.")
