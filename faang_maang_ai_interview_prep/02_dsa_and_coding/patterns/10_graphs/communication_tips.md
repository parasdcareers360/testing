# Communication Tips — Graphs

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask directed vs. undirected, weighted vs. unweighted, and whether the graph
  can be disconnected or contain cycles — these four answers alone usually determine which of the
  six algorithms in `concept.md` applies, so getting them before you start coding prevents a
  mid-solution pivot. Also ask how the graph is given (edge list, adjacency list/matrix already
  built, or implicit like a grid) since that changes your setup code.
- **Name the algorithm out loud before coding it**: "this is asking for the fewest steps between
  two nodes in an unweighted graph, so I'll use BFS" is a much stronger signal than silently writing
  a `deque` import and hoping the interviewer infers your reasoning. This pattern rewards showing
  *recognition*, not just correct syntax.
- **Brute force (step 3):** for reachability/shortest-path questions there often isn't a
  meaningfully different brute force from the optimal traversal — say so ("BFS/DFS is already the
  natural approach here, there isn't a slower brute force worth mentioning") rather than forcing an
  artificial O(n^3) strawman. For shortest-path-with-weights, the honest brute force is "try all
  paths," which you can dismiss in one sentence (exponential) before going to Dijkstra.
- **Derive the optimized approach (step 4):** when the choice is BFS vs. DFS, state *why* explicitly
  — "I need BFS specifically, not DFS, because DFS doesn't guarantee the first path found is
  shortest." When it's Union-Find vs. a traversal sweep, state the trade-off — "since edges arrive
  one at a time and I need connectivity after each one, Union-Find avoids re-running a full
  traversal per query."
- **Coding (step 5):** narrate the visited-set timing decision explicitly — "I'll mark this node
  visited when I enqueue it, not when I dequeue it, to avoid duplicate work." This is the single
  most common silent bug in this pattern (see `common_mistakes.md`), so saying it out loud both
  prevents you from getting it wrong and shows the interviewer you know why it matters.
- **Testing (step 6):** trace through a disconnected graph and a graph with a cycle specifically —
  these are the two edge cases that silently break naive traversal code (missing components) and
  topological sort (infinite loop or wrong "valid" answer) respectively. For Dijkstra, trace a case
  where the shortest path isn't the fewest-edges path (a 2-hop cheap path beating a 1-hop expensive
  one) to prove you're not accidentally doing BFS with weights ignored.
- **Complexity (step 7):** state both V and E in your Big-O, not just "O(n)" — "O(V + E) time, O(V)
  space" — and be ready to explain why: every node is visited once (O(V)) and every edge is
  examined once from each endpoint it's stored at (O(E)). For Dijkstra, the extra `log V` factor
  comes from heap operations — naming it shows you understand the heap's role, not just that you
  memorized "Dijkstra is O(E log V)."
- **Common interviewer follow-up**: "what if the graph is too large to fit in memory / edges arrive
  as a stream?" Have a one-sentence answer ready — this usually points toward Union-Find (processes
  edges one at a time, no need to hold the whole graph) or bidirectional BFS (search from both ends
  to cut the explored space) rather than a full upfront traversal.
