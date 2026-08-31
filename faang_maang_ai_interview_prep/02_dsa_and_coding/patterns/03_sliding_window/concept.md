# Sliding Window

> **Type:** Study notes

## Why interviewers ask this

Sliding window is the pattern that most reliably exposes candidates who "brute force with better
variable names" instead of actually reducing complexity. It's popular in phone screens and
onsites alike because the O(n²) brute force (check every substring/subarray) is obvious to
everyone, so the interviewer's real signal is whether you can articulate *why* the window never
needs to shrink from the left more than it grows from the right — i.e., whether you understand
amortized O(n), not just recite the two-pointer shape.

## The core idea

Instead of re-examining every contiguous subarray/substring from scratch, maintain a running
window `[left, right]` and incrementally update window state as `right` expands and `left`
contracts. Because each index enters and leaves the window at most once, total work across the
whole scan is O(n) even though it "looks like" a nested loop.

Recognize this pattern when you see:
- "contiguous subarray/substring" + "satisfying condition X" (sum ≤ k, at most k distinct chars, no
  repeats, contains all of another string's characters)
- "longest/shortest/maximum/minimum window such that ..."
- A fixed window size stated explicitly ("subarray of size k")

## Key techniques

### 1. Fixed-size window
```python
def max_sum_fixed_window(nums: list[int], k: int) -> int:
    window_sum = sum(nums[:k])
    best = window_sum
    for right in range(k, len(nums)):
        window_sum += nums[right] - nums[right - k]  # add new, drop the one that fell out
        best = max(best, window_sum)
    return best
```
Build the first window explicitly, then slide one step at a time: adding `nums[right]` and
removing `nums[right - k]` is O(1) per step instead of resumming the whole window, which is what
takes this from O(n·k) to O(n).

### 2. Variable-size window — shrink while invalid ("longest substring/subarray satisfying X")
```python
def longest_substring_no_repeat(s: str) -> int:
    last_seen: dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1  # jump left past the previous occurrence
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best
```
This is the "longest window satisfying X" template: expand `right` every iteration; only move
`left` when the window becomes invalid (here, a repeated character inside the current window).
Note `left` jumps directly past the stale duplicate instead of incrementing one step at a time —
still amortized O(n) since `left` only moves forward.

### 3. Variable-size window — shrink until valid again ("shortest subarray satisfying X")
```python
def min_subarray_len(target: int, nums: list[int]) -> int:
    left = 0
    total = 0
    best = len(nums) + 1
    for right, x in enumerate(nums):
        total += x
        while total >= target:          # window is valid -> try to shrink it
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return best if best <= len(nums) else 0
```
Mirror image of technique 2: expand `right` until the window satisfies the condition, then shrink
from `left` *as long as it stays valid*, recording the best (smallest) window each time before it
breaks. This only works when shrinking never makes an invalid window valid again — true here
because all values are positive, so removing elements only decreases `total`.

### 4. Frequency-matching window ("contains all characters of another string")
```python
from collections import Counter

def min_window_substring(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)  # total characters still needed (with multiplicity)
    left = 0
    best_len, best_left = float("inf"), 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:                       # window currently satisfies the condition
            if right - left + 1 < best_len:
                best_len, best_left = right - left + 1, left
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return "" if best_len == float("inf") else s[best_left:best_left + best_len]
```
Same shrink-until-invalid shape as technique 3, but the "is the window valid?" check is a
frequency-count condition (`missing == 0`) instead of a numeric one — recognize that the *shape*
of the loop doesn't change, only what "valid" means.

## Complexity to know cold

| Technique | Time | Space | Key invariant |
|---|---|---|---|
| Fixed-size window | O(n) | O(1) (or O(k) if tracking a window's contents) | window size never changes |
| Variable, expand-only-shrink-on-invalid | O(n) amortized | O(1)-O(alphabet) | `left` only moves forward |
| Variable, shrink-until-invalid | O(n) amortized | O(1)-O(alphabet) | shrinking never re-validates |
| Frequency-matching window | O(n + m) | O(alphabet) | `missing`/`need` counters instead of a single number |

## Exercises

1. Implement `longest_substring_no_repeat` and `min_subarray_len` from memory, then trace
   `min_subarray_len(7, [2,3,1,2,4,3])` by hand — expected answer is `2` (subarray `[4,3]`).
2. Take `min_window_substring` and adapt it to instead return the length of the *longest* substring
   of `s` that contains **at most** `k` distinct characters — identify which of the two "shrink"
   templates (technique 2 vs. technique 3) fits better and explain why out loud.
