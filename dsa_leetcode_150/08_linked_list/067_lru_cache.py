"""
LeetCode Top Interview 150 — #67 (LeetCode #146)
LRU Cache
Category: Linked List | Difficulty: Medium

Problem
-------
Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the `LRUCache` class:
- `LRUCache(int capacity)` initializes the LRU cache with positive size `capacity`.
- `int get(int key)` returns the value of the `key` if it exists, otherwise returns -1.
- `void put(int key, int value)` updates the value of `key` if it exists. Otherwise, adds the
  `key`-`value` pair. If the number of keys exceeds `capacity` from this operation, evict the
  least recently used key.

The functions `get` and `put` must each run in O(1) average time complexity.

A key counts as "used" (moves to most-recently-used) whenever it's read via `get` or written via
`put`.

Constraints
-----------
- 1 <= capacity <= 3000
- 0 <= key <= 10^4
- 0 <= value <= 10^5
- At most 2 * 10^5 calls will be made to get and put.

Examples
--------
Example 1:
    Input:
        ["LRUCache","put","put","get","put","get","put","get","get","get"]
        [[2],[1,1],[2,2],[1],[3,3],[2],[4,4],[1],[3],[4]]
    Output:
        [null,null,null,1,null,-1,null,-1,3,4]
    Explanation:
        LRUCache cache = new LRUCache(2);
        cache.put(1,1);       // cache: {1=1}
        cache.put(2,2);       // cache: {1=1, 2=2}
        cache.get(1);         // returns 1, cache: {2=2, 1=1} (1 now most recent)
        cache.put(3,3);       // evicts key 2 (LRU): cache: {1=1, 3=3}
        cache.get(2);         // returns -1 (not found)
        cache.put(4,4);       // evicts key 1 (LRU): cache: {3=3, 4=4}
        cache.get(1);         // returns -1 (not found)
        cache.get(3);         // returns 3
        cache.get(4);         // returns 4

Intuition
---------
The value lookup itself is trivial with a hashmap, but "know which key was used *longest ago*" in
O(1) is the real challenge. The naive approach (Approach 1) keeps a plain dict for values plus a
separate Python list recording keys in order of use; every `get`/`put` that touches an existing
key must find and remove it from the middle of that list (`list.remove`, O(n)) before re-appending
it as most-recent, and eviction pops the front (`list.pop(0)`, also O(n) since it shifts every
remaining element). The O(1) fix combines a hashmap (key -> node) with a hand-rolled *doubly
linked list* ordered by recency: a node can be unlinked from wherever it sits and relinked at the
"most recently used" end in O(1), because a doubly linked list lets you touch a node's neighbors
directly without scanning for them. Two sentinel (dummy) head/tail nodes remove every "is this the
first/last node?" special case. Python's `collections.OrderedDict` gives the same O(1) guarantees
for free, since it's internally backed by exactly this kind of doubly linked list -- `move_to_end`
and `popitem(last=False)` do in one call what the hand-rolled version does with explicit pointers,
making it a genuinely different (library-leveraging) way to hit the same complexity.
"""

from typing import Optional
from collections import OrderedDict


# ============================================================
# Approach 1: Brute Force (dict + plain list for recency order, O(n))
# ============================================================
# Idea: store values in a dict; track usage order in a separate list where
# the front is least-recently-used and the back is most-recently-used.
# Touching a key means finding and removing it from the middle of that list
# (O(n)) before re-appending it at the back.
# Time:  O(n) per get/put — list.remove and list.pop(0) both scan/shift
# Space: O(capacity)
class LRUCacheNaive:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._values = {}
        self._order = []  # front = least recently used, back = most recently used

    def get(self, key: int) -> int:
        if key not in self._values:
            return -1
        self._order.remove(key)  # O(n) scan
        self._order.append(key)
        return self._values[key]

    def put(self, key: int, value: int) -> None:
        if key in self._values:
            self._order.remove(key)  # O(n) scan
        elif len(self._values) >= self._capacity:
            lru_key = self._order.pop(0)  # O(n) shift
            del self._values[lru_key]
        self._values[key] = value
        self._order.append(key)


# ============================================================
# Approach 3: Optimal (hashmap + hand-rolled doubly linked list)
# ============================================================
# Idea: a hashmap gives O(1) access to any key's node; a doubly linked list
# gives O(1) removal/reinsertion of that node once found, because each node
# knows its own neighbors -- no scanning needed. Two sentinels (`head` =
# LRU end, `tail` = MRU end) mean every insert/remove is the same code path
# regardless of whether the list is empty or the node is at an edge.
# Time:  O(1) for every get/put   Space: O(capacity)
class _DLLNode:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev: "Optional[_DLLNode]" = None
        self.next: "Optional[_DLLNode]" = None


