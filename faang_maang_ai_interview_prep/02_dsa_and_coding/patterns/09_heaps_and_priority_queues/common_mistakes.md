# Common Mistakes — Heaps & Priority Queues

> **Type:** Study notes

- **Assuming `heapq` has a max-heap mode.** It doesn't — there's no `heapq.heappush_max` or a flag
  to flip the ordering. Forgetting to negate on both `push` and `pop` (negating only one side) is the
  single most common bug in this pattern; wrap it in a small class (see `template.py` Shape 1) if
  you're using it more than twice in a solution, so the negation logic lives in one place.
- **Pushing raw tuples where the second element isn't comparable.** `heapq` compares tuples
  element-by-element, so if two items tie on the first field, Python compares the second field next —
  if that's a custom object without `__lt__`, you get a `TypeError` at runtime. In `merge_k_sorted`
  (Shape 3), the tuple includes `list_index` specifically so ties on `value` fall back to comparing
  ints, never comparing the list contents themselves.
- **Popping from an empty heap without checking.** `heapq.heappop([])` raises `IndexError` — guard
  with `if heap:` before popping, especially in merge-K-lists style loops where a source list can run
  out mid-merge.
- **Confusing "bounded heap keeps the top K" with "bounded heap keeps K in sorted order."** A heap of
  size K after the top-K loop (`template.py` Shape 2) contains the correct *set* of top-K elements,
  but the heap array itself is not sorted — call `sorted()` on it if the problem wants an ordered
  result, don't return the raw internal list and assume it's ordered.
- **Rebuilding the heap from scratch on every insert instead of using `heapify` once and
  `heappush`/`heappop` incrementally.** If you're calling `heapq.heapify(list)` inside a loop that
  runs per input element, you've turned an O(log n) incremental operation into O(n log n) —
  `heapify` is for turning an existing full list into a heap *once*, not for maintaining one over a
  stream.
- **Two-heap median: pushing directly into the target heap instead of routing through `small`
  first.** The correct invariant-preserving order is always "push into `small`, move `small`'s max
  into `large`, then rebalance if `large` grew past `small`" (see `template.py` Shape 4) — pushing
  based on comparing `num` to the current tops directly is more error-prone and easy to get backwards
  under pressure; the fixed three-line routine is worth memorizing exactly as-is.
- **Forgetting heaps are for *incremental* extremes, not one-shot sorting.** If you only need the
  final top-K once on static data and don't care about O(n log k) vs O(n log n), `sorted(nums)[-k:]`
  is simpler to write correctly under time pressure — reach for a heap when insertions/removals are
  interleaved with reads (streaming, scheduling), not automatically for every "top K" phrasing.
