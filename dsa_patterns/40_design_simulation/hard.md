# Hard — LFU Cache

**Source**: LeetCode #460
**Pattern**: Design / Simulation
**Difficulty**: Hard

## Problem Statement
Design and implement a data structure for a **Least Frequently Used (LFU) cache**.

Implement the `LFUCache` class:
- `LFUCache(capacity)` initializes the object with the `capacity` of the data structure.
- `get(key)` gets the value of `key` if it exists in the cache; otherwise returns `-1`.
- `put(key, value)` updates the value of `key` if present, or inserts the `key`-`value` pair if not present. When the cache reaches `capacity`, it should invalidate and remove the **least frequently used** key before inserting a new item. For this problem, when there is a **tie** (multiple keys with the same lowest use frequency), the **least recently used** key among the tied keys should be invalidated.

To determine the least frequently used key, a **use counter** is maintained for every key. The use counter for a key is incremented whenever `get(key)` or `put(key, value)` is called on it (including a `put` on a key that already exists — that also counts as a use). When a key is removed, its counter is discarded entirely (a brand new key later reusing the same integer starts fresh at counter 1).

Both `get` and `put` must run in **O(1) average time complexity.**

This is a genuine step up in design complexity from LRU Cache (medium.md in this folder): LRU only needed to track *one* dimension of order (recency). LFU needs to track **two** dimensions simultaneously — frequency (primary eviction key) and recency-within-a-frequency (tie-breaker) — while still guaranteeing O(1) for every operation. This requires layering a second structure per frequency level on top of the LRU idea, plus careful bookkeeping of the current global minimum frequency.

## Constraints
- `0 <= capacity <= 10^4` (capacity 0 means every `put` is immediately a no-op — nothing can ever be stored).
- `0 <= key <= 10^5`
- `0 <= value <= 10^9`
- At most `2 * 10^5` calls will be made to `get` and `put` combined.

## Examples
**Example 1**
```
Input:
["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]

Output:
[null, null, null, 1, null, -1, 3, null, -1, 3, 4]
```
Explanation:
```
LFUCache lfu = new LFUCache(2);
lfu.put(1, 1);   // cache={1:1}, freq: 1->1
lfu.put(2, 2);   // cache={1:1, 2:2}, freq: 1->1, 2->1
lfu.get(1);      // return 1; freq: 1->2, 2->1
lfu.put(3, 3);   // capacity full. Both keys 1 and 2... key 2 has lower freq (1) than key1 (2),
                 // so evict key 2. cache={1:1, 3:3}, freq: 1->2, 3->1
lfu.get(2);      // return -1 (not found)
lfu.get(3);      // return 3; freq: 1->2, 3->2
lfu.put(4, 4);   // capacity full. Keys 1 and 3 are now tied at freq 2 — evict the least
                 // recently used among them, which is key 1 (used at get(1) earlier, before
                 // key 3 was bumped to freq 2 via get(3)). cache={3:3, 4:4}, freq: 3->2, 4->1
lfu.get(1);      // return -1 (evicted)
lfu.get(3);      // return 3; freq: 3->3, 4->1
lfu.get(4);      // return 4; freq: 3->3, 4->2
```

**Example 2**
Input: `capacity = 0`; `put(0, 0)`; `get(0)`.
Output: `null, -1`.
Explanation: With capacity 0, nothing can ever be cached, so `put` is a no-op and every `get` returns `-1`.

## Intuition — Why This Pattern
**Naive approach**: Store everything in a single hashmap `key -> (value, freq)`. On `get`/`put`, increment the frequency. To evict, scan **all** entries to find the minimum-frequency key, breaking ties by... needing to also track recency somehow, which a plain hashmap doesn't preserve. This makes eviction O(n) (a full scan), violating the O(1) requirement, and doesn't even track the recency tie-breaker correctly without extra bookkeeping.

**What's inefficient**: Just like LRU Cache needed a doubly linked list to avoid O(n) search for "the least recently used item," LFU needs an efficient way to find "the least frequently used item, tie-broken by recency" — without scanning everything. The frequency can only ever increase for a given key (never decrease), and it always increases by exactly 1 per use — this structure is exploitable.

