# Hard — Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree

**Source**: LeetCode #1489
**Pattern**: Minimum Spanning Tree (Kruskal's, applied repeatedly with edge inclusion/exclusion)
**Difficulty**: Hard

## Problem Statement
Given a weighted undirected connected graph with `n` vertices numbered from `0` to `n - 1`, and an array `edges` where `edges[i] = [ai, bi, weighti]` represents a bidirectional and weighted edge between nodes `ai` and `bi`. A minimum spanning tree (MST) is a subset of the graph's edges that connects all vertices without cycles and with the minimum possible total edge weight.

Find all the **critical** and **pseudo-critical** edges in the given graph's minimum spanning tree, using the following definitions:
- A **critical** edge is one whose removal from the graph would cause the MST weight to increase (or make the graph disconnected). In other words, this edge *must* be part of every possible MST.
- A **pseudo-critical** edge is one that can appear in *some* MST of the graph, but is not critical (i.e., there exists at least one MST that does not use this edge, but also at least one MST that does use it, without increasing the total weight).

Return a list of size 2, where the first list contains the indices of all critical edges, and the second list contains the indices of all pseudo-critical edges — both with respect to the original `edges` array's indexing, and each sub-list sorted in any order.

This combines the MST pattern with a "what-if" analysis over the graph structure: rather than computing a single MST, you must determine each edge's *necessity* by testing how the MST weight changes when that edge is forcibly excluded or forcibly included — a use of MST computation as a subroutine called many times, one of the trickier applications of the pattern.

## Constraints
- `2 <= n <= 100`
- `1 <= edges.length <= min(200, n * (n - 1) / 2)`
- `edges[i].length == 3`
- `0 <= ai < bi < n`
- `1 <= weighti <= 1000`
- All pairs `(ai, bi)` are distinct (no duplicate edges, no self-loops).

## Examples
**Example 1**
```
Input: n = 5, edges = [[0,1,1],[1,2,1],[2,3,2],[0,3,2],[0,4,3],[3,4,3],[1,4,6]]
Output: [[0,1],[2,3,4,5]]
```
Explanation: The base MST weight is 7 (using edges 0,1,2,4, i.e. weights 1+1+2+3=7, or an equal-weight alternative using edges 0,1,3,4). Edges 0 and 1 (weight 1 each) are critical — removing either forces a higher-weight MST, since they're the only weight-1 edges connecting their respective node pairs into the cheap backbone. Edges 2, 3, 4, 5 are pseudo-critical — each can be swapped for an equal-weight alternative (e.g., edge 2 [2,3,2] can be swapped with edge 3 [0,3,2], both weight 2) without changing the total MST weight. Edge 6 (weight 6) is neither — it's too expensive to ever appear in an MST.

**Example 2**
```
Input: n = 4, edges = [[0,1,1],[1,2,1],[2,3,1],[0,3,1]]
Output: [[],[0,1,2,3]]
```
Explanation: All four edges form a 4-cycle with equal weight 1. Any 3 of the 4 edges form a valid MST of weight 3. Since no single edge is indispensable (any edge can be excluded and the remaining 3 still form an equal-weight MST), there are no critical edges. But every edge CAN appear in some MST (any 3-edge subset of the cycle works), so all 4 are pseudo-critical.

## Intuition — Why This Pattern
**Brute force**: Enumerate every possible spanning tree of the graph, compute each one's weight, and cross-reference which edges appear in the minimum-weight tree(s) vs. all of them vs. none. The number of spanning trees can be exponential (up to n^(n-2) for a complete graph via Cayley's formula), so this is infeasible even for the given constraints (n up to 100).

**What's inefficient**: We don't need every spanning tree — we only need to know, for each edge, how its removal or forced inclusion affects the *achievable minimum* weight, and Kruskal's algorithm gives us a fast, reliable way to compute "the MST weight given a specific set of excluded/included edges" without enumerating all trees.

