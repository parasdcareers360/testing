# Medium — Optimize Water Distribution in a Village

**Source**: LeetCode #1168
**Pattern**: Minimum Spanning Tree (Kruskal's with a virtual node)
**Difficulty**: Medium

## Problem Statement
There are `n` houses in a village, labeled from `1` to `n`. For each house `i`, you may choose to build a well directly in that house, at a cost of `wells[i-1]` (0-indexed array of size `n`, so `wells[i-1]` is the cost of building a well at house `i`).

Alternatively, some houses can be connected by pipes to share water from a well built elsewhere. The cost of connecting house `a` and house `b` with a pipe is given by `pipes[j] = [house1, house2, cost]`.

Return the **minimum total cost** to supply water to all houses — every house must either have its own well, or be connected (directly or transitively through other houses) via pipes to some house that has a well.

The twist here versus a plain MST problem (like connecting all points) is that "building a well" is itself a cost that competes with "laying a pipe" — this is modeled by introducing a **virtual node 0** representing "the water source", where connecting house `i` to node 0 with cost `wells[i-1]` represents "house i gets its own well". The problem then reduces exactly to: find the MST of the graph on nodes `{0, 1, ..., n}`, using both the well-edges (node 0 to each house) and the given pipe-edges.

## Constraints
- `1 <= n <= 10^4`
- `wells.length == n`
- `0 <= wells[i] <= 10^5`
- `1 <= pipes.length <= 10^4`
- `pipes[j].length == 3`
- `1 <= house1j, house2j <= n`
- `0 <= costj <= 10^5`
- `house1j != house2j`

## Examples
**Example 1**
```
Input: n = 3, wells = [1, 2, 2], pipes = [[1,2,1],[2,3,1]]
Output: 3
```
Explanation: Build a well at house 1 (cost 1). Connect house 1 to house 2 via a pipe (cost 1). Connect house 2 to house 3 via a pipe (cost 1). Total cost = 1+1+1 = 3. This is cheaper than building wells at all three houses (1+2+2=5) or other combinations.

**Example 2**
```
Input: n = 2, wells = [1, 1], pipes = [[1,2,100]]
Output: 2
```
Explanation: The pipe between house 1 and house 2 costs 100, far more expensive than just building a well at each house (1+1=2). So the optimal solution is two independent wells, costing 2 total, and the pipe is never used.

## Intuition — Why This Pattern
**Brute force**: Try every possible subset of "which houses get their own well" (2^n possibilities), and for each subset, compute the minimum cost to connect the remaining houses via pipes to at least one well (itself another MST-like sub-problem). This is exponential and completely infeasible for `n` up to 10^4.

**What's inefficient**: We're treating "build a well" as a fundamentally different kind of decision from "lay a pipe", when actually both are just ways of connecting a house to a shared water source at some cost — the only difference is that a well connects a house directly to an abstract, cost-free "infinite water" resource, while a pipe connects two houses to each other.

**The insight**: Introduce a virtual node `0` representing an infinite, always-available water source. Add an edge from node `0` to every house `i` with weight `wells[i-1]` (this "edge" represents building a well at house `i`, competing directly with pipe edges on equal footing). Add the given pipe edges `(house1, house2, cost)` as-is. Now the entire problem becomes: **find a minimum spanning tree over all `n+1` nodes** (the virtual source plus all houses). Any spanning tree of this augmented graph, restricted to real houses, guarantees every house is connected — either directly to the source (meaning it gets its own well) or transitively through pipes to some house that connects to the source. Kruskal's algorithm (sort all edges — both well-edges and pipe-edges — by cost, then greedily add any edge that doesn't create a cycle, using Union-Find) solves this in O(E log E) where E = n (well edges) + len(pipes) (pipe edges), a massive improvement over exponential subset enumeration.

