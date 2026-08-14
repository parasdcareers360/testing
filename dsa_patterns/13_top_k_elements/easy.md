# Easy — Kth Largest Element in an Array

**Source**: LeetCode #215
**Pattern**: Top K Elements (Heap)
**Difficulty**: Easy

## Problem Statement
Given an integer array `nums` and an integer `k`, return the `k`-th largest element in the array.

Note that "k-th largest" means the k-th largest element in **sorted (descending) order**, not the k-th *distinct* element. For example, in `[3, 3, 2]`, the 2nd largest element is `3` (there are two 3's; the sequence sorted descending is `[3, 3, 2]`, and the 2nd position holds `3`).

You must solve it without fully sorting the array where possible (or at least understand and demonstrate the heap-based approach), since sorting the entire array is more work than necessary just to find one order statistic.

## Constraints
- `1 <= k <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Examples
**Example 1**
Input: `nums = [3, 2, 1, 5, 6, 4]`, `k = 2`
Output: `5`
Explanation: Sorted descending: `[6, 5, 4, 3, 2, 1]`. The 2nd largest is `5`.

**Example 2**
Input: `nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]`, `k = 4`
Output: `4`
Explanation: Sorted descending: `[6, 5, 5, 4, 3, 3, 2, 2, 1]`. The 4th largest is `4`.

## Intuition — Why This Pattern
**Brute force**: Sort the entire array in descending order and return `nums[k-1]`. This costs O(n log n) time and, if we needed to repeat the query for many different `k` values or on a growing stream, we'd be resorting the whole array every time — wasteful when we only care about a small set of "top" elements.

**What's inefficient**: Full sorting determines the *complete* order of every element, but we only need the relative order of the top `k` elements — the rest of the array's internal ordering is irrelevant to the answer.

**The insight**: Maintain a **min-heap of size k**. Push elements onto the heap one at a time; whenever the heap grows past size `k`, pop the smallest element off. After processing the entire array, the heap contains exactly the `k` largest elements seen so far, and the smallest element remaining in that heap (the heap's root) is precisely the k-th largest element overall — because everything smaller than it has already been evicted, and everything currently in the heap is one of the top `k`. This runs in O(n log k) time, which beats O(n log n) whenever `k` is much smaller than `n`, and it generalizes naturally to streaming input (you never need to see the whole array at once).

## Approach
1. Initialize an empty min-heap `heap`.
2. For each number `num` in `nums`:
   a. Push `num` onto `heap`.
   b. If `len(heap) > k`, pop the smallest element off the heap.
3. After processing all elements, the heap's root (smallest element in the heap) is the k-th largest element in the array — return it.

## Dry Run
Trace `nums = [3, 2, 1, 5, 6, 4]`, `k = 2`.

| Step | num | Push | Heap contents (as a set, min-heap) | Size > k? | Pop smallest | Heap after |
|------|-----|------|--------------------------------------|-----------|----------------|------------|
| 1 | 3 | push 3 | {3} | no (size 1) | - | {3} |
| 2 | 2 | push 2 | {2, 3} | no (size 2) | - | {2, 3} |
| 3 | 1 | push 1 | {1, 2, 3} | yes (size 3 > 2) | pop 1 | {2, 3} |
| 4 | 5 | push 5 | {2, 3, 5} | yes (size 3 > 2) | pop 2 | {3, 5} |
| 5 | 6 | push 6 | {3, 5, 6} | yes (size 3 > 2) | pop 3 | {5, 6} |
| 6 | 4 | push 4 | {4, 5, 6} | yes (size 3 > 2) | pop 4 | {5, 6} |

Final heap: `{5, 6}`. The smallest element in this heap (its root) is `5`, which is the 2nd largest element overall — matches the expected output.

## Solution (Python 3)
```python
import heapq
from typing import List


def find_kth_largest(nums: List[int], k: int) -> int:
    """Return the k-th largest element using a size-k min-heap."""
    heap: List[int] = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]  # root of the min-heap = k-th largest overall


if __name__ == "__main__":
    print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))                  # Expected: 5
    print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))         # Expected: 4
```

## Complexity Analysis
- Time: O(n log k) — each of the n elements triggers at most one push and one pop on a heap of size at most k+1, and each heap operation costs O(log k).
- Space: O(k) — the heap never holds more than k elements at a time.

## Key Takeaways
- The core Top-K idiom: use a **min-heap of size k** to find the k largest elements (the heap's root is the smallest of the "keepers", making it cheap to evict); symmetrically, use a **max-heap of size k** to find the k smallest elements.
- A common mistake is using a max-heap of the whole array (or a min-heap without capping its size at k) — that degrades back to O(n log n) and defeats the purpose of the pattern.
- Python's `heapq` module only provides a min-heap; to simulate a max-heap, push negated values (`-num`) — useful to remember for variants of this pattern.
- Related/variant problems to try next: **Top K Frequent Elements** (heap keyed by frequency instead of raw value) and **Kth Largest Element in a Stream** (LeetCode #703 — same heap idea, but the heap persists across repeated `add` calls instead of being built once).
