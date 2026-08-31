"""
Graphs — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

import heapq
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Shape 0: build an adjacency list from an edge list
# ---------------------------------------------------------------------------
def build_adjacency_list(
    n: int, edges: List[Tuple[int, int]], directed: bool = False
) -> Dict[int, List[int]]:
    graph: Dict[int, List[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph


# ---------------------------------------------------------------------------
# Shape 1: BFS — shortest path (edge count) in an unweighted graph
# ---------------------------------------------------------------------------
def bfs(graph: Dict[int, List[int]], start: int) -> Dict[int, int]:
    distances: Dict[int, int] = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances


# ---------------------------------------------------------------------------
# Shape 2: DFS — recursive
# ---------------------------------------------------------------------------
def dfs_recursive(
    graph: Dict[int, List[int]], start: int, visited: Optional[Set[int]] = None
) -> Set[int]:
    if visited is None:
        visited = set()
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited


# ---------------------------------------------------------------------------
# Shape 3: DFS — iterative (explicit stack)
# ---------------------------------------------------------------------------
def dfs_iterative(graph: Dict[int, List[int]], start: int) -> Set[int]:
    visited = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return visited


# ---------------------------------------------------------------------------
# Shape 4: topological sort — Kahn's algorithm (BFS / in-degree based)
# ---------------------------------------------------------------------------
def topological_sort_kahn(n: int, edges: List[Tuple[int, int]]) -> List[int]:
    """edges are (prerequisite, dependent) pairs. Returns [] if a cycle exists."""
    graph: Dict[int, List[int]] = defaultdict(list)
    in_degree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order: List[int] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []


# ---------------------------------------------------------------------------
# Shape 5: topological sort — DFS-based (postorder reversal, 3-color cycle check)
# ---------------------------------------------------------------------------
def topological_sort_dfs(n: int, edges: List[Tuple[int, int]]) -> List[int]:
    graph: Dict[int, List[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2
    state = [WHITE] * n
    order: List[int] = []
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
        order.append(node)

    for i in range(n):
        if state[i] == WHITE:
            dfs(i)

    return [] if has_cycle else order[::-1]


# ---------------------------------------------------------------------------
# Shape 6: Dijkstra's algorithm — weighted shortest path, non-negative weights
# ---------------------------------------------------------------------------
def dijkstra(graph: Dict[int, List[Tuple[int, int]]], start: int) -> Dict[int, float]:
    """graph[u] = list of (neighbor, weight)."""
    distances: Dict[int, float] = {start: 0}
    heap: List[Tuple[float, int]] = [(0, start)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distances.get(node, float("inf")):
            continue
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return distances


# ---------------------------------------------------------------------------
# Shape 7: Union-Find / Disjoint Set Union — path compression + union by rank
# ---------------------------------------------------------------------------
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
            return False  # already connected
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


if __name__ == "__main__":
    # Shape 0 + 1: BFS shortest path on an undirected graph
    g = build_adjacency_list(5, [(0, 1), (1, 2), (2, 3), (0, 4)])
    dist = bfs(g, 0)
    assert dist == {0: 0, 1: 1, 4: 1, 2: 2, 3: 3}

    # Shape 2 + 3: DFS reachability, recursive and iterative agree
    assert dfs_recursive(g, 0) == {0, 1, 2, 3, 4}
    assert dfs_iterative(g, 0) == {0, 1, 2, 3, 4}

    # Shape 4: Kahn's — valid DAG produces a full order; a cycle produces []
    valid_order = topological_sort_kahn(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    assert len(valid_order) == 4
    assert valid_order.index(0) < valid_order.index(1) < valid_order.index(3)
    assert valid_order.index(0) < valid_order.index(2) < valid_order.index(3)
    assert topological_sort_kahn(3, [(0, 1), (1, 2), (2, 0)]) == []

    # Shape 5: DFS-based topo sort agrees with Kahn's on validity (cycle -> [])
    dfs_order = topological_sort_dfs(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    assert len(dfs_order) == 4
    assert dfs_order.index(0) < dfs_order.index(1) < dfs_order.index(3)
    assert topological_sort_dfs(3, [(0, 1), (1, 2), (2, 0)]) == []

    # Shape 6: Dijkstra on a small weighted graph
    weighted_graph: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v, w in [(0, 1, 4), (0, 2, 1), (2, 1, 1), (1, 3, 1), (2, 3, 5)]:
        weighted_graph[u].append((v, w))
    shortest = dijkstra(weighted_graph, 0)
    assert shortest[0] == 0
    assert shortest[2] == 1
    assert shortest[1] == 2  # via 0 -> 2 -> 1 (1 + 1) beats 0 -> 1 directly (4)
    assert shortest[3] == 3  # via 0 -> 2 -> 1 -> 3 (1 + 1 + 1)

    # Shape 7: Union-Find — connectivity + cycle detection
    uf = UnionFind(5)
    assert uf.union(0, 1) is True
    assert uf.union(1, 2) is True
    assert uf.union(3, 4) is True
    assert uf.connected(0, 2) is True
    assert uf.connected(0, 3) is False
    assert uf.union(0, 2) is False  # already connected -> this edge closes a cycle
    assert uf.count == 2  # two components: {0,1,2} and {3,4}

    print("All template shapes verified.")
