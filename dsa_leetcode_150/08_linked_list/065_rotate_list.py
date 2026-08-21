"""
LeetCode Top Interview 150 — #65 (LeetCode #61)
Rotate List
Category: Linked List | Difficulty: Medium

Problem
-------
Given the head of a linked list, rotate the list to the right by `k` places.

Constraints
-----------
- The number of nodes in the list is in the range [0, 500].
- -100 <= Node.val <= 100
- 0 <= k <= 2 * 10^9

Examples
--------
Example 1:
    Input: head = [1,2,3,4,5], k = 2
    Output: [4,5,1,2,3]

Example 2:
    Input: head = [0,1,2], k = 4
    Output: [2,0,1]

Intuition
---------
`k` can be far larger than the list's length (up to 2*10^9 vs. at most 500 nodes), so the very
first insight -- needed even for a naive solution -- is that rotating right by `k` is identical to
rotating right by `k mod length`, since a full lap brings the list back to itself. The naive
approach (Approach 1) then just simulates the definition directly: `k mod length` times, chop off
the last node and re-attach it at the front -- correct, but each "move the last node" step is
itself O(n) to find the tail, giving O(n * (k mod n)) overall. The optimal approach recognizes that
a right-rotation by `k` only changes *where the list is cut*: if you connect the tail back to the
head (temporarily making the list circular) and then break the circle at the right spot -- exactly
`length - k mod length` nodes after the original head -- you get the rotated list directly, no
repeated single-node moves required, in a single pass.
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
# Approach 1: Brute Force (repeatedly move the last node to the front)
# ============================================================
# Idea: reduce k modulo the list length first (otherwise this would never
# finish for large k), then literally simulate the rotation: k times, find
# the last node (walking from the head each time), detach it, and re-attach
# it as the new head.
# Time:  O(n * (k mod n)) — an O(n) tail-find repeated (k mod n) times
# Space: O(1)
def solve_brute_force(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    if head is None or head.next is None:
        return head

    length = 0
    node = head
    while node is not None:
        length += 1
        node = node.next
    k %= length

    for _ in range(k):
        prev = head
        while prev.next.next is not None:
            prev = prev.next
        last = prev.next
        prev.next = None
        last.next = head
        head = last

    return head


# ============================================================
# Approach 3: Optimal (make it circular, then cut at the right spot)
# ============================================================
# Idea: find the length and the current tail in one pass, reduce k modulo
# the length, then link tail -> head to form a ring. The new tail is the
# node `length - k` steps from the original head; the node right after it
# is the new head. Breaking the ring there (new_tail.next = None) produces
# the rotated list directly.
# Dry run: head=[1,2,3,4,5], k=2, length=5, k%=5 -> 2
#   tail(5).next = head(1)   -- now circular: 1->2->3->4->5->1->...
#   steps_to_new_tail = 5-2-1 = 2 -> walk from head: 1 -> 2 -> 3 (new_tail=3)
#   new_head = new_tail.next = 4; new_tail.next = None
#   result: 4 -> 5 -> 1 -> 2 -> 3
# Time:  O(n) — one pass to measure + one pass to find the cut
# Space: O(1)
def solve_optimal(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    if head is None or head.next is None or k == 0:
        return head

    length = 1
    tail = head
    while tail.next is not None:
        tail = tail.next
        length += 1
    k %= length
    if k == 0:
        return head

    tail.next = head  # temporarily circular

    steps_to_new_tail = length - k - 1
    new_tail = head
    for _ in range(steps_to_new_tail):
        new_tail = new_tail.next

    new_head = new_tail.next
    new_tail.next = None
    return new_head


# ============================================================
# Key Takeaways
# ============================================================
# - Reducing k modulo the length is the first move for *any* rotation
#   problem -- it bounds the work and correctly handles k values far larger
#   than the structure itself.
# - Common mistake: forgetting to break the temporary circular link after
#   finding the new tail -- an un-terminated list will loop forever on any
#   later traversal.
# - Related/variant problems to try next: Rotate Array (the array analogue,
#   same mod-then-reposition idea), Reverse Nodes in k-Group, Linked List
#   Cycle (detecting rather than creating a cycle).


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3]),
        (([0, 1, 2], 4), [2, 0, 1]),
        (([], 0), []),
        (([1], 5), [1]),
        (([1, 2], 0), [1, 2]),
        (([1, 2, 3], 3), [1, 2, 3]),
        (([1, 2, 3, 4, 5], 5), [1, 2, 3, 4, 5]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            values, k = args
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head, k))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, k)!r:30s} -> {result!r}  [{status}]")
