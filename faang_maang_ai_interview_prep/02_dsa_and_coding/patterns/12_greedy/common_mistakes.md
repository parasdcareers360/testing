# Common Mistakes — Greedy

> **Type:** Study notes

- **Sorting interval-scheduling problems by start time instead of end time.** Sorting by start time
  and greedily taking non-overlapping intervals looks reasonable and passes simple test cases, but
  fails on inputs like `[(1, 10), (2, 3), (4, 5)]` — sorting by start picks `(1, 10)` first and
  blocks everything else (answer 1), while the correct end-time sort picks `(2, 3)` then `(4, 5)`
  (answer 2). This is the single most common wrong-but-plausible greedy mistake — see
  `template.py` Shape 1 and always double check which field you sorted by.
- **Applying the "max non-overlapping intervals" greedy to "minimum rooms needed" problems.**
  These look similar but ask different questions — one wants the largest non-overlapping subset
  (sort by end time, discard overlaps), the other wants peak concurrent usage (sort by start time,
  track active end times in a heap). Using the wrong one silently gives a plausible but incorrect
  number; confirm which question is actually being asked before picking the shape.
- **Assuming a greedy approach is correct because it passes the example given in the prompt.** The
  interviewer's example is rarely adversarial enough to expose a wrong greedy rule — you need to
  either state the exchange-argument justification out loud or actively try to construct a
  counter-example yourself (3-4 element input) before committing to greedy as your final answer.
- **Reaching for greedy on a problem where choices interact (capacity/budget constraints).** Any
  "maximize/minimize value subject to a weight/cost/capacity budget" phrasing (0/1 knapsack, coin
  change with arbitrary denominations) is a strong signal that individual items' local scores don't
  determine the global optimum — taking the best-ratio item first can block a better *combination*
  later. Default to DP for this shape; see "Greedy vs. DP" in `concept.md`.
- **Assuming greedy coin change works for arbitrary denominations.** Greedy (always take the
  largest coin that fits) is only correct for "canonical" coin systems like US currency
  (1, 5, 10, 25) — for an arbitrary denomination set (e.g. `[1, 3, 4]` making change for `6`), greedy
  gives `4 + 1 + 1` (3 coins) when `3 + 3` (2 coins) is optimal. If the problem doesn't guarantee a
  canonical coin system, this needs DP, not greedy — don't apply the "obvious" greedy without
  checking that assumption.
- **Not resetting cleanly in running-total problems (Gas Station shape).** Forgetting to reset
  `total = 0` when it goes negative (or resetting `start` to the wrong index) either produces a
  wrong starting index or degrades the algorithm to O(n^2) by re-checking segments that were
  already proven invalid — the whole point of the reset is discarding a proven-bad segment in O(1)
  instead of retrying it station by station.
- **Confusing "sort ascending" with "sort descending" and not justifying the direction.** Greedy
  problems often hinge on sort direction (earliest end time, largest ratio, smallest remaining
  capacity) — always state *why* you're sorting the way you are, not just that you sorted, since
  getting the direction backward is a common last-minute bug that's easy to miss in a self-review
  because the code still runs without erroring.
- **Not stating what happens if the input is already invalid/impossible.** Gas Station-style
  problems need an explicit total-feasibility check (`sum(gas) < sum(cost) -> -1`) before running
  the single-pass greedy — skipping it means the greedy pass can return a plausible-looking index
  even when no valid answer exists.
