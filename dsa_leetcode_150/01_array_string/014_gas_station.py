"""
LeetCode Top Interview 150 — #14 (LeetCode #134)
Gas Station
Category: Array / String | Difficulty: Medium

Problem
-------
There are `n` gas stations arranged in a circle. You are given two integer arrays `gas` and
`cost`, where `gas[i]` is the amount of gas available at station `i`, and `cost[i]` is the gas
needed to travel from station `i` to station `i + 1` (the station after the last one wraps
around to station 0).

You start with an empty tank at one of the gas stations. Return the starting gas station's index
if you can travel around the circuit once in the clockwise direction without running out of gas
at any point, otherwise return -1. If a solution exists, it is guaranteed to be unique.

Constraints
-----------
- n == gas.length == cost.length
- 1 <= n <= 10^5
- 0 <= gas[i], cost[i] <= 10^4

Examples
--------
Example 1:
    Input: gas = [1,2,3,4,5], cost = [3,4,5,1,2]
    Output: 3
    Explanation: Starting at station 3, tank = 4. Travel to 4: tank = 4-1+5 = 8. Travel to 0:
    tank = 8-2+1 = 7. Travel to 1: tank = 7-3+2 = 6. Travel to 2: tank = 6-4+3 = 5. Travel to 3:
    tank = 5-5+4 = 4 >= 0. Completed the circuit.

Example 2:
    Input: gas = [2,3,4], cost = [3,4,3]
    Output: -1
    Explanation: No matter which station you start at, you run out of gas before returning.

Intuition
---------
The brute force just tries every starting station and simulates the full loop, which is
correct but O(n^2). Two facts collapse this to O(n): first, a valid start exists only if
sum(gas) >= sum(cost) overall — if the total gas can't cover the total cost, no starting point
can ever work, since fuel is fungible across the whole circuit. Second, if the tank ever goes
negative while starting from station `s` and testing station `i`, then *no* station between `s`
and `i` (inclusive) can be a valid start either — starting from any of them would arrive at that
same failing point with an equal or smaller tank, since the sum from `s` to that station was
non-negative for all prefixes tried so far. That lets a single forward pass reset the candidate
start to `i + 1` the moment the running tank dips below zero, discarding the whole failed range
in one step instead of retrying each station individually.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every station as a starting point and simulate the full circuit,
# tracking the tank; if it never goes negative, that start works.
# Time:  O(n^2) — n starting points, each simulated over n stations
# Space: O(1)
def solve_brute_force(gas: List[int], cost: List[int]) -> int:
    n = len(gas)
    for start in range(n):
        tank = 0
        completed = True
        for step in range(n):
            i = (start + step) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                completed = False
                break
        if completed:
            return start
    return -1


# ============================================================
# Approach 2: Optimal (greedy single pass)
# ============================================================
# Idea: if total gas < total cost, no answer exists. Otherwise, walk once
# around the array accumulating tank; whenever tank goes negative, the
# current candidate start (and everything since) is disqualified, so reset
# the candidate to the next station and the running tank to 0.
# Dry run: gas=[1,2,3,4,5], cost=[3,4,5,1,2]
#   i=0: tank=1-3=-2 <0 -> start=1, tank=0
#   i=1: tank=0+2-4=-2 <0 -> start=2, tank=0
#   i=2: tank=0+3-5=-2 <0 -> start=3, tank=0
#   i=3: tank=0+4-1=3
#   i=4: tank=3+5-2=6
#   total gas=15, total cost=15 -> feasible -> return start=3
# Time:  O(n) — one pass
# Space: O(1)
def solve_optimal(gas: List[int], cost: List[int]) -> int:
    total_tank = 0
    running_tank = 0
    start = 0

    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total_tank += diff
        running_tank += diff
        if running_tank < 0:
            # Every station from `start` to `i` fails as a starting point;
            # the next candidate is i + 1, with a fresh tank of 0.
            start = i + 1
            running_tank = 0

    return start if total_tank >= 0 else -1


# ============================================================
# Key Takeaways
# ============================================================
# - When a running prefix sum going negative disqualifies an entire range of
#   candidates at once, you can jump the candidate pointer past the whole
#   failed range instead of retrying each one — the same idea behind Kadane's
#   algorithm's "reset on negative running sum".
# - Common mistake: forgetting to check total(gas) >= total(cost) first, or
#   returning the greedy `start` even when no valid answer exists.
# - Related/variant problems to try next: Jump Game, Jump Game II, Candy.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), 3),
        (([2, 3, 4], [3, 4, 3]), -1),
        (([5, 1, 2, 3, 4], [4, 4, 1, 5, 1]), 4),
        (([3, 3, 4], [3, 4, 4]), -1),
        (([0], [0]), 0),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")
