"""
LeetCode Top Interview 150 — #93 (LeetCode #207)
Course Schedule
Category: Graph General | Difficulty: Medium

Problem
-------
There are `numCourses` courses labeled `0` to `numCourses - 1`. You are given an array
`prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you must take course `bi`
first if you want to take course `ai`.

Return `true` if you can finish all courses, or `false` if it's impossible (i.e. there is a cycle
in the prerequisite graph).

Constraints
-----------
- 1 <= numCourses <= 2000
- 0 <= prerequisites.length <= 5000
- prerequisites[i].length == 2
- 0 <= ai, bi < numCourses
- All the pairs prerequisites[i] are unique.

Examples
--------
Example 1:
    Input: numCourses = 2, prerequisites = [[1,0]]
    Output: true
    Explanation: Take course 0, then course 1. No cycle.

Example 2:
    Input: numCourses = 2, prerequisites = [[1,0],[0,1]]
    Output: false
    Explanation: Course 1 needs course 0, and course 0 needs course 1 — a cycle, so neither can
    ever be started.

Intuition
---------
"Can all courses be finished" is exactly "does the prerequisite graph contain a cycle" — a directed
graph has a valid ordering of all its nodes if and only if it's a DAG. There are two equally
standard, equally O(V+E) ways to detect that, so unlike most problems in this repo there's no
slow-brute-force-vs-fast-optimal gap here; they're parallel techniques. The first is DFS with
three-color marking: track each node as unvisited / "currently on the recursion stack" / "fully
done", and a cycle exists precisely when a DFS walk reaches a node that is still on the current
stack (a back edge to an ancestor). The second is Kahn's algorithm: repeatedly peel off nodes whose
in-degree is currently zero (courses with no remaining unmet prerequisites) — if every node can
eventually be peeled off this way, there's no cycle; if some nodes are left stranded with indegree
> 0 at the end, they (and whatever they depend on) form a cycle. This file presents DFS-based cycle
detection as the primary approach and Kahn's BFS as the alternate, since Kahn's has the added
benefit (used directly in Course Schedule II) of naturally producing a valid ordering as a
byproduct, not just a yes/no answer.
"""

from collections import deque
from typing import List


# ============================================================
# Approach 1: DFS (three-color cycle detection)
# ============================================================
# Idea: build an adjacency list where course -> list of courses that depend
# on it (bi -> ai for each [ai, bi]). DFS from every unvisited node, marking
# nodes 0=unvisited, 1=in-progress (on the current recursion stack), 2=done.
# Reaching a node marked in-progress means we've looped back onto our own
# path — a cycle.
# Time:  O(V + E) — every node/edge visited once
# Space: O(V + E) — adjacency list, plus O(V) state array and recursion stack
def solve_dfs(numCourses: int, prerequisites: List[List[int]]) -> bool:
    graph: List[List[int]] = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        graph[b].append(a)  # b must be done before a

    UNVISITED, IN_PROGRESS, DONE = 0, 1, 2
    state = [UNVISITED] * numCourses

    def has_cycle(node: int) -> bool:
        if state[node] == IN_PROGRESS:
            return True
        if state[node] == DONE:
            return False

        state[node] = IN_PROGRESS
        for nxt in graph[node]:
            if has_cycle(nxt):
                return True
        state[node] = DONE
        return False

    for course in range(numCourses):
        if state[course] == UNVISITED:
            if has_cycle(course):
                return False
    return True


# ============================================================
# Approach 2: BFS (Kahn's algorithm, topological sort by in-degree)
# ============================================================
# Idea: compute each course's in-degree (number of unmet prerequisites).
# Start a queue with every course that already has in-degree 0 (no
# prerequisites). Repeatedly pop a course, count it as "completed", and
# decrement the in-degree of everything that depended on it — any neighbor
# that drops to 0 becomes newly available and joins the queue. If every
# course eventually gets completed this way, there's no cycle.
# Dry run: numCourses=2, prerequisites=[[1,0]]  (course 1 needs course 0)
#   graph: 0 -> [1]; indegree = [0, 1]
#   queue = [0] (only course with indegree 0)
#   pop 0, completed=1; neighbor 1: indegree[1] -= 1 -> 0 -> push 1
#   pop 1, completed=2; no neighbors
#   completed == numCourses (2) -> True
# Time:  O(V + E) — every node enqueued/dequeued once, every edge relaxed once
# Space: O(V + E) — adjacency list and in-degree array, plus O(V) queue
def solve_bfs(numCourses: int, prerequisites: List[List[int]]) -> bool:
    graph: List[List[int]] = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for a, b in prerequisites:
        graph[b].append(a)
        indegree[a] += 1

    queue = deque(course for course in range(numCourses) if indegree[course] == 0)
    completed = 0

    while queue:
        node = queue.popleft()
        completed += 1
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return completed == numCourses


# ============================================================
# Key Takeaways
# ============================================================
# - "Can this be scheduled" / "does this dependency graph resolve" problems
#   are cycle-detection problems in disguise — DFS three-color marking and
#   Kahn's in-degree BFS are the two standard tools, both O(V+E).
# - Common mistake: in the DFS version, marking a node DONE (instead of just
#   IN_PROGRESS) too early, or not resetting/distinguishing "currently on
#   this path" from "already fully explored" — collapsing those two states
#   into one boolean `visited` breaks cycle detection on diamond-shaped
#   (non-cyclic) graphs.
# - Related/variant problems to try next: Course Schedule II, Alien
#   Dictionary, Minimum Height Trees.


if __name__ == "__main__":
    tests = [
        ((2, [[1, 0]]), True),
        ((2, [[1, 0], [0, 1]]), False),
        ((1, []), True),
        ((3, [[1, 0], [2, 1]]), True),
        ((4, [[1, 0], [2, 1], [3, 2], [1, 3]]), False),  # 1->3->2->1 style cycle
        ((5, []), True),  # no prerequisites at all
    ]

    approaches = [solve_dfs, solve_bfs]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
