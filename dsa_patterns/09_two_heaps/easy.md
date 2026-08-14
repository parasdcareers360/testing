# Easy — Find Median from Data Stream

**Source**: LeetCode #295
**Pattern**: Two Heaps
**Difficulty**: Easy

## Problem Statement
Design a data structure that supports the following two operations on a stream of integers arriving one at a time:
- `add_num(num)`: adds an integer from the data stream to the data structure.
- `find_median()`: returns the median of all elements added so far.

The median is the middle value when the numbers are sorted. If the count of numbers is even, the median is the average of the two middle values. Answers within `1e-5` of the actual value are accepted.

## Constraints
- `-10^5 <= num <= 10^5`
- The total number of calls to `add_num` and `find_median` combined does not exceed `5 * 10^4`.
- `find_median` is only called after at least one call to `add_num`.

## Examples
**Example 1**
Operations: `add_num(1)`, `add_num(2)`, `find_median()`
Output of `find_median()`: `1.5`
Explanation: After adding `1` and `2`, the sorted data is `[1, 2]`; the median is the average of both, `1.5`.

**Example 2**
Operations: `add_num(1)`, `add_num(2)`, `find_median()`, `add_num(3)`, `find_median()`
Output of the two `find_median()` calls: `1.5`, then `2.0`
Explanation: After adding `3`, the sorted data becomes `[1, 2, 3]`; the median is the single middle value, `2`.

## Intuition — Why This Pattern
A naive approach keeps a list of every number seen so far and, on every `find_median()` call, sorts the whole list and reads off the middle element(s) — O(n log n) per query, or O(n^2 log n) across n queries in total. A slightly better naive approach keeps the list always sorted by inserting each new number at its correct position (e.g., via `bisect.insort`), but insertion into a sorted list still requires shifting elements, costing O(n) per insertion — still O(n^2) overall for a long stream. The real problem is that both approaches maintain a *fully* sorted order when all we actually need is fast access to the *middle*.

The insight: split the stream into two halves — a max-heap holding the smaller half (so its largest element, sitting right at the boundary, is instantly available at the top) and a min-heap holding the larger half (so its smallest element, the other boundary value, is instantly available at the top). If we keep the two heaps balanced in size (differing by at most one), the median is always derivable in O(1) from just the two heap tops, and each insertion costs only O(log n) to push/rebalance — no full sort ever needed.

## Approach
1. Maintain `small`, a max-heap holding the smaller half of the numbers (implemented as a min-heap of **negated** values, since Python's `heapq` only supports min-heaps).
2. Maintain `large`, a plain min-heap holding the larger half.
3. `add_num(num)`:
   a. Push `-num` onto `small`.
   b. If both heaps are non-empty and the max of `small` (`-small[0]`) exceeds the min of `large` (`large[0]`), pop from `small` and push that value onto `large` — this fixes any ordering violation.
   c. Rebalance sizes: if `small` has grown more than one larger than `large`, move its top to `large`; if `large` has grown larger than `small`, move its top to `small`.
4. `find_median()`:
   a. If `len(small) > len(large)`, return `-small[0]` (small holds the extra middle element).
   b. Otherwise (equal sizes), return the average of `-small[0]` and `large[0]`.

## Dry Run
Operations: `add_num(1)`, `add_num(2)`, `find_median()`, `add_num(3)`, `find_median()`

| Step | Action | small (max-heap, negated) | large (min-heap) | find_median() |
|------|--------|------------------------------|--------------------|-----------------|
| 1 | `add_num(1)` | push -1 → `[-1]` | `[]` | — |
| 2 | `add_num(2)` | push -2 → `[-1,-2]`, top max=2; sizes 2 vs 0 → move max (2) to large | `small=[-1]`, `large=[2]` | — |
| 3 | `find_median()` | sizes equal (1,1) | | avg(1, 2) = **1.5** |
| 4 | `add_num(3)` | push -3 → `small=[-1,-3]`, max=3; but max(3) > min(large)=2 → move 3 to large; now `small=[-1]`, `large=[2,3]`; sizes 1 vs 2 → move large's min (2) back to small | `small=[-1,-2]`, `large=[3]` | — |
| 5 | `find_median()` | sizes: small=2, large=1, small bigger | | `-small[0]` = `-(-2)` = **2.0** |

Both `find_median()` calls return `1.5` then `2.0`, matching the expected outputs.

## Solution (Python 3)
```python
import heapq


class MedianFinder:
    def __init__(self):
        self.small = []  # max-heap, storing negated values (smaller half)
        self.large = []  # min-heap (larger half)

    def add_num(self, num: int) -> None:
        heapq.heappush(self.small, -num)

        # Ensure every element in `small` <= every element in `large`
        if self.small and self.large and (-self.small[0] > self.large[0]):
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)

        # Rebalance sizes so they differ by at most 1
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        elif len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2.0


if __name__ == "__main__":
    mf = MedianFinder()
    mf.add_num(1)
    mf.add_num(2)
    print(mf.find_median())  # Expected: 1.5
    mf.add_num(3)
    print(mf.find_median())  # Expected: 2.0
```

## Complexity Analysis
- Time: O(log n) per `add_num` call (heap push/pop); O(1) per `find_median` call.
- Space: O(n) to store all numbers seen so far, split across the two heaps.

## Key Takeaways
- The Two Heaps pattern maintains an always-balanced split (max-heap for the lower half, min-heap for the upper half), trading O(log n) insertion for O(1) median lookup.
- Common mistake: forgetting that Python's `heapq` is min-heap only, so a max-heap must be simulated via negation — and forgetting to negate values back when reading or returning them.
- Another common bug: fixing the size balance *before* fixing the small-vs-large ordering violation. Always resolve ordering first, then rebalance sizes.
- Related/variant problems to try next: **Sliding Window Median**, **IPO (Maximize Capital)**.
