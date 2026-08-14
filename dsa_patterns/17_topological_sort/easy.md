# Easy — Course Schedule

**Source**: LeetCode #207
**Pattern**: Topological Sort
**Difficulty**: Easy

## Problem Statement
There are `numCourses` courses labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` means that in order to take course `a`, you must first take course `b`.

Determine whether it is possible to finish all courses. Return `True` if you can finish all courses, or `False` otherwise.

This is fundamentally a cycle-detection problem on a directed graph: if the "must take before" relationships form a cycle, it is impossible to satisfy all prerequisites, since finishing course A requires finishing course B which requires finishing course A, and so on forever.

## Constraints
- `1 <= numCourses <= 2000`
- `0 <= prerequisites.length <= 5000`
- `prerequisites[i].length == 2`
- `0 <= a, b < numCourses`
- `a != b`
- All pairs `[a, b]` are distinct.

## Examples
**Example 1**
```
Input: numCourses = 2, prerequisites = [[1, 0]]
Output: true
```
Explanation: To take course 1 you need course 0. Take course 0 first, then course 1. No cycle, so it's possible.

**Example 2**
```
Input: numCourses = 2, prerequisites = [[1, 0], [0, 1]]
Output: false
```
Explanation: To take course 1 you need course 0, but to take course 0 you need course 1. This is a cycle — impossible to finish either.

## Intuition — Why This Pattern
**Brute force**: You could try to simulate picking any course with no unmet prerequisites, removing it, and repeating, checking every course each round to see if it has become available. That works but if done naively (rescanning every course from scratch every round) costs O(V^2 + V*E) in the worst case, and it's easy to get the "when am I stuck" check wrong.

**What's inefficient**: Repeatedly rescanning all courses to find one with zero remaining prerequisites is wasteful — most courses' prerequisite counts don't change between rounds.

**The insight**: This is exactly the definition of topological sorting a directed graph, and whether a valid topological order exists at all is exactly the test for "is this graph a DAG (no cycles)". Kahn's algorithm computes an in-degree (number of unmet prerequisites) for every node once, then processes nodes with in-degree 0 in a queue, decrementing neighbors' in-degrees as they get "completed". If we can process all `numCourses` nodes this way, there's no cycle and the answer is `True`. If the queue empties before all nodes are processed, some nodes are stuck in a cycle (or depend on a cycle) and the answer is `False`. This does the same work as the brute force but each edge and node is only touched a constant number of times: O(V + E).

## Approach
1. Build an adjacency list `graph` where `graph[b]` contains `a` for every prerequisite pair `[a, b]` (b must be taken before a, so b -> a is a directed edge).
2. Compute `in_degree[i]` = number of prerequisites required for course `i`, for every course.
3. Initialize a queue with all courses whose `in_degree` is 0 (no prerequisites, immediately takeable).
4. Initialize `taken = 0` (count of courses successfully "completed").
5. While the queue is not empty:
   a. Pop a course `node` from the queue, increment `taken`.
   b. For every neighbor `nbr` in `graph[node]` (courses that depend on `node`), decrement `in_degree[nbr]` by 1.
   c. If `in_degree[nbr]` becomes 0, push `nbr` onto the queue.
6. After the loop, if `taken == numCourses`, every course was reachable in some valid order — return `True`. Otherwise some courses were never freed from their prerequisites (they're part of, or depend on, a cycle) — return `False`.

## Dry Run
Example 2: `numCourses = 2`, `prerequisites = [[1, 0], [0, 1]]`.

- Build graph: edge `0 -> 1` (from pair `[1,0]`, since 0 must precede 1) and edge `1 -> 0` (from pair `[0,1]`, since 1 must precede 0).
  `graph = {0: [1], 1: [0]}`
- Compute in-degrees: course 0 needs course 1 done first → `in_degree[0] = 1`. Course 1 needs course 0 done first → `in_degree[1] = 1`.
  `in_degree = [1, 1]`
- Queue initialization: no course has in-degree 0. `queue = []`, `taken = 0`.
- Loop: queue is empty immediately, so the while loop body never executes.
- Final check: `taken (0) != numCourses (2)` → return `False`. Matches expected output.

Now trace Example 1: `numCourses = 2`, `prerequisites = [[1, 0]]`.
- Graph: edge `0 -> 1`. `graph = {0: [1], 1: []}`
- In-degrees: `in_degree[0] = 0` (nothing required), `in_degree[1] = 1` (needs course 0).
  `in_degree = [0, 1]`
- Queue init: course 0 has in-degree 0 → `queue = [0]`, `taken = 0`.
- Iteration 1: pop `0`, `taken = 1`. Neighbors of 0: `[1]`. Decrement `in_degree[1]` from 1 to 0 → push 1. `queue = [1]`.
- Iteration 2: pop `1`, `taken = 2`. Neighbors of 1: `[]`. Nothing to do. `queue = []`.
- Loop ends (queue empty). `taken (2) == numCourses (2)` → return `True`. Matches expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List


def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        # b must be taken before a: edge b -> a
        graph[b].append(a)
        in_degree[a] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    taken = 0

    while queue:
        node = queue.popleft()
        taken += 1
        for nbr in graph[node]:
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)

    return taken == num_courses


if __name__ == "__main__":
    print(can_finish(2, [[1, 0]]))          # Expected: True
    print(can_finish(2, [[1, 0], [0, 1]]))  # Expected: False
```

## Complexity Analysis
- Time: O(V + E) — each course (vertex) and each prerequisite pair (edge) is processed a constant number of times: once when building the graph/in-degree, once when popped from the queue, and once per outgoing edge when decrementing a neighbor's in-degree.
- Space: O(V + E) — the adjacency list stores every edge once, plus O(V) for the in-degree array and the queue.

## Key Takeaways
- "Can all tasks/courses be completed given dependency pairs" is the canonical signal for cycle detection via topological sort (Kahn's algorithm).
- You don't need to actually output an order for this problem — just check whether all `V` nodes get consumed by the algorithm. If not, a cycle exists.
- Common mistake: getting the edge direction backwards. For `[a, b]` meaning "b before a", the edge must go `b -> a`, and `in_degree[a]` (not `in_degree[b]`) should be incremented.
- Related/variant problems to try next: Course Schedule II (return the actual valid order), Graph Valid Tree, Minimum Height Trees.