**The insight (layered Design/Simulation)**: Think of the cache as **many small LRU caches, one per frequency level**, plus one hashmap that lets you jump straight to which frequency-bucket a given key currently lives in:
1. `cache: key -> (value, freq)` — O(1) lookup of a key's current value and frequency.
2. `freq_to_keys: freq -> OrderedDict of key (in recency order)` — for each frequency level, an ordered structure (acting exactly like the recency-list inside LRU Cache) where the oldest (least-recently-used) key at that frequency sits at the front, and the newest at the back. Python's `dict`/`OrderedDict` gives O(1) average `move_to_end`, O(1) average delete-by-key, and O(1) `popitem(last=False)` to pop the front — perfect for this.
3. `min_freq` — track the current global minimum frequency across all keys, updated incrementally so we never need to scan for it.

On every `get`/`put`-on-existing-key, a key's frequency goes from `f` to `f+1`: remove it from `freq_to_keys[f]` (O(1) average dict delete) and insert it at the *end* (most-recently-used position) of `freq_to_keys[f+1]` (O(1) average dict insert, which in Python's regular/ordered dict always appends new keys at the end). If removing it emptied `freq_to_keys[f]` **and** `f` was the current `min_freq`, then `min_freq` must increase — and it always increases by exactly 1, because the only way to reach frequency `f` was by coming from `f-1`, so if `f` was the minimum, no keys exist below `f`, and after this removal the smallest remaining frequency is exactly `f+1` (the bucket we just inserted into, which is now non-empty). On eviction, pop the front (LRU) entry of `freq_to_keys[min_freq]` — that's simultaneously the lowest frequency and, within that frequency, the least recently used, exactly the tie-break rule the problem requires.

