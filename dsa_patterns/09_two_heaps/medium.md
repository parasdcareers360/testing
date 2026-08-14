# Medium — Sliding Window Median

**Source**: LeetCode #480
**Pattern**: Two Heaps
**Difficulty**: Medium

## Problem Statement
The median is the middle value in an ordered list of numbers; if the list size is even, the median is the average of the two middle values. Given an integer array `nums` and an integer `k`, there is a sliding window of size `k` that moves from the very left of the array to the very right, one position at a time. Only `k` numbers are inside the window at any point. Each time the window slides one position to the right, return the median of the current window's contents. Return an array of the medians of all windows.

## Constraints
- `1 <= k <= nums.length <= 100`
- `-2^31 <= nums[i] <= 2^31 - 1`

## Examples
**Example 1**
Input: `nums = [1,3,-1,-3,5,3,6,7]`, `k = 3`
Output: `[1,-1,-1,3,5,6]`
Explanation: Window `[1,3,-1]` sorted is `[-1,1,3]`, median `1`. Window `[3,-1,-3]` sorted is `[-3,-1,3]`, median `-1`. Window `[-1,-3,5]` sorted is `[-3,-1,5]`, median `-1`. Window `[-3,5,3]` sorted is `[-3,3,5]`, median `3`. Window `[5,3,6]` sorted is `[3,5,6]`, median `5`. Window `[3,6,7]` sorted is `[3,6,7]`, median `6`.

**Example 2**
Input: `nums = [1,2,3,4,2,3,1,4,2]`, `k = 3`
Output: `[2,3,3,3,2,3,2]`
Explanation: The seven windows are `[1,2,3]`, `[2,3,4]`, `[3,4,2]`, `[4,2,3]`, `[2,3,1]`, `[3,1,4]`, `[1,4,2]`, with medians `2, 3, 3, 3, 2, 3, 2` respectively.

## Intuition — Why This Pattern
The brute-force approach re-sorts the current window from scratch at every position — O(k log k) per window, O(n * k log k) overall — even though each new window shares `k-1` elements with the previous one, throwing away almost all of that reusable work.

The basic two-heaps median finder (as used for "Find Median from Data Stream") supports fast *insertion*, but a plain heap has no efficient way to remove an arbitrary value buried in the middle — heaps only support O(log n) removal of their own top. That is exactly the new twist this problem adds: elements must be **removed** (the window's expiring left element) as well as added (the window's incoming right element).

The fix is **lazy deletion**: keep the same max-heap(`small`)/min-heap(`large`) split, but when an element needs to leave, don't dig it out of the heap immediately — just record it in a "pending deletion" counter. Whenever a heap's top happens to be a value that's pending deletion, pop and discard it at that point (this is the only place we ever need to check). This lets both insertion and removal be handled in amortized O(log k) time, without ever needing true arbitrary-position heap deletion.

