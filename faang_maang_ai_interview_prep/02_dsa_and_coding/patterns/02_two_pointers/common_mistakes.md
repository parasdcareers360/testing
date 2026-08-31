# Common Mistakes — Two Pointers

> **Type:** Study notes

- **Forgetting the array must be sorted first.** Opposite-direction two-sum only works because
  moving `left` strictly increases the sum and moving `right` strictly decreases it — on an
  unsorted array that guarantee doesn't hold, and you'll silently produce wrong answers instead of
  crashing. If the input isn't sorted and you need original indices, sort a list of
  `(value, original_index)` pairs, not the raw array.
- **Moving the wrong wall in Container With Most Water.** Moving the *taller* wall inward can never
  increase the area (width shrinks, and the limiting height is still capped by the shorter wall or
  gets worse) — always move the shorter wall. Moving the taller one "because it looks bigger" is
  the single most common bug in this problem.
- **Off-by-one on the `while left < right` vs. `while left <= right` boundary.** For pair-finding,
  `left < right` is correct — `left == right` means the same element twice, which is invalid unless
  the problem explicitly allows reusing an index. For partition-style problems (e.g. Dutch national
  flag), the correct condition may differ; re-derive it, don't copy blindly.
- **Not skipping duplicates in 3Sum/4Sum.** After sorting, failing to advance past repeated values
  for the outer loop *and* for `left`/`right` after a match produces duplicate triplets in the
  output — this is the most common reason a correct-looking 3Sum fails on LeetCode's test cases.
- **Using `read`/`write` pointers but forgetting `write` starts one behind `read`.** In
  `remove_duplicates_sorted`, initializing `write = 1` instead of `0` (or comparing
  `nums[read] != nums[read - 1]` instead of `nums[write]`) breaks as soon as more than one
  duplicate run appears back to back.
- **Applying fast/slow cycle detection without checking `fast.next` too.** `fast = fast.next.next`
  will throw `AttributeError: 'NoneType' object has no attribute 'next'` on an even-length
  non-cyclic list if you only check `while fast is not None` — the loop condition must be
  `while fast and fast.next`.
- **Confusing "cycle exists" with "find the cycle's start."** The meeting point from Floyd's
  algorithm is *not* the start of the cycle — finding the start requires resetting one pointer to
  `head` and advancing both one step at a time until they meet again (see
  [`05_linked_lists/concept.md`](../05_linked_lists/concept.md)). Don't return the meeting node
  when the question asks for the cycle's entry point.
