"""
LeetCode Top Interview 150 — #62 (LeetCode #25)
Reverse Nodes in k-Group
Category: Linked List | Difficulty: Hard

Problem
-------
Given the head of a linked list, reverse the nodes of the list `k` at a time, and return the
modified list.

`k` is a positive integer and is less than or equal to the length of the linked list. If the
number of nodes is not a multiple of `k`, then the nodes left out at the end should remain in
their original order (not reversed).

You may not alter the values in the list's nodes — only the nodes themselves may be changed.

Constraints
-----------
- The number of nodes in the list is n.
- 1 <= k <= n <= 5000
- 0 <= Node.val <= 1000

Examples
--------
Example 1:
    Input: head = [1,2,3,4,5], k = 2
    Output: [2,1,4,3,5]

Example 2:
    Input: head = [1,2,3,4,5], k = 3
    Output: [3,2,1,4,5]

Intuition
---------
The naive approach sidesteps pointers entirely: dump every value into an array, reverse each
contiguous block of `k` values (leaving a short trailing remainder untouched), and write the
values back into the existing nodes — correct and O(n), but it needs O(n) extra space and never
manipulates `next` pointers, which misses the point of the exercise. The in-place technique
processes the list one group at a time: before reversing a group you must first check it actually
has `k` nodes (by walking ahead `k` steps) — if not, that tail is left untouched. Then reverse just
that group's internal links, and reconnect the previous group's tail to the new group head, saving
a pointer to the current group's (now-)tail to link to whatever comes next. The same "reverse a
group of k, then handle the rest" idea can be expressed recursively instead — reverse the first k
nodes, then let the recursive call handle everything after, and stitch the two together — trading
the loop's O(1) space for O(n/k) call-stack frames but reading arguably cleaner.
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
# Approach 1: Brute Force (extract values, reverse each block, write back)
# ============================================================
# Idea: collect all values into an array, reverse every full block of k
# values (a trailing partial block of fewer than k is left as-is), then walk
# the original nodes again writing the reordered values back in.
# Time:  O(n)   Space: O(n) — the values array
def solve_brute_force(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    values = []
    node = head
    while node is not None:
        values.append(node.val)
        node = node.next

    full_groups_end = (len(values) // k) * k
    for start in range(0, full_groups_end, k):
        values[start:start + k] = reversed(values[start:start + k])

    node = head
    for v in values:
        node.val = v
        node = node.next

    return head


# ============================================================
# Approach 3: Optimal (iterative in-place group reversal)
# ============================================================
# Idea: use a dummy head; `group_prev` always points to the node right
# before the group currently being processed. First walk `k` steps ahead to
# confirm a full group exists (if not, stop -- the remainder stays as-is).
# Reverse the group's internal links (standard 3-pointer reversal, bounded by
# `group_next`), then splice: `group_prev.next` becomes the group's old tail
# (now its head), and the group's old head (now its tail, saved as `tmp`)
# becomes the next `group_prev`.
# Dry run: head=[1,2,3,4,5], k=2
#   group1 [1,2]: kth=2 found -> reverse -> 2->1, group_prev(dummy).next=2, group_prev=1
#   group2 [3,4]: kth=4 found -> reverse -> 4->3, group_prev(1).next=4, group_prev=3
#   group3 [5]: walk 1 more step -> kth=None (only 1 node left) -> stop, leave [5] as-is
#   result: 2 -> 1 -> 4 -> 3 -> 5
# Time:  O(n) — every node visited O(1) times   Space: O(1) — pointer rewiring only
def solve_optimal(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next

        prev, curr = group_next, group_prev.next
        while curr is not group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt

        tmp = group_prev.next  # old head of the group, now its tail
        group_prev.next = kth  # kth was the old tail, now the group's head
        group_prev = tmp


# ============================================================
# Approach 4: Best / Alternate Optimal (recursive)
# ============================================================
# Idea: check whether at least k nodes remain by walking ahead; if fewer
# than k remain, return the list untouched (base case). Otherwise reverse
# just the first k nodes (standard iterative reversal), then recursively
# process everything after them, and attach that recursive result after the
# original head (which is now the tail of the reversed first group).
# Time:  O(n)   Space: O(n/k) call-stack frames (one per group)
def solve_best(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    node = head
    count = 0
    while node is not None and count < k:
        node = node.next
        count += 1
    if count < k:
        return head  # fewer than k nodes left -- leave this tail untouched

    prev, curr = None, head
    for _ in range(k):
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    # `head` is now the tail of this reversed group; attach the recursively
    # reversed remainder after it.
    head.next = solve_best(curr, k)
    return prev


# ============================================================
# Key Takeaways
# ============================================================
# - "Look ahead k steps before committing to reverse" is essential whenever
#   a problem processes a linked list in fixed-size chunks: you must confirm
#   a full chunk exists before mutating any of its pointers, or you'll
#   corrupt a trailing partial group.
# - Common mistake: losing track of `group_prev` (or the equivalent "what to
#   attach the next processed group to") — after reversing a group its old
#   head becomes its tail, and that's the node the *next* group must attach
#   after, not the group's new head.
# - Related/variant problems to try next: Reverse Linked List II (reverse a
#   single arbitrary sublist instead of every group), Swap Nodes in Pairs
#   (the k=2 special case), Rotate List.


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4, 5], 2), [2, 1, 4, 3, 5]),
        (([1, 2, 3, 4, 5], 3), [3, 2, 1, 4, 5]),
        (([1, 2, 3, 4, 5, 6], 2), [2, 1, 4, 3, 6, 5]),
        (([1], 1), [1]),
        (([1, 2, 3], 1), [1, 2, 3]),
        (([1, 2, 3, 4, 5, 6, 7, 8], 3), [3, 2, 1, 6, 5, 4, 7, 8]),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            values, k = args
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head, k))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={(values, k)!r:35s} -> {result!r}  [{status}]")
