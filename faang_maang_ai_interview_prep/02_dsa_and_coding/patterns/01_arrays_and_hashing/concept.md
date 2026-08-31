# Arrays & Hashing

> **Type:** Study notes

## Why interviewers ask this

Arrays and hash maps are the "warm-up" pattern at almost every company — often the first phone
screen problem. It's a low bar to entry technically, but a high bar for *communication and clean
code*, since there's nowhere to hide behind algorithmic complexity. Interviewers use it to check
baseline signal before harder rounds.

## The core idea

A large fraction of array problems reduce to: "for each element, do I need fast lookup of something
I've seen before (or need later)?" A hash map (`dict`) gives O(1) average-case lookup/insert,
turning an O(n²) nested-loop approach into O(n). A hash set (`set`) is the same idea when you only
need membership, not an associated value.

Recognize this pattern when you see:
- "Find two/three elements that sum to X" (complement lookup)
- "Find duplicates" / "find the first unique element"
- "Group elements by some derived key" (anagrams, same digit sum, etc.)
- "Count frequency of X" (`collections.Counter`)

## Key techniques

### 1. Complement lookup (one-pass hash map)
```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}  # value -> index
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
    return []
```
Why one pass works: by the time you reach index `i`, `seen` contains everything *before* `i`, so
checking `complement in seen` is really "did an earlier element already complete this pair?" —
you never need to look forward.

### 2. Frequency counting
```python
from collections import Counter

def is_anagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)
```
`Counter` is a `dict` subclass — comparing two `Counter`s compares value-by-value, giving you
frequency-equality in one line instead of manually building and comparing dicts.

### 3. Grouping by derived key
```python
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))  # canonical form: same letters -> same key
        groups[key].append(s)
    return list(groups.values())
```
The trick is always the same shape: find a **canonical key** two "equivalent" items share (sorted
letters, sorted digits, normalized form), then bucket by that key.

### 4. Prefix sums (array variant of "precompute to avoid recomputation")
```python
def prefix_sums(nums: list[int]) -> list[int]:
    prefix = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    return prefix  # sum(nums[l:r]) == prefix[r] - prefix[l]
```
Turns "sum of any subarray" from O(n) per query into O(1) per query after an O(n) precompute —
recognize this whenever a problem asks many range-sum-style questions against a fixed array.

## Complexity to know cold

| Operation | Average case | Worst case (hash collisions) |
|---|---|---|
| `dict`/`set` insert | O(1) | O(n) |
| `dict`/`set` lookup | O(1) | O(n) |
| `list` index access | O(1) | O(1) |
| `list` `in` check (unsorted) | O(n) | O(n) |
| `list.append` | O(1) amortized | O(n) on resize (amortized to O(1)) |

The worst case for hash structures essentially never comes up in interviews unless you're
specifically discussing hash function design — state the average case, mention worst case exists
if pushed.

## Exercises

1. Implement `two_sum` above from memory, without looking, then verify against the 3 example cases
   in `problem_tracker.md`.
2. Given `nums = [1,1,1,2,2,3]`, write (from scratch) a function returning the k most frequent
   elements using `Counter` + sorting, then again using `Counter` + a heap — compare when each is
   better (heap wins when k is small relative to n; sort is simpler and fine for small inputs).