## Approach
1. Maintain `small` (max-heap via negation) and `large` (min-heap), tracking the current window's elements split at the median boundary, with logical size counters `small_count` / `large_count` (counts of *active*, non-pending-deletion elements — the physical heaps may also contain stale entries not yet popped).
2. Maintain a `delayed` map counting how many times each value is currently pending lazy deletion.
3. `prune(heap)`: while the heap's top value has a positive pending-deletion count, decrement that count and physically pop it.
4. `add(num)`: decide which heap `num` belongs to by comparing it against the current max of `small`; push it there; then rebalance.
5. `remove(num)` (the window's outgoing left element): decide its side the same way. If it happens to be sitting exactly at that heap's top, pop it immediately; otherwise mark it in `delayed` for later lazy removal. Then rebalance.
6. `rebalance()`: prune both heaps' tops first (so comparisons are never against stale entries), then move one real element between heaps if the size difference exceeds the allowed balance (`small_count` should equal `large_count`, or be exactly one more, for odd `k`).
7. Slide across `nums`: for each index `i`, `add(nums[i])`; once `i >= k`, `remove(nums[i-k])`; once the window is full (`i >= k-1`), prune both tops and record the median (`-small[0]` if `k` is odd, else the average of both tops).

## Dry Run
Input: `nums = [1,3,-1,-3,5,3,6,7]`, `k = 3` (odd, so median = top of `small`)

| i | num added | num removed | small (active values) | large (active values) | median recorded |
|---|-----------|-------------|--------------------------|---------------------------|--------------------|
| 0 | 1 | — | {1} | {} | — (window not full) |
| 1 | 3 | — | {1} | {3} | — (window not full) |
| 2 | -1 | — | {-1, 1} | {3} | **1** |
| 3 | -3 | 1 | {-3, -1} | {3} | **-1** |
| 4 | 5 | 3 | {-3, -1} | {5} | **-1** |
| 5 | 3 | -1 | {-3, 3} | {5} | **3** |
| 6 | 6 | -3 | {3, 5} | {6} | **5** |
| 7 | 7 | 5 | {3, 6} | {7} | **6** |

At every step, `small` holds the two smallest active values in the current window (with its top being the median), and `large` holds the single largest. The recorded medians are `[1, -1, -1, 3, 5, 6]`, exactly matching the expected output. (Internally, some outgoing values — like the `1` removed at `i=3` — are not sitting at a heap's top when removed, so they are only marked in `delayed` and physically discarded later once they surface at the top; this never affects the reported median because `prune` always runs before a top is read.)

## Solution (Python 3)
```python
import heapq
from collections import defaultdict
from typing import List


def median_sliding_window(nums: List[int], k: int) -> List[float]:
    small: List[int] = []   # max-heap of the smaller half, stored negated
    large: List[int] = []   # min-heap of the larger half
    small_count = 0
    large_count = 0
    delayed = defaultdict(int)

    def prune(heap: List[int], negate: bool) -> None:
        while heap:
            top = -heap[0] if negate else heap[0]
            if delayed[top] > 0:
                delayed[top] -= 1
                heapq.heappop(heap)
            else:
                return

    def rebalance() -> None:
        nonlocal small_count, large_count
        prune(small, True)
        prune(large, False)
        if small_count > large_count + 1:
            val = -heapq.heappop(small)
            small_count -= 1
            heapq.heappush(large, val)
            large_count += 1
            prune(small, True)
        elif large_count > small_count:
            val = heapq.heappop(large)
            large_count -= 1
            heapq.heappush(small, -val)
            small_count += 1
            prune(large, False)

    def add(num: int) -> None:
        nonlocal small_count, large_count
        prune(small, True)
        if small_count == 0 or num <= -small[0]:
            heapq.heappush(small, -num)
            small_count += 1
        else:
            heapq.heappush(large, num)
            large_count += 1
        rebalance()

    def remove(num: int) -> None:
        nonlocal small_count, large_count
        prune(small, True)
        if small_count > 0 and num <= -small[0]:
            small_count -= 1
            if num == -small[0]:
                heapq.heappop(small)
            else:
                delayed[num] += 1
        else:
            large_count -= 1
            if large and num == large[0]:
                heapq.heappop(large)
            else:
                delayed[num] += 1
        rebalance()

    result: List[float] = []
    for i, num in enumerate(nums):
        add(num)
        if i >= k:
            remove(nums[i - k])
        if i >= k - 1:
            prune(small, True)
            prune(large, False)
            if k % 2 == 1:
                result.append(float(-small[0]))
            else:
                result.append((-small[0] + large[0]) / 2.0)
    return result


if __name__ == "__main__":
    print(median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))  # Expected: [1, -1, -1, 3, 5, 6]
    print(median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3))  # Expected: [2, 3, 3, 3, 2, 3, 2]
```

## Complexity Analysis
- Time: O(n log k) amortized — each element is pushed and eventually popped a bounded number of times across the whole run, and lazy deletion means removals never require scanning a heap for an arbitrary element.
- Space: O(k) for the two heaps, plus O(k) for the `delayed` map in the worst case.

## Key Takeaways
- Lazy deletion is the standard technique for supporting "remove an arbitrary element" from a heap-based structure: never search for it, just mark it and let `prune` discard it later once it naturally surfaces at the top.
- Common mistake: comparing a heap's top against another value *before* pruning it — a stale, already-deleted entry sitting at the top will silently produce a wrong answer if it's read before being pruned away.
- Related/variant problems to try next: **Find Median from Data Stream** (the same two-heap balancing idea without the removal twist), **Sliding Window Maximum** (a different pattern — Monotonic Deque — for a related but distinct sliding-window aggregate).
