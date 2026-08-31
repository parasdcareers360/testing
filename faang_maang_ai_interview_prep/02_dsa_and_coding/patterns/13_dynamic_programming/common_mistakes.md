# Common Mistakes — Dynamic Programming

> **Type:** Study notes

- **Jumping to code before stating the state definition in one sentence.** If you can't say "`dp[i]`
  means ___" out loud, you will write a transition that's internally inconsistent (e.g. sometimes
  treating `dp[i]` as "including index i" and sometimes as "up to but excluding index i" in the same
  function). Say the state definition first, every time — see `concept.md`'s 5-step process.
- **Getting the 0/1 knapsack iteration direction backwards.** Iterating capacity ascending in 0/1
  knapsack lets the same item be added to `dp[cap]` more than once in a single pass (because
  `dp[cap - w]` may already include this item), silently turning it into unbounded knapsack. If
  items can only be used once, iterate capacity **descending** — see `template.py` Shape 6 vs. 7.
- **Off-by-one in the base row/column of 2D grid DP.** `edit_distance`'s `dp[i][0] = i` and
  `dp[0][j] = j` represent "delete/insert everything" — forgetting these (leaving them as 0) breaks
  every value that depends on them, and the bug won't show up until you test against real strings,
  not just the empty-string edge case.
- **Confusing "number of ways" DP with "is it possible" DP.** `dp[i] = dp[i-1] + dp[i-2]` (sum, for
  counting) vs. `dp[i] = dp[i-1] or dp[i-2]` (boolean, for reachability) look almost identical but
  answer different questions — misreading which one the problem wants (e.g. "can you climb the
  stairs" vs. "how many ways") produces code that runs without error but answers the wrong question.
- **Recomputing subproblems in a "memoized" solution because the cache key is wrong.** If the
  recursive function's arguments don't fully capture the state (e.g. forgetting to include "have I
  used the free skip yet" as part of the key in a variant problem), `lru_cache` will silently cache
  wrong values under a collapsed key — the state definition must include *everything* the answer
  depends on, not just the loop index.
- **Assuming bottom-up is always better than top-down.** Top-down only computes the subproblems
  actually reachable from the top query; bottom-up fills the entire table even if large parts are
  never used. For problems with a huge state space but a sparse reachable subset (e.g. some game/DP
  on a graph), top-down can be asymptotically better — don't default to bottom-up without checking.
- **Forgetting `amount = 0` / `capacity = 0` base cases in knapsack-shaped problems.** Coin change's
  `dp[0] = 0` (zero coins to make zero) and knapsack's implicit `dp[0] = 0` are easy to skip when
  initializing the array with the wrong fill value (e.g. all zeros instead of `inf` for a
  minimization problem) — this makes every other cell compute a wrong minimum silently.
- **Not stating the space-optimization follow-up.** Interviewers routinely ask "can you reduce the
  space?" after a working O(n) or O(m·n) solution. If your `dp[i]` only depends on the last 1-2
  rows/values (true for house robber, climbing stairs, and often knapsack), say so before being
  asked — see `concept.md`'s O(1) rolling-variable version of climbing stairs.