## Approach
1. Create a unified edge list: for each house `i` (1-indexed from 1 to n), add edge `(0, i, wells[i-1])` (virtual source to house i, weight = well cost). For each pipe `[house1, house2, cost]`, add edge `(house1, house2, cost)` as-is.
2. Sort all edges by weight in ascending order.
3. Initialize Union-Find over nodes `0` to `n` (n+1 total nodes, including the virtual source).
4. Initialize `total_cost = 0` and `edges_used = 0`.
5. For each edge `(u, v, cost)` in sorted order:
   a. If `find(u) != find(v)` (adding this edge would not create a cycle): `union(u, v)`, add `cost` to `total_cost`, increment `edges_used`.
   b. If `edges_used == n` (we've connected all n+1 nodes with n edges, forming a spanning tree), stop early.
6. Return `total_cost`.

## Dry Run
Example 1: `n = 3`, `wells = [1, 2, 2]`, `pipes = [[1,2,1],[2,3,1]]`.

- Build edges: well-edges `(0,1,1)`, `(0,2,2)`, `(0,3,2)`; pipe-edges `(1,2,1)`, `(2,3,1)`.
- All edges: `[(0,1,1), (0,2,2), (0,3,2), (1,2,1), (2,3,1)]`.
- Sort by cost: `[(0,1,1), (1,2,1), (2,3,1), (0,2,2), (0,3,2)]` (ties among cost-1 edges broken arbitrarily; ties among cost-2 edges likewise).
- Init: `parent = [0,1,2,3]` (nodes 0,1,2,3). `total_cost=0`, `edges_used=0`.
- Edge `(0,1,1)`: `find(0)=0`, `find(1)=1`. Different → union: `parent[0]=1` (say). `total_cost=1`, `edges_used=1`. `parent=[1,1,2,3]`.
- Edge `(1,2,1)`: `find(1)=1`, `find(2)=2`. Different → union: `parent[1]=2` (say). `total_cost=2`, `edges_used=2`. `parent=[1,2,2,3]`. (Note: `find(0)` now resolves 0→1→2, root 2, with path compression along the way.)
- Edge `(2,3,1)`: `find(2)=2`, `find(3)=3`. Different → union: `parent[2]=3` (say). `total_cost=3`, `edges_used=3`. `parent=[1,2,3,3]`.
- `edges_used == n == 3` → stop early (all 4 nodes {0,1,2,3} are now connected with exactly 3 edges — a valid spanning tree).
- Return `total_cost = 3`. Matches expected output.

## Solution (Python 3)
```python
from typing import List


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

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
        return True


def min_cost_to_supply_water(n: int, wells: List[int], pipes: List[List[int]]) -> int:
    edges = []
    for i in range(1, n + 1):
        edges.append((wells[i - 1], 0, i))
    for house1, house2, cost in pipes:
        edges.append((cost, house1, house2))

    edges.sort()  # sort by cost ascending

    uf = UnionFind(n + 1)  # nodes 0..n
    total_cost = 0
    edges_used = 0

    for cost, u, v in edges:
        if uf.union(u, v):
            total_cost += cost
            edges_used += 1
            if edges_used == n:
                break

    return total_cost


if __name__ == "__main__":
    print(min_cost_to_supply_water(3, [1, 2, 2], [[1, 2, 1], [2, 3, 1]]))  # Expected: 3
    print(min_cost_to_supply_water(2, [1, 1], [[1, 2, 100]]))              # Expected: 2
```

## Complexity Analysis
- Time: O(E log E) where E = n + len(pipes) — dominated by sorting all edges; the Union-Find operations afterward are near O(1) amortized each.
- Space: O(E) for the edge list, plus O(n) for the Union-Find arrays.

## Key Takeaways
- The "virtual node" trick — modeling an abstract resource (here, "having your own well") as edges to a shared dummy node — is a powerful and reusable technique for turning "connect to a shared resource OR connect to each other" problems into a single, clean MST problem.
- Kruskal's algorithm (sort edges, greedily union if no cycle) is usually easier to adapt to these "extra edge types" tricks than Prim's, since it just needs a flat, unified edge list regardless of what each edge conceptually represents.
- Common mistake: forgetting to include node 0 in the Union-Find node count (`n + 1` nodes total, not `n`), or forgetting to stop as soon as `n` edges have been used (though continuing wouldn't produce a wrong answer since remaining edges would all be skipped as cycle-forming — it's just a minor efficiency optimization).
- Related/variant problems to try next: Min Cost to Connect All Points (plain MST, no virtual node), Connecting Cities With Minimum Cost, Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree.
