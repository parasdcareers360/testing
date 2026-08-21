"""
LeetCode Top Interview 150 — #124 (LeetCode #295)
Find Median from Data Stream
Category: Heap | Difficulty: Hard

Problem
-------
The median is the middle value in an ordered integer list. If the size of the list is even, there
is no single middle value, and the median is the mean of the two middle values.

Design a data structure that supports the following two operations on a stream of numbers, added
one at a time:
- `void addNum(int num)` adds an integer from the data stream to the data structure.
- `double findMedian()` returns the median of all elements added so far.

Constraints
-----------
- -10^5 <= num <= 10^5
- There will be at least one element in the data structure before `findMedian` is called.
- At most 5 * 10^4 calls will be made to `addNum` and `findMedian`.

Examples
--------
Example 1:
    Input:
        ["MedianFinder","addNum","addNum","findMedian","addNum","findMedian"]
        [[],[1],[2],[],[3],[]]
    Output:
        [null,null,null,1.5,null,2.0]
    Explanation:
        MedianFinder mf = new MedianFinder();
        mf.addNum(1);
        mf.addNum(2);
        mf.findMedian(); // (1+2)/2 = 1.5
        mf.addNum(3);
        mf.findMedian(); // 2.0

Intuition
---------
The brute-force approach is to keep every number in a list, and on each `findMedian` call sort a
fresh copy and read off the middle — correct, but O(n log n) *per query*, which is disastrous when
queries interleave with tens of thousands of inserts. A better baseline keeps the list sorted at
all times, inserting each new number at its correct position (via binary search for the position,
O(log n), but O(n) to physically shift array elements to make room) — findMedian becomes O(1), but
addNum is still O(n). The optimal trick needs only *the middle* to be efficiently accessible, not
the whole ordering: split the stream into two halves via two heaps — a max-heap holding the
smaller half of numbers seen so far (so its top is the largest of the small half) and a min-heap
holding the larger half (so its top is the smallest of the large half). Keep the two heaps
balanced in size (differing by at most 1); the median is then either the top of the larger heap
(odd total count) or the average of both heaps' tops (even count) — both O(1) to read, with each
insert costing only O(log n) to rebalance.
"""

import heapq
from typing import List


# ============================================================
# Approach 1: Brute Force (sort on every findMedian call)
# ============================================================
# Idea: store all numbers in an unsorted list; addNum is a plain append.
# findMedian sorts a snapshot of the list every time it's called and reads
# the middle element(s).
# Time:  addNum O(1); findMedian O(n log n) -- resorts everything each call
# Space: O(n) -- stores every number ever added
class MedianFinderBruteForce:
    def __init__(self):
        self._nums: List[int] = []

    def addNum(self, num: int) -> None:  # noqa: N802 (LeetCode's required name)
        self._nums.append(num)

    def findMedian(self) -> float:  # noqa: N802
        ordered = sorted(self._nums)
        n = len(ordered)
        mid = n // 2
        if n % 2 == 1:
            return float(ordered[mid])
        return (ordered[mid - 1] + ordered[mid]) / 2.0


