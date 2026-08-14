# Medium — Gas Station

**Source**: LeetCode #134
**Pattern**: Greedy Algorithms
**Difficulty**: Medium

## Problem Statement
There are `n` gas stations arranged in a **circle**, numbered `0` to `n-1`. You are given two integer arrays `gas` and `cost` of length `n`, where `gas[i]` is the amount of gas available at station `i`, and `cost[i]` is the amount of gas required to travel from station `i` to the next station `(i + 1) % n`.

You begin the journey with an empty gas tank at one of the gas stations. Determine the index of the starting gas station from which you can travel around the entire circuit exactly once in the clockwise direction, without ever running out of gas. If no such starting station exists, return `-1`. It is guaranteed that if a solution exists, it is unique.

The twist compared to the Easy problem in this pattern: the array is **circular** (you must wrap around from the last station back to the first), and instead of a simple reachability yes/no, you must identify a specific **starting index**, which requires a greedy insight about where a valid start *cannot* be, layered on top of a running-feasibility-tracking scan.

## Constraints
- `n == gas.length == cost.length`
- `1 <= n <= 10^5`
- `0 <= gas[i], cost[i] <= 10^4`

## Examples
**Example 1**
Input: `gas = [1, 2, 3, 4, 5]`, `cost = [3, 4, 5, 1, 2]`
Output: `3`
Explanation: Starting at station 3: tank = 0 + gas[3] - cost[3] = 4 - 1 = 3 (travel to station 4). Tank = 3 + gas[4] - cost[4] = 3 + 5 - 2 = 6 (travel to station 0, wrapping around). Tank = 6 + gas[0] - cost[0] = 6 + 1 - 3 = 4 (travel to station 1). Tank = 4 + gas[1] - cost[1] = 4 + 2 - 4 = 2 (travel to station 2). Tank = 2 + gas[2] - cost[2] = 2 + 3 - 5 = 0 (arrive back at station 3, completing the circuit with an empty but never-negative tank). Starting anywhere else fails at some point.

**Example 2**
Input: `gas = [2, 3, 4]`, `cost = [3, 4, 3]`
Output: `-1`
Explanation: Total gas = 9, total cost = 10. Since total gas < total cost, it is impossible to complete the circuit from any starting station — you will always run out somewhere.

## Intuition — Why This Pattern
**Brute force**: Try every possible starting station `s` from `0` to `n-1`; for each, simulate the entire circular trip, tracking the tank level, and check whether it ever goes negative. This costs O(n) work per starting station, giving O(n^2) total — too slow for `n` up to `10^5`.

**What's inefficient**: The brute force restarts the simulation completely from scratch for every candidate starting station, even though a lot of that work is redundant — if starting at station `a` fails somewhere before reaching station `b`, that failure carries useful information about station `b` (and everything between `a` and the failure point) that the brute force throws away.

**The insight (Greedy, two-part)**:
1. **Feasibility check**: A full circuit is possible at all if and only if `sum(gas) >= sum(cost)` — total gas produced must be at least total gas consumed, otherwise no starting point can ever work (this mirrors "Example 2" above).
2. **Finding the starting index**: Do a single pass around the array (starting arbitrarily, say at index 0), maintaining a running `tank` that accumulates `gas[i] - cost[i]` at each step, and a candidate `start` index (initially 0). Whenever `tank` goes negative at some index `i`, it proves that **no station between the current `start` and `i` (inclusive) could possibly be a valid starting point** — because each of those stations, if tried, would inherit a tank level that is *the same or worse* than what we just accumulated starting from `start` (by the time we simulate through to index `i`, any of those intermediate starting choices would have hit the same net deficit or worse). So we can safely jump our candidate start to `i + 1` and reset `tank = 0`, without ever re-examining any station in the discarded range. Because the problem guarantees a unique solution exists whenever `sum(gas) >= sum(cost)`, the `start` value we land on after one full pass through all n stations is guaranteed correct.

