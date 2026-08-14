# Hard — Candy

**Source**: LeetCode #135
**Pattern**: Greedy Algorithms (Two-Pass)
**Difficulty**: Hard

## Problem Statement
There are `n` children standing in a line, each assigned a `rating` value given in the integer array `ratings` (0-indexed). You are giving out candies to these children subject to the following requirements:

1. Every child must receive **at least one** candy.
2. Any child with a **higher rating** than an **immediately adjacent** neighbor must receive **more candies** than that neighbor.

Return the **minimum** total number of candies you need to distribute to satisfy both requirements.

The twist compared to the earlier problems in this pattern: the constraint is **bidirectional** — a child's candy count depends on comparisons with *both* the neighbor to the left and the neighbor to the right simultaneously — so a single left-to-right (or right-to-left) greedy pass alone is insufficient; you need to combine **two** greedy passes and merge their results correctly to guarantee the true minimum.

## Constraints
- `n == ratings.length`
- `1 <= n <= 2 * 10^4`
- `0 <= ratings[i] <= 2 * 10^4`

## Examples
**Example 1**
Input: `ratings = [1, 0, 2]`
Output: `5`
Explanation: One optimal distribution is `[2, 1, 2]`. Child 0 (rating 1) > child 1 (rating 0), so child 0 gets more candy than child 1 (`2 > 1`, satisfied). Child 2 (rating 2) > child 1 (rating 0), so child 2 gets more than child 1 (`2 > 1`, satisfied). Total = 2+1+2 = 5.

