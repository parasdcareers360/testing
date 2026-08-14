# Easy — Subsets

**Source**: LeetCode #78
**Pattern**: Subsets / Backtracking
**Difficulty**: Easy

## Problem Statement
Given an integer array `nums` of **unique** elements, return all possible subsets (the power set). The solution set must not contain duplicate subsets. You may return the solution in any order.

## Constraints
- `1 <= nums.length <= 10`
- `-10 <= nums[i] <= 10`
- All the numbers of `nums` are **unique**.

## Examples
1. Input: `nums = [1,2,3]`
   Output: `[[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]`
   Explanation: Every one of the 2^3 = 8 combinations of "include/exclude" each element is a valid subset, including the empty set and the full set.

2. Input: `nums = [0]`
   Output: `[[],[0]]`
   Explanation: With one element there are only 2^1 = 2 subsets: the empty subset and the subset containing the single element.

## Intuition — Why This Pattern
The brute-force way to think about "all subsets" is to notice that each element has exactly two states: it is either **in** the subset or **not in** the subset. With `n` elements that gives `2^n` total subsets. You could try to generate them by counting from `0` to `2^n - 1` in binary and using each bit as an inclusion flag, but that's clunky to reason about and doesn't generalize to problems where the "choices" aren't binary (e.g. combination sum, permutations).

The backtracking pattern makes this explicit and general: build a subset incrementally by walking through the array once. At each recursive call you have a "path so far" (the current subset being built) and a `start` index marking which elements are still available. You record the path as one valid subset immediately (since *every* prefix of choices — including making no more choices — is a valid subset), then try adding each remaining element one at a time, recurse, and undo (pop) before trying the next one. This "choose -> explore -> un-choose" loop is the entire backtracking template, and it naturally enumerates all `2^n` subsets without duplicates because we only ever look forward (`start` index prevents re-using earlier elements or reordering).

## Approach
1. Initialize an empty list `result` to collect all subsets and an empty list `path` to represent the subset currently being built.
2. Define a recursive helper `backtrack(start)`:
   a. Append a **copy** of `path` to `result` — the current partial path is itself always a valid subset.
   b. Loop `i` from `start` to `len(nums) - 1`:
      - Add `nums[i]` to `path` (choose).
      - Recurse with `backtrack(i + 1)` (explore) — using `i + 1` (not `start + 1`) ensures each element is only considered once per branch and prevents duplicate/reordered subsets.
      - Remove the last element from `path` (un-choose / backtrack).
3. Call `backtrack(0)` to start with the full array available and an empty path.
4. Return `result`.

## Dry Run
Trace `nums = [1, 2, 3]`.

- `backtrack(0)`, path=`[]` -> record `[]`. Loop i=0,1,2.
  - i=0: path=`[1]`. Call `backtrack(1)`, path=`[1]` -> record `[1]`. Loop i=1,2.
    - i=1: path=`[1,2]`. Call `backtrack(2)`, path=`[1,2]` -> record `[1,2]`. Loop i=2.
      - i=2: path=`[1,2,3]`. Call `backtrack(3)`, path=`[1,2,3]` -> record `[1,2,3]`. Loop range is empty (start=3 == len(nums)). Return.
      - pop -> path=`[1,2]`.
    - loop ends. pop -> path=`[1]`.
    - i=2: path=`[1,3]`. Call `backtrack(3)`, path=`[1,3]` -> record `[1,3]`. Loop empty. Return.
    - pop -> path=`[1]`.
  - loop ends. pop -> path=`[]`.
  - i=1: path=`[2]`. Call `backtrack(2)`, path=`[2]` -> record `[2]`. Loop i=2.
    - i=2: path=`[2,3]`. Call `backtrack(3)`, path=`[2,3]` -> record `[2,3]`. Return.
    - pop -> path=`[2]`.
  - pop -> path=`[]`.
  - i=2: path=`[3]`. Call `backtrack(3)`, path=`[3]` -> record `[3]`. Return.
  - pop -> path=`[]`.
- Final `result` = `[[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]` — exactly 8 subsets, matching Example 1.

## Solution (Python 3)
```python
from typing import List


def subsets(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int) -> None:
        # Every partial path is itself a valid subset.
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])       # choose
            backtrack(i + 1)           # explore
            path.pop()                 # un-choose (backtrack)

    backtrack(0)
    return result


if __name__ == "__main__":
    print(subsets([1, 2, 3]))
    # [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]

    print(subsets([0]))
    # [[], [0]]
```

## Complexity Analysis
- Time: O(n * 2^n) — there are 2^n subsets total, and copying each path into `result` costs up to O(n).
- Space: O(n * 2^n) for the output (dominates), plus O(n) recursion depth / auxiliary space for `path`.

## Key Takeaways
- The "record on entry, loop with `i+1` as the next `start`" shape is the canonical way to generate subsets without duplicates — recording on every call (not just at leaves) is what makes it produce *all* subsets rather than just full-length ones.
- Common mistake: appending `path` directly instead of `path[:]` (or `list(path)`) — since `path` is mutated in place, every entry in `result` would end up referring to the same (eventually empty) list.
- Common mistake: recursing with `backtrack(start)` instead of `backtrack(i + 1)`, which would allow reusing the same element multiple times.
- Related problems to try next: **Subsets II** (LeetCode #90, array has duplicates — sort first and skip repeated siblings at the same recursion depth) and **Permutations** (LeetCode #46, same template but track "used" elements instead of a `start` index since order matters).
