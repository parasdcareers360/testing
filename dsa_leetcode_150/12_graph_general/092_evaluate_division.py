"""
LeetCode Top Interview 150 — #92 (LeetCode #399)
Evaluate Division
Category: Graph General | Difficulty: Medium

Problem
-------
You are given an array of variable pairs `equations` and an array of real numbers `values`, where
`equations[i] = [Ai, Bi]` and `values[i]` represent the equation `Ai / Bi = values[i]`. Each `Ai`
or `Bi` is a string representing a single variable.

You are also given some queries, where `queries[j] = [Cj, Dj]` represents the question
`Cj / Dj = ?`. Return the answers to all queries. If a single answer cannot be determined, return
`-1.0` for that query. If a query involves a variable that never appears in `equations`, return
`-1.0` for that query too.

Note: the input is always valid — you will not encounter contradictions or division by zero.

Constraints
-----------
- 1 <= equations.length <= 20
- equations[i].length == 2
- 1 <= Ai.length, Bi.length <= 5
- values.length == equations.length
- 0.0 < values[i] <= 20.0
- 1 <= queries.length <= 20
- queries[i].length == 2
- 1 <= Cj.length, Dj.length <= 5
- Ai, Bi, Cj, Dj consist of lowercase English letters and digits.

Examples
--------
Example 1:
    Input: equations = [["a","b"],["b","c"]], values = [2.0,3.0],
           queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
    Output: [6.00000,0.50000,-1.00000,1.00000,-1.00000]
    Explanation: a/b=2, b/c=3, so a/c = a/b * b/c = 6. b/a = 1/2. "e" never appears -> -1. a/a=1
    trivially. "x" never appears in equations at all -> -1.

Example 2:
    Input: equations = [["a","b"],["b","c"],["bc","cd"]], values = [1.5,2.5,5.0],
           queries = [["a","c"],["c","b"],["bc","cd"],["cd","bc"]]
    Output: [3.75000,0.40000,5.00000,0.20000]

Example 3:
    Input: equations = [["a","b"]], values = [0.5], queries = [["a","b"],["b","a"],["a","c"],["x","y"]]
    Output: [0.50000,2.00000,-1.00000,-1.00000]

Intuition
---------
Each equation `A/B = v` is really a weighted, directed edge: going from A to B multiplies by `v`,
and the reverse edge B -> A must exist with weight `1/v`. Once every equation is loaded as a pair
of directed edges, a query `C/D` is just "find a path from C to D and multiply the edge weights
along it" — if no path exists (or either variable was never seen), the answer is undetermined. The
direct way to answer each query is to build this weighted graph once, then run a DFS (or BFS) from
`C` toward `D` per query, multiplying the running product by each edge weight and returning it the
moment `D` is reached. That's correct and cheap for a handful of queries, but it re-walks the graph
from scratch for every query, costing O(Q * (V + E)). The distinct, genuinely different idea is
Union-Find: instead of treating each query as an independent search, maintain connected components
where every node also stores its ratio *relative to its component's root*. Union two variables by
attaching one root under the other and computing the correct relative weight so the invariant
holds; then a query is answered by finding both roots (with path compression collapsing each node's
weight straight to the root along the way) — if they're in different components, undetermined,
otherwise the answer is just the ratio of their two accumulated weights. This turns most queries
into a near-O(1) lookup after an O((V+Q)*alpha(V)) amortized build, rather than a fresh graph walk
each time.
"""

from typing import Dict, List, Tuple


# ============================================================
# Approach 1: Brute Force (weighted graph + DFS per query)
# ============================================================
# Idea: build an adjacency list where each equation contributes two directed
# edges (A->B weight v, B->A weight 1/v). For each query, DFS from the
# source, multiplying the accumulated product by each edge's weight, until
# the target is reached (or the search is exhausted).
# Time:  O(Q * (V + E)) — a fresh graph traversal for every query
# Space: O(V + E) for the graph, O(V) recursion/visited-set per query
def solve_brute_force(
    equations: List[List[str]], values: List[float], queries: List[List[str]]
) -> List[float]:
    graph: Dict[str, List[Tuple[str, float]]] = {}
    for (a, b), v in zip(equations, values):
        graph.setdefault(a, []).append((b, v))
        graph.setdefault(b, []).append((a, 1.0 / v))

    def dfs(curr: str, target: str, visited: set, product: float) -> float:
        if curr == target:
            return product
        visited.add(curr)
        for neighbor, weight in graph.get(curr, []):
            if neighbor not in visited:
                result = dfs(neighbor, target, visited, product * weight)
                if result != -1.0:
                    return result
        return -1.0

    answers = []
    for c, d in queries:
        if c not in graph or d not in graph:
            answers.append(-1.0)
        else:
            answers.append(dfs(c, d, set(), 1.0))
    return answers