**Example 2**
Input: `ratings = [1, 2, 2]`
Output: `4`
Explanation: One optimal distribution is `[1, 2, 1]`. Child 1 (rating 2) > child 0 (rating 1), so child 1 gets more than child 0 (`2 > 1`, satisfied). Child 1 and child 2 have equal ratings (both 2) — the "more candy" rule does NOT apply between equal ratings, so child 2 can validly get just 1 candy (there's no requirement forcing it higher, and giving it only 1 keeps the total minimal). Total = 1+2+1 = 4.

## Intuition — Why This Pattern
**Brute force**: Start everyone at 1 candy, then repeatedly scan the whole array looking for any adjacent pair that violates the rating/candy relationship, bump up the violating child's candy count, and repeat the scan until no violations remain (a "relax until stable" / Bellman-Ford-like approach). This can take many passes to converge (each violation fix can trigger new violations elsewhere), giving a much worse than O(n) time bound in the worst case, and it's easy to under- or over-count if implemented carelessly.

**What's inefficient**: The naive relaxation approach doesn't recognize that each child's requirement decomposes cleanly into two **independent, one-directional sub-constraints**: "am I greater than my left neighbor?" and "am I greater than my right neighbor?" Each of these can be satisfied by its own single greedy pass, without ever needing to re-visit earlier decisions.

**The insight (Greedy, two passes, then combine)**:
1. **Left-to-right pass**: Initialize every child's candy count to 1. Scan left to right; whenever `ratings[i] > ratings[i-1]`, set `left[i] = left[i-1] + 1` (this greedily satisfies only the "compare to left neighbor" half of the constraint, and is provably minimal for that half in isolation, using the exact same reasoning as the Jump Game "track a running best" greedy).
2. **Right-to-left pass**: Symmetrically, initialize every child's candy count to 1 again (a separate array), scan right to left; whenever `ratings[i] > ratings[i+1]`, set `right[i] = right[i+1] + 1`. This satisfies only the "compare to right neighbor" half.
3. **Combine**: For each child `i`, the true minimum candy count that satisfies *both* halves simultaneously is `max(left[i], right[i])` — taking the max of the two independently-greedy-optimal values guarantees both constraints hold at once, and it can be proven this is still the overall minimum (giving less than `max(left[i], right[i])` to child `i` would violate whichever of the two one-directional constraints demanded the larger value).

This two-pass-then-combine technique turns what looks like a genuinely coupled bidirectional constraint into two independent O(n) greedy scans plus an O(n) merge — O(n) total, with a clean correctness argument, instead of an uncertain-convergence relaxation loop.

## Approach
1. Let `n = len(ratings)`. If `n == 0`, return `0` (edge case; not reachable given constraints but good practice).
2. Initialize `left = [1] * n` (everyone starts with 1 candy for the left-to-right pass).
3. Left-to-right pass: for `i` from `1` to `n - 1`: if `ratings[i] > ratings[i - 1]`, set `left[i] = left[i - 1] + 1`.
4. Initialize `right = [1] * n` (everyone starts with 1 candy for the right-to-left pass).
5. Right-to-left pass: for `i` from `n - 2` down to `0`: if `ratings[i] > ratings[i + 1]`, set `right[i] = right[i + 1] + 1`.
6. Combine: compute `total = sum(max(left[i], right[i]) for i in range(n))`.
7. Return `total`.

## Dry Run
Trace `ratings = [1, 0, 2]` (`n = 3`).

**Left-to-right pass:** `left = [1, 1, 1]` initially.
- `i=1`: `ratings[1]=0 > ratings[0]=1`? No (`0 > 1` is false). `left[1]` stays `1`.
- `i=2`: `ratings[2]=2 > ratings[1]=0`? Yes. `left[2] = left[1] + 1 = 1 + 1 = 2`.

Final `left = [1, 1, 2]`.

**Right-to-left pass:** `right = [1, 1, 1]` initially.
- `i=1` (going from `n-2=1` down to `0`): `ratings[1]=0 > ratings[2]=2`? No. `right[1]` stays `1`.
- `i=0`: `ratings[0]=1 > ratings[1]=0`? Yes. `right[0] = right[1] + 1 = 1 + 1 = 2`.

Final `right = [2, 1, 1]`.

**Combine:**
- Child 0: `max(left[0], right[0]) = max(1, 2) = 2`.
- Child 1: `max(left[1], right[1]) = max(1, 1) = 1`.
- Child 2: `max(left[2], right[2]) = max(2, 1) = 2`.

Distribution: `[2, 1, 2]`. Total = `2 + 1 + 2 = 5` — matches the expected output.

Sanity check against the constraints: child 0 (rating 1) > child 1 (rating 0) and gets more candy (`2 > 1`, correct). Child 2 (rating 2) > child 1 (rating 0) and gets more candy (`2 > 1`, correct). Both adjacent-pair rules are satisfied, and the total (5) matches the known minimum for this input.

## Solution (Python 3)
```python
from typing import List


def candy(ratings: List[int]) -> int:
    """Minimum total candies satisfying the adjacent-rating rule, via two
    independent greedy passes (left-to-right, right-to-left) combined with
    an elementwise max."""
    n = len(ratings)
    if n == 0:
        return 0

    left = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            left[i] = left[i - 1] + 1

    right = [1] * n
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            right[i] = right[i + 1] + 1

    return sum(max(left[i], right[i]) for i in range(n))


if __name__ == "__main__":
    print(candy([1, 0, 2]))     # Expected: 5
    print(candy([1, 2, 2]))     # Expected: 4
```

## Complexity Analysis
- Time: O(n) — two linear passes to build `left` and `right`, plus one linear pass to combine and sum. All constant work per index.
- Space: O(n) for the two auxiliary arrays `left` and `right` (this can be optimized to O(1) extra space with a more intricate single right-to-left pass that tracks run lengths of increasing/decreasing streaks, but the two-array version is clearer and still meets typical interview expectations).

## Key Takeaways
- When a constraint is genuinely bidirectional (depends on both neighbors), a strong general technique is to **decompose it into two independent one-directional greedy passes** and then **combine with an elementwise max (or min, depending on the problem)** — this is a reusable escalation of the single-pass greedy idea seen in Jump Game and Gas Station.
- A common mistake is trying to solve this with a single pass and ad-hoc "look both ways" logic at each index — this either misses cases or requires unbounded backtracking; the clean two-pass decomposition avoids that entirely.
- Remember that **equal adjacent ratings impose no ordering constraint at all** — don't accidentally force strictly increasing/decreasing candy counts across ties, or you'll overcount the total (see Example 2, where the tie between child 1 and child 2's ratings is what allows child 2 to receive just 1 candy).
- Related/variant problems to try next: **Jump Game** and **Gas Station** (single-direction greedy warm-ups building toward this two-pass technique) and **Trapping Rain Water** (a classic problem that similarly decomposes into a left-max pass and a right-max pass combined with a min/formula, structurally very similar to this two-pass greedy merge).
