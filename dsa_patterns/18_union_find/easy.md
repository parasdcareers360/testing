# Easy — Number of Provinces

**Source**: LeetCode #547
**Pattern**: Union Find (Disjoint Set Union)
**Difficulty**: Easy

## Problem Statement
There are `n` cities. Some of them are directly connected, while some are not. If city `a` is directly connected to city `b`, and city `b` is directly connected to city `c`, then city `a` is indirectly connected to city `c`.

A **province** is a group of directly or indirectly connected cities and no other cities outside of the group.

You are given an `n x n` matrix `isConnected` where `isConnected[i][j] = 1` if the `i`-th city and the `j`-th city are directly connected, and `isConnected[i][j] = 0` otherwise.

Return the total number of provinces (i.e., the number of connected components in this city graph).

## Constraints
- `1 <= n <= 200`
- `n == isConnected.length == isConnected[i].length`
- `isConnected[i][j]` is `1` or `0`.
- `isConnected[i][i] == 1` for every city (a city is always connected to itself).
- `isConnected[i][j] == isConnected[j][i]` (the matrix is symmetric).

## Examples
**Example 1**
```
Input: isConnected = [[1,1,0],
                       [1,1,0],
                       [0,0,1]]
Output: 2
```
Explanation: City 0 and city 1 are directly connected, forming one province {0, 1}. City 2 is isolated, forming its own province {2}. Total: 2 provinces.

**Example 2**
```
Input: isConnected = [[1,0,0],
                       [0,1,0],
                       [0,0,1]]
Output: 3
```
Explanation: No city is connected to any other city, so each city is its own province. Total: 3 provinces.

## Intuition — Why This Pattern
**Brute force**: Run a DFS or BFS starting from every unvisited city, marking all cities reachable from it as visited and counting that as one province, then move to the next unvisited city. This works fine and is O(n^2) since the graph is given as an adjacency matrix (you must scan a full row to find neighbors), but it requires building recursion/explicit stack logic and a visited array.

**What Union-Find offers instead**: Since all we ultimately want is "how many separate groups of mutually connected cities are there", we don't need to explicitly traverse the graph structure at all — we just need to know, for every pair of directly connected cities, that they belong in the same group. Union-Find (DSU) is built exactly for this: start each city in its own singleton group (`parent[i] = i`), and whenever `isConnected[i][j] == 1`, call `union(i, j)` to merge their groups. After processing the whole matrix, the number of provinces is simply the number of distinct "root" parents remaining. With path compression and union by rank, each union/find operation is nearly O(1) amortized, so the whole algorithm is O(n^2) (dominated by scanning the matrix) but with much simpler, non-recursive bookkeeping than DFS/BFS, and it generalizes trivially to streaming/online updates (which DFS-based approaches do not handle well).

## Approach
1. Initialize a `parent` array of size `n` where `parent[i] = i` (every city starts as its own root).
2. Define `find(x)`: follow `parent` pointers until reaching a node that is its own parent (the root), applying path compression by setting each visited node's parent directly to the found root.
3. Define `union(x, y)`: find the roots of `x` and `y`; if they differ, set one root's parent to the other, merging the two groups into one.
4. Iterate over all pairs `(i, j)` with `i < j` in the `isConnected` matrix; whenever `isConnected[i][j] == 1`, call `union(i, j)`.
5. After processing all pairs, count the number of distinct roots by calling `find(i)` for every city `i` and counting distinct results — this is the number of provinces.

## Dry Run
Example 1: `isConnected = [[1,1,0],[1,1,0],[0,0,1]]`, `n = 3`.

- Initialize `parent = [0, 1, 2]`.
- Scan pairs `(i, j)` with `i < j`:
  - `(0, 1)`: `isConnected[0][1] = 1` → union(0, 1). `find(0) = 0`, `find(1) = 1`. Different roots → set `parent[0] = 1` (attach root of 0 under root of 1). `parent = [1, 1, 2]`.
  - `(0, 2)`: `isConnected[0][2] = 0` → skip.
  - `(1, 2)`: `isConnected[1][2] = 0` → skip.
- Final `parent = [1, 1, 2]`.
- Count distinct roots: `find(0)` → parent[0]=1, parent[1]=1 (self) → root is 1. `find(1)` → root is 1. `find(2)` → parent[2]=2 (self) → root is 2.
- Distinct roots found: `{1, 2}` → 2 distinct roots.
- Output: 2. Matches expected output.

## Solution (Python 3)
```python
from typing import List


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression (halving)
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def find_circle_num(is_connected: List[List[int]]) -> int:
    n = len(is_connected)
    uf = UnionFind(n)

    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j] == 1:
                uf.union(i, j)

    roots = {uf.find(i) for i in range(n)}
    return len(roots)


if __name__ == "__main__":
    print(find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]]))  # Expected: 2
    print(find_circle_num([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))  # Expected: 3
```

## Complexity Analysis
- Time: O(n^2 * alpha(n)) ~ O(n^2) — we scan the n x n matrix once (O(n^2) pairs), and each union/find call is nearly O(1) amortized with path compression (alpha is the inverse Ackermann function, effectively constant).
- Space: O(n) for the `parent` array.

## Key Takeaways
- Union-Find is a strong alternative to DFS/BFS whenever you only need "how many groups" or "are these two items in the same group", without needing the actual traversal path.
- Always implement path compression (and ideally union by rank/size) — without it, `find` degrades to O(n) per call in adversarial chains, making the whole algorithm O(n^2) to O(n^3).
- Common mistake: forgetting that `isConnected[i][i] == 1` always (self-loops) — this doesn't affect the union-find result since union(i, i) is a no-op, but don't let it confuse your loop bounds; iterating `j` from `i+1` avoids the issue entirely.
- Related/variant problems to try next: Graph Valid Tree, Redundant Connection, Number of Islands II (dynamic/online connectivity).
