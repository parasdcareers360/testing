# Easy — Climbing Stairs

**Source**: LeetCode #70
**Pattern**: Dynamic Programming — 1D
**Difficulty**: Easy

## Problem Statement
You are climbing a staircase that has `n` steps to reach the top. Each time you can either climb `1` or `2` steps. In how many distinct ways can you climb to the top?

For example, with 3 steps, you could climb: 1+1+1, 1+2, or 2+1 — three distinct sequences of moves, so the answer is 3.

## Constraints
- `1 <= n <= 45`

## Examples
**Example 1**
```
Input: n = 2
Output: 2
```
Explanation: There are two ways to climb to the top: (1 step + 1 step), or (2 steps). So the answer is 2.

**Example 2**
```
Input: n = 3
Output: 3
```
Explanation: The three distinct ways are: (1+1+1), (1+2), (2+1). Note (1+2) and (2+1) are counted separately since the order of steps matters (they are different sequences of moves).

## Intuition — Why This Pattern
**Brute force**: Recursively try both choices (take 1 step, or take 2 steps) from every position, counting how many complete paths reach exactly step `n`. This works: `ways(n) = ways(n-1) + ways(n-2)` with base cases `ways(0)=1, ways(1)=1`, but implemented as plain recursion without memoization, this recomputes `ways(k)` for the same `k` an exponential number of times (it's structurally identical to naive Fibonacci recursion), giving O(2^n) time.

**What's inefficient**: `ways(5)` calls `ways(4)` and `ways(3)`; `ways(4)` itself calls `ways(3)` again — the same subproblem `ways(3)` gets recomputed from scratch every time it's needed, and this duplication compounds exponentially as `n` grows.

**The insight**: Since the number of ways to reach step `i` depends only on the number of ways to reach steps `i-1` and `i-2` (both smaller, already-solved subproblems), store each computed value in a 1D array (or even just two rolling variables) the first time it's computed, and reuse it every subsequent time it's needed. This is the core 1D DP insight: build up `dp[i]` from `dp[i-1]` and `dp[i-2]` in a single forward pass, turning O(2^n) into O(n) time (and O(1) space if only the last two values are kept, since nothing further back is ever needed again).

## Approach
1. Handle small `n` directly: if `n == 1`, return 1; if `n == 2`, return 2.
2. Initialize `prev2 = 1` (ways to reach step 1) and `prev1 = 2` (ways to reach step 2).
3. For `i` from 3 to `n`:
   a. Compute `curr = prev1 + prev2` (ways to reach step `i` = ways to reach `i-1` [then take 1 step] plus ways to reach `i-2` [then take 2 steps]).
   b. Shift the rolling variables: `prev2 = prev1`, `prev1 = curr`.
4. After the loop, `prev1` holds `ways(n)`. Return `prev1`.

## Dry Run
Example 2: `n = 3`.

- `n != 1` and `n != 2`, so proceed to the loop. `prev2 = 1` (ways(1)), `prev1 = 2` (ways(2)).
- Loop `i = 3` (since `n = 3`, the loop runs just once, for `i` from 3 to 3):
  - `curr = prev1 + prev2 = 2 + 1 = 3` (ways(3) = ways(2) + ways(1)).
  - Shift: `prev2 = prev1 = 2`, `prev1 = curr = 3`.
- Loop ends (i would be 4, exceeding n=3). Return `prev1 = 3`.
- Output: 3. Matches expected output.

As a sanity check on the recurrence itself: ways(1)=1 (just "1"), ways(2)=2 ("1+1", "2"), ways(3) should equal ways(2)+ways(1)=2+1=3, matching the three sequences enumerated in the problem statement (1+1+1, 1+2, 2+1).

## Solution (Python 3)
```python
def climb_stairs(n: int) -> int:
    if n == 1:
        return 1
    if n == 2:
        return 2

    prev2, prev1 = 1, 2  # ways(1), ways(2)

    for i in range(3, n + 1):
        curr = prev1 + prev2
        prev2, prev1 = prev1, curr

    return prev1


if __name__ == "__main__":
    print(climb_stairs(2))  # Expected: 2
    print(climb_stairs(3))  # Expected: 3
    print(climb_stairs(5))  # Expected: 8 (1,1,1,1,1 / 1,1,1,2 in all orders / 2,2,1 in all orders etc. -> Fibonacci-like: 1,2,3,5,8)
```

## Complexity Analysis
- Time: O(n) — a single forward loop from 3 to n, each iteration doing O(1) work.
- Space: O(1) — only two rolling variables are kept (`prev1`, `prev2`); no full array is needed since each `dp[i]` only ever depends on the two immediately preceding values.

## Key Takeaways
- This problem's recurrence `dp[i] = dp[i-1] + dp[i-2]` is literally the Fibonacci sequence in disguise — recognizing "count the number of ways" problems that only depend on a fixed small window of previous states is the central 1D DP pattern-matching skill.
- Space can almost always be optimized from O(n) (a full `dp` array) down to O(1) (a few rolling variables) whenever `dp[i]` only depends on a constant number of previous entries — do this optimization once the recurrence is correct, not before.
- Common mistake: off-by-one errors in the base cases (forgetting that `ways(0) = 1`, representing "one way to be already at the top by taking zero steps," which is implicitly used if you set up the recurrence starting from `dp[0]` instead of `dp[1]`/`dp[2]` directly).
- Related/variant problems to try next: House Robber I / II, Fibonacci Number, Min Cost Climbing Stairs (LC #746, adds per-step costs).
