# Greedy

> **Type:** Study notes

## Why interviewers ask this

Greedy problems test whether you can *prove* an approach is correct instead of just implementing
it — the code for a greedy solution is often trivially short (a sort plus a single pass), so the
entire interview signal is in your reasoning about *why* the locally-best choice at each step leads
to the globally-best answer. This is also the pattern where candidates most often get the code
right for the wrong reason (it happens to pass the given examples) without being able to defend it,
which is exactly what a good interviewer probes for with a follow-up counter-example.

## The core idea

A greedy algorithm builds a solution by making the choice that looks best *right now*, at each
step, and never reconsiders it. This only produces a correct (globally optimal) answer when the
problem has a specific structural property: **the locally optimal choice at each step is provably
part of some globally optimal solution.** Two common ways to justify this in an interview, stated
informally (a full proof is never expected):

- **Exchange argument**: assume an optimal solution that does *not* make the greedy choice at some
  step, then show you can swap in the greedy choice without making the solution worse — this proves
  the greedy choice is "at least as good," which is enough to justify taking it.
- **Matroid-like structure** (rarely worth naming explicitly, but the intuition matters): the
  problem's feasible solutions have a structure where locally extending the best available option
  never blocks a better global option later. Interval scheduling is the textbook example — picking
  the meeting that ends earliest never costs you a later opportunity, because any meeting it "blocks"
  would have been blocked by a later-ending choice too.

If you can't articulate *why* the greedy choice can't hurt you, that's the signal you should be
checking whether a counter-example exists (see "Greedy vs. DP" below) rather than trusting the
approach.

## Key techniques

### 1. Interval scheduling — sort by end time, greedily pick non-overlapping intervals
```python
def max_non_overlapping_intervals(intervals: list[tuple[int, int]]) -> int:
    intervals = sorted(intervals, key=lambda pair: pair[1])  # sort by END time
    count = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```
Sorting by **end time**, not start time, is the crux of the proof: the interval that ends earliest
leaves the most room for everything after it, so it's always at least as good a first choice as any
other interval that could be picked. Sorting by start time is the classic wrong-but-plausible
mistake — it passes some test cases and fails others (see `common_mistakes.md`).

### 2. Meeting Rooms II shape — track concurrent usage, not just pairwise overlap
```python
import heapq

def min_meeting_rooms(intervals: list[tuple[int, int]]) -> int:
    intervals = sorted(intervals, key=lambda pair: pair[0])  # sort by START time
    room_end_times: list[int] = []  # min-heap of end times of rooms currently in use
    for start, end in intervals:
        if room_end_times and room_end_times[0] <= start:
            heapq.heapreplace(room_end_times, end)  # reuse the earliest-freeing room
        else:
            heapq.heappush(room_end_times, end)
    return len(room_end_times)
```
This isn't a "sort by end time, take non-overlapping" problem — it's asking for peak concurrency,
so the greedy move is different: sort by start time, and greedily reuse a room the instant it frees
up (tracked via a min-heap of end times) rather than opening a new one.

### 3. Jump Game family — track the farthest reachable index in one pass
```python
def can_jump(nums: list[int]) -> bool:
    farthest = 0
    for i, x in enumerate(nums):
        if i > farthest:
            return False  # this index is unreachable, so nothing after it matters
        farthest = max(farthest, i + x)
    return True


def jump_game_min_jumps(nums: list[int]) -> int:
    jumps = 0
    current_end = 0     # farthest index reachable using `jumps` jumps so far
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:            # must jump now to make further progress
            jumps += 1
            current_end = farthest
    return jumps
```
The greedy insight: you never need to track *which* jump got you to a position, only the farthest
index reachable so far — any jump that reaches at least as far as another dominates it, so you can
discard the "how" and keep only "how far," collapsing what looks like a DP state space into O(1)
extra state.

### 4. Gas Station shape — a running-total reset is a valid greedy move
```python
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1  # not enough total fuel, no starting point works
    total = 0
    start = 0
    for i in range(len(gas)):
        total += gas[i] - cost[i]
        if total < 0:
            start = i + 1   # this segment can't be part of any valid start -> jump past it
            total = 0
    return start
```
The exchange-argument justification: if the tank goes negative between some start `s` and index
`i`, no station between `s` and `i` (inclusive) can be a valid starting point either — starting
later in that range only gives you strictly less fuel by the time you reach `i`. So the entire
failed segment can be discarded in one step rather than retried station-by-station.

## Greedy vs. DP — when greedy fails and DP is needed

Greedy is a bet: "the locally best choice never needs to be reconsidered." When that bet is wrong,
greedy gives a plausible-looking wrong answer instead of erroring — which is why disambiguating
matters more here than in most patterns.

**Classic case where greedy fails: 0/1 Knapsack.** Greedily taking items by best value-to-weight
ratio until the capacity is full is *not* optimal — e.g. capacity 10, items (weight 6, value 6) and
two items (weight 5, value 5): greedy by ratio picks the weight-6 item first (ratio 1.0, tied) then
can't fit anything else (value 6), while taking both weight-5 items gives value 10. The reason
greedy fails here: an earlier "locally best" choice (best ratio) can consume capacity that a
*combination* of later choices would have used more effectively — there's no exchange argument that
saves you, because the interaction between items' weights (not just their individual scores)
determines the optimum. This forces DP: try both "take this item" and "don't," and let the table
remember the best of both, which is exactly what greedy refuses to do (it commits to one choice and
never revisits).

**Rule of thumb to say out loud in an interview:**
- If a locally best choice can be shown to never conflict with a later optimal choice (interval
  scheduling: earliest end time never blocks a better later option) -> greedy.
- If choices **interact** — taking one changes what's optimal for the rest in a way that depends on
  the *combination*, not just each choice's individual merit (knapsack, most "maximize/minimize
  subject to a capacity/budget constraint" problems) -> DP, because you need to keep multiple
  candidate sub-solutions alive instead of committing early.
- **Fast sanity check**: try to construct a small counter-example (3-4 elements) where the greedy
  rule and brute force disagree. If you can construct one in under a minute, it's not greedy. If you
  try and can't, that's weak evidence for greedy but say explicitly you'd want the exchange argument
  to be sure, not just "I couldn't find a counter-example."

## Complexity to know cold

| Technique | Time | Space | Notes |
|---|---|---|---|
| Interval scheduling (max non-overlapping) | O(n log n) | O(1) extra (O(n) for sort) | Dominated by the sort |
| Meeting Rooms II (min rooms) | O(n log n) | O(n) for the heap | Heap size bounded by peak concurrency |
| Jump Game (reachability) | O(n) | O(1) | Single pass, no sort needed |
| Jump Game II (min jumps) | O(n) | O(1) | Single pass, "BFS by levels" intuition without a queue |
| Gas Station | O(n) | O(1) | Single pass; the reset step is what makes it O(n) not O(n^2) |

## Exercises

1. Implement `max_non_overlapping_intervals` sorting by **start** time instead of end time, then
   find a concrete input where it gives a wrong (too-small) answer compared to sorting by end time
   — this is the fastest way to internalize why end-time sorting is load-bearing, not a stylistic
   choice.
2. Take the 0/1 Knapsack counter-example above (capacity 10, items `(6,6)`, `(5,5)`, `(5,5)`) and
   write both the greedy-by-ratio version (wrong) and a brute-force check-all-subsets version
   (correct) to confirm they disagree — then articulate out loud, in one sentence, what "choices
   interact" means concretely for this input.
