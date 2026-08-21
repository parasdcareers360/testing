"""
LeetCode Top Interview 150 — #63 (LeetCode #19)
Remove Nth Node From End of List
Category: Linked List | Difficulty: Medium

Problem
-------
Given the head of a linked list, remove the `n`th node from the end of the list, and return its
head.

Constraints
-----------
- The number of nodes in the list is sz.
- 1 <= sz <= 30
- 0 <= Node.val <= 100
- 1 <= n <= sz

Examples
--------
Example 1:
    Input: head = [1,2,3,4,5], n = 2
    Output: [1,2,3,5]

Example 2:
    Input: head = [1], n = 1
    Output: []

Example 3:
    Input: head = [1,2], n = 1
    Output: [1]

Intuition
---------
"The nth node from the end" is awkward on a singly linked list because we can't walk backward and
we don't know the length up front. The truly naive fix (Approach 1) collects every node reference
into an array as we pass through once — now "the node before the target" is just an index
computation, and we relink directly through the array without a second traversal, at the cost of
O(n) extra space for the references. A leaner fix (Approach 2) avoids that array: do one pass just
to *count* the list's length, then do a second pass, walking exactly `length - n` steps from a
dummy head to land on the node right before the target. That's O(1) space but two full passes. The
one-pass trick (Approach 3, the intended optimal) collapses those two passes into one: advance a
`fast` pointer `n` steps ahead first, then move `fast` and `slow` together until `fast` falls off
the end — by construction `slow` is now sitting exactly `n` nodes behind `fast`, i.e. right before
the target, using a single walk down the list.
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
# Approach 1: Brute Force (collect node references into an array)
# ============================================================
# Idea: walk the list once, appending every node (including a leading dummy)
# to an array. "The node before the target" is then a direct index lookup:
# target sits at index `len(nodes) - n` (1-indexed from the dummy), so its
# predecessor is one slot before that.
# Time:  O(n)   Space: O(n) — the array of node references
def solve_brute_force(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    nodes = [dummy]
    node = head
    while node is not None:
        nodes.append(node)
        node = node.next

    target_index = len(nodes) - n
    prev = nodes[target_index - 1]
    prev.next = prev.next.next
    return dummy.next


# ============================================================
# Approach 2: Better (two-pass: count length, then walk to target)
# ============================================================
# Idea: same relinking logic as Approach 1, but without paying for an array
# -- first pass just counts the length, second pass walks `length - n`
# steps from a dummy head to reach the predecessor directly.
# Time:  O(n) — two full passes   Space: O(1)
def solve_better(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    length = 0
    node = head
    while node is not None:
        length += 1
        node = node.next

    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(length - n):
        prev = prev.next
    prev.next = prev.next.next
    return dummy.next


# ============================================================
# Approach 3: Optimal (one-pass two-pointer gap)
# ============================================================
# Idea: advance `fast` n steps ahead of `slow` first (both starting at a
# dummy head). Then advance both together until `fast` runs off the list --
# the fixed n-node gap means `slow` is now exactly at the predecessor of the
# node that is n from the end, discovered in a single walk.
# Dry run: head=[1,2,3,4,5], n=2
#   fast advances 2: dummy -> 1 -> 2
#   step together until fast.next is None:
#     slow=dummy,fast=2 -> slow=1,fast=3 -> slow=2,fast=4 -> slow=3,fast=5(fast.next=None,stop)
#   slow(=3).next = slow.next.next  -> unlinks 4 -> [1,2,3,5]
# Time:  O(n) — single pass   Space: O(1)
def solve_optimal(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    fast = slow = dummy

    for _ in range(n):
        fast = fast.next

    while fast.next is not None:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - A fixed-size gap between two pointers is the general trick for "find the
#   node n away from an endpoint" on a singly linked list without knowing
#   the length up front and without a second pass.
# - Common mistake: forgetting the dummy head, which is what makes removing
#   the actual head node (when n == length) work without a special case.
# - Related/variant problems to try next: Middle of the Linked List (same
#   fast/slow pointer family), Linked List Cycle, Rotate List (also needs
#   the list's length).


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5], 2), [1, 2, 3, 5]),
        (([1], 1), []),
        (([1, 2], 1), [1]),
        (([1, 2], 2), [2]),
        (([1, 2, 3, 4, 5], 5), [2, 3, 4, 5]),
        (([1, 2, 3, 4, 5], 1), [1, 2, 3, 4]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            values, n = args
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head, n))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, n)!r:30s} -> {result!r}  [{status}]")
