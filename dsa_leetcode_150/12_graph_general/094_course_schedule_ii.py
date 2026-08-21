"""
LeetCode Top Interview 150 — #94 (LeetCode #210)
Course Schedule II
Category: Graph General | Difficulty: Medium

Problem
-------
There are `numCourses` courses labeled `0` to `numCourses - 1`. You are given an array
`prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course `bi`
first if you want to take course `ai`.

Return **any** valid ordering of courses you could take to finish all of them. If it is impossible
to finish all courses (there is a cycle), return an empty array.

Constraints
-----------
- 1 <= numCourses <= 2000
- 0 <= prerequisites.length <= numCourses * (numCourses - 1)
- prerequisites[i].length == 2
- 0 <= ai, bi < numCourses
- ai != bi
- All the pairs [ai, bi] are distinct.

Examples
--------
Example 1:
    Input: numCourses = 2, prerequisites = [[1,0]]
    Output: [0,1]
    Explanation: Course 0 has no prerequisites, then course 1.

Example 2:
    Input: numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]
    Output: [0,1,2,3] or [0,2,1,3]
    Explanation: Both orderings satisfy every prerequisite; either is accepted.

Example 3:
    Input: numCourses = 1, prerequisites = []
    Output: [0]

Intuition
---------
This is Course Schedule (#93) with the answer upgraded from "is it possible" to "show me an actual
order" — which is exactly what a topological sort produces, so both of that problem's O(V+E)
techniques extend directly here with no complexity gap between them (same as #93, this file
presents them as parallel alternatives rather than slow-vs-fast). With DFS, build the graph in the
"depends on" direction (course -> its prerequisites) and do a post-order walk: recurse into all of
a course's prerequisites first, and only append the course itself to the result *after* all of them
are done — so by construction every prerequisite lands in the output before the course that needs
it, with no extra reversal step required. A three-state color marking (unvisited / in-progress /
done) still detects cycles exactly as in #93; hit a node that's in-progress and the whole answer is
`[]`. With Kahn's BFS, the graph runs the opposite direction (prerequisite -> dependents) and
courses are appended to the result in the order their in-degree hits zero — the queue naturally
enforces prerequisites-before-dependents without needing a reversal either. Because multiple valid
orderings can exist whenever courses are independent of each other, there is no single "the"
correct output to compare against — correctness has to be checked by verifying every prerequisite
constraint is respected in whatever order came out, not by matching one fixed expected list.
"""

from collections import deque
from typing import List


# ============================================================
# Approach 1: DFS (post-order topological sort)
# ============================================================
# Idea: build the graph as course -> its direct prerequisites. DFS from
# every unvisited course; only append a course to `order` after recursing
# into (and finishing) all of its prerequisites, so the append order is
# automatically a valid topological order — no reversal needed. Three-state
# marking (0=unvisited, 1=in-progress, 2=done) catches cycles: revisiting an
# in-progress node means the graph has a cycle, so no valid order exists.
# Time:  O(V + E) — every node/edge visited once
# Space: O(V + E) — adjacency list, plus O(V) state array and recursion stack
def solve_dfs(numCourses: int, prerequisites: List[List[int]]) -> List[int]:
    graph: List[List[int]] = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        graph[a].append(b)  # a depends on (needs to run dfs into) b

    UNVISITED, IN_PROGRESS, DONE = 0, 1, 2
    state = [UNVISITED] * numCourses
    order: List[int] = []

    def dfs(node: int) -> bool:
        """Returns False the instant a cycle is detected."""
        if state[node] == IN_PROGRESS:
            return False
        if state[node] == DONE:
            return True

        state[node] = IN_PROGRESS
        for prereq in graph[node]:
            if not dfs(prereq):
                return False
        state[node] = DONE
        order.append(node)
        return True

    for course in range(numCourses):
        if state[course] == UNVISITED:
            if not dfs(course):
                return []
    return order


# ============================================================
# Approach 2: BFS (Kahn's algorithm, topological sort by in-degree)
# ============================================================
# Idea: same as Course Schedule's BFS approach, but instead of just counting
# completions, append each course to `order` as it's popped off the queue.
# Courses with in-degree 0 are already unblocked, so they can be appended
# right away; popping one and decrementing its dependents' in-degree makes
# more courses unblocked over time, always in a prerequisite-respecting
# order.
# Dry run: numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]
#   graph: 0->[1,2], 1->[3], 2->[3]; indegree=[0,1,1,2]
#   queue=[0] (only indegree-0 course)
#   pop 0 -> order=[0]; neighbors 1,2: indegree->[0,1,0,2]... push 1? indegree[1]=0->push;
#     push 2 similarly (indegree[2]=0) -> queue=[1,2]
#   pop 1 -> order=[0,1]; neighbor 3: indegree[3] 2->1, not 0 yet, don't push
#   pop 2 -> order=[0,1,2]; neighbor 3: indegree[3] 1->0 -> push -> queue=[3]
#   pop 3 -> order=[0,1,2,3]
#   len(order)==numCourses -> return [0,1,2,3]
# Time:  O(V + E)
# Space: O(V + E) — adjacency list and in-degree array, plus O(V) queue
def solve_bfs(numCourses: int, prerequisites: List[List[int]]) -> List[int]:
    graph: List[List[int]] = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for a, b in prerequisites:
        graph[b].append(a)
        indegree[a] += 1

    queue = deque(course for course in range(numCourses) if indegree[course] == 0)
    order: List[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return order if len(order) == numCourses else []


def is_valid_order(
    order: List[int], numCourses: int, prerequisites: List[List[int]]
) -> bool:
    """A result is correct if it's a permutation of every course (0..n-1)
    and every prerequisite constraint b-before-a is respected — regardless
    of which specific valid ordering came out."""
    if len(order) != numCourses or set(order) != set(range(numCourses)):
        return False
    position = {course: i for i, course in enumerate(order)}
    return all(position[b] < position[a] for a, b in prerequisites)


# ============================================================
# Key Takeaways
# ============================================================
# - A topological sort is what you get "for free" once you can detect
#   cycles: DFS post-order naturally emits nodes in a valid order (no
#   reversal needed if the graph is built prerequisite-ward), and Kahn's
#   BFS emits nodes in the order their dependencies clear.
# - Common mistake: building the DFS graph in the wrong direction and then
#   forgetting to reverse the post-order result — or building it the
#   "depends on" direction (as here) and reversing anyway, which silently
#   produces a backwards, invalid order.
# - Related/variant problems to try next: Course Schedule, Alien
#   Dictionary, Sequence Reconstruction.


if __name__ == "__main__":
    tests = [
        (2, [[1, 0]], True),
        (4, [[1, 0], [2, 0], [3, 1], [3, 2]], True),
        (1, [], True),
        (2, [[1, 0], [0, 1]], False),  # cycle -> impossible
        (3, [[1, 0], [2, 1], [0, 2]], False),  # 0->1->2->0 cycle
        (5, [], True),  # no prerequisites, any permutation works
    ]

    approaches = [solve_dfs, solve_bfs]
    for numCourses, prerequisites, expect_possible in tests:
        args = (numCourses, prerequisites)
        for fn in approaches:
            result = fn(*args)
            if expect_possible:
                ok = is_valid_order(result, numCourses, prerequisites)
            else:
                ok = result == []
            status = "OK" if ok else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")
