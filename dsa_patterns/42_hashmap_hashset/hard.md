# Hard — Longest Consecutive Sequence

**Source**: LeetCode #128
**Pattern**: HashMap / HashSet
**Difficulty**: Hard

## Problem Statement
Given an unsorted array of integers `nums`, return the length of the **longest run of consecutive integers** (i.e., a sequence of integers with no gaps, like `[3, 4, 5, 6]`) that all appear somewhere in `nums`. The consecutive numbers do **not** need to appear in the array in order or adjacent to each other positionally — you only care whether each integer *value* in a candidate run exists anywhere in the array.

You must solve this in **O(n) time** — the tightest complexity requirement in this folder. Note that this immediately rules out the seemingly obvious approach of sorting the array first (sorting is O(n log n)), which is what makes this a genuinely hard hashset problem rather than a straightforward one.

## Constraints
- `0 <= nums.length <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- The algorithm must run in **O(n)** time (not O(n log n)).

## Examples
**Example 1**
Input: `nums = [100, 4, 200, 1, 3, 2]`
Output: `4`
Explanation: The longest run of consecutive integers is `[1, 2, 3, 4]`, which has length 4. Note these values appear scattered at positions 3, 5, 4, 1 in the original array — order in the array is irrelevant.

**Example 2**
Input: `nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]`
Output: `9`
Explanation: The longest run is `[0, 1, 2, 3, 4, 5, 6, 7, 8]`, length 9. Note `0` appears twice in the input (duplicate), but it only counts once toward the consecutive run.

## Intuition — Why This Pattern
**Naive approach**: Sort `nums`, then do a single linear scan counting the longest run of consecutive values (resetting the running count whenever there's a gap or handling duplicates by skipping them). This is correct and reasonably simple, but sorting costs O(n log n), which **violates the problem's explicit O(n) requirement** — this is exactly why this problem is "hard" for the HashMap/HashSet pattern: the obvious, simple solution is disallowed, forcing you to find a genuinely linear-time technique.

**What's inefficient about sorting here**: Sorting does more work than necessary — it fully orders *all* n elements, when all we actually need is, for each distinct value, an O(1) way to check "is `value - 1` present?" and "is `value + 1` present?" without needing any global order at all.

**The insight (HashSet-driven sequence expansion)**: Put every number from `nums` into a **hashset** (this handles de-duplication for free, and gives O(1) average membership checks). Now, for each **distinct** number `num` in the set, check whether `num - 1` is in the set. If it is, then `num` is *not* the start of a consecutive run (some earlier run already covers it, or will be counted when we process that smaller starting point) — skip it, to avoid redundant work. If `num - 1` is **not** in the set, then `num` genuinely is the start of a run — walk forward (`num + 1`, `num + 2`, ...) counting how far the consecutive run extends while each next value is present in the set, and record the total run length. Because every run is only ever fully walked once (starting exactly from its true minimum, guaranteed by the `num - 1 not in set` check), and every number is only "walked over" as part of the one run it belongs to, the total work across all runs combined is O(n), even though it looks like nested loops.

## Approach
1. If `nums` is empty, return `0` immediately.
2. Build a hashset `num_set` from all elements of `nums` (this also deduplicates).
3. Initialize `longest = 0`.
4. For each `num` in `num_set` (iterate over the **set**, not the original array, so duplicates are only processed once):
   a. If `num - 1` is in `num_set`, skip this `num` entirely (it is not the start of a run — some smaller number will trigger the walk that includes this one).
   b. Otherwise (`num` is the start of a run): initialize `current = num` and `length = 1`. While `current + 1` is in `num_set`: increment `current` and `length`.
   c. Update `longest = max(longest, length)`.
5. Return `longest`.

## Dry Run
`nums = [100, 4, 200, 1, 3, 2]`. `num_set = {100, 4, 200, 1, 3, 2}` (order doesn't matter for a set; shown here in a convenient order for tracing).

| num being examined | num - 1 in set? | Action | length found (if start of run) | longest so far |
|---------------------|-------------------|--------|-----------------------------------|-------------------|
| 100                 | 99 not in set     | start of a run: walk 101? not in set -> length=1 | 1 | 1 |
| 4                   | 3 in set          | skip (not a run start) | — | 1 |
| 200                 | 199 not in set    | start of a run: walk 201? not in set -> length=1 | 1 | 1 |
| 1                   | 0 not in set      | start of a run: walk 2 in set(len=2), 3 in set(len=3), 4 in set(len=4), 5 not in set -> stop | 4 | 4 |
| 3                   | 2 in set          | skip (not a run start) | — | 4 |
| 2                   | 1 in set          | skip (not a run start) | — | 4 |

(The exact iteration order over a Python set isn't guaranteed, but every element is visited exactly once regardless of order, and the result is order-independent since each run is only fully walked from its true minimum.)

Final `longest = 4`, matching Example 1's expected output `4` (the run `[1,2,3,4]`).

## Solution (Python 3)
```python
from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums:
            return 0

        num_set = set(nums)
        longest = 0

        for num in num_set:
            # Only start counting from the true beginning of a run.
            if (num - 1) in num_set:
                continue

            current = num
            length = 1
            while (current + 1) in num_set:
                current += 1
                length += 1

            longest = max(longest, length)

        return longest


if __name__ == "__main__":
    sol = Solution()
    print(sol.longestConsecutive([100, 4, 200, 1, 3, 2]))              # 4
    print(sol.longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))      # 9
    print(sol.longestConsecutive([]))                                  # 0
    print(sol.longestConsecutive([1, 2, 0, 1]))                         # 3 (duplicate '1' ignored)
```

## Complexity Analysis
- Time: O(n) amortized. Building the set is O(n). The main loop looks like it could be O(n^2) in the worst case (a loop over all numbers, each potentially triggering an inner while-loop), but because the `num - 1 not in set` guard ensures every run is only ever walked starting from its true minimum, and each number is visited by the inner while-loop **at most once total** across the entire algorithm (once it's "consumed" as part of walking a run, it's never re-walked as the start of another), the total work done inside all the while-loops combined, across every iteration of the outer loop, is bounded by O(n).
- Space: O(n) for the hashset.

## Key Takeaways
- The key trick that makes this O(n) rather than O(n^2): only ever start an expansion walk from a number that is provably the **minimum** of its run (checked via `num - 1 not in set`). Without this guard, you'd redundantly re-walk the same run once for every one of its members, degrading to O(n^2) in the worst case (e.g., an array that is itself one giant consecutive run).
- Common mistake: iterating over the original array `nums` (with duplicates) in the main loop instead of the deduplicated `num_set` — this doesn't break correctness (duplicates still get skipped by the `num-1` guard, or redundantly re-walk the same run since the guard doesn't fire on duplicates of already-consumed starts... actually re-walking the *same* number twice as a "start" wastes time but doesn't change the answer) but it's cleaner and slightly more efficient to iterate the set directly.
- Common mistake: trying to solve this with sorting because it feels more "natural" — remind yourself the problem explicitly requires O(n), and sorting is O(n log n), disqualifying that approach even though it would pass on many judges with generous time limits (LeetCode does enforce this though, and more importantly, understanding *why* the hashset approach achieves true O(n) is the whole point of the exercise).
- Related/variant problems to try next: **Subarray Sum Equals K** (see medium.md in this folder — hashmap-of-frequency rather than hashset-of-membership) and **Longest Consecutive Sequence II / Binary Tree Longest Consecutive Sequence** style variants that adapt the same "is neighbor present?" expansion idea to trees or graphs instead of a flat integer range.
