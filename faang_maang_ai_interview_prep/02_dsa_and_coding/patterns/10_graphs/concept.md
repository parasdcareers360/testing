# Graphs

> **Type:** Study notes

## Why interviewers ask this

Graphs are the pattern where "I know the algorithms" and "I can implement them correctly under
pressure, from scratch, in 25 minutes" separate hardest. Almost every mid-to-senior backend role
touches graph-shaped problems in production — service dependency graphs, permission/role
hierarchies, task scheduling with dependencies (think Celery DAGs), org charts, network topology —
so interviewers use this pattern to check both algorithmic range and whether you reach for the
right tool (BFS vs DFS vs Union-Find vs Dijkstra) without being told which one to use. It's also
the pattern most likely to appear as an *unnamed* problem — "here's a list of dependencies, tell me
if they're satisfiable" — where recognizing "this is a graph, and specifically this is topological
sort" is the actual skill being tested, not the coding.

## The core idea

A graph is just nodes + relationships between them. Once you represent it as an **adjacency list**
(a `dict`/`defaultdict` mapping node -> list/set of neighbors), almost every graph problem is one of
a small number of traversal or ordering questions:

- **"Can I reach X from Y?" / "explore everything reachable"** -> BFS or DFS.
- **"What's the shortest path (fewest edges)?"** -> BFS (unweighted only).
- **"What's the shortest path with weighted edges (non-negative)?"** -> Dijkstra's.
- **"Is there a valid ordering respecting dependencies?"** -> topological sort (only valid on a DAG).
- **"Are these two nodes connected? / how many connected components?"** -> Union-Find (great when
  connectivity queries interleave with edge additions) or a plain DFS/BFS sweep (great when the
  graph is static and given upfront).

Recognize the pattern from phrasing: "prerequisites," "dependencies," "islands," "connected
components," "shortest path," "can you schedule/order these," "is it possible to visit all," "clone
this structure," "friend circles" — these are almost always graph problems even when the word
"graph" never appears in the prompt.

## Representations

```python
from collections import defaultdict

# Adjacency list from an edge list — the representation you'll build from scratch most often
def build_adjacency_list(n: int, edges: list[tuple[int, int]], directed: bool = False) -> dict[int, list[int]]:
    graph: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph
```

Adjacency list is the default choice: O(V + E) space, O(1) to iterate a node's neighbors, and it's
what BFS/DFS/Dijkstra/topo-sort all expect. An adjacency **matrix** (`grid[u][v] = weight`) only
wins when the graph is dense (E close to V^2) or you need O(1) "are u and v directly connected"
checks — mention it exists, but default to the list. A **grid** (2D array where cells are implicit
nodes, adjacency = up/down/left/right) is graphs in disguise — "number of islands," "rotting
oranges" — treat `(row, col)` tuples as node identities.

## Key techniques

### 1. BFS (breadth-first search) — shortest path in unweighted graphs, level-order exploration
```python
from collections import deque

def bfs(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    """Returns distance (in edges) from start to every reachable node."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances
```
BFS explores in layers, so the first time you *reach* a node is guaranteed to be via a shortest
path — that's the entire reason BFS (not DFS) is the answer whenever a problem says "shortest" or
"fewest steps" on an unweighted graph. Mark a node visited **at enqueue time**, not at dequeue time
— marking at dequeue lets the same node get enqueued multiple times through different paths,
wasting work and in the worst case blowing up the queue size.

### 2. DFS (depth-first search) — recursive
```python
def dfs_recursive(graph: dict[int, list[int]], start: int, visited: set[int] | None = None) -> set[int]:
    if visited is None:
        visited = set()
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited
```
Use recursive DFS when the call stack depth is bounded and known-safe (most interview-sized
graphs). Python's default recursion limit (~1000) is a real constraint — say so if the input could
be a long chain, and mention `sys.setrecursionlimit` or switching to iterative DFS as the fix.

### 3. DFS — iterative (explicit stack)
```python
def dfs_iterative(graph: dict[int, list[int]], start: int) -> set[int]:
    visited = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return visited
```
Same reachability result as recursive DFS but avoids stack-overflow risk and makes the "state" you
carry explicit — useful when the interviewer asks "can you do this without recursion?" or when you
need to track extra per-node state (e.g. path so far) that's awkward to thread through recursive
calls.

### 4. Topological sort — Kahn's algorithm (BFS-based, in-degree)
```python
def topological_sort_kahn(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """edges are (prerequisite, course) pairs. Returns [] if a cycle exists (no valid order)."""
    graph: dict[int, list[int]] = defaultdict(list)
    in_degree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []  # shorter than n => cycle
```
Kahn's is the version most people should default to: it's iterative (no recursion depth worry) and
cycle detection is a free byproduct — if `len(order) != n`, some nodes never hit in-degree 0, which
can only happen if they're stuck in a cycle.

