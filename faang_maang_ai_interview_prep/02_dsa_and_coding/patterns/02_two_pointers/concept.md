# Two Pointers

> **Type:** Study notes

## Why interviewers ask this

Two pointers is the pattern that separates candidates who reach for extra space by reflex from
candidates who first ask "does the input structure (sorted order, array-ness) let me avoid that?"
It's cheap for the interviewer to verify you actually understand the invariant (as opposed to
having memorized a shape), because a single wrong pointer-move direction breaks the solution
immediately and visibly during your manual trace.

## The core idea

Instead of nested loops (O(n²)) or extra hash-map space (O(n)) to compare pairs of elements, walk
two indices through the array (or string / linked list) according to a rule that guarantees you
never need to revisit a position. The rule almost always depends on the input being **sorted** (or
sortable) or on a **monotonic property** you can exploit (e.g., water trapped can only be bounded
by the shorter wall).

Recognize this pattern when you see:
- "sorted array" + "find a pair/triplet with property X" (opposite-direction pointers)
- "in-place" + "remove/overwrite elements" (same-direction / fast-slow pointers)
- "container holds water" / "area between two lines" (opposite-direction, greedy shrink)
- linked list + "detect a cycle" / "find the middle" (fast-slow pointers)

## Key techniques

### 1. Opposite-direction pointers on a sorted array (two-sum II)
```python
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1   # need a bigger sum -> drop the smaller value
        else:
            right -= 1  # need a smaller sum -> drop the larger value
    return []
```
The invariant: at every step, one of the two remaining extremes *cannot* be part of any valid
pair, so it's safe to discard it forever. This is what makes O(n) correct instead of just fast.

### 2. Container With Most Water (opposite-direction, greedy shrink)
```python
def max_area(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        width = right - left
        best = max(best, width * min(heights[left], heights[right]))
        # moving the taller wall inward can only shrink width without raising the limiting height
        # -> always move the shorter wall, it's the only move that could improve the answer
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best
```
The Trapping Rain Water intuition builds on the same idea: water trapped above index `i` is
bounded by `min(max_height_to_left, max_height_to_right) - height[i]`. A two-pointer version
tracks `left_max`/`right_max` while walking inward, always advancing the side with the smaller
max, because that side's bound is already known and final.

### 3. Same-direction pointers (in-place overwrite / remove duplicates)
```python
def remove_duplicates_sorted(nums: list[int]) -> int:
    if not nums:
        return 0
    write = 0  # last position of a confirmed-unique element
    for read in range(1, len(nums)):
        if nums[read] != nums[write]:
            write += 1
            nums[write] = nums[read]
    return write + 1  # new logical length
```
`read` scans ahead looking for the next value worth keeping; `write` marks the boundary of the
"cleaned" prefix. This shape generalizes directly to "remove all instances of val", "move zeroes
to the end", and "remove duplicates allowing at most 2 copies" (compare `nums[read]` against
`nums[write - 1]` instead).

### 4. Fast/slow pointers (cycle detection intuition)
```python
def has_cycle_intuition(get_next):
    """get_next(node) -> next node. Full linked-list version lives in 05_linked_lists/."""
    slow = fast = get_next(None)  # placeholder start; see 05_linked_lists for real Node usage
    while fast is not None and get_next(fast) is not None:
        slow = get_next(slow)
        fast = get_next(get_next(fast))
        if slow is fast:
            return True
    return False
```
Slow moves 1 step, fast moves 2 steps. If there's a cycle, fast laps slow inside it and they meet;
if there's no cycle, fast hits the end first. The full Floyd's cycle detection (including finding
the cycle's *start* node) is covered with real `Node` objects in
[`05_linked_lists/concept.md`](../05_linked_lists/concept.md) — here, just recognize that
"two pointers moving at different speeds" is the same family as opposite-direction pointers: both
exploit a monotonic relationship to avoid revisiting state.

## Complexity to know cold

| Technique | Time | Space | Requires |
|---|---|---|---|
| Opposite-direction (sorted array) | O(n) | O(1) | sorted input (or sort first: O(n log n)) |
| Container With Most Water | O(n) | O(1) | none — greedy shrink works on unsorted heights |
| Same-direction in-place overwrite | O(n) | O(1) | none, but usually needs sorted input for "duplicates" problems |
| Fast/slow (cycle detection) | O(n) | O(1) | a "next" relation (linked list, or functional graph) |

## Exercises

1. Implement `two_sum_sorted` and `max_area` from memory, then trace both by hand on
   `heights = [1,8,6,2,5,4,8,3,7]` (expected max area: 49, between indices 1 and 8).
2. Given an unsorted array, write a two-pointer solution for "move all zeroes to the end while
   preserving the relative order of non-zero elements" in-place, O(n) time, O(1) space — then
   explain out loud why this is the same `read`/`write` shape as `remove_duplicates_sorted`.
