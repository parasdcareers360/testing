# Medium — LRU Cache

**Source**: LeetCode #146
**Pattern**: Design / Simulation
**Difficulty**: Medium

## Problem Statement
Design a data structure that follows the constraints of a **Least Recently Used (LRU) cache**.

Implement the `LRUCache` class:
- `LRUCache(capacity)` initializes the LRU cache with **positive size** `capacity`.
- `get(key)` returns the value of the `key` if the key exists in the cache, otherwise returns `-1`. Accessing a key via `get` counts as "using" it, making it the most recently used.
- `put(key, value)` updates the value of `key` if it exists. Otherwise, adds the `key`-`value` pair to the cache. If the number of keys exceeds the `capacity` from this operation, **evict the least recently used key**. Inserting/updating a key via `put` also counts as "using" it, making it the most recently used.

The functions `get` and `put` must each run in **O(1) average time complexity**.

This is a step up in design complexity from Min Stack (easy.md): now you must coordinate **two data structures in sync** — one for O(1) key lookup, one for O(1) "move to front / evict from back" ordering — and keep them consistent across every operation, including the tricky case of updating an *existing* key's value via `put` (which must also refresh its recency without creating a duplicate entry).

## Constraints
- `1 <= capacity <= 3000`
- `0 <= key <= 10^4`
- `0 <= value <= 10^5`
- At most `2 * 10^5` calls will be made to `get` and `put`.

## Examples
**Example 1**
```
Input:
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]

Output:
[null, null, null, 1, null, -1, null, -1, 3, 4]
```
Explanation:
```
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1); // cache is {1=1}
lRUCache.put(2, 2); // cache is {1=1, 2=2}
lRUCache.get(1);    // return 1, cache order (LRU->MRU): {2=2, 1=1}
lRUCache.put(3, 3); // capacity exceeded, evicts key 2 (LRU); cache is {1=1, 3=3}
lRUCache.get(2);    // returns -1 (not found)
lRUCache.put(4, 4); // evicts key 1 (LRU); cache is {3=3, 4=4}
lRUCache.get(1);    // return -1 (not found)
lRUCache.get(3);    // return 3
lRUCache.get(4);    // return 4
```

**Example 2**
Input: `capacity = 1`; `put(2, 1)`; `get(2)`; `put(3, 2)` (evicts key 2 since capacity is 1); `get(2)`; `get(3)`.
Output: `null, 1, null, -1, 2`.
Explanation: With capacity 1, every new `put` for a different key evicts the sole existing entry.

## Intuition — Why This Pattern
**Naive approach**: Use a plain Python `dict` for `key -> value` storage (giving O(1) `get`/`put` for the value lookup itself), plus a separate Python `list` to track usage order, moving the accessed key to the end whenever it's used. The problem: to "move a key to the end" of a list, you first have to *find* it (O(n) scan, or O(n) `list.remove(key)`), and evicting the least-recently-used key means removing from the front, which is also O(n) for a plain list (shifting all elements). This violates the required O(1) average time.

**What's inefficient**: Both "find and remove an arbitrary key from an ordered sequence" and "identify the least-recently-used entry" need to be O(1), but a single data structure (dict alone, or list alone) can't give you both O(1) key lookup *and* O(1) reordering/removal from arbitrary positions.

**The insight (Design/Simulation pattern)**: Combine two data structures, each strong where the other is weak:
1. A **hashmap** (`dict`) mapping `key -> node`, where `node` is a node in...
2. ...a **doubly linked list** that maintains the usage order, with the least-recently-used node at one end (say, right after a `head` sentinel) and the most-recently-used node at the other end (right before a `tail` sentinel).

