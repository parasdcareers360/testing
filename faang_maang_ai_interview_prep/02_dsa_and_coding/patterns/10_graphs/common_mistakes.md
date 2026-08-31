# Common Mistakes — Graphs

> **Type:** Study notes

- **Marking visited at dequeue time instead of enqueue time in BFS.** If you only add to `visited`
  when a node is popped, the same node can be pushed onto the queue multiple times by different
  neighbors before it's ever processed — this doesn't just waste time, it can make a "shortest
  path" BFS return a wrong (larger) distance if a longer path's copy of the node gets processed
  after a shorter one was already popped and expanded. Mark visited the moment you enqueue, in
  `template.py` Shape 1.
- **Forgetting the graph can be disconnected.** A single `bfs(graph, 0)` or `dfs_recursive(graph,
  0)` only reaches node 0's component. "Count connected components," "number of islands," and
  "clone graph"-style problems need an outer loop over *every* node that runs a traversal from any
  node not yet visited — a single traversal call silently gives you the wrong answer on a
  disconnected input and this is easy to miss if your test graph happens to be connected.
- **Using recursive DFS on inputs that can form a long chain.** Python's default recursion limit is
  about 1000; a skewed input (e.g. a linked-list-shaped graph with 5000 nodes) triggers
  `RecursionError`. If the problem doesn't bound depth, default to iterative DFS or BFS, or say out
  loud that you're assuming bounded depth and would switch to iterative for production code.
- **Re-adding a node to Dijkstra's heap without the staleness check.** Because `heapq` has no
  decrease-key, you push a new `(dist, node)` entry every time you find a shorter path instead of
  mutating an old one — skipping the `if dist > distances.get(node, inf): continue` guard at the
  top of the loop means you'll re-process a node with an already-superseded (larger) distance and
  can corrupt neighbors' distances with a stale value.
- **Running Dijkstra on a graph with negative edge weights.** Dijkstra's greedy "the closest
  unfinished node is finalized" assumption breaks the moment a negative edge exists — it can
  produce a wrong (too-large) shortest distance without erroring. If weights can be negative, say
  so and name Bellman-Ford instead; don't silently apply Dijkstra to a graph you haven't confirmed
  is non-negative.
- **Skipping path compression or union by rank in Union-Find.** A naive `find` (no path
  compression) degrades to O(n) per call on a chain-shaped union history, turning what should be
  near-O(1) operations into O(n) each — this is the difference between "passes" and "times out" on
  a large `accounts merge` or `number of provinces` input. Always implement both optimizations
  together, as in `template.py` Shape 7.
- **Confusing "no valid order" with "empty input" in topological sort.** Both Kahn's and the
  DFS-based version return `[]` when `n == 0` *and* when a cycle exists — if the problem needs to
  distinguish "no courses to take" from "impossible schedule," check `n == 0` explicitly before
  trusting an empty result as "cycle detected."
- **Treating a grid problem as "not a graph" and hand-rolling ad hoc traversal logic.** "Number of
  islands," "rotting oranges," "surrounded regions" are BFS/DFS on an implicit graph where nodes are
  `(row, col)` tuples and edges are the 4 (or 8) neighboring cells — reach for the same
  `visited`/`queue`/`stack` shapes from `template.py` instead of writing bespoke nested-loop
  traversal logic, it's faster to get right under time pressure.
