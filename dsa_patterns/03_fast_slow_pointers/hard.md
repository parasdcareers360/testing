# Hard — Find the Duplicate Number

**Source**: LeetCode #287
**Pattern**: Fast & Slow Pointers
**Difficulty**: Hard

## Problem Statement
Given an array of integers `nums` containing `n + 1` integers where each integer is in the range `[1, n]` inclusive, there is exactly one repeated number in `nums` (it may be repeated more than twice). Return this repeated number.

You must solve the problem **without modifying** the array `nums` and using only **constant extra space**.

## Constraints
- `1 <= n <= 10^5`
- `nums.length == n + 1`
- `1 <= nums[i] <= n`
- All the integers in `nums` appear only once except for precisely one integer which appears two or more times.

## Examples
**Example 1**
Input: `nums = [1, 3, 4, 2, 2]`
Output: `2`
Explanation: `n = 4` (since length is 5 = n+1), values are in `[1,4]`. The value `2` appears twice.

**Example 2**
Input: `nums = [3, 1, 3, 4, 2]`
Output: `3`
Explanation: The value `3` appears twice.

## Intuition — Why This Pattern
This is a hard problem because it **combines** two ideas: it looks like a job for **Cyclic Sort** (pattern #5) since values are restricted to `[1, n]` — but Cyclic Sort requires modifying the array in place via swaps, which this problem explicitly forbids. A hash-set brute force finds the duplicate in O(n) time but uses O(n) space, which is also forbidden. Sorting the array first would let you scan for adjacent equal values in O(n log n) time — but sorting typically requires either modifying the input or O(n) extra space for a copy, and it's slower than the O(n) bound we can achieve.

The key trick that resolves the conflicting constraints: **treat the array itself as a implicit "linked list" / functional graph**, without ever writing to it. Define a function `f(i) = nums[i]`. Since every value is in `[1, n]` and there are `n+1` indices `[0, n]`, this function maps `{0, 1, ..., n}` into `{1, ..., n}` — meaning it's not injective (a value in `[1,n]` cannot be mapped to by all n+1 possible indices without some value repeating as an output). Walking `index -> nums[index] -> nums[nums[index]] -> ...` therefore *must* eventually revisit a node, forming a cycle in this implicit graph — and the node where the cycle begins is provably the duplicate value! This turns the problem into **exactly** the "Linked List Cycle II" problem (the medium problem in this pattern), just where "next pointer" is replaced by "array value as index," and we never mutate the array — we only read it.

## Approach
1. Initialize `slow = nums[0]`, `fast = nums[0]` — think of this as starting from a virtual entry node 0 and immediately taking one step (equivalent to starting "before" index 0 conceptually; the standard implementation starts both at `nums[0]` and applies the function to advance).
2. **Phase 1 — find a meeting point** (same as Floyd's cycle detection): repeat `slow = nums[slow]` (one step) and `fast = nums[nums[fast]]` (two steps) until `slow == fast`.
3. **Phase 2 — find the cycle's entrance** (= the duplicate value): reset `slow = nums[0]` (back to the start), keep `fast` at the meeting point. Move both one step at a time (`slow = nums[slow]`, `fast = nums[fast]`) until `slow == fast`. That common value is the duplicate number.
4. Return `slow` (or equivalently `fast`, they are equal at that point).

## Dry Run
Input: `nums = [1, 3, 4, 2, 2]` (indices 0..4, so n=4)

Think of it as function `f(i) = nums[i]`: f(0)=1, f(1)=3, f(2)=4, f(3)=2, f(4)=2.

**Phase 1**:
- Init: slow = nums[0] = 1. fast = nums[0] = 1.
- Step 1: slow = nums[slow] = nums[1] = 3. fast = nums[nums[fast]] = nums[nums[1]] = nums[3] = 2.
- Step 2: slow = nums[3] = 2. fast = nums[nums[2]] = nums[4] = 2.
- Check: slow(2) == fast(2)? **Yes!** Meeting point = 2.

**Phase 2**:
- slow = nums[0] = 1 (reset). fast = 2 (meeting point, unchanged).
- Check slow==fast? 1 vs 2 → no.
- Step: slow = nums[1] = 3. fast = nums[2] = 4.
- Check slow==fast? 3 vs 4 → no.
- Step: slow = nums[3] = 2. fast = nums[4] = 2.
- Check slow==fast? 2 vs 2 → **Yes!**

Return `2` — matches the expected output.

## Solution (Python 3)
```python
from typing import List


def find_duplicate(nums: List[int]) -> int:
    # Phase 1: find the meeting point inside the cycle
    slow = nums[0]
    fast = nums[0]

    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    # Phase 2: find the entrance to the cycle (the duplicate number)
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]

    return slow


if __name__ == "__main__":
    print(find_duplicate([1, 3, 4, 2, 2]))  # Expected: 2
    print(find_duplicate([3, 1, 3, 4, 2]))  # Expected: 3
    print(find_duplicate([1, 1]))           # Expected: 1
```

## Complexity Analysis
- Time: O(n) — both phases of Floyd's algorithm run in O(n) time on a functional graph with n+1 nodes.
- Space: O(1) — only `slow` and `fast` scalar variables are used; the input array is never modified and no auxiliary structures are created.

## Key Takeaways
- This problem is the textbook example of **recognizing a disguised pattern**: the array-as-function-graph reframing turns "find a duplicate under strict space/mutation constraints" into "Linked List Cycle II," even though there's no linked list in sight. Learning to spot "values in `[1,n]` with array of length `n+1`, one duplicate, no mutation allowed" as a Floyd's-cycle signal is the main lesson.
- Common mistakes: forgetting that `fast` needs a double application `nums[nums[fast]]` per phase-1 step (not `nums[fast]` twice sequentially misapplied) — actually both are the same thing computed correctly, but a common bug is computing `fast = nums[fast]` twice using an already-updated intermediate incorrectly, or starting the reset pointer at index `0` instead of `nums[0]` in Phase 2.
- Contrast with **Missing Number** or **Set Mismatch**, which allow O(n) space or array mutation and are typically solved with Cyclic Sort or XOR instead — this problem's "no mutation, no extra space" constraint is exactly what rules those out and forces Floyd's cycle approach.
- Related/variant problems to try next: **Linked List Cycle II**, **Circular Array Loop**.
