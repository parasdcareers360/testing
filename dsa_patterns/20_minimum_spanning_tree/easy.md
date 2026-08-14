# Easy — Min Cost to Connect All Points

**Source**: LeetCode #1584
**Pattern**: Minimum Spanning Tree (Prim's / Kruskal's)
**Difficulty**: Easy

## Problem Statement
You are given an array `points` representing integer coordinates of some points on a 2D plane, where `points[i] = [xi, yi]`.

The cost of connecting two points `[xi, yi]` and `[xj, yj]` is the **Manhattan distance** between them: `|xi - xj| + |yi - yj|`.

Return the minimum cost to make all points connected. All points are connected if there is exactly one simple path between any two points (i.e., the connections form a spanning tree — every point reachable from every other, using the minimum total edge weight).

## Constraints
- `1 <= points.length <= 1000`
- `-10^6 <= xi, yi <= 10^6`
- All pairs `(xi, yi)` are distinct.

## Examples
**Example 1**
```
Input: points = [[0,0],[2,2],[3,10],[5,2],[7,0]]
Output: 20
```
Explanation: Labeling the points P0=(0,0), P1=(2,2), P2=(3,10), P3=(5,2), P4=(7,0), the minimum spanning tree uses edges P1-P3 (cost 3), P0-P1 (cost 4), P3-P4 (cost 4), and P1-P2 (cost 9), for a total of 3+4+4+9=20. No other combination of 4 edges connecting all 5 points costs less.

**Example 2**
```
Input: points = [[3,12],[-2,5],[-4,1]]
Output: 18
```
Explanation: Manhattan distances: (3,12)-(-2,5) = |3-(-2)|+|12-5| = 5+7 = 12. (3,12)-(-4,1) = 7+11 = 18. (-2,5)-(-4,1) = 2+4 = 6. The cheapest way to connect all 3 points is edges (3,12)-(-2,5) [cost 12] and (-2,5)-(-4,1) [cost 6], totaling 18.

## Intuition — Why This Pattern
**Brute force**: With `n` points there are `n*(n-1)/2` possible edges (every pair, since it's a complete graph under Manhattan distance). Trying every possible subset of `n-1` edges to find a spanning tree of minimum total weight is combinatorially infeasible — the number of spanning trees of a complete graph grows extremely fast (n^(n-2) by Cayley's formula).

