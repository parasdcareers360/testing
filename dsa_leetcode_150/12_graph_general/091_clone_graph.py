"""
LeetCode Top Interview 150 — #91 (LeetCode #133)
Clone Graph
Category: Graph General | Difficulty: Medium

Problem
-------
Given a reference to a node in a connected undirected graph, return a deep copy (clone) of the
graph. Each node in the graph contains an integer value (`val`) and a list of references to its
neighbors (`List[Node]`).

Every node has a unique value, and the graph has no repeated edges and no self-loops. The graph is
represented via an adjacency-list style input for testing purposes: `adjList[i]` is the list of
values of node `(i+1)`'s neighbors (node values are 1-indexed).

Constraints
-----------
- The number of nodes in the graph is in the range [0, 100].
- 1 <= Node.val <= 100
- Node.val is unique for each node.
- There are no repeated edges and no self-loops in the graph.
- The graph is connected, and you can visit every node from the given node.

Examples
--------
Example 1:
    Input: adjList = [[2,4],[1,3],[2,4],[1,3]]
    Output: [[2,4],[1,3],[2,4],[1,3]]
    Explanation: Node 1's neighbors are nodes 2 and 4; node 2's neighbors are nodes 1 and 3; etc.
    The output is a completely separate deep copy with the same structure.

Example 2:
    Input: adjList = [[]]
    Output: [[]]
    Explanation: A single node with no neighbors.

Example 3:
    Input: adjList = []
    Output: []
    Explanation: An empty graph.

Intuition
---------
This is graph traversal plus bookkeeping: you must visit every node reachable from the start
exactly once (DFS or BFS both work — there's no complexity difference), but the real challenge is
avoiding infinite loops on cycles and making sure each original node maps to exactly one cloned
node, even though a node can be reached from multiple neighbors. The fix is a hashmap from
original-node -> cloned-node, populated the moment a node is first discovered (before recursing
into its neighbors). That way, if a cycle leads back to a node already being cloned, the recursive
call sees it already in the map and reuses the existing clone instead of recursing forever or
creating a duplicate. There's no meaningful "brute force vs optimal" complexity gap here — both
DFS and BFS are O(V+E) — the two approaches are genuinely different traversal *mechanics* for the
same core idea (clone-on-first-visit via a visited map), so this file presents DFS-recursive and
BFS-iterative as parallel, equally valid solutions rather than a slow-vs-fast progression.
"""

from collections import deque
from typing import Dict, List, Optional


