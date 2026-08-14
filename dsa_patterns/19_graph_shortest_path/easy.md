# Easy — Network Delay Time

**Source**: LeetCode #743
**Pattern**: Graph Shortest Path (Dijkstra)
**Difficulty**: Easy

## Problem Statement
You are given a network of `n` nodes, labeled from `1` to `n`. You are also given `times`, a list of travel times represented as directed edges `times[i] = (ui, vi, wi)`, where `ui` is the source node, `vi` is the target node, and `wi` is the time it takes for a signal to travel from `ui` to `vi`.

We send a signal from a given node `k`. Return the **minimum** time it takes for all the `n` nodes to receive the signal. If it is impossible for all `n` nodes to receive the signal, return `-1`.

In other words: compute the shortest-path distance from node `k` to every other node in this weighted directed graph, and return the maximum of those shortest distances (since the last node to receive the signal determines when "all nodes" have received it). If any node is unreachable, the answer is `-1`.

## Constraints
- `1 <= k <= n <= 100`
- `1 <= times.length <= 6000`
- `times[i].length == 3`
- `1 <= ui, vi <= n`
- `ui != vi`
- `0 <= wi <= 100`
- All pairs `(ui, vi)` are distinct (i.e., no duplicate directed edges).

## Examples
**Example 1**
```
Input: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
Output: 2
```
Explanation: Signal starts at node 2. It reaches node 1 in 1 unit, node 3 in 1 unit, and node 4 (via node 3) in 1+1=2 units. The maximum of the shortest distances {1, 1, 2} is 2 — that's when the last node (4) receives it.

**Example 2**
```
Input: times = [[1,2,1]], n = 2, k = 1
Output: 1
```
Explanation: Signal starts at node 1, reaches node 2 in 1 unit. Maximum of {1} is 1.

**Example 3** (unreachable case)
```
Input: times = [[1,2,1]], n = 2, k = 2
Output: -1
```
Explanation: Signal starts at node 2, but there's no edge leaving node 2 to reach node 1 (the edge only goes 1 -> 2). Node 1 is unreachable, so the answer is -1.

## Intuition — Why This Pattern
**Brute force**: Try every possible path from `k` to every other node (DFS exploring all paths), tracking the minimum time to reach each node. Since edge weights are non-negative but a graph can have many paths (including ones that revisit nodes via different routes), naive DFS without pruning can revisit the same node many times, leading to exponential blowup in the worst case (especially with cycles).

**What's inefficient**: Most of that repeated exploration is wasted — once we know the true shortest time to reach a node, re-exploring paths through it that arrive later can never produce a better answer for anything downstream.

**The insight**: Since all edge weights are non-negative, Dijkstra's algorithm applies directly: greedily and permanently finalize the shortest distance to the *closest* not-yet-finalized node at each step (using a min-heap to always pick the next closest node), and relax (potentially improve) its neighbors' distances. Because weights are non-negative, once a node is popped from the heap with its current best-known distance, that distance can never be improved later — so each node needs to be "finalized" only once. This gives O(E log V) instead of exponential path enumeration. After computing shortest distances from `k` to all nodes, the answer is just the maximum finite distance (or -1 if any node remains unreachable/infinite).

## Approach
1. Build a weighted adjacency list `graph[u] = list of (v, w)` from the `times` edges.
2. Initialize `dist = {node: infinity for all nodes 1..n}`, then set `dist[k] = 0`.
3. Initialize a min-heap `pq` with `(0, k)`.
4. While `pq` is not empty:
   a. Pop `(d, u)` with the smallest current distance.
   b. If `d > dist[u]`, this entry is stale (a better path was already finalized) — skip it.
   c. Otherwise, for each neighbor `(v, w)` of `u`: if `d + w < dist[v]`, update `dist[v] = d + w` and push `(d + w, v)` onto the heap.
5. After the heap empties, find `max_dist = max(dist.values())`.
6. If `max_dist` is infinity, some node was never reached — return `-1`. Otherwise, return `max_dist`.

## Dry Run
Example 1: `times = [[2,1,1],[2,3,1],[3,4,1]]`, `n = 4`, `k = 2`.

- Graph: `graph = {2: [(1,1), (3,1)], 3: [(4,1)], 1: [], 4: []}`.
- Init: `dist = {1: inf, 2: 0, 3: inf, 4: inf}`. `pq = [(0, 2)]`.
- Pop `(0, 2)`: `d=0 == dist[2]=0`, proceed. Neighbors of 2: `(1,1)` → `0+1=1 < inf` → `dist[1]=1`, push `(1,1)`. `(3,1)` → `0+1=1 < inf` → `dist[3]=1`, push `(1,3)`. `pq = [(1,1),(1,3)]` (heap order may vary but both have priority 1).
- Pop `(1, 1)` (node 1, distance 1): `d=1 == dist[1]=1`, proceed. Neighbors of 1: none. Nothing changes.
- Pop `(1, 3)` (node 3, distance 1): `d=1 == dist[3]=1`, proceed. Neighbors of 3: `(4,1)` → `1+1=2 < inf` → `dist[4]=2`, push `(2,4)`.
- Pop `(2, 4)`: `d=2 == dist[4]=2`, proceed. Neighbors of 4: none.
- Heap empty. Final `dist = {1:1, 2:0, 3:1, 4:2}`.
- `max_dist = max(1,0,1,2) = 2`. No infinities remain. Return `2`. Matches expected output.

## Solution (Python 3)
```python
import heapq
from typing import List


def network_delay_time(times: List[List[int]], n: int, k: int) -> int:
    graph = {i: [] for i in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0

    pq = [(0, k)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    max_dist = max(dist.values())
    return max_dist if max_dist != float('inf') else -1


if __name__ == "__main__":
    print(network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2))  # Expected: 2
    print(network_delay_time([[1, 2, 1]], 2, 1))                        # Expected: 1
    print(network_delay_time([[1, 2, 1]], 2, 2))                        # Expected: -1
```

## Complexity Analysis
- Time: O(E log V) — each edge relaxation potentially pushes a heap entry (O(log V) per push/pop), and there are O(E) relaxations total plus O(V) pops.
- Space: O(V + E) for the adjacency list, distance map, and heap.

## Key Takeaways
- Dijkstra's algorithm is the go-to whenever weights are non-negative and you need single-source shortest distances — always check the "stale entry" condition (`if d > dist[u]: continue`) since Python's `heapq` doesn't support decrease-key, so you may push multiple outdated entries for the same node.
- The "when do all nodes receive it" framing is just "take the max over all single-source shortest distances" — a common wrapper around vanilla Dijkstra.
- Common mistake: forgetting to handle unreachable nodes (`dist[v]` remains infinity) — always check for `inf` before returning the max.
- Related/variant problems to try next: Cheapest Flights Within K Stops (adds a hop-count constraint), Path With Minimum Effort, Path with Maximum Probability.