class LRUCacheOptimal:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._map = {}
        # Sentinels: head.next .. tail.prev holds real nodes, LRU -> MRU.
        self._head = _DLLNode()
        self._tail = _DLLNode()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _DLLNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_tail(self, node: _DLLNode) -> None:
        """Insert right before the tail sentinel -- i.e. the MRU position."""
        prev = self._tail.prev
        prev.next = node
        node.prev = prev
        node.next = self._tail
        self._tail.prev = node

    def get(self, key: int) -> int:
        if key not in self._map:
            return -1
        node = self._map[key]
        self._remove(node)
        self._insert_at_tail(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self._map:
            node = self._map[key]
            node.value = value
            self._remove(node)
            self._insert_at_tail(node)
            return

        if len(self._map) >= self._capacity:
            lru = self._head.next  # node right after the head sentinel
            self._remove(lru)
            del self._map[lru.key]

        node = _DLLNode(key, value)
        self._map[key] = node
        self._insert_at_tail(node)


# ============================================================
# Approach 4: Best / Alternate Optimal (collections.OrderedDict)
# ============================================================
# Idea: OrderedDict is internally backed by a doubly linked list too, so it
# exposes the same O(1) operations as Approach 3 through built-in methods
# instead of hand-rolled pointers: `move_to_end(key)` promotes a key to
# most-recently-used, and `popitem(last=False)` evicts the least-recently-
# used (first) item. Same complexity as Approach 3, but leans on the
# standard library instead of a custom node graph.
# Time:  O(1) amortized for every get/put   Space: O(capacity)
class LRUCacheOrderedDict:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._data: "OrderedDict[int, int]" = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self._data:
            return -1
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: int, value: int) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        elif len(self._data) >= self._capacity:
            self._data.popitem(last=False)
        self._data[key] = value


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a design problem needs O(1) "touch this and mark it most
#   recent" alongside O(1) "evict the least recent," a doubly linked list is
#   the enabling structure -- it's the only way to remove/reinsert an
#   arbitrary element in O(1) without scanning, because each node already
#   knows its own neighbors.
# - Common mistake: using a plain array/list (or singly linked list) for the
#   recency order -- removing an arbitrary element from either requires an
#   O(n) scan or shift, silently breaking the required O(1) bound.
# - Related/variant problems to try next: LFU Cache (harder: tie-break by
#   frequency, not just recency), Design a Data Structure with GetMax
#   (another "hashmap + O(1) ordering structure" design), All O`one Data
#   Structure.


if __name__ == "__main__":
    # Design problems don't fit the plain args-in/expected-out table, so we
    # replay the same sequence of operations against each implementation and
    # assert every observable result matches across all variants.
    def run(cls, capacity, operations):
        cache = cls(capacity)
        results = []
        for op, args in operations:
            if op == "get":
                results.append(cache.get(*args))
            else:  # "put"
                results.append(cache.put(*args))
        return results

    implementations = [LRUCacheNaive, LRUCacheOptimal, LRUCacheOrderedDict]

    # Scenario 1: the canonical LeetCode example.
    capacity1 = 2
    operations1 = [
        ("put", (1, 1)), ("put", (2, 2)), ("get", (1,)),
        ("put", (3, 3)), ("get", (2,)), ("put", (4, 4)),
        ("get", (1,)), ("get", (3,)), ("get", (4,)),
    ]
    expected1 = [None, None, 1, None, -1, None, -1, 3, 4]

    for cls in implementations:
        results = run(cls, capacity1, operations1)
        status = "OK" if results == expected1 else "FAIL"
        print(f"{cls.__name__:20s} scenario1 results={results!r:45s} -> expected={expected1!r}  [{status}]")

    # Scenario 2: longer sequence with repeated updates and re-evictions,
    # to stress-test recency ordering across many touches.
    capacity2 = 3
    operations2 = [
        ("put", (1, 10)), ("put", (2, 20)), ("put", (3, 30)),
        ("get", (1,)),                       # 1 becomes MRU; LRU order: 2,3,1
        ("put", (4, 40)),                    # evicts 2 (LRU); order: 3,1,4
        ("get", (2,)),                       # -1, evicted
        ("put", (3, 33)),                    # update 3's value, 3 -> MRU; order: 1,4,3
        ("get", (4,)),                       # 4 -> MRU; order: 1,3,4
        ("put", (5, 50)),                    # evicts 1 (LRU); order: 3,4,5
        ("get", (1,)),                       # -1, evicted
        ("get", (3,)),                       # 33
        ("get", (4,)),                       # 40
        ("get", (5,)),                       # 50
    ]
    expected2 = [
        None, None, None,
        10,
        None,
        -1,
        None,
        40,
        None,
        -1,
        33,
        40,
        50,
    ]

    for cls in implementations:
        results = run(cls, capacity2, operations2)
        status = "OK" if results == expected2 else "FAIL"
        print(f"{cls.__name__:20s} scenario2 results={results!r:55s} -> expected={expected2!r}  [{status}]")
