# Hard — Shortest Path Visiting All Nodes

**Source**: LeetCode #847
**Pattern**: Dynamic Programming — Bitmask
**Difficulty**: Hard

## Problem Statement
You have an undirected, connected graph of `n` nodes labeled `0` to `n - 1`. You are given an array `graph` where `graph[i]` is a list of all the nodes connected with node `i` by an edge.

Return the length of the shortest path that visits every node. You may start and stop at any node, you may revisit nodes multiple times, and you may reuse edges multiple times. Each edge traversal counts as a step of length 1.

## Constraints
- `n == graph.length`
- `1 <= n <= 12`
- `0 <= graph[i].length < n`
- `graph[i]` does not contain `i`.
- If `graph[a]` contains `b`, then `graph[b]` contains `a` (the graph is undirected).
- The input graph is always connected.

## Examples
1. Input: `graph = [[1,2,3],[0],[0],[0]]` -> Output: `4`
   Explanation: One shortest route is `1 -> 0 -> 2 -> 0 -> 3`, which has 4 edges and visits every node (0,1,2,3). Node 0 is revisited, which is allowed.
2. Input: `graph = [[1],[0,2,4],[1,3,4],[2],[1,2]]` -> Output: `4`
   Explanation: One shortest route is `0 -> 1 -> 4 -> 2 -> 3`, which has 4 edges and visits every node exactly once in this case.

## Intuition — Why This Pattern
**Brute force**: Since nodes can be revisited and edges reused, a plain DFS/backtracking search over all possible walks has no natural stopping bound — walks can be arbitrarily long, so naive exhaustive search doesn't even terminate cleanly without extra bookkeeping, and even bounding it by some max length would be exponential in the worst case.

**Why this is harder than plain bitmask-DP TSP**: In the Traveling Salesman easy example, movement was a complete graph — any city could be reached directly from any other in one hop, with a known cost. Here, the graph is **sparse** (not complete): you can only move along actual edges, and reaching an unvisited node from your current node might require passing *through* already-visited nodes first. This means the DP transition ("move to an adjacent node") must be layered with an actual **shortest-path graph search** (BFS) *on top of* the bitmask-DP state space — the transition itself isn't a simple O(1) edge-cost lookup like in TSP; it's a walk over a graph. Combining bitmask DP (over subsets of visited nodes) with graph BFS (over which node to move to next) is precisely the kind of "combines this pattern with another concept" escalation that makes a problem Hard.

**Insight — the state**: Since `n <= 12`, encode "which nodes have been visited so far" as a bitmask (up to `2^12 = 4096` masks). Define:

`dist[mask][i]` = the minimum number of edges walked so far, having visited exactly the set of nodes in `mask`, currently standing at node `i` (bit `i` must be set in `mask`).

