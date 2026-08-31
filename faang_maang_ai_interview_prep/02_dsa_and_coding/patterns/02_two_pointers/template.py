"""
Two Pointers — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import List, Optional


# ---------------------------------------------------------------------------
# Shape 1: opposite-direction pointers on a sorted array
# ---------------------------------------------------------------------------
def two_sum_sorted_template(nums: List[int], target: int) -> List[int]:
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return []


# ---------------------------------------------------------------------------
# Shape 2: opposite-direction, greedy shrink (container / trapping-water family)
# ---------------------------------------------------------------------------
def max_area_template(heights: List[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        width = right - left
        best = max(best, width * min(heights[left], heights[right]))
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best


def trap_rain_water_template(heights: List[int]) -> int:
    if not heights:
        return 0
    left, right = 0, len(heights) - 1
    left_max, right_max = heights[left], heights[right]
    trapped = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, heights[left])
            trapped += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            trapped += right_max - heights[right]
    return trapped


# ---------------------------------------------------------------------------
# Shape 3: same-direction pointers (in-place read/write overwrite)
# ---------------------------------------------------------------------------
def remove_duplicates_sorted_template(nums: List[int]) -> int:
    if not nums:
        return 0
    write = 0
    for read in range(1, len(nums)):
        if nums[read] != nums[write]:
            write += 1
            nums[write] = nums[read]
    return write + 1


def move_zeroes_template(nums: List[int]) -> None:
    """In-place: move all zeroes to the end, preserving order of non-zero elements."""
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1


# ---------------------------------------------------------------------------
# Shape 4: fast/slow pointers (cycle detection intuition — see 05_linked_lists for real Node use)
# ---------------------------------------------------------------------------
class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def has_cycle_template(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


if __name__ == "__main__":
    assert two_sum_sorted_template([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum_sorted_template([1, 2, 3, 4, 6], 6) == [1, 3]

    assert max_area_template([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_area_template([1, 1]) == 1

    assert trap_rain_water_template([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap_rain_water_template([]) == 0

    nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    new_len = remove_duplicates_sorted_template(nums)
    assert new_len == 5
    assert nums[:new_len] == [0, 1, 2, 3, 4]

    zeroes_input = [0, 1, 0, 3, 12]
    move_zeroes_template(zeroes_input)
    assert zeroes_input == [1, 3, 12, 0, 0]

    # 3 -> 4 -> 5 -> 3 (cycle) vs. a clean 1 -> 2 -> None
    a, b, c = ListNode(3), ListNode(4), ListNode(5)
    a.next, b.next, c.next = b, c, a
    assert has_cycle_template(a) is True
    x, y = ListNode(1), ListNode(2)
    x.next = y
    assert has_cycle_template(x) is False

    print("All template shapes verified.")