**What's inefficient**: We don't need to consider arbitrary subsets — a classical greedy result (the "cut property" of MSTs) guarantees that always picking the globally cheapest edge that doesn't create a cycle (Kruskal's) or always growing a single tree by its cheapest available outgoing edge (Prim's) produces a *minimum* spanning tree, without ever needing to backtrack or reconsider a choice.

**The insight**: Since every pair of points is connected by an edge (it's a dense/complete graph, as any two points can be directly linked), Prim's algorithm is a great fit: start from any point, and repeatedly grow a "visited" set by adding the cheapest edge connecting a visited point to an unvisited one, using a min-heap to always pick the next cheapest available edge. This is O(n^2 log n) (or O(n^2) with an array-based Prim's, avoiding the heap's log factor since the graph is complete), far better than considering exponentially many spanning trees. (Kruskal's would require generating and sorting all O(n^2) edges first, which is also viable but slightly more memory-heavy for a complete graph; Prim's naturally avoids materializing all edges upfront.)

## Approach
1. Let `n = len(points)`. If `n <= 1`, the cost is 0 (nothing to connect).
2. Initialize `in_mst = [False] * n`, `min_edge = [infinity] * n` (the cheapest known edge cost from the growing tree to each not-yet-included point), and set `min_edge[0] = 0` (start the tree at point 0).
3. Initialize `total_cost = 0`.
4. Repeat `n` times:
   a. Find the unvisited point `u` with the smallest `min_edge[u]` (linear scan over all points, since the graph is complete and we're using array-based Prim's).
   b. Mark `in_mst[u] = True`, add `min_edge[u]` to `total_cost`.
   c. For every other unvisited point `v`, compute the Manhattan distance `d(u, v)`; if `d(u, v) < min_edge[v]`, update `min_edge[v] = d(u, v)`.
5. Return `total_cost`.

## Dry Run
Example 2: `points = [[3,12],[-2,5],[-4,1]]`, label them P0=(3,12), P1=(-2,5), P2=(-4,1).

- Distances: d(P0,P1)=12, d(P0,P2)=18, d(P1,P2)=6.
- Init: `in_mst=[F,F,F]`, `min_edge=[0, inf, inf]`, `total_cost=0`.
- Iteration 1: smallest `min_edge` among unvisited is `min_edge[0]=0` → pick `u=0`. Mark `in_mst[0]=True`. `total_cost += 0 → 0`.
  - Update neighbors: P1 unvisited, d(0,1)=12 < min_edge[1]=inf → `min_edge[1]=12`. P2 unvisited, d(0,2)=18 < min_edge[2]=inf → `min_edge[2]=18`.
  - State: `min_edge=[0,12,18]`.
- Iteration 2: smallest `min_edge` among unvisited {1,2} is `min_edge[1]=12` → pick `u=1`. Mark `in_mst[1]=True`. `total_cost += 12 → 12`.
  - Update neighbors: P2 unvisited, d(1,2)=6 < min_edge[2]=18 → `min_edge[2]=6`.
  - State: `min_edge=[0,12,6]`.
- Iteration 3: smallest `min_edge` among unvisited {2} is `min_edge[2]=6` → pick `u=2`. Mark `in_mst[2]=True`. `total_cost += 6 → 18`.
  - No more unvisited points to update.
- All 3 points visited. Return `total_cost = 18`. Matches expected output.

## Solution (Python 3)
```python
from typing import List


def min_cost_connect_points(points: List[List[int]]) -> int:
    n = len(points)
    if n <= 1:
        return 0

    def manhattan(i: int, j: int) -> int:
        return abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])

    in_mst = [False] * n
    min_edge = [float('inf')] * n
    min_edge[0] = 0
    total_cost = 0

    for _ in range(n):
        u = -1
        best = float('inf')
        for i in range(n):
            if not in_mst[i] and min_edge[i] < best:
                best = min_edge[i]
                u = i

        in_mst[u] = True
        total_cost += best

        for v in range(n):
            if not in_mst[v]:
                d = manhattan(u, v)
                if d < min_edge[v]:
                    min_edge[v] = d

    return total_cost


if __name__ == "__main__":
    print(min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]))  # Expected: 20
    print(min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]]))               # Expected: 18
```

## Complexity Analysis
- Time: O(n^2) — array-based Prim's does n iterations, each scanning all n points twice (once to find the minimum, once to update neighbors), giving O(n^2), which is optimal here since the graph is complete (O(n^2) edges exist implicitly).
- Space: O(n) for the `in_mst` and `min_edge` arrays.

## Key Takeaways
- For **dense/complete graphs** (like this one, where every pair of points has an implicit edge), array-based Prim's O(n^2) beats heap-based Prim's or Kruskal's O(E log E) = O(n^2 log n), because materializing and sorting all O(n^2) edges is wasteful when you can grow the tree greedily with simple array scans.
- Recognize the "connect all points/cities with minimum total cost" phrasing as the MST signal — the cost function (Manhattan distance here) doesn't matter to the algorithm; it's just edge weight.
- Common mistake: trying to use Kruskal's naively by generating all n*(n-1)/2 edges as explicit tuples for large n — this can be memory-heavy (though still technically works for n <= 1000 in this problem); Prim's avoids ever materializing the full edge list.
- Related/variant problems to try next: Optimize Water Distribution in a Village (adds a "virtual source" trick), Connecting Cities With Minimum Cost, Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree.