Because multiple *different* starting nodes can each grow their own visited-set independently, and revisits are allowed (so this isn't a simple DAG of masks), the cleanest correct way to compute `dist[mask][i]` for all reachable `(mask, i)` pairs simultaneously is a **multi-source 0/1-weighted BFS** over the *state graph* whose "positions" are `(mask, node)` pairs: from state `(mask, i)`, we can move to `(mask | (1<<j), j)` for every actual graph-neighbor `j` of `i`, at a step cost of exactly 1. Since all edges in this state graph have equal weight (1), a standard multi-source BFS (not Dijkstra) correctly computes shortest distances.

## Approach
1. Let `n = len(graph)`. If `n == 1`, return `0` immediately (a single node needs zero moves to "visit all nodes").
2. Initialize a BFS queue with **every node as its own starting state**: for each node `i` from `0` to `n-1`, push `(mask = 1 << i, node = i)` with distance `0` — since we can start anywhere, all `n` single-node masks are simultaneously valid starting points (multi-source BFS).
3. Maintain a `visited` set (or a 2D boolean array `seen[mask][node]`) to avoid processing the same `(mask, node)` state more than once; mark all `n` starting states as seen with distance 0.
4. Run a standard BFS: repeatedly pop the front of the queue `(mask, node, dist)`. For every neighbor `j` in `graph[node]`:
   - Compute `next_mask = mask | (1 << j)`.
   - If `next_mask == (1 << n) - 1` (all nodes now visited), return `dist + 1` immediately — this is guaranteed to be the shortest such path because BFS explores states in non-decreasing order of distance.
   - Otherwise, if `(next_mask, j)` has not been seen yet, mark it seen and push `(next_mask, j, dist + 1)`.
5. (The graph is guaranteed connected, so a full-visitation state is always eventually reached — no explicit "no solution" case is needed.)

## Dry Run
Example: `graph = [[1,2,3],[0],[0],[0]]` (node 0 connects to 1, 2, 3; nodes 1, 2, 3 each connect only to node 0). `n = 4`, `full_mask = 1111` binary `= 15`. Expected output: `4`.

**Initialize** (multi-source, distance 0 states): `(mask=0001, node=0)`, `(mask=0010, node=1)`, `(mask=0100, node=2)`, `(mask=1000, node=3)`. None of these masks equal `15`, so BFS proceeds.

**Distance 1 layer** — expand each distance-0 state:
- From `(0001, 0)`: neighbors of node 0 are `{1,2,3}`.
  - -> `(0011, 1)` new, dist 1.
  - -> `(0101, 2)` new, dist 1.
  - -> `(1001, 3)` new, dist 1.
- From `(0010, 1)`: neighbor of node 1 is `{0}`.
  - -> `(0011, 0)` new, dist 1.
- From `(0100, 2)`: neighbor of node 2 is `{0}`.
  - -> `(0101, 0)` new, dist 1.
- From `(1000, 3)`: neighbor of node 3 is `{0}`.
  - -> `(1001, 0)` new, dist 1.

None of the distance-1 states have `mask == 15` yet (best masks so far have only 2 bits set). Continue.

**Distance 2 layer** — expand each distance-1 state (showing the ones that matter):
- From `(0011, 1)` [visited {0,1}, at node 1]: neighbor `{0}` -> `(0011, 0)` already seen, skip.
- From `(0011, 0)` [visited {0,1}, at node 0]: neighbors `{1,2,3}`:
  - -> `(0011, 1)` already visited mask+node combo? `(0011,1)` was seen at dist 1, skip.
  - -> `(0111, 2)` new, dist 2 (visited {0,1,2}).
  - -> `(1011, 3)` new, dist 2 (visited {0,1,3}).
- From `(0101, 2)` and `(0101, 0)` similarly produce `(0111, ...)`-type and `(1101, ...)`-type states with 3 bits set (visited {0,1,2} or {0,2,3}) at dist 2 — e.g. `(1101, 3)` visited {0,2,3}.
- From `(1001, 3)` and `(1001, 0)` similarly produce `(1011, ...)` and `(1101, ...)` states with 3 bits set at dist 2.

After distance 2, several 3-bit masks are reached (`0111`, `1011`, `1101` — each missing exactly one of nodes 1, 2, or 3), but none equal `1111` (4 bits) yet.

**Distance 3 layer** — expand a 3-bit state, e.g. `(0111, 2)` [visited {0,1,2}, at node 2]: neighbor of node 2 is `{0}` only -> `(0111, 0)` new, dist 3 (mask still `0111`, only node changed — still missing node 3).

**Distance 4 layer** — expand `(0111, 0)` [visited {0,1,2}, at node 0, dist 3]: neighbors `{1,2,3}`:
- -> `(1111, 3)`: `next_mask = 0111 | 1000 = 1111 = 15 = full_mask`! Return `dist + 1 = 3 + 1 = 4`.

Final answer: `4`, matching the expected output — consistent with the example route `1 -> 0 -> 2 -> 0 -> 3` (4 edges): start at node 1 (mask 0010, dist 0) -> node 0 (mask 0011, dist 1) -> node 2 (mask 0111, dist 2) -> node 0 (mask 0111, dist 3) -> node 3 (mask 1111, dist 4).

## Solution (Python 3)
```python
from collections import deque


def shortest_path_length(graph: list[list[int]]) -> int:
    n = len(graph)
    if n == 1:
        return 0

    full_mask = (1 << n) - 1
    queue = deque()
    seen = set()

    for i in range(n):
        start_mask = 1 << i
        queue.append((start_mask, i, 0))
        seen.add((start_mask, i))

    while queue:
        mask, node, dist = queue.popleft()

        for neighbor in graph[node]:
            next_mask = mask | (1 << neighbor)
            if next_mask == full_mask:
                return dist + 1

            state = (next_mask, neighbor)
            if state not in seen:
                seen.add(state)
                queue.append((next_mask, neighbor, dist + 1))

    return -1  # unreachable in theory; graph is guaranteed connected per constraints


if __name__ == "__main__":
    print(shortest_path_length([[1, 2, 3], [0], [0], [0]]))          # Expected: 4
    print(shortest_path_length([[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]))  # Expected: 4
```

## Complexity Analysis
- Time: O(n^2 * 2^n) — there are `O(n * 2^n)` distinct `(mask, node)` states, and each is expanded across up to `n` neighbors (bounded by `n` since `graph[i].length < n`).
- Space: O(n * 2^n) for the `seen` set and BFS queue in the worst case.

## Key Takeaways
- The key generalization introduced here: bitmask DP doesn't have to be a simple table-filling loop — it can be the **state space of a graph search** (BFS in this case), where each "position" in the search is a `(mask, current_node)` pair rather than a single node. This "product state space" idea (combine a small structural dimension like a bitmask with a search algorithm) generalizes to many hard graph + DP hybrid problems.
- Common mistake: using plain DFS/backtracking instead of BFS — since edges can be reused and nodes revisited, only BFS (which explores strictly in order of increasing distance) guarantees the *first* time `full_mask` is reached is via the *shortest* possible path; DFS would require additional pruning/memoization to avoid both incorrectness and non-termination.
- Multi-source BFS (seeding the queue with **all** `n` single-node starting states at distance 0 simultaneously) is essential — the problem allows starting from any node, so restricting to a single start would miss shorter paths that begin elsewhere.
- Related/variant problems to try next: **Traveling Salesman Problem** (the easy problem in this folder, a complete-graph bitmask DP without the graph-BFS layering) and **Smallest Sufficient Team** (LeetCode #1125, bitmask DP over "skills covered" rather than "nodes visited," a good next problem for practicing bitmask-over-abstract-sets rather than bitmask-over-physical-graph-nodes).