This reduces the total work from O(n^2) to a single O(n) pass — every station is examined exactly once, and the "which prefixes to skip" decision is made greedily and never revisited.

## Approach
1. Compute `total_gas = sum(gas)` and `total_cost = sum(cost)`. If `total_gas < total_cost`, return `-1` immediately (no solution can exist).
2. Initialize `tank = 0` and `start = 0`.
3. Iterate `i` from `0` to `n - 1`:
   a. Update `tank += gas[i] - cost[i]`.
   b. If `tank < 0`, this means starting anywhere from `start` through `i` fails by the time we reach `i` — set `start = i + 1` and reset `tank = 0`.
4. After the loop, return `start` (guaranteed to be a valid answer given the problem's uniqueness guarantee and the feasibility check in step 1).

## Dry Run
Trace `gas = [1, 2, 3, 4, 5]`, `cost = [3, 4, 5, 1, 2]`, `n = 5`.

**Feasibility check:** `total_gas = 1+2+3+4+5 = 15`. `total_cost = 3+4+5+1+2 = 15`. `15 >= 15` — feasible, proceed.

Initialize `tank = 0`, `start = 0`.

| i | gas[i]-cost[i] | tank += (...) | tank < 0? | action |
|---|-----------------|-------------------|-------------|-----------|
| 0 | 1-3=-2 | 0 + (-2) = -2 | yes | start = 1, tank = 0 |
| 1 | 2-4=-2 | 0 + (-2) = -2 | yes | start = 2, tank = 0 |
| 2 | 3-5=-2 | 0 + (-2) = -2 | yes | start = 3, tank = 0 |
| 3 | 4-1=3 | 0 + 3 = 3 | no | (no change to start) |
| 4 | 5-2=3 | 3 + 3 = 6 | no | (no change to start) |

Loop ends. Return `start = 3` — matches the expected output.

Notice how stations 0, 1, and 2 were each ruled out the moment `tank` went negative right after considering them — the algorithm never had to separately re-simulate starting from station 1 or station 2 to know they'd fail; the cumulative deficit already proved it.

## Solution (Python 3)
```python
from typing import List


def can_complete_circuit(gas: List[int], cost: List[int]) -> int:
    """Find the unique valid starting gas station index via a single greedy
    pass, or return -1 if the circuit is infeasible."""
    n = len(gas)

    if sum(gas) < sum(cost):
        return -1

    tank = 0
    start = 0

    for i in range(n):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0

    return start


if __name__ == "__main__":
    print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))  # Expected: 3
    print(can_complete_circuit([2, 3, 4], [3, 4, 3]))              # Expected: -1
```

## Complexity Analysis
- Time: O(n) — one pass to compute the sums (or fold into the main loop), plus one pass for the greedy scan.
- Space: O(1) — only a handful of accumulator variables.

## Key Takeaways
- The key greedy proof technique here — "if a running total goes negative after including some suffix of already-tried starts, none of those starting points could have worked, so they can all be discarded at once" — recurs across many circular/prefix-sum greedy problems; it's worth internalizing as a reusable proof pattern, not just memorizing for this problem.
- Always check the *global* feasibility condition first (`sum(gas) >= sum(cost)`) before trusting the single-pass scan's output — the scan alone will still produce *some* index even when no valid solution exists, so skipping the feasibility check is a common source of wrong answers.
- A common implementation mistake is resetting `start` but forgetting to also reset `tank` to 0 at the same time — without the reset, the accumulated deficit incorrectly carries over into the next candidate window.
- Related/variant problems to try next: **Jump Game** (a simpler non-circular greedy feasibility scan, good prerequisite) and **Jump Game II** (greedy that computes a minimum count rather than a boolean/index) and **Candy** (a two-directional greedy that builds on the "single running feasibility pass" idea but requires combining a left-to-right and a right-to-left pass).
