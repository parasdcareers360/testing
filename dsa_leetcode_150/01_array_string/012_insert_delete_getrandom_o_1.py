"""
LeetCode Top Interview 150 — #12 (LeetCode #380)
Insert Delete GetRandom O(1)
Category: Array / String | Difficulty: Medium

Problem
-------
Implement the `RandomizedSet` class, a data structure that supports the following operations, all
in average O(1) time:

- `RandomizedSet()` initializes an empty set.
- `bool insert(int val)` inserts `val` into the set if not already present. Returns `True` if
  `val` was inserted, `False` if it was already present.
- `bool remove(int val)` removes `val` from the set if present. Returns `True` if `val` was
  removed, `False` if it wasn't present.
- `int getRandom()` returns a random element from the current set of elements, with each element
  having an equal probability of being returned. It is guaranteed that at least one element exists
  whenever `getRandom` is called.

Constraints
-----------
- -2^31 <= val <= 2^31 - 1
- At most 2 * 10^5 calls total will be made to insert, remove, and getRandom.
- There will be at least one element in the data structure when getRandom is called.

Examples
--------
Example 1:
    Input:
        ["RandomizedSet","insert","remove","insert","getRandom","remove","insert","getRandom"]
        [[],[1],[2],[2],[],[1],[2],[]]
    Output:
        [null,true,false,true,2,true,false,2]
    Explanation:
        RandomizedSet rs = new RandomizedSet();
        rs.insert(1);     // [1] -> true (1 wasn't present)
        rs.remove(2);     // -> false (2 wasn't present)
        rs.insert(2);     // [1,2] -> true
        rs.getRandom();   // returns 1 or 2, each with probability 1/2
        rs.remove(1);     // [2] -> true
        rs.insert(2);     // -> false (2 already present)
        rs.getRandom();   // returns 2 (only element left)

Intuition
---------
A plain Python list naively satisfies "insert" (append) and "getRandom" (random.choice) in O(1),
but checking "is val already present" before inserting, and finding val's position before
removing it, both require a linear scan -- O(n) per call. The insight that fixes both operations
at once: keep a hashmap from value -> its current index in a backing array, alongside the array
itself. Membership checks and index lookups become O(1) hashmap lookups. The one remaining wrinkle
is removal from the middle of an array, which is normally O(n) because everything after the
removed slot must shift -- we avoid that entirely by swapping the element-to-remove with the
*last* element in the array before popping, so the only slot that changes position is the last
one (whose new index we simply update in the hashmap). getRandom stays a trivial O(1)
random-index lookup into the backing array throughout.
"""

import random
from typing import Dict, List


# ============================================================
# Approach 1: Brute Force (list with linear search)
# ============================================================
# Idea: store elements in a plain list. insert() must scan the list to
# check "already present" before appending; remove() must scan to find
# the value's index before deleting it (list.remove/index are both O(n)).
# getRandom() is O(1) via random.choice on the backing list.
# Time:  insert O(n), remove O(n), getRandom O(1)
# Space: O(n)
class RandomizedSetBruteForce:
    def __init__(self):
        self._data: List[int] = []

    def insert(self, val: int) -> bool:
        if val in self._data:  # O(n) linear scan
            return False
        self._data.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self._data:  # O(n) linear scan
            return False
        self._data.remove(val)  # O(n) shift after removal
        return True

    def getRandom(self) -> int:  # noqa: N802 (LeetCode's required method name)
        return random.choice(self._data)


# ============================================================
# Approach 2: Optimal (hashmap of value -> index, + swap-to-end removal)
# ============================================================
# Idea: maintain a backing array `_data` for O(1) random access, plus a
# hashmap `_index` mapping value -> its current position in `_data`. To
# remove a value in O(1) without shifting the array, swap it with the last
# element (updating the swapped element's index in the hashmap), then pop
# the now-last (target) element off the end.
# Time:  insert O(1) avg, remove O(1) avg, getRandom O(1)
# Space: O(n)
class RandomizedSetOptimal:
    def __init__(self):
        self._data: List[int] = []
        self._index: Dict[int, int] = {}

    def insert(self, val: int) -> bool:
        if val in self._index:
            return False
        self._index[val] = len(self._data)
        self._data.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self._index:
            return False
        idx = self._index[val]
        last_val = self._data[-1]
        # Move the last element into the slot being vacated...
        self._data[idx] = last_val
        self._index[last_val] = idx
        # ...then drop the true last slot (which now holds a duplicate of
        # last_val, or is the removed value itself if val was already last).
        self._data.pop()
        del self._index[val]
        return True

    def getRandom(self) -> int:  # noqa: N802
        return random.choice(self._data)


# ============================================================
# Key Takeaways
# ============================================================
# - "O(1) insert/remove/random-access all at once" is a signature that a
#   single data structure won't do it alone -- pairing a hashmap (for O(1)
#   lookup) with an array (for O(1) random indexing) is the standard combo.
# - Common mistake: removing an element by shifting the array (or using
#   list.remove/pop(idx) on a middle index), which silently reintroduces
#   O(n) removal -- swap-with-last-then-pop is what keeps it O(1).
# - Related/variant problems to try next: Insert Delete GetRandom O(1) -
#   Duplicates Allowed, LRU Cache (hashmap + list/linked-list combo, same
#   spirit), Design a HashSet.


if __name__ == "__main__":
    # Design problems don't fit the plain args-in/expected-out table. We
    # replay a scripted sequence of insert/remove calls (whose results are
    # deterministic) against each implementation, and separately verify
    # getRandom() only ever returns a value currently present in the set
    # (since which exact value it returns is random by design).
    operations = [
        ("insert", 1), ("remove", 2), ("insert", 2),
        ("remove", 1), ("insert", 2),
    ]
    expected_results = [True, False, True, True, False]

    implementations = [RandomizedSetBruteForce, RandomizedSetOptimal]
    for cls in implementations:
        obj = cls()
        results = []
        for op, val in operations:
            if op == "insert":
                results.append(obj.insert(val))
            elif op == "remove":
                results.append(obj.remove(val))
        status = "OK" if results == expected_results else "FAIL"
        print(f"{cls.__name__:24s} results={results!r:35s} -> expected={expected_results!r}  [{status}]")

    # getRandom sanity check: after a scripted sequence of inserts/removes,
    # every value getRandom() returns must currently be a member of the
    # set, and repeated calls must (eventually) surface every member.
    for cls in implementations:
        obj = cls()
        for val in [10, 20, 30, 40]:
            obj.insert(val)
        obj.remove(20)
        current = {10, 30, 40}
        seen = set()
        all_valid = True
        for _ in range(200):
            r = obj.getRandom()
            seen.add(r)
            if r not in current:
                all_valid = False
        status = "OK" if all_valid and seen == current else "FAIL"
        print(f"{cls.__name__:24s} getRandom seen={sorted(seen)!r:20s} expected_members={sorted(current)!r}  [{status}]")

    # Duplicate insert / missing remove must both correctly return False.
    for cls in implementations:
        obj = cls()
        r1 = obj.insert(5)
        r2 = obj.insert(5)
        r3 = obj.remove(99)
        results = [r1, r2, r3]
        expected = [True, False, False]
        status = "OK" if results == expected else "FAIL"
        print(f"{cls.__name__:24s} dup/missing results={results!r:20s} -> expected={expected!r}  [{status}]")
