# Medium — Course Schedule II

**Source**: LeetCode #210
**Pattern**: Topological Sort
**Difficulty**: Medium

## Problem Statement
There are `numCourses` courses labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` means you must take course `b` before course `a`.

Return **any** ordering of courses you should take to finish all courses. If it is impossible to finish all courses (because of a cycle in the prerequisites), return an empty array.

This extends the "can you finish" decision problem (Course Schedule I) by requiring you to actually construct and output a valid order, not just answer yes/no.

## Constraints
- `1 <= numCourses <= 2000`
- `0 <= prerequisites.length <= numCourses * (numCourses - 1)`
- `prerequisites[i].length == 2`
- `0 <= a, b < numCourses`
- `a != b`
- All pairs `[a, b]` are distinct.

## Examples
**Example 1**
```
Input: numCourses = 4, prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]
Output: [0, 1, 2, 3]  (or [0, 2, 1, 3])
```
Explanation: Course 0 has no prerequisites, so it comes first. Courses 1 and 2 both require course 0. Course 3 requires both 1 and 2. Either order of 1 and 2 is valid as long as both precede 3 and both follow 0.

**Example 2**
```
Input: numCourses = 2, prerequisites = [[1, 0], [0, 1]]
Output: []
```
Explanation: Course 1 needs course 0, and course 0 needs course 1 — a cycle. No valid order exists.

## Intuition — Why This Pattern
**Brute force**: Try every permutation of the `numCourses` labels and check whether it respects every prerequisite pair. This is O(V! * E) — utterly infeasible even for small `numCourses`.

**A smarter brute force**: repeatedly scan all courses, find one whose prerequisites are all already scheduled, append it, and repeat. This works but rescans everything every round: O(V^2 + V*E) in the worst case, and you need a separate mechanism to detect "stuck" (cyclic) states.

**The insight**: This is precisely what topological sort computes, and Kahn's algorithm gives you the actual order "for free" as a side effect of cycle detection. Track in-degree (number of unmet prerequisites) for each course, start with all in-degree-0 courses in a queue, and every time you pop a course to add to the result, decrement its neighbors' in-degrees. A neighbor becomes available (in-degree 0) exactly when all of its prerequisites have been placed before it in the output — so the queue naturally emits courses in a valid dependency order. If the final result doesn't contain all `numCourses` courses, some subset is trapped in a cycle, so we return `[]`. This achieves O(V + E) instead of the polynomial/exponential brute-force approaches.

## Approach
1. Build an adjacency list `graph` where `graph[b]` contains `a` for every prerequisite pair `[a, b]` (edge `b -> a`, meaning b must precede a).
2. Compute `in_degree[i]` for every course `i` = number of prerequisites it has.
3. Initialize a queue with all courses whose `in_degree` is 0.
4. Initialize an empty list `order`.
5. While the queue is not empty:
   a. Pop a course `node`, append it to `order`.
   b. For each neighbor `nbr` of `node`, decrement `in_degree[nbr]`.
   c. If `in_degree[nbr]` reaches 0, push `nbr` onto the queue.
6. If `len(order) == numCourses`, return `order` (a valid topological order). Otherwise, return `[]` (a cycle exists, blocking some courses from ever reaching in-degree 0).

## Dry Run
Example 1: `numCourses = 4`, `prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]`.

- Build graph (edge `b -> a` for `[a, b]`):
  - `[1, 0]` → edge `0 -> 1`
  - `[2, 0]` → edge `0 -> 2`
  - `[3, 1]` → edge `1 -> 3`
  - `[3, 2]` → edge `2 -> 3`
  - `graph = {0: [1, 2], 1: [3], 2: [3], 3: []}`
- In-degrees: course 1 needs 0 (deg 1), course 2 needs 0 (deg 1), course 3 needs 1 and 2 (deg 2), course 0 needs nothing (deg 0).
  `in_degree = [0, 1, 1, 2]`
- Queue init: only course 0 has in-degree 0. `queue = [0]`, `order = []`.
- Iteration 1: pop `0` → `order = [0]`. Neighbors `[1, 2]`: decrement `in_degree[1]` 1→0 (push 1), decrement `in_degree[2]` 1→0 (push 2). `queue = [1, 2]`, `in_degree = [0, 0, 0, 2]`.
- Iteration 2: pop `1` → `order = [0, 1]`. Neighbors `[3]`: decrement `in_degree[3]` 2→1 (not zero, don't push). `queue = [2]`, `in_degree = [0, 0, 0, 1]`.
- Iteration 3: pop `2` → `order = [0, 1, 2]`. Neighbors `[3]`: decrement `in_degree[3]` 1→0 (push 3). `queue = [3]`, `in_degree = [0, 0, 0, 0]`.
- Iteration 4: pop `3` → `order = [0, 1, 2, 3]`. Neighbors `[]`: nothing. `queue = []`.
- Loop ends. `len(order) == 4 == numCourses` → return `[0, 1, 2, 3]`. Matches expected output.

## Solution (Python 3)
```python
from collections import deque
from typing import List


def find_order(num_courses: int, prerequisites: List[List[int]]) -> List[int]:
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses

    for a, b in prerequisites:
        # b must be taken before a: edge b -> a
        graph[b].append(a)
        in_degree[a] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nbr in graph[node]:
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)

    return order if len(order) == num_courses else []


if __name__ == "__main__":
    print(find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))  # Expected: [0, 1, 2, 3]
    print(find_order(2, [[1, 0], [0, 1]]))                  # Expected: []
    print(find_order(1, []))                                # Expected: [0]
```

## Complexity Analysis
- Time: O(V + E) — building the graph and in-degree array is O(V + E); the BFS/Kahn loop visits every vertex once and every edge once.
- Space: O(V + E) for the adjacency list, in-degree array, queue, and output list.

## Key Takeaways
- Kahn's algorithm both detects cycles and produces a valid order in one pass — no need for a separate "is it a DAG" check followed by a separate ordering step.
- Multiple valid outputs can exist when several nodes have in-degree 0 simultaneously (the tie-breaking order among them is arbitrary, e.g., popping course 1 before course 2 or vice versa in the dry run above) — most judges accept any valid topological order.
- Common mistake: forgetting the edge case `numCourses` courses with zero prerequisites listed — the queue should still initialize correctly and output all courses in any order (e.g., `[0, 1, ..., n-1]`).
- Related/variant problems to try next: Alien Dictionary (build the graph from string comparisons instead of explicit pairs), Sequence Reconstruction, Minimum Height Trees.
