# Common Mistakes — Backtracking

> **Type:** Study notes

- **Appending `path` instead of `path[:]` (or `list(path)`) to the result.** `path` is the *same*
  list object being mutated throughout the recursion — appending it directly means every entry in
  `result` ends up pointing at the same, eventually-empty list once backtracking finishes popping
  everything off. This is the single most common bug in this pattern and it's silent: the code
  runs, the count of results is even right, but every result is wrong (usually `[]` or the final
  state repeated). Always copy at the point of recording, as in every shape in `template.py`.
- **Forgetting the un-choose step.** Skipping `path.pop()` (or the equivalent `used[i] = False`,
  `cols.remove(col)`) after the recursive call means state leaks across sibling branches — the
  second branch in a `for` loop sees state left over from the first, producing wrong or missing
  results. Backtracking is only correct if the state after exploring branch `i` is identical to the
  state before it, so every "choose" needs a matching "un-choose" on every code path, including
  when you prune before recursing (in which case there's nothing to undo, since nothing was chosen
  yet).
- **Using `start` index for permutations or `used` array for subsets.** These two index-management
  strategies are not interchangeable: subsets/combinations need `start` (never revisit an earlier
  position, order doesn't matter) while permutations need `used` (revisit any unused position,
  order matters). Mixing them up produces either missing permutations or duplicate subsets.
- **Deduplicating with a `set` of results instead of skipping duplicates during the search.**
  Generating all subsets/permutations first and deduplicating with `set(tuple(x) for x in result)`
  afterward wastes exponential work regenerating duplicates you're about to throw away — the
  correct fix is the sort-then-skip-same-value-sibling check (`if i > start and nums[i] ==
  nums[i-1]: continue`), done *during* the search so duplicate branches are never explored.
- **Checking `i > 0` instead of `i > start` in the duplicate-skip condition.** `i > start` means
  "skip if this is not the first choice *at this recursion depth*" — using `i > 0` instead would
  also forbid the first element of a branch from equaling an element used in a completely different
  branch higher up the tree, which incorrectly prunes valid results (e.g. it would wrongly block
  `[2, 2]` as a subset of `[1, 2, 2]`).
- **Pruning after recursing instead of before.** Checking validity inside the recursive call (at
  the top of `backtrack`) instead of in the `for` loop before calling `backtrack` still does the
  work of entering the call frame and often still explores one extra level before bailing out — for
  constraint-heavy problems like N-Queens this is the difference between a solution that finishes
  and one that doesn't within interview time. Check `is_valid` in the loop, before the choose step.
- **Not stating the exponential complexity out loud.** Writing correct backtracking code without
  ever saying "this is O(2^n)" or "O(n!)" reads as not understanding what you just wrote —
  interviewers expect you to name the complexity unprompted for this pattern specifically, since
  the whole point of recognizing "this needs backtracking" is recognizing you've accepted
  exponential time because the problem asks for *all* solutions.
- **Rebuilding the board/string from scratch every recursive call instead of mutating and undoing
  in place.** For N-Queens/Sudoku-shaped problems, passing a fresh copy of the board down each
  recursive call instead of mutating shared state (and undoing the mutation on the way back) turns
  an O(n) per-step cost into an O(n^2) or worse per-step cost — mutate the shared `placement`
  array / board and undo it, don't reconstruct.