class Node:
    def __init__(self, val: int = 0, neighbors: Optional[List["Node"]] = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def build_graph(adj_list: List[List[int]]) -> Optional[Node]:
    """Build a graph from a LeetCode-style adjacency list (1-indexed values) and
    return a reference to node 1 (or None if the graph is empty)."""
    if not adj_list:
        return None
    nodes: Dict[int, Node] = {i + 1: Node(i + 1) for i in range(len(adj_list))}
    for i, neighbor_vals in enumerate(adj_list):
        node = nodes[i + 1]
        node.neighbors = [nodes[v] for v in neighbor_vals]
    return nodes[1]


def graph_to_adj_list(start: Optional[Node]) -> List[List[int]]:
    """Serialize a graph back to LeetCode's adjacency-list format via BFS, so
    two structurally-equal but differently-allocated graphs compare equal."""
    if start is None:
        return []
    visited: Dict[int, Node] = {}
    queue = deque([start])
    visited[start.val] = start
    while queue:
        node = queue.popleft()
        for nb in node.neighbors:
            if nb.val not in visited:
                visited[nb.val] = nb
                queue.append(nb)
    return [sorted(nb.val for nb in visited[v].neighbors) for v in sorted(visited)]


def assert_deep_copy(original: Optional[Node], clone: Optional[Node]) -> bool:
    """Verify `clone` is a structurally-identical but fully separate object
    graph from `original` — same values/edges, but no shared node objects."""
    if original is None:
        return clone is None
    if clone is None:
        return False

    visited_pairs = set()
    stack = [(original, clone)]
    while stack:
        orig_node, clone_node = stack.pop()
        if orig_node is clone_node:
            return False  # clone must never reuse an original node object
        if orig_node.val != clone_node.val:
            return False
        if len(orig_node.neighbors) != len(clone_node.neighbors):
            return False
        key = orig_node.val
        if key in visited_pairs:
            continue
        visited_pairs.add(key)
        orig_sorted = sorted(orig_node.neighbors, key=lambda n: n.val)
        clone_sorted = sorted(clone_node.neighbors, key=lambda n: n.val)
        for o_nb, c_nb in zip(orig_sorted, clone_sorted):
            stack.append((o_nb, c_nb))
    return True


# ============================================================
# Approach 1: DFS (recursive, clone-on-first-visit via hashmap)
# ============================================================
# Idea: recursively clone each node; a map from original -> clone ensures
# each node is cloned exactly once and cycles terminate (a node already in
# the map is returned immediately instead of being re-cloned/re-recursed).
# Time:  O(V + E) — every node cloned once, every edge relaxed once
# Space: O(V) — the map, plus O(V) recursion stack in the worst case (a
#        path-shaped graph)
def solve_dfs(node: Optional[Node]) -> Optional[Node]:
    if node is None:
        return None

    cloned: Dict[Node, Node] = {}

    def dfs(n: Node) -> Node:
        if n in cloned:
            return cloned[n]
        copy = Node(n.val)
        cloned[n] = copy
        copy.neighbors = [dfs(nb) for nb in n.neighbors]
        return copy

    return dfs(node)


# ============================================================
# Approach 2: BFS (iterative, clone-on-first-visit via hashmap + queue)
# ============================================================
# Idea: same clone-on-first-visit map as the DFS version, but discover nodes
# level by level with an explicit queue instead of recursing. Preferred when
# the graph could be deep enough to risk hitting Python's recursion limit.
# Dry run: adjList=[[2],[1]] (two nodes, mutually connected)
#   start=node(1); cloned={1: clone(1)}; queue=[node(1)]
#   pop node(1): for neighbor node(2) -> not cloned -> cloned={1:c1,2:c2},
#                queue=[node(2)]; c1.neighbors=[c2]
#   pop node(2): for neighbor node(1) -> already cloned -> reuse c1;
#                c2.neighbors=[c1]
#   result: clone graph with c1<->c2, structurally identical, separate objects
# Time:  O(V + E)
# Space: O(V) — map + BFS queue
def solve_bfs(node: Optional[Node]) -> Optional[Node]:
    if node is None:
        return None

    cloned: Dict[Node, Node] = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        curr = queue.popleft()
        for nb in curr.neighbors:
            if nb not in cloned:
                cloned[nb] = Node(nb.val)
                queue.append(nb)
            cloned[curr].neighbors.append(cloned[nb])
    return cloned[node]


# ============================================================
# Key Takeaways
# ============================================================
# - "Clone-on-first-visit via a hashmap keyed by the original node" is the
#   general pattern for deep-copying any graph/linked structure that may
#   contain cycles (see also: Copy List with Random Pointer).
# - Common mistake: cloning a node's `val` but not populating the map entry
#   *before* recursing/enqueuing into its neighbors — that ordering is what
#   breaks infinite loops on cycles.
# - Related/variant problems to try next: Copy List with Random Pointer,
#   Number of Islands (different flavor of graph traversal), Graph Valid
#   Tree.


if __name__ == "__main__":
    tests = [
        ([[2, 4], [1, 3], [2, 4], [1, 3]],),
        ([[]],),
        ([],),
        ([[2, 3], [1, 3], [1, 2]],),
    ]

    approaches = [solve_dfs, solve_bfs]
    for (adj_list,) in tests:
        original = build_graph(adj_list)
        for fn in approaches:
            source = build_graph(adj_list)  # fresh graph per approach, never shared
            clone = fn(source)
            result_adj = graph_to_adj_list(clone)
            expected_adj = [sorted(x) for x in adj_list]
            is_deep_copy = assert_deep_copy(source, clone)
            status = "OK" if (result_adj == expected_adj and is_deep_copy) else "FAIL"
            print(f"{fn.__name__:20s} args={(adj_list,)!r:40s} -> {result_adj!r} deep_copy={is_deep_copy}  [{status}]")
