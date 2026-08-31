# Common Mistakes — Binary Search

> **Type:** Study notes

- **Mixing `left <= right` with `left = mid` / `right = mid`.** The classic exact-match loop uses
  `left <= right` with `left = mid + 1` / `right = mid - 1` (both bounds shrink past `mid` every
  iteration). The boundary-search loop uses `left < right` with `right = mid` (not `mid - 1`) —
  mixing the two idioms causes infinite loops (`mid` never excluded) or off-by-one misses. Pick one
  idiom per problem and stay consistent for the whole function.
- **`right = mid` without also using `mid = left + (right - left) // 2` (floor division).** In the
  `left < right` / `right = mid` idiom, if `left` and `right` are adjacent (`right = left + 1`),
  floor division makes `mid = left`, so `right = mid` doesn't shrink the space and you loop forever.
  Trace the two-element case by hand before trusting any boundary-search implementation.
- **Forgetting the search space doesn't have to be an array.** Candidates who only drill classic
  binary search freeze on "minimize the maximum" style problems because there's no array to index
  into — the array informs a *feasibility check* (see `template.py` Shape 3), and the thing you're
  binary searching over is a range of integers (capacity, speed, time), not indices.
- **Non-monotonic feasibility predicate.** Binary search on the answer only works if `feasible(x)`
  is `False...False True...True` (or the reverse) across the whole range — verify this explicitly
  before coding. A common bug is writing a `feasible` function that isn't actually monotonic because
  of an unhandled edge case, which silently breaks the binary search without an obvious symptom.
- **In rotated-array search, checking `nums[mid] < nums[right]` first instead of `nums[left] <=
  nums[mid]`.** Both determine "which half is sorted," but using `<=` against `left` handles the
  two-element case (`left == mid`) correctly; some `<` variants against `right` mishandle it. Pick
  the `nums[left] <= nums[mid]` form from `template.py` Shape 4 and memorize it rather than
  re-deriving the comparison live.
- **Not handling duplicates in rotated search.** If duplicates are allowed (`nums[left] ==
  nums[mid] == nums[right]`), you can't tell which half is sorted — the fallback is to shrink both
  ends by one (`left += 1; right -= 1`) and retry, which degrades worst case to O(n). State this
  explicitly if the interviewer says duplicates are possible.
- **Confusing `bisect_left`/`bisect_right` return semantics.** Both return an *insertion point*, not
  necessarily an index of a matching element — always check `i < len(nums) and nums[i] == target`
  (or the `bisect_right - 1` equivalent) before treating the result as a found index.