## Approach
1. **Constructor**: store `capacity`; `cache = {}` (key -> [value, freq]); `freq_to_keys = defaultdict(OrderedDict)`; `min_freq = 0`.
2. **Helper `_touch(key)`** (bump a key's frequency by 1, used by both `get` and the "existing key" branch of `put`):
   a. `value, freq = cache[key]`.
   b. Delete `key` from `freq_to_keys[freq]`.
   c. If `freq_to_keys[freq]` is now empty: delete that empty bucket; if `freq == min_freq`, set `min_freq += 1`.
   d. Insert `key` into `freq_to_keys[freq + 1]` (appends at the "most recent" end automatically).
   e. Update `cache[key] = [value, freq + 1]`.
3. **`get(key)`**:
   a. If `key not in cache`: return `-1`.
   b. Otherwise `_touch(key)`, then return `cache[key][0]` (the value).
4. **`put(key, value)`**:
   a. If `capacity == 0`: do nothing, return.
   b. If `key` already in `cache`: update `cache[key][0] = value`, then `_touch(key)` (bumps frequency, handles recency), return.
   c. Otherwise (new key): if `len(cache) >= capacity`, evict — pop the front item of `freq_to_keys[min_freq]` via `popitem(last=False)` (this is simultaneously the lowest-frequency and, among those, least-recently-used key), and delete it from `cache`.
   d. Insert the new key: `cache[key] = [value, 1]`; put `key` into `freq_to_keys[1]`; set `min_freq = 1` (a brand new key always starts the frequency landscape fresh at 1, so 1 is now trivially the minimum).
5. Every step above only does O(1)-average hashmap/OrderedDict operations (`del`, `[]=`, `popitem(last=False)`), so both `get` and `put` are O(1) average overall.

## Dry Run
Trace Example 1 with `capacity = 2`. Notation: `cache = {key: (value, freq)}`; `freq_to_keys = {freq: [keys in recency order, oldest first]}`.

| Operation | cache | freq_to_keys | min_freq | Returned |
|-----------|-------|---------------|----------|----------|
| put(1,1)  | {1:(1,1)} | {1:[1]} | 1 | — |
| put(2,2)  | {1:(1,1), 2:(2,1)} | {1:[1,2]} | 1 | — |
| get(1)    | {1:(1,2), 2:(2,1)} | {1:[2], 2:[1]} | 1 (freq 1 bucket non-empty, still has 2) | 1 |
| put(3,3)  | len(cache)=2 >= capacity(2): evict front of freq_to_keys[min_freq=1] -> key 2. cache={1:(1,2)}. Insert 3: cache={1:(1,2), 3:(3,1)} | {1:[3], 2:[1]} | 1 | — |
| get(2)    | (unchanged; 2 not in cache) | (unchanged) | 1 | -1 |
| get(3)    | {1:(1,2), 3:(3,2)} | {1:[] deleted, 2:[1,3]} | freq 1 bucket emptied and 1==min_freq -> min_freq=2 | 3 |
| put(4,4)  | len(cache)=2 >= capacity(2): evict front of freq_to_keys[min_freq=2] -> [1,3], front is 1 (added to freq2 first, at get(1)); evict key 1. cache={3:(3,2)}. Insert 4: cache={3:(3,2), 4:(4,1)} | {1:[4], 2:[3]} | 1 (new key resets min_freq) | — |
| get(1)    | (unchanged; 1 not in cache) | (unchanged) | 1 | -1 |
| get(3)    | {3:(3,3), 4:(4,1)} | {1:[4], 2:[] deleted, 3:[3]} | min_freq stays 1 (freq2 emptied but 2 != min_freq) | 3 |
| get(4)    | {3:(3,3), 4:(4,2)} | {1:[] deleted, 2:[4], 3:[3]} | freq1 bucket emptied and 1==min_freq -> min_freq=2 | 4 |

Final sequence of returned `get` values: `1, -1, 3, -1, 3, 4` — matching Example 1's expected output exactly (`[.., 1, .., -1, 3, .., -1, 3, 4]`).

## Solution (Python 3)
```python
from collections import defaultdict, OrderedDict


class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> [value, freq]
        self.freq_to_keys = defaultdict(OrderedDict)  # freq -> OrderedDict(key -> None), oldest first
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        value, freq = self.cache[key]
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        self.freq_to_keys[freq + 1][key] = None
        self.cache[key] = [value, freq + 1]

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self._touch(key)
        return self.cache[key][0]

    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return

        if key in self.cache:
            self.cache[key][0] = value
            self._touch(key)
            return

        if len(self.cache) >= self.capacity:
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            if not self.freq_to_keys[self.min_freq]:
                del self.freq_to_keys[self.min_freq]
            del self.cache[evict_key]

        self.cache[key] = [value, 1]
        self.freq_to_keys[1][key] = None
        self.min_freq = 1


if __name__ == "__main__":
    lfu = LFUCache(2)
    print(lfu.put(1, 1))   # None
    print(lfu.put(2, 2))   # None
    print(lfu.get(1))      # 1
    print(lfu.put(3, 3))   # None (evicts key 2)
    print(lfu.get(2))      # -1
    print(lfu.get(3))      # 3
    print(lfu.put(4, 4))   # None (evicts key 1, tie-broken by recency)
    print(lfu.get(1))      # -1
    print(lfu.get(3))      # 3
    print(lfu.get(4))      # 4

    print("---")
    zero_cap = LFUCache(0)
    zero_cap.put(0, 0)
    print(zero_cap.get(0))  # -1
```

## Complexity Analysis
- Time: O(1) average for both `get` and `put`. All operations are hashmap/`OrderedDict` operations (`del d[k]`, `d[k] = v`, `popitem(last=False)`), each O(1) average in Python.
- Space: O(capacity) — `cache` holds at most `capacity` entries, and `freq_to_keys` collectively holds at most `capacity` keys spread across at most `capacity` distinct frequency buckets.

## Key Takeaways
- LFU generalizes LRU Cache's "hashmap + ordered structure" idea by adding a **second dimension** (frequency) on top of recency: think of it as "many LRU caches, one per frequency level, plus a pointer to which one currently has the minimum frequency."
- The `min_freq` invariant — it only ever needs to be incremented by exactly 1 when its bucket empties, and reset to 1 on any new insertion — is the crux of making this O(1); without it you'd need to scan all buckets to find the new minimum after an eviction empties one.
- Common mistake: forgetting that a `put` on an **already-existing** key must also count as a "use" (bump its frequency), not just update its value.
- Common mistake: not cleaning up empty `OrderedDict` buckets in `freq_to_keys` — while not strictly required for correctness (an empty bucket is simply never chosen since `min_freq` skips it correctly, and `defaultdict` would silently recreate it if referenced), leaving them around is a memory leak in a long-running cache; the reference solution above deletes them proactively.
- Related/variant problems to try next: **LRU Cache** (LeetCode #146, see medium.md — the single-dimension version of this same design idea) and **Design Twitter** (LeetCode #355, hashmap + heap/K-way-merge to build a chronological news feed) as another hashmap-centric design exercise at similar complexity.
