# Hard — Reorganize String

**Source**: LeetCode #767
**Pattern**: Top K Elements (Heap) + Greedy
**Difficulty**: Hard

## Problem Statement
Given a string `s`, rearrange the characters of `s` so that no two adjacent characters are the same. Return **any** valid rearrangement. If no valid rearrangement exists (i.e., it is impossible to separate all repeated characters), return an empty string `""`.

This escalates the Top-K-Elements pattern: it's no longer enough to just identify the top frequencies — you must repeatedly extract the *currently* most frequent remaining character and greedily place it, while enforcing an adjacency constraint (never place the same character you just placed), which requires the heap to be re-queried after every single placement.

## Constraints
- `1 <= s.length <= 500`
- `s` consists of lowercase English letters only.

## Examples
**Example 1**
Input: `s = "aab"`
Output: `"aba"`
Explanation: `"aab"` rearranged so no two adjacent characters match. `"aba"` is the only such arrangement (up to the trivial identity).

**Example 2**
Input: `s = "aaab"`
Output: `""`
Explanation: `'a'` appears 3 times out of a string of length 4. Since `3 > ceil(4/2) = 2`, it is impossible to place all three `'a'`s without two of them ending up adjacent — no valid rearrangement exists.

**Example 3**
Input: `s = "vvvlo"`
Output: `"vlvov"` (one valid answer among several)
Explanation: `'v'` appears 3 times, `'l'` and `'o'` once each, length 5. `3 <= ceil(5/2) = 3`, so it's exactly at the feasibility boundary — a valid arrangement exists, and `"vlvov"` has no two adjacent characters equal.

## Intuition — Why This Pattern
**Brute force**: Generate all permutations of `s` and check each for the no-adjacent-duplicates property, returning the first valid one found. This is O(n!) — completely infeasible even for modest string lengths, and it ignores the obvious structure of the problem (character frequency is all that matters).

**What's inefficient**: A brute-force permutation search treats every character as distinguishable and explores orderings that are obviously doomed (e.g., placing three `'a'`s consecutively) without any lookahead. The real constraint is entirely frequency-driven: intuitively, if any character's count exceeds "half" the string (rounded up), it becomes impossible to spread it out enough to avoid adjacency, no matter the arrangement.

