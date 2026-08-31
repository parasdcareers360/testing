# Common Mistakes — Intervals

> **Type:** Study notes

- **Forgetting to sort, or sorting by the wrong key.** Merge/meeting-room problems need a sort by
  `start`; the greedy "maximum non-overlapping intervals" problem needs a sort by `end` — using the
  wrong key silently produces a wrong-but-plausible-looking answer instead of an obvious crash.
  Decide the sort key *before* writing the loop, and say which one and why.
- **Using strict `<` instead of `<=` (or vice versa) in the overlap check.** Whether touching
  intervals (`[1,3]` and `[3,5]`) count as "overlapping" is a real ambiguity the problem statement
  usually settles — clarify it in step 1 instead of guessing, since it flips every downstream
  comparison (`merge_intervals`, `insert_interval`, room counting) between `<` and `<=`.
  `template.py` Shape 1 uses `<=`/`<=` (touching counts as overlap) — confirm this matches the
  problem before reusing it.
- **Mutating the input list of intervals in place** while sorting or merging, when the interviewer
  expects the original list preserved (or when doing so causes confusing aliasing bugs with nested
  lists). `merge_intervals_template` copies with `intervals[0][:]` and appends new lists rather than
  mutating elements of the input — do the same unless in-place mutation is explicitly fine.
- **Comparing non-adjacent intervals directly instead of trusting the sorted sweep.** Once sorted by
  start, you never need an O(n²) all-pairs comparison — if you find yourself writing a nested loop
  over intervals, you've missed that sorting already collapsed the problem to one linear pass.
- **Off-by-one in the meeting-rooms heap check.** `end_times[0] <= start` (room frees up exactly
  when the new meeting starts, back-to-back meetings can share a room) versus `end_times[0] < start`
  is the same ambiguity as the general overlap check — get the problem's convention on touching
  intervals right, or the room count will be off by one on inputs with back-to-back meetings.
- **Solving "insert interval" by appending then calling the general merge function.** It works, but
  it's O(n log n) with an unnecessary sort on an input that's already sorted — the three-phase
  single-pass version (`template.py` Shape 3) is O(n) and is what interviewers are checking for when
  they specifically state the input is pre-sorted.
- **Not clarifying whether intervals can be empty or a single point** (`[5, 5]`) — a zero-length
  interval is a legal edge case in some problem variants and breaks assumptions like `start < end`
  if you bake that assumption into a comparison.
