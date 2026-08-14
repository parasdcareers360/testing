# Medium — Combination Sum

**Source**: LeetCode #39
**Pattern**: Subsets / Backtracking
**Difficulty**: Medium

## Problem Statement
Given an array of distinct integers `candidates` and a target integer `target`, return a list of all unique combinations of `candidates` where the chosen numbers sum to `target`. You may return the combinations in any order.

The **same number** may be chosen from `candidates` an **unlimited number of times**. Two combinations are unique if the frequency of at least one of the chosen numbers is different.

## Constraints
- `1 <= candidates.length <= 30`
- `2 <= candidates[i] <= 40`
- All elements of `candidates` are distinct.
- `1 <= target <= 40`

## Examples
1. Input: `candidates = [2,3,6,7]`, `target = 7`
   Output: `[[2,2,3],[7]]`
   Explanation: `2+2+3 = 7` and `7 = 7` are the only two combinations (using each candidate any number of times) that sum to 7.

2. Input: `candidates = [2,3,5]`, `target = 8`
   Output: `[[2,2,2,2],[2,3,3],[3,5]]`
   Explanation: These are the three distinct multisets of `2, 3, 5` (with repetition allowed) whose elements sum to 8.

## Intuition — Why This Pattern
This looks similar to Subsets, but it adds a twist: elements can be **reused** and we only want combinations that hit an exact `target` sum, so brute force can't just enumerate all `2^n` subsets — the search space is effectively unbounded without a stopping rule (you could keep re-adding the same number forever). A naive brute force would try to generate every possible multiset of candidates up to some arbitrary length and check sums, which has no natural bound and would be both incorrect (infinite in principle) and wildly redundant (many orderings represent the same multiset).

The backtracking insight is to treat this exactly like Subsets but change two things: (1) instead of a fixed-size array walk, track the **remaining target** and stop (prune) a branch as soon as `remaining < 0` (or, if we sort first, as soon as the current candidate exceeds what's left — everything after it is even bigger, so we can break immediately); and (2) allow reusing the current index (`backtrack(i, ...)` instead of `backtrack(i + 1, ...)`) so a number can be picked multiple times, while still using a `start` index to prevent picking indices *before* the current one — that's what stops us from generating `[2,3,2]` and `[3,2,2]` as "different" combinations when they're really the same multiset. Sorting the candidates first lets us prune early with a `break` the moment a candidate is too big, which is the key efficiency gain over unpruned brute force.

## Approach
1. Sort `candidates` in ascending order (enables early pruning/breaking).
2. Initialize `result = []` and `path = []`.
3. Define `backtrack(start, remaining)`:
   a. If `remaining == 0`: this path sums exactly to `target` — append a copy of `path` to `result` and return.
   b. Loop `i` from `start` to `len(candidates) - 1`:
      - Let `c = candidates[i]`. If `c > remaining`, **break** the loop entirely (since the array is sorted, every later candidate is also too big).
      - Add `c` to `path` (choose).
      - Recurse: `backtrack(i, remaining - c)` — note we pass `i`, **not** `i + 1`, so `c` itself may be reused in the recursive call.
      - Remove `c` from `path` (un-choose).
4. Call `backtrack(0, target)`.
5. Return `result`.

## Dry Run
Trace `candidates = [2,3,6,7]` (already sorted), `target = 7`.

- `backtrack(0, 7)`, path=`[]`. remaining=7≠0. Loop i=0..3.
  - i=0, c=2 (≤7): path=`[2]`. Call `backtrack(0, 5)`.
    - remaining=5≠0. Loop i=0..3.
      - i=0, c=2: path=`[2,2]`. Call `backtrack(0, 3)`.
        - remaining=3≠0. Loop i=0..3.
          - i=0, c=2: path=`[2,2,2]`. Call `backtrack(0,1)`.
            - remaining=1≠0. i=0, c=2>1 -> break immediately. Return (no solutions).
          - pop -> path=`[2,2]`.
          - i=1, c=3: path=`[2,2,3]`. Call `backtrack(1,0)`.
            - remaining=0 -> **record `[2,2,3]`**. Return.
          - pop -> path=`[2,2]`.
          - i=2, c=6>3 -> break.
        - Return.
      - pop -> path=`[2]`.
      - i=1, c=3: path=`[2,3]`. Call `backtrack(1,2)`.
        - remaining=2≠0. i=1,c=3>2 -> break. Return.
      - pop -> path=`[2]`.
      - i=2, c=6>5 -> break.
    - Return.
  - pop -> path=`[]`.
  - i=1, c=3: path=`[3]`. Call `backtrack(1,4)`.
    - remaining=4≠0. Loop i=1..3.
      - i=1, c=3: path=`[3,3]`. Call `backtrack(1,1)`.
        - remaining=1≠0. i=1,c=3>1 -> break. Return.
      - pop -> path=`[3]`.
      - i=2, c=6>4 -> break.
    - Return.
  - pop -> path=`[]`.
  - i=2, c=6: path=`[6]`. Call `backtrack(2,1)`.
    - remaining=1≠0. i=2,c=6>1 -> break. Return.
  - pop -> path=`[]`.
  - i=3, c=7: path=`[7]`. Call `backtrack(3,0)`.
    - remaining=0 -> **record `[7]`**. Return.
  - pop -> path=`[]`.
- Final `result = [[2,2,3],[7]]`, matching Example 1.

## Solution (Python 3)
```python
from typing import List


def combinationSum(candidates: List[int], target: int) -> List[List[int]]:
    candidates = sorted(candidates)
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break  # sorted, so every later candidate is also too big
            path.append(c)          # choose
            backtrack(i, remaining - c)  # explore (i, not i+1: allow reuse)
            path.pop()               # un-choose

    backtrack(0, target)
    return result


if __name__ == "__main__":
    print(combinationSum([2, 3, 6, 7], 7))
    # [[2, 2, 3], [7]]

    print(combinationSum([2, 3, 5], 8))
    # [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
```

## Complexity Analysis
- Time: O(2^target) worst case (loose bound — each candidate of value >= 1 could in principle be included many times before hitting target; in practice the `c > remaining` break and the sort prune the tree heavily). A tighter characterization is O(N^(T/M + 1)) where N is the number of candidates, T is target, and M is the minimum candidate value, since the recursion depth is bounded by T/M.
- Space: O(T / M) for recursion depth / `path` length in the worst case, plus O(number of valid combinations x average combination length) for the output.

## Key Takeaways
- The key variant vs. plain Subsets: pass `i` (not `i + 1`) to the recursive call to allow **reusing the same element**, while still using `start`/`i` as a floor to prevent generating permutations of the same multiset.
- Sorting first is what makes the `break`-on-too-large pruning valid and effective — without sorting you'd have to use `continue` and check every remaining candidate, which is much slower.
- Common mistake: forgetting to copy `path` (`path[:]`) when appending to `result`, or reusing `i + 1` and silently turning this into "each number used at most once" (which is actually **Combination Sum II**, LeetCode #40, where candidates *can* have duplicates and each is used at most once — that variant also needs a `if i > start and candidates[i] == candidates[i-1]: continue` duplicate-skip).
- Related problems to try next: **Combination Sum II** (#40, duplicates + use-once) and **Combination Sum III** (#216, fixed-size k-element combinations from 1-9 summing to target).
