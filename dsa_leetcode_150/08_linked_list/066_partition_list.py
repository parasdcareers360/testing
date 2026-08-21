"""
LeetCode Top Interview 150 — #66 (LeetCode #86)
Partition List
Category: Linked List | Difficulty: Medium

Problem
-------
Given the head of a linked list and a value `x`, partition it such that all nodes with a value
less than `x` come before all nodes with a value greater than or equal to `x`.

You should preserve the original relative order of the nodes within each of the two partitions.

Constraints
-----------
- The number of nodes in the list is in the range [0, 200].
- -100 <= Node.val <= 100
- -200 <= x <= 200

Examples
--------
Example 1:
    Input: head = [1,4,3,2,5,2], x = 3
    Output: [1,2,2,4,3,5]

Example 2:
    Input: head = [2,1], x = 2
    Output: [1,2]

Intuition
---------
The naive approach reads the values out into an array, filters it into two lists (`< x` and
`>= x`) using stable list comprehensions -- which trivially preserves relative order -- and builds
a brand-new linked list from the concatenation. It's correct and linear, but it discards every
original node and pays O(n) extra space for the arrays and the rebuilt list. Since we're allowed
to reorder nodes (not values), the optimal approach reuses the *existing* nodes directly: walk the
list once, and as each node is visited, splice it onto the tail of one of two growing chains --
one for "less than x", one for "greater-or-equal" -- built with their own dummy heads to avoid
special-casing empty partitions. A single pass later, join the `< x` chain's tail to the `>= x`
chain's head. The one sharp edge: the last node of the `>= x` chain still has its *original* `next`
pointer lingering, which must be explicitly set to `None` or the result silently contains a cycle
back into already-visited nodes.
"""

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_linked_list(values) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def linked_list_to_list(head: Optional[ListNode]) -> list:
    out = []
    while head is not None:
        out.append(head.val)
        head = head.next
    return out


# ============================================================
# Approach 1: Brute Force (extract values, stable-filter, rebuild)
# ============================================================
# Idea: read every value into an array, split it into "< x" and ">= x"
# sublists via list comprehensions (order-preserving by construction), then
# build a brand-new list from their concatenation.
# Time:  O(n)   Space: O(n) — the value arrays + all-new nodes
def solve_brute_force(head: Optional[ListNode], x: int) -> Optional[ListNode]:
    values = []
    node = head
    while node is not None:
        values.append(node.val)
        node = node.next

    less = [v for v in values if v < x]
    ge = [v for v in values if v >= x]
    return build_linked_list(less + ge)


# ============================================================
# Approach 3: Optimal (split into two chains, reusing existing nodes)
# ============================================================
# Idea: walk the list once, splicing each node onto the tail of one of two
# dummy-headed chains depending on whether its value is < x or >= x. Both
# chains preserve relative order automatically since we only ever append.
# Join `less` chain's tail to `ge` chain's head, and terminate the `ge`
# chain's tail explicitly (its `next` may still point at an already-visited
# node from the original list).
# Dry run: head=[1,4,3,2,5,2], x=3
#   1<3 -> less=[1];       4>=3 -> ge=[4];    3>=3 -> ge=[4,3]
#   2<3 -> less=[1,2];     5>=3 -> ge=[4,3,5]; 2<3 -> less=[1,2,2]
#   ge_tail.next=None; less_tail.next=ge_dummy.next(=4)
#   result: 1 -> 2 -> 2 -> 4 -> 3 -> 5
# Time:  O(n) — single pass   Space: O(1) extra (no new nodes)
def solve_optimal(head: Optional[ListNode], x: int) -> Optional[ListNode]:
    less_dummy = ListNode()
    ge_dummy = ListNode()
    less_tail, ge_tail = less_dummy, ge_dummy

    node = head
    while node is not None:
        if node.val < x:
            less_tail.next = node
            less_tail = less_tail.next
        else:
            ge_tail.next = node
            ge_tail = ge_tail.next
        node = node.next

    ge_tail.next = None  # cut the lingering original tail pointer
    less_tail.next = ge_dummy.next
    return less_dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - "Split into two dummy-headed chains, then join" is the standard pattern
#   for any linked-list partition/bucketing problem that must preserve
#   relative order within each bucket -- appending only ever preserves order.
# - Common mistake: forgetting to terminate the second chain's tail
#   (`ge_tail.next = None`) -- its last node's `next` still points at
#   whatever followed it in the *original* list, which can recreate a cycle
#   once the two chains are joined.
# - Related/variant problems to try next: Sort Colors (in-place 3-way
#   partition on an array), Odd Even Linked List, Remove Duplicates from
#   Sorted List II (also splices in place with dummy heads).


if __name__ == "__main__":
    tests = [
        (([1, 4, 3, 2, 5, 2], 3), [1, 2, 2, 4, 3, 5]),
        (([2, 1], 2), [1, 2]),
        (([], 0), []),
        (([1], 2), [1]),
        (([1, 2, 3], 0), [1, 2, 3]),
        (([3, 2, 1], 4), [3, 2, 1]),
        (([1, 1, 1], 1), [1, 1, 1]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            values, x = args
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head, x))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, x)!r:35s} -> {result!r}  [{status}]")
