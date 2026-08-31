# Binary Search

> **Type:** Study notes

## Why interviewers ask this

Binary search *looks* trivial (everyone can recite "find the middle") but the boundary conditions
(`<` vs `<=`, `mid` vs `mid + 1`) are where candidates fall apart under pressure. Interviewers use
it to check whether you can reason precisely about invariants, not whether you know the name of the
algorithm. It also shows up disguised — "search space binary search" — where the array itself
isn't even sorted, only some monotonic *property* of the answer is, and recognizing that disguise is
the real signal at Medium/Hard difficulty.

## The core idea

Binary search only requires a **monotonic predicate**: a function `f(x)` that is `False` for a
prefix of the search space and `True` for the rest (or vice versa), so you can discard half the
space on every check. A sorted array is the simplest case (`f(i) = nums[i] >= target`), but the same
shape applies to "search space binary search" where the space is a range of possible *answers*
(e.g. capacities, speeds, distances) rather than array indices.

Recognize this pattern when you see:
- "Find X in a sorted array" (classic lookup, first/last occurrence)
- "Find the minimum/maximum value such that condition Y holds" (binary search on the answer)
- "Sorted array, but rotated" (modified classic binary search)
- Anything promising O(log n) on a problem that looks O(n) at first glance

## Key techniques

### 1. Classic binary search (exact match)
```python
def binary_search(nums: list[int], target: int) -> int:
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
```
`left + (right - left) // 2` instead of `(left + right) // 2` avoids overflow in languages with
fixed-width ints — not a real concern in Python, but say it out loud anyway; interviewers notice
when you know why the idiom exists even in a language where it doesn't matter.

### 2. Finding boundaries (first/last occurrence) with `bisect`
```python
from bisect import bisect_left, bisect_right

def first_occurrence(nums: list[int], target: int) -> int:
    i = bisect_left(nums, target)
    return i if i < len(nums) and nums[i] == target else -1

def last_occurrence(nums: list[int], target: int) -> int:
    i = bisect_right(nums, target) - 1
    return i if i >= 0 and nums[i] == target else -1
```
`bisect_left` finds the leftmost insertion point (first index where `nums[i] >= target`);
`bisect_right` finds the rightmost insertion point (first index where `nums[i] > target`). Knowing
these cold saves you from hand-rolling boundary binary search live — but be ready to hand-roll it
anyway, since some interviewers explicitly forbid the module to test the underlying logic.

### 3. Search space binary search ("minimize the maximum")
```python
def min_capacity_to_ship(weights: list[int], days: int) -> int:
    def days_needed(capacity: int) -> int:
        trips, current_load = 1, 0
        for w in weights:
            if current_load + w > capacity:
                trips += 1
                current_load = 0
            current_load += w
        return trips

    left, right = max(weights), sum(weights)
    while left < right:
        mid = left + (right - left) // 2
        if days_needed(mid) <= days:  # mid is "feasible" -> try smaller
            right = mid
        else:
            left = mid + 1
    return left
```
The search space is *capacities*, not array indices. The predicate `days_needed(mid) <= days` is
monotonic (larger capacity never needs more days), which is the only requirement for binary search
to apply — the input array doesn't need to be sorted at all.

### 4. Search in rotated sorted array
```python
def search_rotated(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:          # left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                # right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```
At every step, at least one half (`[left, mid]` or `[mid, right]`) is guaranteed sorted — determine
which half is sorted first, then check if `target` falls inside that half's range to decide which
side to discard.

## Complexity to know cold

| Technique | Time | Space |
|---|---|---|
| Classic binary search | O(log n) | O(1) |
| `bisect_left` / `bisect_right` | O(log n) | O(1) |
| Search space binary search | O(n log(range)) — n for the feasibility check per step | O(1) |
| Search in rotated sorted array | O(log n) | O(1) |

## Exercises

1. Implement `first_occurrence` and `last_occurrence` by hand without `bisect`, using `left <=
   right` loops, then verify they agree with the `bisect`-based versions on `[1,2,2,2,3]` for
   `target=2` and `target=4` (not present).
2. Given `weights = [1,2,3,4,5,6,7,8,9,10]` and `days = 5`, trace `min_capacity_to_ship` by hand:
   what does `left`/`right` converge to, and why is the answer exactly `days_needed(answer) <= 5`
   but `days_needed(answer - 1) > 5`?