A doubly linked list lets you remove *any* node in O(1) once you have a direct reference to it (no searching needed — that's exactly what the hashmap gives you), because removing a node only requires relinking its two neighbors, which you have direct pointers to (`node.prev`, `node.next`). Using two sentinel (dummy) nodes for `head` and `tail` avoids fiddly None-checks for the "list is empty" or "removing the only node" edge cases.

## Approach
1. Define a doubly linked list `Node` with fields `key`, `value`, `prev`, `next`.
2. In the constructor:
   a. Store `capacity`.
   b. Create a hashmap `cache: dict[key -> Node]`.
   c. Create two sentinel nodes, `head` and `tail`; link them to each other (`head.next = tail`, `tail.prev = head`). The list's "most recently used" end will be right before `tail`; "least recently used" end will be right after `head`.
3. Helper `_remove(node)`: unlink `node` from the list by connecting `node.prev.next = node.next` and `node.next.prev = node.prev`. O(1).
4. Helper `_add_to_front(node)` (front = most-recently-used end, right after `head`): insert `node` right after `head` — set `node.prev = head`, `node.next = head.next`, `head.next.prev = node`, `head.next = node`. O(1).
5. `get(key)`:
   a. If `key` not in `cache`, return `-1`.
   b. Otherwise, get `node = cache[key]`, `_remove(node)`, `_add_to_front(node)` (mark as most recently used), and return `node.value`.
6. `put(key, value)`:
   a. If `key` already in `cache`: get `node = cache[key]`, update `node.value = value`, `_remove(node)`, `_add_to_front(node)` (refresh recency). Return.
   b. Otherwise (new key): if `len(cache) == capacity`, evict the least-recently-used node — that's `tail.prev` (the node right before the tail sentinel, since most-recently-used is at the front near `head`). Remove it from the list with `_remove`, and also `del cache[evicted_node.key]`.
   c. Create a new `Node(key, value)`, `_add_to_front(new_node)`, and set `cache[key] = new_node`.
7. All steps are O(1): hashmap lookup/insert/delete is O(1) average, and all linked-list operations only touch a constant number of pointers.

## Dry Run
Trace Example 1 with `capacity = 2`: `put(1,1)`, `put(2,2)`, `get(1)`, `put(3,3)`, `get(2)`, `put(4,4)`, `get(1)`, `get(3)`, `get(4)`.

Notation: list shown as `head <-> [LRU ... MRU] <-> tail`, i.e., leftmost real node is least-recently-used, rightmost real node is most-recently-used.

| Operation  | List order (LRU -> MRU) | cache keys | Returned |
|------------|--------------------------|------------|----------|
| put(1,1)   | [1]                      | {1}        | — |
| put(2,2)   | [1, 2]                   | {1,2}      | — |
| get(1)     | [2, 1] (1 moved to MRU end) | {1,2}   | 1 |
| put(3,3)   | capacity(2) exceeded -> evict LRU (2); then add 3: [1, 3] | {1,3} | — |
| get(2)     | [1, 3] (unchanged, 2 not found) | {1,3} | -1 |
| put(4,4)   | capacity(2) exceeded -> evict LRU (1); then add 4: [3, 4] | {3,4} | — |
| get(1)     | [3, 4] (unchanged, 1 not found) | {3,4} | -1 |
| get(3)     | [4, 3] (3 moved to MRU end) | {3,4} | 3 |
| get(4)     | [3, 4] (4 moved to MRU end) | {3,4} | 4 |

Final sequence of returned values: `1, -1, -1, 3, 4` — exactly matching Example 1's expected output `[1, -1, -1, 3, 4]` (ignoring the `null`s from `put` calls).

## Solution (Python 3)
```python
class Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head = Node()  # sentinel: head.next is the LRU end
        self.tail = Node()  # sentinel: tail.prev is the MRU end
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node) -> None:
        # "front" = most-recently-used end, right after head sentinel
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return

        if len(self.cache) == self.capacity:
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]

        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node


if __name__ == "__main__":
    cache = LRUCache(2)
    print(cache.put(1, 1))   # None
    print(cache.put(2, 2))   # None
    print(cache.get(1))      # 1
    print(cache.put(3, 3))   # None (evicts key 2)
    print(cache.get(2))      # -1
    print(cache.put(4, 4))   # None (evicts key 1)
    print(cache.get(1))      # -1
    print(cache.get(3))      # 3
    print(cache.get(4))      # 4

    print("---")
    c2 = LRUCache(1)
    c2.put(2, 1)
    print(c2.get(2))     # 1
    c2.put(3, 2)         # evicts key 2
    print(c2.get(2))     # -1
    print(c2.get(3))     # 2
```

## Complexity Analysis
- Time: O(1) average for both `get` and `put` — hashmap access is O(1) average, and doubly linked list insertion/removal given a direct node reference is O(1).
- Space: O(capacity) — the hashmap and linked list each hold at most `capacity` entries.

## Key Takeaways
- The canonical "design" combo is **hashmap (for O(1) lookup) + doubly linked list (for O(1) reordering/removal by reference)** — this exact combo reappears in LFU Cache (see hard.md), "Design a Skiplist," and various "most/least recently used" style designs.
- Common mistake: using a singly linked list or a plain array/deque instead of a doubly linked list — without `prev` pointers, removing an arbitrary interior node still requires O(n) to find its predecessor.
- Common mistake: forgetting to refresh recency on `put` when the key **already exists** (only handling the "new key" branch) — the problem statement explicitly requires that updating an existing key's value also marks it as most-recently-used.
- Common mistake: off-by-one on eviction timing — you must evict *before* inserting the new node when at capacity, not after (otherwise the cache temporarily holds `capacity + 1` items, and if you check size after inserting you might evict the wrong node, e.g. the one you just added).
- Related/variant problems to try next: **LFU Cache** (LeetCode #460, see hard.md — a harder variant evicting by frequency-then-recency instead of pure recency) and **Design Twitter** (LeetCode #355, hashmap + heap/merge for a news-feed-like design).