# ============================================================
# Approach 2: Optimal (two heaps -- max-heap lower half, min-heap upper half)
# ============================================================
# Idea: maintain `lo` (a max-heap, via negated values, holding the smaller
# half of all numbers) and `hi` (a min-heap holding the larger half), kept
# balanced so len(lo) is always either == len(hi) or exactly one more.
# Every addNum pushes into `lo` first (to enforce the "value belongs in the
# smaller half" ordering via a compare-and-swap with `lo`'s max), then
# rebalances sizes by moving `lo`'s max into `hi` if `lo` grew too big, or
# pulling `hi`'s min back into `lo` if `hi` overtook it. findMedian is then
# a pure O(1) read: `lo`'s max alone (odd total) or the average of both
# heaps' exposed tops (even total).
# Dry run: addNum(1) -> lo=[-1]; addNum(2) -> push 2 into lo(cmp with max
#   1: 2>=1 so goes to hi instead) -> lo=[-1], hi=[2]; balanced (1,1) ->
#   findMedian: even, (1+2)/2=1.5. addNum(3): 3 >= lo.max(1) -> push to hi
#   -> hi=[2,3], now len(hi)=2 > len(lo)=1 -> move hi.min(2) to lo ->
#   lo=[-2,-1], hi=[3] -> findMedian: odd, lo.max=2.0
# Time:  addNum O(log n); findMedian O(1)
# Space: O(n) -- two heaps together hold every number added
class MedianFinderTwoHeaps:
    def __init__(self):
        self._lo: List[int] = []  # max-heap (negated) -- smaller half
        self._hi: List[int] = []  # min-heap -- larger half

    def addNum(self, num: int) -> None:  # noqa: N802
        # Route into lo first so ties/ordering with lo's current max decide
        # which half num belongs to, then fix up sizes.
        if not self._lo or num <= -self._lo[0]:
            heapq.heappush(self._lo, -num)
        else:
            heapq.heappush(self._hi, num)

        # Rebalance: lo may hold at most one more element than hi.
        if len(self._lo) > len(self._hi) + 1:
            val = -heapq.heappop(self._lo)
            heapq.heappush(self._hi, val)
        elif len(self._hi) > len(self._lo):
            val = heapq.heappop(self._hi)
            heapq.heappush(self._lo, -val)

    def findMedian(self) -> float:  # noqa: N802
        if len(self._lo) > len(self._hi):
            return float(-self._lo[0])
        return (-self._lo[0] + self._hi[0]) / 2.0


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a running median (or any "middle-of-stream" statistic) must be
#   queried repeatedly while data keeps arriving, split the data into two
#   balanced halves with a max-heap/min-heap pair -- it turns an O(n log n)
#   re-sort per query into O(log n) per insert and O(1) per query.
# - Common mistake: forgetting to rebalance heap *sizes* after every insert
#   (letting one heap drift more than one element ahead), which silently
#   breaks the "top of each heap is adjacent to the true median" invariant.
# - Related/variant problems to try next: Sliding Window Median, IPO (a
#   different greedy use of a heap), Kth Largest Element in a Stream.


if __name__ == "__main__":
    # Design problems don't fit the plain args-in/expected-out table, so we
    # replay the same sequence of operations against each implementation
    # and assert every observable result matches across all variants.
    operations = [
        ("addNum", 1), ("addNum", 2), ("findMedian", None),
        ("addNum", 3), ("findMedian", None),
    ]
    expected_results = [None, None, 1.5, None, 2.0]

    implementations = [MedianFinderBruteForce, MedianFinderTwoHeaps]
    for cls in implementations:
        obj = cls()
        results = []
        for op, arg in operations:
            if op == "addNum":
                results.append(obj.addNum(arg))
            elif op == "findMedian":
                results.append(obj.findMedian())
        status = "OK" if results == expected_results else "FAIL"
        print(f"{cls.__name__:20s} results={results!r:40s} -> expected={expected_results!r}  [{status}]")

    # A second, longer scenario mixing negative numbers, duplicates, and
    # more interleaving of odd/even total counts.
    operations2 = [
        ("addNum", -1), ("findMedian", None),
        ("addNum", -2), ("findMedian", None),
        ("addNum", -3), ("findMedian", None),
        ("addNum", 5), ("findMedian", None),
        ("addNum", 5), ("findMedian", None),
        ("addNum", 0), ("findMedian", None),
    ]
    expected_results2 = [
        None, -1.0,
        None, -1.5,
        None, -2.0,
        None, -1.5,
        None, -1.0,
        None, -0.5,
    ]
    for cls in implementations:
        obj = cls()
        results = []
        for op, arg in operations2:
            if op == "addNum":
                results.append(obj.addNum(arg))
            elif op == "findMedian":
                results.append(obj.findMedian())
        status = "OK" if results == expected_results2 else "FAIL"
        print(f"{cls.__name__:20s} scenario2 results={results!r:55s} -> expected={expected_results2!r}  [{status}]")