**The insight (Greedy + Heap)**: At every step of building the output string, the safest choice is to place the character that currently has the **highest remaining frequency** (as long as it isn't the same as the character just placed) — placing the most abundant character first leaves the most "room" later for the less frequent ones. This greedy rule is enforced efficiently with a **max-heap keyed by remaining frequency** (the Top-K-Elements idiom, but continuously re-queried rather than built once):
1. Push every distinct `(count, char)` onto a max-heap.
2. Repeatedly pop the most frequent character, append it to the result, decrement its count, and — critically — **hold it back for one round** (don't push it back immediately) so it can't be chosen again as the very next character. Push the *previous* round's used character back into the heap only after placing the current one (as long as it still has remaining count).
3. If at some point the heap is empty but the previously-held-back character still has count remaining, no valid placement exists — return `""`.

A quick feasibility pre-check also falls out of this reasoning: if `max_count > ceil(n / 2)`, it's mathematically impossible to interleave that character enough, so we can short-circuit and return `""` immediately (this is `max_count > (n + 1) // 2` in integer arithmetic).

## Approach
1. Count the frequency of each character in `s` using a hash map, e.g. `Counter(s)`.
2. Let `n = len(s)`. If `max(freq.values()) > (n + 1) // 2`, return `""` immediately — no valid arrangement can exist.
3. Build a max-heap of `(-count, char)` pairs for every distinct character (negate counts since Python's `heapq` is a min-heap).
4. Initialize `result = []` and `prev = None` (a placeholder representing "no character on hold").
5. While the heap is not empty:
   a. Pop the most frequent remaining character `(count, char)` (remember: `count` is stored negated).
   b. Append `char` to `result`; increment `count` toward zero (since it's negative, i.e., `count += 1`).
   c. If `prev` is currently held and still has remaining count (`prev_count < 0`), push `prev` back onto the heap now that one placement has passed since it was used.
   d. Set `prev = (count, char)` — hold the character just used so it can't be immediately reused next iteration.
6. After the loop, if `len(result) != n`, some character(s) still had unplaced remaining count when the heap ran dry — return `""`. Otherwise, join `result` into a string and return it.

## Dry Run
Trace `s = "aab"`.

**Step 1 — frequency count:** `freq = {'a': 2, 'b': 1}`, `n = 3`.

**Step 2 — feasibility check:** `max_count = 2`, `(n + 1) // 2 = 2`. `2 > 2` is false, so it's feasible — proceed.

**Step 3 — build max-heap** of `(-count, char)`: `[(-2, 'a'), (-1, 'b')]` (heapified as a min-heap on negated counts, so `-2` — the most frequent — pops first).

**Step 4 — greedy placement loop:**

Initialize `result = []`, `prev = None`.

*Iteration 1:*
- Pop most frequent: `(-2, 'a')` → `count = -2`, `char = 'a'`.
- Append `'a'` → `result = ['a']`.
- Increment count: `count = -2 + 1 = -1`.
- `prev` is `None`, nothing to push back.
- Set `prev = (-1, 'a')`.
- Heap now: `[(-1, 'b')]`.

*Iteration 2:*
- Pop most frequent: `(-1, 'b')` → `count = -1`, `char = 'b'`.
- Append `'b'` → `result = ['a', 'b']`.
- Increment count: `count = -1 + 1 = 0`.
- `prev = (-1, 'a')` has `prev_count = -1 < 0`, so push it back: heap now `[(-1, 'a')]`.
- Set `prev = (0, 'b')` (count 0 means `'b'` is exhausted, but we still hold it per the algorithm — it simply won't be pushed back next round since its count isn't `< 0`).
- Heap now: `[(-1, 'a')]`.

*Iteration 3:*
- Pop most frequent: `(-1, 'a')` → `count = -1`, `char = 'a'`.
- Append `'a'` → `result = ['a', 'b', 'a']`.
- Increment count: `count = -1 + 1 = 0`.
- `prev = (0, 'b')` has `prev_count = 0`, which is not `< 0`, so it is NOT pushed back (correctly — `'b'` has no remaining count).
- Set `prev = (0, 'a')`.
- Heap now: `[]` (empty).

Loop ends (heap empty). `len(result) = 3 = n`. Join: `"aba"` — matches the expected output.

## Solution (Python 3)
```python
import heapq
from collections import Counter


def reorganize_string(s: str) -> str:
    """Rearrange s so no two adjacent characters match, via greedy + max-heap
    (Top-K-Elements idiom, re-queried after every placement)."""
    n = len(s)
    freq = Counter(s)

    max_count = max(freq.values())
    if max_count > (n + 1) // 2:
        return ""  # provably impossible to separate the most frequent char enough

    # Max-heap simulated with negated counts.
    heap = [(-count, char) for char, count in freq.items()]
    heapq.heapify(heap)

    result = []
    prev = None  # (count, char) held back for exactly one round

    while heap:
        count, char = heapq.heappop(heap)
        result.append(char)
        count += 1  # move count closer to 0 (it's stored negated)

        if prev is not None and prev[0] < 0:
            heapq.heappush(heap, prev)

        prev = (count, char)

    if len(result) != n:
        return ""  # ran out of distinct choices before placing everything

    return "".join(result)


if __name__ == "__main__":
    out1 = reorganize_string("aab")
    print(out1, all(out1[i] != out1[i + 1] for i in range(len(out1) - 1)))  # "aba" True

    print(reorganize_string("aaab"))  # Expected: ""

    out3 = reorganize_string("vvvlo")
    print(out3, all(out3[i] != out3[i + 1] for i in range(len(out3) - 1)))  # some valid arrangement, True
```

## Complexity Analysis
- Time: O(n log u), where n = `len(s)` and u = number of distinct characters (u <= 26 for lowercase English letters, so this is effectively O(n)). Building the heap costs O(u), and each of the n placements does at most one push and one pop, each O(log u).
- Space: O(u) for the heap and frequency map, plus O(n) for the output buffer.

## Key Takeaways
- This is the "Greedy + Heap" escalation of Top-K-Elements: instead of building the heap once and reading off a fixed answer, you repeatedly re-extract the current maximum and feed a modified value back in — a pattern that recurs in Task Scheduler, Rearrange String k Distance Apart, and other "greedily pick the currently-best option under a cooldown/adjacency constraint" problems.
- The "hold back for exactly one round" trick (via the `prev` variable) is the standard way to implement an adjacency/cooldown constraint on top of a max-heap — a common mistake is pushing the just-used character back into the heap immediately, which allows illegal adjacent repeats.
- The feasibility short-circuit (`max_count > (n + 1) // 2` implies impossible) is a classic pigeonhole-principle argument worth memorizing — it lets you fail fast without running the full greedy simulation.
- Related/variant problems to try next: **Task Scheduler** (LeetCode #621 — same greedy-max-heap-with-cooldown idea, but with a fixed cooldown length `n` instead of a strict adjacency-of-1 constraint) and **Rearrange String k Distance Apart** (generalizes the "distance 1" constraint here to an arbitrary distance `k`).
