"""
LeetCode Top Interview 150 — #57 (LeetCode #141)
Linked List Cycle
Category: Linked List | Difficulty: Easy

Problem
-------
Given `head`, the head of a singly linked list, determine if the linked list has a cycle in it.

There is a cycle in a linked list if some node in the list can be reached again by continuously
following the `next` pointer. Internally, a cycle is represented by an integer `pos`, which
denotes the index (0-indexed) of the node that the tail's `next` pointer connects back to. `pos`
is not passed to your function — it exists only to construct the test case.

Return `True` if there is a cycle in the linked list, otherwise return `False`.

Constraints
-----------
- The number of nodes in the list is in the range [0, 10^4].
- -10^5 <= Node.val <= 10^5
- pos is -1 or a valid index in the linked list.

Examples
--------
Example 1:
    Input: head = [3,2,0,-4], pos = 1
    Output: true
    Explanation: the tail (-4) connects back to the node at index 1 (value 2), forming a cycle.

Example 2:
    Input: head = [1,2], pos = 0
    Output: true

Example 3:
    Input: head = [1], pos = -1
    Output: false
    Explanation: there is no cycle; the list terminates normally.

Intuition
---------
The most direct approach is to remember every node you've already visited (by identity, not
value — values can repeat) in a hash set, and check membership before advancing; the moment you
revisit a node, you've found a cycle, and if you fall off the end (`next is None`) there wasn't
one. That works in O(n) time but pays O(n) extra space for the set. The classic trick to drop
space to O(1) is Floyd's cycle detection ("tortoise and hare"): walk one pointer one step at a
time and another two steps at a time. If there's no cycle, the fast pointer simply reaches the
end first. If there is a cycle, the fast pointer eventually laps the slow pointer from behind and
the two become equal — they are guaranteed to meet because each step the fast pointer closes the
gap between them by exactly one node once both are inside the cycle.
"""

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_linked_list(values, pos: int = -1) -> Optional[ListNode]:
    """Build a singly linked list from `values`. If pos >= 0, the tail's `next`
    is wired back to the node at index `pos`, creating a cycle for testing.
    (Does NOT return a converter back to a Python list — a cyclic list can't be
    walked to completion, so no linked_list_to_list helper is needed here.)"""
    if not values:
        return None
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos >= 0:
        nodes[-1].next = nodes[pos]
    return nodes[0]


# ============================================================
# Approach 1: Brute Force (hash set of visited nodes)
# ============================================================
# Idea: walk the list, remembering every node object seen so far. If we ever
# land on a node already in the set, we've looped back -> cycle. Reaching
# None means the list terminated normally -> no cycle.
# Time:  O(n)   Space: O(n) — the visited set can hold every node
def solve_brute_force(head: Optional[ListNode]) -> bool:
    visited = set()
    node = head
    while node is not None:
        if id(node) in visited:
            return True
        visited.add(id(node))
        node = node.next
    return False


# ============================================================
# Approach 2: Optimal (Floyd's tortoise and hare)
# ============================================================
# Idea: two pointers, slow moves 1 step, fast moves 2 steps. No cycle -> fast
# (or fast.next) hits None first. Cycle -> fast re-enters the loop behind
# slow and gains on it by 1 node per step, so they must eventually collide.
# Dry run: 3 -> 2 -> 0 -> -4 -> (back to 2)
#   start: slow=3, fast=3
#   step1: slow=2, fast=0
#   step2: slow=0, fast=2   (fast wrapped through -4 back to 2)
#   step3: slow=-4, fast=-4 -> slow == fast -> cycle detected, return True
# Time:  O(n)   Space: O(1) — only two pointers, no extra storage
def solve_optimal(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


# ============================================================
# Key Takeaways
# ============================================================
# - Floyd's tortoise-and-hare is the go-to O(1)-space pattern whenever you
#   need to detect a cycle (or find its start, or find a duplicate via the
#   "linked list" trick as in Find the Duplicate Number).
# - Common mistake: comparing node *values* instead of node *identity* — two
#   different nodes can legitimately hold the same value, so `slow is fast`
#   (or `id(node) in visited`), never `slow.val == fast.val`.
# - Related/variant problems to try next: Linked List Cycle II (find the
#   entry point), Happy Number (cycle detection on a value sequence),
#   Find the Duplicate Number.


if __name__ == "__main__":
    tests = [
        ((build_linked_list([3, 2, 0, -4], pos=1),), True),
        ((build_linked_list([1, 2], pos=0),), True),
        ((build_linked_list([1], pos=-1),), False),
        ((build_linked_list([], pos=-1),), False),
        ((build_linked_list([1, 2, 3, 4, 5], pos=-1),), False),
        ((build_linked_list([1, 2, 3, 4, 5], pos=4),), True),  # self-loop at tail
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} expected={expected!r:8s} -> {result!r}  [{status}]")