### 5. Topological sort — DFS-based (postorder reversal)
```python
def topological_sort_dfs(n: int, edges: list[tuple[int, int]]) -> list[int]:
    graph: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2  # unvisited, in-progress (on current path), done
    state = [WHITE] * n
    order = []
    has_cycle = False

    def dfs(node: int) -> None:
        nonlocal has_cycle
        state[node] = GRAY
        for neighbor in graph[node]:
            if state[neighbor] == GRAY:
                has_cycle = True
            elif state[neighbor] == WHITE:
                dfs(neighbor)
        state[node] = BLACK
        order.append(node)  # postorder: append after all descendants are done

    for i in range(n):
        if state[i] == WHITE:
            dfs(i)

    return [] if has_cycle else order[::-1]
```
The three-color (white/gray/black) scheme is the standard way to detect a cycle *during* DFS: gray
means "on the current recursion path" — hitting a gray node means you found a back-edge, i.e. a
cycle. This is the same coloring trick interviewers expect for "detect a cycle in a directed graph"
even when topological order isn't asked for.

### 6. Dijkstra's algorithm — shortest path, weighted, non-negative edges
```python
import heapq

def dijkstra(graph: dict[int, list[tuple[int, int]]], start: int) -> dict[int, float]:
    """graph[u] = list of (neighbor, weight). Returns shortest distance from start to every node."""
    distances: dict[int, float] = {start: 0}
    heap = [(0, start)]  # (distance, node)
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distances.get(node, float("inf")):
            continue  # stale heap entry — a shorter path to `node` was already found
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return distances
```
This is BFS generalized to weighted edges: instead of a plain queue (which processes in insertion
order = distance order only when all edges cost 1), a min-heap always pops the globally closest
unfinished node next. The stale-entry check (`if dist > distances.get(node, inf): continue`) is
what makes a "lazy deletion" heap correct without needing a decrease-key operation, which Python's
`heapq` doesn't support natively. **Requires non-negative weights** — negative edges break the
greedy "closest node is finalized" assumption; that's Bellman-Ford's job instead, mention it exists
but it's rarely expected at this level.

### 7. Union-Find / Disjoint Set Union (path compression + union by rank)
```python
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of disjoint components

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False  # already connected — union did nothing (useful for cycle detection)
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        self.count -= 1
        return True
```
Reach for Union-Find (over a DFS/BFS connected-components sweep) whenever edges arrive
**incrementally** and you need "are these two connected *right now*" queries interleaved with
adding edges — redoing a full traversal per query would be O(V+E) per query, while Union-Find
amortizes to nearly O(1) per operation (technically O(α(n)), the inverse Ackermann function,
effectively constant for any n you'll ever see). Classic tells: "number of provinces," "redundant
connection," "accounts merge," "is the graph fully connected after adding these edges one at a
time." `union` returning `False` when both nodes are already connected is exactly the check for
"this edge would create a cycle" — that's how Union-Find detects cycles in an undirected graph and
underlies Kruskal's MST algorithm.

## Complexity to know cold

| Algorithm | Time | Space | Use when |
|---|---|---|---|
| BFS | O(V + E) | O(V) | Unweighted shortest path, level-order, "fewest steps" |
| DFS (recursive/iterative) | O(V + E) | O(V) | Reachability, connected components, cycle detection, backtracking-adjacent problems |
| Topological sort (Kahn) | O(V + E) | O(V) | Ordering with dependencies; cycle detection as a byproduct |
| Topological sort (DFS) | O(V + E) | O(V) (+ call stack) | Same as above; natural when you're already doing DFS-based cycle detection |
| Dijkstra (heap-based) | O((V + E) log V) | O(V) | Weighted shortest path, non-negative weights only |
| Union-Find (path compression + rank) | ~O(α(n)) per op, effectively O(1) | O(V) | Dynamic connectivity, cycle detection in undirected graphs, MST (Kruskal's) |

## Exercises

1. Implement `topological_sort_kahn` from memory, then run it on a graph you know has a cycle
   (e.g. edges `[(0, 1), (1, 2), (2, 0)]`) and confirm it returns `[]` — then explain out loud
   *why* the cycle prevents any node in the cycle from ever reaching in-degree 0.
2. Given a static undirected graph as an edge list, implement "count connected components" two
   ways — once with DFS (sweep every unvisited node), once with `UnionFind` (union every edge, then
   count distinct roots) — and confirm both give the same answer on `n = 5`,
   `edges = [(0, 1), (1, 2), (3, 4)]` (expected: 2 components).
