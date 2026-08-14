# Easy — Jump Game

**Source**: LeetCode #55
**Pattern**: Greedy Algorithms
**Difficulty**: Easy

## Problem Statement
You are given an integer array `nums`. You start at index `0`. Each element `nums[i]` represents the maximum number of steps you are allowed to jump forward from index `i` (you may jump anywhere from `1` up to `nums[i]` steps forward, or choose to jump fewer steps — you are not required to use the maximum).

Return `true` if you can reach the last index of the array, or `false` otherwise.

## Constraints
- `1 <= nums.length <= 10^4`
- `0 <= nums[i] <= 10^5`

## Examples
**Example 1**
Input: `nums = [2, 3, 1, 1, 4]`
Output: `true`
Explanation: Jump 1 step from index 0 to index 1, then 3 steps to the last index (index 4).

**Example 2**
Input: `nums = [3, 2, 1, 0, 4]`
Output: `false`
Explanation: No matter which jumps you make earlier, you will always land on index 3, whose value is 0, which permanently strands you there — index 4 becomes unreachable.

## Intuition — Why This Pattern
**Brute force**: From index 0, try every possible jump length (recursively try all reachable next indices), and check if any sequence of choices reaches the last index. This is a backtracking/DFS search with branching factor up to `nums[i]` at each step, giving exponential O(2^n)-ish worst-case time — massively overkill for a question that's ultimately just "yes or no, reachable".

**What's inefficient**: The brute force explores many different *paths* to the same index, redoing work. But we don't actually care *how* we get to an index — we only care about *the furthest index reachable so far*. Once we know the furthest reachable position after considering the first `i` elements, all specific path choices that achieve that same reach are equivalent for the purposes of answering the yes/no question.

**The insight (Greedy)**: Scan through the array once, left to right, maintaining a single number: `max_reach`, the furthest index we know we can reach using any combination of jumps from index 0 through the current index. At each index `i`, if `i > max_reach`, we've hit a gap we can never cross (nothing before `i` could ever jump this far), so return `false` immediately. Otherwise, greedily update `max_reach = max(max_reach, i + nums[i])` — always keep the best (furthest) reach seen so far, since a strictly greater reach can never hurt and only helps future steps. If we finish the scan without ever failing, or if `max_reach` ever reaches or exceeds the last index, we know it's reachable.

## Approach
1. Let `n = len(nums)`. If `n <= 1`, return `true` immediately (you start on the last index already).
2. Initialize `max_reach = 0` (before considering any jumps, you can trivially "reach" index 0 — where you start).
3. Iterate `i` from `0` to `n - 1`:
   a. If `i > max_reach`, index `i` is unreachable given everything seen so far — return `false` immediately.
   b. Update `max_reach = max(max_reach, i + nums[i])`.
   c. (Optional early exit) If `max_reach >= n - 1`, you can already reach the last index — return `true` immediately.
4. If the loop completes without returning `false`, return `true` (the fact that we processed every index without ever finding `i > max_reach` means the last index was always reachable along the way).

## Dry Run
Trace `nums = [2, 3, 1, 1, 4]` (`n = 5`, last index = 4).

Initialize `max_reach = 0`.

| i | nums[i] | i > max_reach? | max_reach = max(max_reach, i+nums[i]) | max_reach >= 4 (n-1)? |
|---|---------|------------------|------------------------------------------|--------------------------|
| 0 | 2 | 0 > 0? no | max(0, 0+2)=2 | 2>=4? no |
| 1 | 3 | 1 > 2? no | max(2, 1+3)=4 | 4>=4? **yes** -> return `true` |

The loop exits early at `i = 1` because `max_reach` already reached `4`, the last index. Return `true` — matches the expected output.

Now trace `nums = [3, 2, 1, 0, 4]` (`n = 5`, last index = 4) to confirm the failure path.

Initialize `max_reach = 0`.

| i | nums[i] | i > max_reach? | max_reach update | max_reach >= 4? |
|---|---------|------------------|----------------------|---------------------|
| 0 | 3 | 0 > 0? no | max(0, 0+3)=3 | 3>=4? no |
| 1 | 2 | 1 > 3? no | max(3, 1+2)=3 | 3>=4? no |
| 2 | 1 | 2 > 3? no | max(3, 2+1)=3 | 3>=4? no |
| 3 | 0 | 3 > 3? no | max(3, 3+0)=3 | 3>=4? no |
| 4 | 4 | **4 > 3? yes** -> return `false` | | |

At `i = 4`, `max_reach` is still stuck at `3` (index 3's own value of `0` contributed nothing), and `4 > 3`, meaning index 4 is unreachable given everything scanned so far. Return `false` — matches the expected output.

## Solution (Python 3)
```python
from typing import List


def can_jump(nums: List[int]) -> bool:
    """Greedily track the furthest reachable index in a single left-to-right pass."""
    n = len(nums)
    if n <= 1:
        return True

    max_reach = 0
    for i in range(n):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + nums[i])
        if max_reach >= n - 1:
            return True

    return True


if __name__ == "__main__":
    print(can_jump([2, 3, 1, 1, 4]))  # Expected: True
    print(can_jump([3, 2, 1, 0, 4]))  # Expected: False
```

## Complexity Analysis
- Time: O(n) — a single pass through the array, constant work per index.
- Space: O(1) — only the `max_reach` accumulator is used.

## Key Takeaways
- The greedy insight in reachability/scheduling problems is often "track the best single summary value seen so far" (here, furthest reachable index) instead of enumerating every possible path — this collapses an exponential search into a linear scan.
- A common mistake is checking `i >= max_reach` instead of `i > max_reach` for the failure condition — `i == max_reach` is still fine (you can stand exactly at the current furthest-reachable index), only strictly exceeding it is fatal.
- Greedy correctness here relies on the fact that a larger `max_reach` is *never* worse than a smaller one for any future decision — this "monotonic dominance" argument is the hallmark of when greedy is provably optimal, and it's worth explicitly checking for in any greedy problem you attempt.
- Related/variant problems to try next: **Jump Game II** (LeetCode #45 — find the *minimum number* of jumps needed, not just feasibility, via a greedy "level expansion" variant) and **Gas Station** (a greedy problem with a similar "track a running feasibility metric" flavor) and **Jump Game III/IV** (variants that add different reachability constraints, sometimes requiring BFS instead of pure greedy).
