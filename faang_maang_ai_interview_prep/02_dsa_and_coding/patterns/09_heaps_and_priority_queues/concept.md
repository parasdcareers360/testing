# Heaps & Priority Queues

> **Type:** Study notes

## Why interviewers ask this

Heaps are the go-to structure whenever a problem needs "the current smallest/largest so far,
repeatedly, while the data keeps changing" — top-K, running medians, merging many sorted sources.
Interviewers use this pattern to check whether you reach for O(log n) incremental maintenance instead
of re-sorting the whole collection on every update, which is a very common production-code
performance bug (repeatedly sorting a list in a loop) as much as an interview one.

## The core idea

Python's `heapq` module only implements a **min-heap** on a plain `list` — there's no built-in
max-heap or a dedicated `PriorityQueue` class you'd reach for by default. Everything in this pattern
is either using the min-heap directly, or negating values on the way in/out to simulate a max-heap.
The heap gives O(log n) push/pop while always keeping the minimum (or, negated, the maximum) at
index 0 accessible in O(1).

Recognize this pattern when you see:
- "Find the K largest/smallest/most-frequent elements"
- "Merge K sorted lists/arrays"
- "Find the running median of a stream"
- "Schedule tasks by priority" / "process events by earliest time"

## Key techniques

### 1. `heapq` basics and the max-heap negation trick
```python
import heapq

min_heap: list[int] = []
heapq.heappush(min_heap, 5)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 3)
heapq.heappop(min_heap)          # 1 — heapq only ever gives you the minimum

max_heap: list[int] = []
for x in [5, 1, 3]:
    heapq.heappush(max_heap, -x)  # store negated
-heapq.heappop(max_heap)          # 5 — negate again on the way out
```
`heapq.heapify(list)` converts an existing list into a heap in O(n) (not O(n log n) — it's cheaper
than pushing n items one at a time), which matters when you're told the input is already available
as a full list rather than arriving one element at a time.

### 2. Top-K pattern (bounded heap)
```python
def top_k_frequent(nums: list[int], k: int) -> list[int]:
    from collections import Counter
    counts = Counter(nums)
    heap: list[tuple[int, int]] = []
    for val, freq in counts.items():
        heapq.heappush(heap, (freq, val))
        if len(heap) > k:
            heapq.heappop(heap)   # evict the current smallest, keeping only the top k
    return [val for freq, val in heap]
```
Keeping the heap size capped at `k` means it holds candidates for "top k," and popping the minimum
whenever it overflows is correct because the minimum is exactly the one item guaranteed *not* to be
in the top k once you have k+1 candidates. This runs in O(n log k), better than O(n log n) full sort
when `k` is small relative to `n`.

### 3. Merge K sorted lists
```python
def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int, int]] = []   # (value, list_index, element_index)
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []
    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return result
```
The heap holds one "frontier" element per list at all times. Including `list_index`/`element_index`
in the tuple both breaks ties deterministically (so Python never tries to compare list objects
directly, which would raise `TypeError`) and lets you find the next element to push once the current
minimum is popped.

### 4. Two-heap median pattern
```python
class MedianFinder:
    def __init__(self):
        self.small: list[int] = []  # max-heap (negated) — lower half
        self.large: list[int] = []  # min-heap — upper half

    def add_num(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```
Two heaps split the stream into a lower half (max-heap, so its max is the largest of the small
values) and an upper half (min-heap, so its min is the smallest of the large values). Every insert
routes through `small` first, then rebalances by moving one element across — this keeps the two
halves sizes within 1 of each other at all times, so the median is always readable in O(1) from the
tops.

## Complexity to know cold

| Operation | Time | Space |
|---|---|---|
| `heapq.heappush` / `heappop` | O(log n) | O(1) |
| `heapq.heapify` | O(n) | O(1) extra |
| Top-K via bounded heap | O(n log k) | O(k) |
| Merge K sorted lists (total N elements) | O(N log k) | O(k) for the heap |
| Two-heap median, per `add_num` | O(log n) | O(n) total |

## Exercises

1. Implement `top_k_frequent` from memory, then compare it against the `Counter.most_common(k)`
   one-liner from [Arrays & Hashing](../01_arrays_and_hashing/concept.md) — know both, and be ready
   to explain when the heap version's O(n log k) beats `most_common`'s effectively O(n log n) sort.
2. Trace `MedianFinder` by hand inserting `5, 15, 1, 3` in that order — after each insert, state the
   size of `small` and `large` and the current median, to confirm the rebalancing invariant holds.
