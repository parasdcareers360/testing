"""
LeetCode Top Interview 150 — #61 (LeetCode #92)
Reverse Linked List II
Category: Linked List | Difficulty: Medium

Problem
-------
Given the head of a singly linked list and two integers `left` and `right` where
`1 <= left <= right <= n` (n = number of nodes), reverse the nodes of the list from position
`left` to position `right` (1-indexed, inclusive), and return the head of the modified list.

Constraints
-----------
- The number of nodes in the list is n.
- 1 <= n <= 500
- -500 <= Node.val <= 500
- 1 <= left <= right <= n

Examples
--------
Example 1:
    Input: head = [1,2,3,4,5], left = 2, right = 4
    Output: [1,4,3,2,5]

Example 2:
    Input: head = [5], left = 1, right = 1
    Output: [5]

Intuition
---------
The naive approach doesn't need to think about pointers at all: pull every value into an array,
reverse just the `[left-1, right)` slice of that array, and write the values back into the
existing nodes in order. It's correct and O(n), but it's "cheating" the spirit of a linked-list
problem (it never touches `next` pointers) and needs O(n) extra space for the array. The real
technique reverses the sublist via pointer surgery, in place, in a single pass: walk to the node
just before position `left` (call it `prev`), then repeatedly take the node right after `prev`
and re-insert it at the front of the growing reversed segment — each iteration does exactly one
"head insertion," and after `right - left` iterations the whole sublist is reversed with `prev`
and its original successor correctly bookending it. A dummy head node avoids a special case when
`left == 1` (i.e., the reversal starts at the very head of the list).
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
# Approach 1: Brute Force (extract values, reverse slice, write back)
# ============================================================
# Idea: read every node's value into an array, reverse the `[left-1, right)`
# slice in the array, then walk the list again writing the (possibly
# reordered) values back into the existing nodes. Never touches `next`.
# Time:  O(n)   Space: O(n) — the values array
def solve_brute_force(head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
    values = []
    node = head
    while node is not None:
        values.append(node.val)
        node = node.next

    values[left - 1:right] = reversed(values[left - 1:right])

    node = head
    for v in values:
        node.val = v
        node = node.next

    return head


# ============================================================
# Approach 3: Optimal (in-place reversal via repeated head insertion)
# ============================================================
# Idea: use a dummy node so `left == 1` needs no special case. Walk `prev` to
# the node just before position `left`. Then `curr` always stays pointed at
# the *first* node of the not-yet-reversed remainder; each iteration detaches
# the node right after `curr` and re-inserts it immediately after `prev`,
# which is exactly "push this node to the front of the reversed segment."
# Dry run: head=[1,2,3,4,5], left=2, right=4
#   prev -> 1, curr -> 2 (curr never moves during the reversal)
#   iter1: temp=3; curr.next=4; 3.next=prev.next(=2); prev.next=3
#          list so far: 1 -> 3 -> 2 -> 4 -> 5
#   iter2: temp=4; curr.next=4.next=5; 4.next=prev.next(=3); prev.next=4
#          list so far: 1 -> 4 -> 3 -> 2 -> 5
#   right-left=2 iterations done -> result [1,4,3,2,5]
# Time:  O(n) — single pass to reach `left`, then O(right-left) swaps
# Space: O(1) — pointer rewiring only
def solve_optimal(head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next

    curr = prev.next
    for _ in range(right - left):
        temp = curr.next
        curr.next = temp.next
        temp.next = prev.next
        prev.next = temp

    return dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - "Repeated head insertion" is the standard trick for reversing an
#   arbitrary sublist in place: `curr` stays fixed as the eventual tail of
#   the reversed segment, while each following node gets detached and
#   reinserted right after `prev`, one at a time.
# - Common mistake: forgetting the dummy head, which forces an awkward
#   special case whenever `left == 1` (there's no real "node before left").
# - Related/variant problems to try next: Reverse Linked List (the full-list
#   special case), Reverse Nodes in k-Group (repeat this reversal for every
#   block of k), Swap Nodes in Pairs.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5], 2, 4), [1, 4, 3, 2, 5]),
        (([5], 1, 1), [5]),
        (([1, 2], 1, 2), [2, 1]),
        (([1, 2, 3, 4, 5], 1, 5), [5, 4, 3, 2, 1]),
        (([3, 5], 1, 2), [5, 3]),
        (([1, 2, 3], 3, 3), [1, 2, 3]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            values, left, right = args
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head, left, right))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, left, right)!r:30s} -> {result!r}  [{status}]")
