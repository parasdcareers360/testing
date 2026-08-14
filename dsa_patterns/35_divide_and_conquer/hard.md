# Hard — Count of Smaller Numbers After Self

**Source**: LeetCode #315
**Pattern**: Recursion / Divide & Conquer (Merge Sort Variant)
**Difficulty**: Hard

## Problem Statement
Given an integer array `nums`, return an integer array `counts` where `counts[i]` is the number of elements to the **right** of index `i` (i.e., at some index `j > i`) whose value is **strictly smaller** than `nums[i]`.

## Constraints
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Examples
**Example 1**
Input: `nums = [5,2,6,1]`
Output: `[2,1,1,0]`
Explanation: To the right of `5` (index 0): `2,6,1` — of these, `2` and `1` are smaller → count `2`. To the right of `2` (index 1): `6,1` — only `1` is smaller → count `1`. To the right of `6` (index 2): `1` — smaller → count `1`. To the right of `1` (index 3): nothing → count `0`.

**Example 2**
Input: `nums = [-1,-1]`
Output: `[0,0]`
Explanation: Neither `-1` is *strictly* smaller than the other (they're equal), so both counts are `0` even though there is one element to the right of the first.

## Intuition — Why This Pattern
The brute-force approach checks, for every index `i`, every index `j > i`, comparing `nums[j] < nums[i]` directly: `O(n^2)` time. For `n` up to `10^5`, that's up to `10^10` comparisons — far too slow.

This is a natural "hard" escalation of the plain merge-sort divide-and-conquer template (as used in "Sort an Array"): the twist is that we don't actually want the sorted array as the final answer — we want a **side-effect measurement** (a count, per original index) computed *while* the sort happens. This is the key insight: **merging two sorted halves is exactly where cross-comparisons between "left-half elements" and "right-half elements" naturally occur** — and since after dividing the array in half, every index in the right half is, by construction, a later original position than every index in the left half, any time we discover during a merge that a right-half element is smaller than a pending left-half element, we've found one of the "smaller number after self" relationships we need to count.

Concretely: track each value alongside its **original index** (`(value, original_index)` pairs) through the recursion, so that after merge sort finishes, we still know where each value came from. During each merge step, whenever we're about to place a left-half element into the merged result, every right-half element already placed before it (because it was smaller) is a count that should be added to that left-half element's original index. This piggybacks the counting entirely onto the existing `O(n log n)` merge-sort machinery, with no extra asymptotic cost — turning an `O(n^2)` brute force into `O(n log n)`.

## Approach
1. Pair each value with its original index: `pairs = [(nums[0], 0), (nums[1], 1), ..., (nums[n-1], n-1)]`.
2. Initialize a `counts` array of `n` zeros (indexed by *original* index, not by position in any intermediate sorted list).
3. Define `sort_and_count(pairs)`, a merge sort over the list of `(value, original_index)` pairs:
   - **Base case**: if `len(pairs) <= 1`, return it as-is (already trivially sorted, nothing to count).
   - **Divide**: split into `left = pairs[:mid]`, `right = pairs[mid:]`.
   - **Conquer**: recursively compute `sorted_left = sort_and_count(left)`, `sorted_right = sort_and_count(right)`.
   - **Combine with counting** — merge `sorted_left` and `sorted_right` (both ascending by value) using two pointers `i, j` and a running counter `right_taken` (how many right-half elements have been placed into the merge so far):
     - If `sorted_left[i].value <= sorted_right[j].value`: this left element is being placed now. Every right element placed *before* it (there are `right_taken` of them) was strictly smaller than it (because of the tie-breaking rule: we only place a right element ahead of a left element when it is strictly smaller, never when equal). Add `counts[sorted_left[i].original_index] += right_taken`. Append `sorted_left[i]` to the merged result; advance `i`.
     - Else (`sorted_right[j].value < sorted_left[i].value`): append `sorted_right[j]` to the merged result; increment `right_taken`; advance `j`.
     - After one side is exhausted, append the rest of the other side directly — but if `left` still has elements remaining and `right` is exhausted, each remaining left element must still receive `counts[...] += right_taken` (using the final `right_taken` value, since all of `right` has, by then, been confirmed smaller and already placed).
   - Return the merged, sorted list of pairs.
4. Call `sort_and_count(pairs)` (its sorted return value is discarded — only its side effect on `counts` matters) and return `counts`.

## Dry Run
Input: `nums = [5, 2, 6, 1]` → `pairs = [(5,0), (2,1), (6,2), (1,3)]`, `counts = [0,0,0,0]` initially.

**Divide**: `left = [(5,0), (2,1)]`, `right = [(6,2), (1,3)]`.

**Recurse into `left = [(5,0), (2,1)]`**: split into `[(5,0)]` and `[(2,1)]` (both base cases). Merge them:
- `i=0,j=0`: `left[0].value=5 <= right[0].value=2`? No → place `(2,1)` from right, `right_taken = 1`, `j=1`.
- Right exhausted (`j=1` = len). Remaining left `[(5,0)]`: `counts[0] += right_taken(1)` → `counts = [1,0,0,0]`. Append `(5,0)`.
- Merged result: `[(2,1), (5,0)]`.

**Recurse into `right = [(6,2), (1,3)]`**: split into `[(6,2)]` and `[(1,3)]`. Merge them:
- `i=0,j=0`: `left[0].value=6 <= right[0].value=1`? No → place `(1,3)`, `right_taken = 1`, `j=1`.
- Right exhausted. Remaining left `[(6,2)]`: `counts[2] += right_taken(1)` → `counts = [1,0,1,0]`. Append `(6,2)`.
- Merged result: `[(1,3), (6,2)]`.

**Top-level merge** of `sorted_left = [(2,1), (5,0)]` and `sorted_right = [(1,3), (6,2)]`, `right_taken = 0`:
- `i=0,j=0`: `left[0].value=2 <= right[0].value=1`? No → place `(1,3)` from right, `right_taken = 1`, `j=1`.
- `i=0,j=1`: `left[0].value=2 <= right[1].value=6`? Yes → `counts[1] += right_taken(1)` → `counts = [1,1,1,0]`. Place `(2,1)`, `i=1`.
- `i=1,j=1`: `left[1].value=5 <= right[1].value=6`? Yes → `counts[0] += right_taken(1)` → `counts[0] = 1+1 = 2` → `counts = [2,1,1,0]`. Place `(5,0)`, `i=2`.
- `i=2` = len(left) → left exhausted. Append remaining right `[(6,2)]` directly (no count update needed — this branch of the algorithm only updates counts when placing *left* elements).

Final `counts = [2, 1, 1, 0]`. ✅ matches Example 1's expected output `[2,1,1,0]`.

## Solution (Python 3)
```python
from typing import List, Tuple


def count_smaller(nums: List[int]) -> List[int]:
    n = len(nums)
    counts = [0] * n
    pairs = [(val, idx) for idx, val in enumerate(nums)]  # (value, original_index)

    def sort_and_count(arr: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = sort_and_count(arr[:mid])
        right = sort_and_count(arr[mid:])

        merged = []
        i = j = 0
        right_taken = 0

        while i < len(left) and j < len(right):
            if left[i][0] <= right[j][0]:
                counts[left[i][1]] += right_taken
                merged.append(left[i])
                i += 1
            else:
                right_taken += 1
                merged.append(right[j])
                j += 1

        while i < len(left):
            counts[left[i][1]] += right_taken
            merged.append(left[i])
            i += 1

        while j < len(right):
            merged.append(right[j])
            j += 1

        return merged

    sort_and_count(pairs)
    return counts


if __name__ == "__main__":
    print(count_smaller([5, 2, 6, 1]))   # Expected: [2, 1, 1, 0]
    print(count_smaller([-1, -1]))       # Expected: [0, 0]
    print(count_smaller([1, 2, 3, 4]))   # Expected: [0, 0, 0, 0] (already ascending, nothing smaller follows any element)
    print(count_smaller([4, 3, 2, 1]))   # Expected: [3, 2, 1, 0] (strictly descending, everything after is smaller)
```

## Complexity Analysis
- Time: `O(n log n)` — identical shape to plain merge sort: `O(log n)` levels of recursion, each doing `O(n)` total merge work (the counting itself is `O(1)` extra work per comparison, not changing the asymptotic bound).
- Space: `O(n)` for the `pairs`/`left`/`right`/`merged` lists created during recursion, plus `O(n)` for the `counts` output array, plus `O(log n)` recursion stack depth.

## Key Takeaways
- This problem is the canonical example of "divide and conquer for a side-effect, not just the combined value" — the returned sorted array is thrown away; the real answer (`counts`) is accumulated as a byproduct of the merge step's comparisons.
- Common mistake: updating `counts` based on the *current position in the merged list* instead of the element's **original index** — since divide-and-conquer shuffles positions around at every level, you must carry the original index through the whole recursion, or the final `counts` array will be scrambled.
- The tie-breaking rule (`left[i][0] <= right[j][0]` places left first on ties) is what makes the count strictly "smaller" rather than "smaller-or-equal" — flipping that comparison silently changes the problem being solved, which is exactly why Example 2 (`[-1,-1]`, expecting `[0,0]`) is a good self-check.
- Related/variant problems to try next: **Count of Range Sum** (LC 327, a harder variant counting prefix-sum-difference ranges via a similar merge-and-count technique), **Reverse Pairs** (LC 493, counts pairs `i<j` with `nums[i] > 2*nums[j]`, same merge-sort-counting skeleton).