**The insight**: First compute the baseline MST weight normally. Then, for each edge `e`:
1. **Test criticality**: Recompute the MST *excluding* edge `e` entirely (skip it in Kruskal's edge list). If the resulting MST weight is strictly greater than the baseline (or the graph becomes disconnected, i.e., no spanning tree exists without `e`), then `e` is critical — no equally-cheap alternative exists without it.
2. **Test pseudo-criticality** (only if not critical): Recompute the MST while *forcing* edge `e` to be included first (union its two endpoints and add its weight before running Kruskal's on the rest). If the resulting total weight equals the baseline, then `e` can participate in an MST without penalty — it's pseudo-critical.

Each of these is a normal Kruskal's run (O(E log E)), and we do this for every edge, giving O(E^2 log E) overall — since `E <= 200` per the constraints, this is fast enough, and vastly better than exponential tree enumeration. The key trick that makes the whole approach correct is that Kruskal's greedy edge-sorting process is easy to "constrain" — just skip or pre-include one edge — without needing to change the rest of the algorithm.

## Approach
1. Attach each edge's original index to it: create tuples `(u, v, w, original_index)`.
2. Write a helper `mst_weight(skip=-1, force=-1)` that:
   a. Initializes Union-Find over `n` nodes.
   b. If `force != -1`, unions that edge's endpoints and adds its weight immediately, counting it as one edge used.
   c. Iterates over all edges sorted by weight (skipping the edge at index `skip`, and skipping the edge at index `force` since it was already added); for each, if its endpoints are in different components, union them and add the weight, counting it as an edge used.
   d. If the total edges used at the end is not `n - 1`, the graph is disconnected under this constraint — return infinity. Otherwise return the total weight.
3. Compute `base = mst_weight()` (no constraints) — the true MST weight.
4. For each edge index `i`:
   a. If `mst_weight(skip=i) > base` (strictly greater, including the infinite/disconnected case), edge `i` is critical.
   b. Otherwise, if `mst_weight(force=i) == base`, edge `i` is pseudo-critical.
5. Return `[critical_list, pseudo_critical_list]`.

## Dry Run
Use Example 2 (the simpler 4-cycle) for a full trace: `n = 4`, `edges = [[0,1,1],[1,2,1],[2,3,1],[0,3,1]]` (indices 0,1,2,3, all weight 1).

**Base MST**: sort edges (all weight 1, keep given order for ties): process edge0 (0-1): union, count=1, weight=1. Process edge1 (1-2): union, count=2, weight=2. Process edge2 (2-3): union, count=3, weight=3. Process edge3 (0-3): `find(0)` and `find(3)` are now in the same component (0-1-2-3 all connected) → skip (would create a cycle). Final count=3=n-1=3 → valid. `base = 3`.

**Testing edge 0 for criticality**: `mst_weight(skip=0)`. Process edge1 (1-2): union {1,2}, count=1, weight=1. Process edge2 (2-3): union {1,2,3}, count=2, weight=2. Process edge3 (0-3): union {0,1,2,3}, count=3, weight=3. Count=3=n-1 → valid, weight=3. Since `3 > base(3)` is False (equal, not greater), edge 0 is NOT critical.

**Testing edge 0 for pseudo-criticality**: `mst_weight(force=0)`. Force-union(0,1), weight=1, count=1. Then process remaining edges (skipping index 0): edge1 (1-2): union {0,1,2}, count=2, weight=2. edge2 (2-3): union {0,1,2,3}, count=3, weight=3. edge3 (0-3): already same component → skip. Count=3=n-1 → valid, weight=3. `3 == base(3)` → True → edge 0 is pseudo-critical.

By the same reasoning (symmetry of the 4-cycle with equal weights), edges 1, 2, and 3 each independently test as not-critical and pseudo-critical.

**Final result**: `critical = []`, `pseudo_critical = [0, 1, 2, 3]`. Output: `[[], [0, 1, 2, 3]]`. Matches expected output.

## Solution (Python 3)
```python
from typing import List


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of distinct components

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1
        return True


def find_critical_and_pseudo_critical_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    indexed_edges = [(u, v, w, i) for i, (u, v, w) in enumerate(edges)]
    sorted_edges = sorted(indexed_edges, key=lambda e: e[2])

    def mst_weight(skip: int = -1, force: int = -1) -> float:
        uf = UnionFind(n)
        total = 0

        if force != -1:
            u, v, w, _ = indexed_edges[force]
            uf.union(u, v)
            total += w

        for u, v, w, i in sorted_edges:
            if i == skip or i == force:
                continue
            if uf.union(u, v):
                total += w

        return total if uf.count == 1 else float('inf')

    base = mst_weight()

    critical = []
    pseudo_critical = []

    for i in range(len(edges)):
        if mst_weight(skip=i) > base:
            critical.append(i)
        elif mst_weight(force=i) == base:
            pseudo_critical.append(i)

    return [critical, pseudo_critical]


if __name__ == "__main__":
    print(find_critical_and_pseudo_critical_edges(
        5, [[0, 1, 1], [1, 2, 1], [2, 3, 2], [0, 3, 2], [0, 4, 3], [3, 4, 3], [1, 4, 6]]
    ))  # Expected: [[0, 1], [2, 3, 4, 5]]

    print(find_critical_and_pseudo_critical_edges(
        4, [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 1]]
    ))  # Expected: [[], [0, 1, 2, 3]]
```

## Complexity Analysis
- Time: O(E^2 log E) — we call `mst_weight` O(E) times (once per edge, for the criticality test, and again for a subset for the pseudo-criticality test), and each call sorts (or re-uses a pre-sorted copy of) the edge list and runs Union-Find operations, costing O(E log E) per call (the sort can be hoisted outside the loop, as done above, reducing each call to O(E * alpha(E))). With the sort hoisted out, overall time is O(E log E) for the initial sort plus O(E^2) for all the Union-Find passes — still commonly described as O(E^2) to O(E^2 log E) depending on implementation details.
- Space: O(n + E) for the Union-Find structure and edge lists.

## Key Takeaways
- A powerful general technique: to test whether a specific element is "forced" or "optional" in an optimal structure (MST, matching, etc.), rerun the optimal-structure algorithm with that element excluded (does the optimum get worse?) or forcibly included (does the optimum stay the same?).
- Hoist expensive setup (like sorting the edge list) outside of any loop that repeatedly reruns the core algorithm — this is a classic and important efficiency fix when an algorithm is used as a repeated subroutine.
- Common mistake: forgetting to check for full graph connectivity when testing edge removal (a removed edge might be a bridge, making the graph disconnected entirely, which should count as "the MST weight became infinitely worse", i.e., critical) — always compare against the component count, not just weight.
- Related/variant problems to try next: Min Cost to Connect All Points, Connecting Cities With Minimum Cost, Redundant Connection (a much simpler single-pass version of "is this edge necessary").
