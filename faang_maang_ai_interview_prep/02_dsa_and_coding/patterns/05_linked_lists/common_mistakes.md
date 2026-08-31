# Common Mistakes — Linked Lists

> **Type:** Study notes

- **Losing the rest of the list during reversal.** Writing `curr.next = prev` before saving
  `nxt = curr.next` overwrites your only reference to the remainder of the list — you can't
  traverse forward anymore because `curr.next` no longer points where it used to. Always save
  `nxt` first; see `template.py` Shape 1.
- **Forgetting to null out the old head's `.next` in recursive reversal.** Skipping
  `head.next = None` after `head.next.next = head` leaves a two-node cycle between the old head and
  its former successor, which corrupts the list (and can cause an infinite loop in later traversal)
  even though the "obvious" part of the reversal looks right.
- **Off-by-one on fast/slow pointer starting position.** Both `slow` and `fast` should start at
  `head` (not `head` and `head.next`) for the standard middle-finding and cycle-detection loop
  conditions (`while fast and fast.next`) to be correct — starting `fast` one step ahead requires
  adjusting the loop condition and changes which "middle" you land on for even-length lists.
- **Checking `while fast` without `fast.next`.** `fast = fast.next.next` raises
  `AttributeError: 'NoneType' object has no attribute 'next'` the moment `fast.next` is `None` but
  `fast` itself isn't — the loop guard must be `while fast and fast.next`, not just `while fast`.
- **Returning the meeting point instead of the cycle's start.** Floyd's algorithm's first phase
  only proves a cycle exists; the meeting point is *not* the cycle's entry node. Finding the entry
  node requires the second phase: reset one pointer to `head`, advance both one step at a time,
  and they'll meet exactly at the start. Skipping phase 2 is the most common way to fail "Linked
  List Cycle II" after getting "Linked List Cycle I" right.
- **Not using a dummy head, then special-casing the removed/inserted node being the head.** Any
  "remove/insert relative to a computed position" problem (remove nth from end, remove duplicates,
  partition list) gets much messier without a dummy node — you end up writing an `if node_to_modify
  is head` branch that a dummy head makes unnecessary. Default to a dummy head whenever the head
  itself might need to change.
- **Comparing node values instead of node identity when checking "is this the same node."** Cycle
  detection and "find the intersection of two lists" need `slow is fast` (identity), not
  `slow.val == fast.val` (value equality) — two different nodes can coincidentally hold the same
  value, which would produce a false positive with `==`.
- **Merging two sorted lists with `<` instead of `<=` (or vice versa) and breaking stability.** For
  problems that require a stable merge (equal elements keep their original relative order), the
  tie-breaking direction in `if a.val <= b.val` matters — verify which list's node should come
  first on a tie before assuming either comparison is fine.
