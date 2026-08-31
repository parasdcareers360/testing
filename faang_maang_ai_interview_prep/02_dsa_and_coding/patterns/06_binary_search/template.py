"""
Binary Search — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from bisect import bisect_left, bisect_right
from typing import Callable, List


# ---------------------------------------------------------------------------
# Shape 1: classic binary search (exact match)
# ---------------------------------------------------------------------------
def binary_search_template(nums: List[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# ---------------------------------------------------------------------------
# Shape 2: first / last occurrence (boundary search)
# ---------------------------------------------------------------------------
def first_occurrence_template(nums: List[int], target: int) -> int:
    i = bisect_left(nums, target)
    return i if i < len(nums) and nums[i] == target else -1


def last_occurrence_template(nums: List[int], target: int) -> int:
    i = bisect_right(nums, target) - 1
    return i if i >= 0 and nums[i] == target else -1


def first_occurrence_manual(nums: List[int], target: int) -> int:
    """Hand-rolled version, for when bisect is off the table."""
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid
            right = mid - 1  # keep searching left for an earlier match
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result


# ---------------------------------------------------------------------------
# Shape 3: search space binary search ("minimize the max" / "maximize the min")
# ---------------------------------------------------------------------------
def search_space_template(
    lo: int, hi: int, feasible: Callable[[int], bool]
) -> int:
    """
    Finds the smallest x in [lo, hi] for which feasible(x) is True, given that
    feasible is monotonic: False, False, ..., False, True, True, ..., True.
    """
    left, right = lo, hi
    while left < right:
        mid = left + (right - left) // 2
        if feasible(mid):
            right = mid
        else:
            left = mid + 1
    return left


def min_capacity_to_ship(weights: List[int], days: int) -> int:
    def days_needed(capacity: int) -> int:
        trips, current_load = 1, 0
        for w in weights:
            if current_load + w > capacity:
                trips += 1
                current_load = 0
            current_load += w
        return trips

    return search_space_template(
        max(weights), sum(weights), lambda cap: days_needed(cap) <= days
    )


# ---------------------------------------------------------------------------
# Shape 4: search in rotated sorted array
# ---------------------------------------------------------------------------
def search_rotated_template(nums: List[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:  # left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


if __name__ == "__main__":
    nums = [1, 3, 5, 7, 9, 11]
    assert binary_search_template(nums, 7) == 3
    assert binary_search_template(nums, 4) == -1

    dup = [1, 2, 2, 2, 3]
    assert first_occurrence_template(dup, 2) == 1
    assert last_occurrence_template(dup, 2) == 3
    assert first_occurrence_template(dup, 4) == -1
    assert first_occurrence_manual(dup, 2) == 1

    assert min_capacity_to_ship([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert min_capacity_to_ship([3, 2, 2, 4, 1, 4], 3) == 6

    rotated = [4, 5, 6, 7, 0, 1, 2]
    assert search_rotated_template(rotated, 0) == 4
    assert search_rotated_template(rotated, 3) == -1

    print("All template shapes verified.")
