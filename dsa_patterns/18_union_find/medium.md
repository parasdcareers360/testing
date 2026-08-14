# Medium — Redundant Connection

**Source**: LeetCode #684
**Pattern**: Union Find (Disjoint Set Union)
**Difficulty**: Medium

## Problem Statement
In this problem, a tree is an undirected graph that is connected and has no cycles.

You are given a graph that started as a tree with `n` nodes labeled from `1` to `n`, with one additional edge added. The added edge has two different vertices chosen from `1` to `n`, and was not an edge that already existed. The graph is represented as an array `edges` of length `n`, where `edges[i] = [ai, bi]` indicates that there is an edge between nodes `ai` and `bi` in the graph.

Return an edge that can be removed so that the resulting graph is a tree of `n` nodes. If there are multiple answers, return the answer that occurs **last** in the input `edges` array.

Unlike the easy version, here we no longer just need to *count* components — we need to identify the exact single edge whose removal restores an acyclic, connected structure, which means we need to detect a cycle *as it forms* while processing edges in order.

## Constraints
- `n == edges.length`
- `3 <= n <= 1000`
- `edges[i].length == 2`
- `1 <= ai < bi <= n`
- `ai != bi`
- There are no repeated edges.
- The given graph is connected.

## Examples
**Example 1**
```
Input: edges = [[1,2],[1,3],[2,3]]
Output: [2,3]
```
Explanation: Edges [1,2] and [1,3] form a valid tree on nodes {1,2,3}. Adding edge [2,3] creates a cycle (1-2-3-1), so removing [2,3] restores a tree. [2,3] is also the last edge in the input that creates a cycle.

**Example 2**
```
Input: edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]
Output: [1,4]
```
Explanation: Edges [1,2],[2,3],[3,4] form a chain 1-2-3-4 (a tree so far). Adding [1,4] closes a cycle (1-2-3-4-1). Edge [1,5] doesn't create a cycle (5 is a new node). [1,4] is the edge whose addition first (and only) creates a cycle, and it's the answer.

## Intuition — Why This Pattern
**Brute force**: For each edge in `edges`, temporarily remove it, then check via DFS/BFS whether the remaining n-1 edges form a valid tree (connected, no cycle, exactly n-1 edges spanning n nodes). Try removing edges from the end of the list backward until you find one that works. This is O(n) candidate removals * O(n) traversal each = O(n^2), and is fiddly to implement correctly (checking connectivity and node count each time).

**What's inefficient**: We're redoing a full graph traversal for every candidate removal, when actually we only need to identify the *first* edge (scanning left to right) whose two endpoints are *already* connected before this edge is added — that's the redundant one. Since a tree has exactly n-1 edges for n nodes, and we're given exactly n edges, there's exactly one edge that, when added, connects two nodes already in the same connected component (i.e., closes a cycle).

**The insight**: Process edges one at a time in the given order, maintaining a Union-Find structure over the nodes. For each edge `(u, v)`, check if `find(u) == find(v)` — if so, `u` and `v` are already connected by some earlier path, so this edge is redundant (it's the answer, since we want the last such edge encountered, which in this problem's guarantee is unique because exactly one edge was added to an otherwise valid tree). If not, `union(u, v)` to merge their components and continue. This finds the answer in a single O(n) pass (with near-O(1) union/find operations), turning the O(n^2) brute force into O(n).

## Approach
1. Initialize a `parent` array of size `n + 1` (1-indexed) where `parent[i] = i`.
2. Define `find(x)` with path compression, and `union(x, y)` that merges roots (optionally by rank/size for balance).
3. Iterate through `edges` in the given order. For each edge `(u, v)`:
   a. Compute `ru = find(u)` and `rv = find(v)`.
   b. If `ru == rv`, then `u` and `v` are already in the same component — this edge closes a cycle. Since we scan in input order and the problem guarantees exactly one redundant edge exists, this is the answer; return `[u, v]` immediately.
   c. Otherwise, `union(u, v)` (e.g., `parent[ru] = rv`) and continue to the next edge.
4. (Unreachable in valid inputs per problem constraints, but as a safety net) if no redundant edge was found by the end, there's no answer — the constraints guarantee this won't happen.

## Dry Run
Example 2: `edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]`, `n = 5`.

- Initialize `parent = [0, 1, 2, 3, 4, 5]` (index 0 unused).
- Edge `[1, 2]`: `find(1) = 1`, `find(2) = 2`. Different → union: `parent[1] = 2`. `parent = [0, 2, 2, 3, 4, 5]`.
- Edge `[2, 3]`: `find(2) = 2`, `find(3) = 3`. Different → union: `parent[2] = 3`. `parent = [0, 2, 3, 3, 4, 5]`.
- Edge `[3, 4]`: `find(3) = 3`, `find(4) = 4`. Different → union: `parent[3] = 4`. `parent = [0, 2, 3, 4, 4, 5]`.
- Edge `[1, 4]`: `find(1)` → follow: parent[1]=2, parent[2]=3, parent[3]=4, parent[4]=4 (self) → root 4 (with path compression, parent[1] gets set to 4 directly along the way). `find(4) = 4`. Roots are equal (`4 == 4`) → cycle detected! Return `[1, 4]`.
- Output: `[1, 4]`. Matches expected output.

## Solution (Python 3)
```python
from typing import List


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n + 1))  # 1-indexed
        self.rank = [0] * (n + 1)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already connected -> this edge is redundant
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def find_redundant_connection(edges: List[List[int]]) -> List[int]:
    n = len(edges)
    uf = UnionFind(n)

    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]

    return []  # unreachable given problem constraints


if __name__ == "__main__":
    print(find_redundant_connection([[1, 2], [1, 3], [2, 3]]))               # Expected: [2, 3]
    print(find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]))  # Expected: [1, 4]
```

## Complexity Analysis
- Time: O(n * alpha(n)) ~ O(n) — we process each of the n edges once, and each union/find operation is amortized nearly O(1) with path compression and union by rank.
- Space: O(n) for the `parent` and `rank` arrays.

## Key Takeaways
- Whenever a problem says "graph started as a tree and one edge was added — find the extra edge," think Union-Find: process edges in order and return the first one that connects two nodes already in the same component.
- Because we scan in the exact input order and return immediately upon finding the cycle-closing edge, we automatically satisfy the "return the edge that occurs last in the input among ties" requirement — there's no need for extra logic to pick "the last" since only one such edge can exist per the problem's guarantee.
- Common mistake: using plain DFS/BFS cycle detection repeatedly (redoing work) instead of incrementally maintaining connectivity — that's asymptotically worse for this incremental setting.
- Related/variant problems to try next: Redundant Connection II (directed graph version — trickier, since a node can have two parents or there can be a cycle without a shared root), Graph Valid Tree, Accounts Merge.
