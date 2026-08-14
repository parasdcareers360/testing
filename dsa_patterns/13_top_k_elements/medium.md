# Medium — Top K Frequent Elements

**Source**: LeetCode #347
**Pattern**: Top K Elements (Heap)
**Difficulty**: Medium

## Problem Statement
Given an integer array `nums` and an integer `k`, return the `k` most **frequent** elements in the array. You may return the answer in any order.

The twist compared to the Easy version of this pattern: instead of ranking raw values, you must first derive a ranking key (frequency of occurrence) via preprocessing, and it is **guaranteed** that the answer (the set of k most frequent elements) is unique — i.e., there won't be an unresolvable tie for the k-th spot that makes the answer ambiguous.

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `k` is in the range `[1, number of distinct elements in nums]`.
- It is guaranteed that the answer is unique.
- Your algorithm's time complexity should be better than O(n log n), where n is the array's size (i.e., you should not need to fully sort all n elements by frequency).

## Examples
**Example 1**
Input: `nums = [1, 1, 1, 2, 2, 3]`, `k = 2`
Output: `[1, 2]`
Explanation: Frequencies are `1 -> 3`, `2 -> 2`, `3 -> 1`. The two most frequent are `1` and `2`.

**Example 2**
Input: `nums = [1]`, `k = 1`
Output: `[1]`
Explanation: Only one distinct element exists, so it is trivially the most frequent.

**Example 3**
Input: `nums = [4, 4, 1, 1, 1, 2, 2, 2, 2]`, `k = 2`
Output: `[2, 1]` (order doesn't matter — `[1, 2]` is equally valid)
Explanation: Frequencies: `4 -> 2`, `1 -> 3`, `2 -> 4`. The two most frequent are `2` (count 4) and `1` (count 3).

## Intuition — Why This Pattern
**Brute force**: Count frequencies with a hash map (O(n)), then sort the map's `(value, frequency)` pairs by frequency descending (O(d log d), where d = number of distinct elements), and take the first `k`. This works but the problem explicitly asks for something faster than O(n log n) — full sorting of all distinct keys is more work than needed just to identify the top `k`.

**What's inefficient**: Just like ranking raw values in the Easy problem, fully sorting all distinct frequencies determines the *complete* order of every element's rank, but we only need to identify the top `k` — the relative order of the remaining `d - k` elements is irrelevant.

**The insight**: This is the exact same size-k min-heap idiom as "Kth Largest Element in an Array", just with the heap ordered by a **derived key (frequency)** instead of the raw value:
1. First pass: build a frequency map with a hash map, O(n).
2. Push each `(frequency, value)` pair from the map onto a min-heap, popping whenever the heap exceeds size `k` (comparing by frequency). This costs O(d log k), where d is the number of distinct values (d <= n).
3. Whatever remains in the heap at the end is exactly the k most frequent elements.

This achieves O(n + d log k) overall, which is asymptotically better than O(n log n) whenever k is small relative to d — satisfying the problem's explicit performance requirement.

## Approach
1. Build a frequency dictionary `freq` mapping each distinct value in `nums` to its occurrence count — one linear pass.
2. Initialize an empty min-heap `heap`.
3. For each `(value, count)` pair in `freq.items()`:
   a. Push the tuple `(count, value)` onto `heap` (Python tuples compare lexicographically, so this orders by count first).
   b. If `len(heap) > k`, pop the smallest-count element off the heap.
4. After processing all distinct values, `heap` contains exactly the k pairs with the highest frequency.
5. Extract and return just the `value` from each remaining `(count, value)` pair (order doesn't matter per the problem statement).

## Dry Run
Trace `nums = [1, 1, 1, 2, 2, 3]`, `k = 2`.

**Step 1 — build frequency map:**
`freq = {1: 3, 2: 2, 3: 1}`

**Step 2 — push each (count, value) pair onto a size-2 min-heap:**

| Pair pushed | Heap contents (as a set) | Size > k=2? | Pop smallest | Heap after |
|-------------|----------------------------|-------------|----------------|------------|
| (3, 1) | {(3,1)} | no (size 1) | - | {(3,1)} |
| (2, 2) | {(2,2), (3,1)} | no (size 2) | - | {(2,2), (3,1)} |
| (1, 3) | {(1,3), (2,2), (3,1)} | yes (size 3 > 2) | pop (1,3) | {(2,2), (3,1)} |

**Step 3 — extract values:** the heap now holds `{(2, 2), (3, 1)}`. Extracting the second element of each tuple gives `[2, 1]` (or `[1, 2]` depending on extraction order) — matching the expected output `[1, 2]` (order-independent).

## Solution (Python 3)
```python
import heapq
from collections import Counter
from typing import List


def top_k_frequent(nums: List[int], k: int) -> List[int]:
    """Return the k most frequent elements using a frequency map + size-k min-heap."""
    freq = Counter(nums)  # O(n): value -> count

    heap: List[tuple] = []
    for value, count in freq.items():
        heapq.heappush(heap, (count, value))
        if len(heap) > k:
            heapq.heappop(heap)

    return [value for _, value in heap]


if __name__ == "__main__":
    print(sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)))              # Expected: [1, 2]
    print(top_k_frequent([1], 1))                                    # Expected: [1]
    print(sorted(top_k_frequent([4, 4, 1, 1, 1, 2, 2, 2, 2], 2)))     # Expected: [1, 2]
```

## Complexity Analysis
- Time: O(n + d log k), where n = `len(nums)` and d = number of distinct values (d <= n). Building the frequency map is O(n); each of the d heap pushes/pops costs O(log k). This is strictly better than O(n log n) whenever k is small.
- Space: O(d + k) — O(d) for the frequency map, O(k) for the heap.

## Key Takeaways
- The Top-K pattern generalizes cleanly: the heap can be ordered by any derived ranking key (frequency, distance, custom score), not just the raw element value — always push a tuple `(key, payload)` so the heap orders by key while you keep the original item alongside.
- A common mistake is sorting all distinct `(value, frequency)` pairs fully (O(d log d)) when the problem explicitly asks for better than O(n log n) — recognize that "top k" almost never requires a full sort.
- Python's `Counter.most_common(k)` internally does something equivalent to this heap approach and is a handy one-liner alternative once you understand the underlying technique.
- Related/variant problems to try next: **Kth Largest Element in an Array** (same heap idea on raw values, simpler baseline) and **K Closest Points to Origin** (heap ordered by Euclidean/squared distance as the derived key) and **Reorganize String** (frequency-ordered max-heap combined with greedy placement — a harder variant).