# ============================================================
# Approach 2: Optimal (weighted Union-Find)
# ============================================================
# Idea: each variable's parent pointer and a per-node `weight` (its ratio
# relative to its own parent) together encode the whole component. `find`
# recursively compresses paths straight to the root while updating `weight`
# to be relative to that root (chaining ratios along the way it removes).
# `union(a, b, val)` — meaning a/b = val — attaches root(a) under root(b)
# with a weight derived so a/root(a) * root(a)/root(b) * root(b)/b stays
# consistent with a/b = val.
# Dry run: equations=[["a","b"],["b","c"]], values=[2.0, 3.0]
#   union(a,b,2.0): parent={a:a,b:b}; rootA=a, rootB=b; parent[a]=b;
#     weight[a] = 2.0 * weight[b]/weight[a] = 2.0 * 1/1 = 2.0  (a/b = 2.0)
#   union(b,c,3.0): rootB=find(b)=b, rootC=c; parent[b]=c;
#     weight[b] = 3.0 * weight[c]/weight[b] = 3.0  (b/c = 3.0)
#   query a/c: find(a) -> parent[a]=b(not root) -> recurse find(b) -> root
#     is c, weight[b] already 3.0 (b/c); weight[a] *= weight[b] -> 2.0*3.0=6.0;
#     parent[a]=c directly (path compressed). find(c)=c, weight[c]=1.0.
#     answer = weight[a] / weight[c] = 6.0 / 1.0 = 6.0
# Time:  O((V + Q) * alpha(V)) amortized — near-constant find/union with
#        path compression
# Space: O(V) — parent and weight maps
def solve_optimal(
    equations: List[List[str]], values: List[float], queries: List[List[str]]
) -> List[float]:
    parent: Dict[str, str] = {}
    weight: Dict[str, float] = {}

    def find(x: str) -> str:
        if parent[x] != x:
            root = find(parent[x])
            weight[x] *= weight[parent[x]]
            parent[x] = root
        return parent[x]

    def union(a: str, b: str, val: float) -> None:
        root_a, root_b = find(a), find(b)
        if root_a == root_b:
            return
        parent[root_a] = root_b
        weight[root_a] = val * weight[b] / weight[a]

    for a, b in equations:
        if a not in parent:
            parent[a] = a
            weight[a] = 1.0
        if b not in parent:
            parent[b] = b
            weight[b] = 1.0

    for (a, b), v in zip(equations, values):
        union(a, b, v)

    answers = []
    for c, d in queries:
        if c not in parent or d not in parent:
            answers.append(-1.0)
        else:
            root_c, root_d = find(c), find(d)
            if root_c != root_d:
                answers.append(-1.0)
            else:
                answers.append(weight[c] / weight[d])
    return answers


# ============================================================
# Key Takeaways
# ============================================================
# - Turning "A/B = v" into a pair of weighted directed edges (v and 1/v)
#   converts a division-chaining problem into a standard graph-reachability
#   problem — this reduction is the key insight, independent of which
#   traversal technique you then use.
# - Common mistake: forgetting the reverse edge (B->A weight 1/v), which
#   silently breaks any query that needs to traverse "backwards" through an
#   equation, or forgetting to check that both query variables actually
#   appear in the graph before searching (they might be totally unknown).
# - Related/variant problems to try next: Number of Provinces (plain
#   Union-Find), Accounts Merge, Graph Valid Tree.


if __name__ == "__main__":
    tests = [
        (
            (
                [["a", "b"], ["b", "c"]],
                [2.0, 3.0],
                [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
            ),
            [6.0, 0.5, -1.0, 1.0, -1.0],
        ),
        (
            (
                [["a", "b"], ["b", "c"], ["bc", "cd"]],
                [1.5, 2.5, 5.0],
                [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
            ),
            [3.75, 0.4, 5.0, 0.2],
        ),
        (
            ([["a", "b"]], [0.5], [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]]),
            [0.5, 2.0, -1.0, -1.0],
        ),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            # Compare with floating point tolerance instead of exact equality.
            ok = len(result) == len(expected) and all(
                abs(r - e) < 1e-4 for r, e in zip(result, expected)
            )
            status = "OK" if ok else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:80s} -> {result!r}  [{status}]")
