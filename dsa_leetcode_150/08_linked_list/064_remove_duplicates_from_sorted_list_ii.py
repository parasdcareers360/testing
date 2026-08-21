"""
LeetCode Top Interview 150 — #64 (LeetCode #82)
Remove Duplicates from Sorted List II
Category: Linked List | Difficulty: Medium

Problem
-------
Given the head of a sorted linked list, delete all nodes that have duplicate numbers, leaving only
distinct numbers from the original list. Return the linked list, still sorted.

Constraints
-----------
- The number of nodes in the list is in the range [0, 300].
- -100 <= Node.val <= 100
- The list is guaranteed to be sorted in ascending order.

Examples
--------
Example 1:
    Input: head = [1,2,3,3,4,4,5]
    Output: [1,2,5]

Example 2:
    Input: head = [1,1,1,2,3]
    Output: [2,3]

Intuition
---------
This is different from "remove duplicates, keep one copy" -- here, any value that appears more
than once must be wiped out *entirely*, including its first occurrence. The naive approach counts
how many times each value occurs (a hashmap pass), then rebuilds the list keeping only values with
count exactly 1 -- correct, and simple, but pays O(n) extra space for the counts and discards the
original nodes. Because the list is already sorted, duplicates of any value are always consecutive,
which means we don't actually need counts at all: walk the list with a `prev` pointer trailing a
`curr` scanner; whenever `curr` and `curr.next` share a value, that's the start of a duplicate run
-- skip forward past every node with that value and splice `prev.next` straight to whatever comes
after the run, never advancing `prev` into a run that got deleted. If there's no duplicate at
`curr`, it's safe to keep and `prev` advances normally.
"""

from typing import Optional
from collections import Counter


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
# Approach 1: Brute Force (count occurrences, rebuild from scratch)
# ============================================================
# Idea: count every value's frequency with a hashmap, then walk the list a
# second time collecting only values whose count is exactly 1 (order is
# preserved automatically since the input is already sorted), and build a
# brand-new list from that filtered sequence.
# Time:  O(n)   Space: O(n) — the counts map + filtered values + new nodes
def solve_brute_force(head: Optional[ListNode]) -> Optional[ListNode]:
    counts = Counter()
    node = head
    while node is not None:
        counts[node.val] += 1
        node = node.next

    values = []
    node = head
    while node is not None:
        if counts[node.val] == 1:
            values.append(node.val)
        node = node.next

    return build_linked_list(values)


# ============================================================
# Approach 3: Optimal (single pass, in-place skip-the-run)
# ============================================================
# Idea: since the list is sorted, all copies of a duplicated value are
# consecutive. A dummy head lets `prev` always trail one real "kept" node
# behind `curr`. When `curr.val == curr.next.val`, advance `curr` through
# the *entire* run of that value, then splice `prev.next` directly to
# whatever follows the run -- `prev` itself never moves into deleted nodes.
# Otherwise `curr` is a unique value: keep it by advancing `prev` too.
# Dry run: head=[1,1,1,2,3]
#   curr=1, curr.next=1 -> run of 1's: skip curr to the node valued 2
#           prev(dummy).next = curr(=2)  -> deleted all three 1's
#   curr=2, curr.next=3 -> no duplicate -> prev=2, curr=3
#   curr=3, curr.next=None -> no duplicate -> prev=3, curr=None -> done
#   result: [2,3]
# Time:  O(n) — each node visited once   Space: O(1)
def solve_optimal(head: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    prev = dummy
    curr = head

    while curr is not None:
        if curr.next is not None and curr.val == curr.next.val:
            dup_val = curr.val
            while curr is not None and curr.val == dup_val:
                curr = curr.next
            prev.next = curr
        else:
            prev = curr
            curr = curr.next

    return dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - Sortedness turns "find all duplicates" into "find consecutive runs" --
#   no hashmap/counting needed, just a trailing pointer that only advances
#   past nodes you've decided to keep.
# - Common mistake: advancing `prev` into a node that's part of a duplicate
#   run before you know the whole run should be deleted -- `prev` must only
#   ever point at a node confirmed unique.
# - Related/variant problems to try next: Remove Duplicates from Sorted List
#   (keep one copy instead of deleting all), Remove Duplicates from Sorted
#   Array II (the array analogue).


if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 3, 4, 4, 5], [1, 2, 5]),
        ([1, 1, 1, 2, 3], [2, 3]),
        ([], []),
        ([1], [1]),
        ([1, 1], []),
        ([1, 1, 2, 2], []),
        ([1, 2, 2, 3, 3, 3, 4], [1, 4]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for values, expected in tests:
        for fn in approaches:
            head = build_linked_list(values)
            result = linked_list_to_list(fn(head))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} values={values!r:30s} -> {result!r}  [{status}]")
