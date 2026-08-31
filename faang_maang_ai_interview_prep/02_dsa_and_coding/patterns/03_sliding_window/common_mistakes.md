# Common Mistakes — Sliding Window

> **Type:** Study notes

- **Resumming the window from scratch each step.** Recomputing `sum(nums[left:right+1])` (or
  rebuilding a `Counter` for the window) inside the loop turns an intended O(n) sliding window into
  O(n·k) or O(n²) — always update state incrementally: add what enters, remove what leaves.
- **Letting `left` decrease.** A correct sliding window never moves `left` backwards; if your
  "fix" for a bug involves decrementing `left`, the window invariant is wrong, not the pointer
  movement — re-derive what "valid" means for the window instead of patching the symptom.
  See `template.py` Shape 2 — `left` is set forward-only via `max`-like logic (`last_seen[ch] + 1`
  is always `>= left`'s current value in a correct implementation).
- **Using `while` where the problem needs `if`, or vice versa.** Shrinking with `if total >= target`
  instead of `while total >= target` (Shape 3) only shrinks by one element per outer step, which
  can leave the window larger than necessary and miss the true minimum — the shrink step needs
  `while` specifically because shrinking by one element might still leave the window valid.
- **Applying the "shrink until invalid" template to negative numbers.** `min_subarray_len_template`
  relies on all values being non-negative — adding an element to the window only ever increases
  `total`, and removing one only ever decreases it. With negative numbers present, shrinking a
  valid window doesn't monotonically make it invalid, and the whole two-pointer approach breaks
  silently (wrong answer, not a crash). Flag this constraint explicitly when you see it.
- **Off-by-one on window length.** `right - left + 1` is the window length; forgetting the `+ 1`
  (a classic when translating from 0-indexed math done on paper) under-reports every window size by
  one — this shows up as "answer is always 1 less than expected" during testing.
- **Forgetting to restore counts when shrinking a frequency-matching window.** In
  `min_window_substring`, decrementing `need[ch]` on expansion but forgetting to increment
  `need[s[left]]` back on shrink corrupts `missing`'s bookkeeping for the rest of the scan — trace
  this one by hand on a small example (`s="a", t="a"`) before trusting it.
- **Not clarifying "substring" vs. "subsequence."** Sliding window only applies to *contiguous*
  substrings/subarrays; if the interviewer says "subsequence" (allowed to skip characters), this
  entire pattern doesn't apply — that's a DP problem instead. Confirm which one is meant before
  committing to this approach.
