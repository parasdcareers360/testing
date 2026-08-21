"""
LeetCode Top Interview 150 — #109 (LeetCode #148)
Sort List
Category: Divide & Conquer | Difficulty: Medium

Problem
-------
Given the head of a singly linked list, sort it in ascending order and return the sorted list's
head.

Follow-up: can you sort the linked list in O(n log n) time and O(1) extra space (i.e. without
using extra memory proportional to the list's length, ignoring recursion stack)?

Constraints
-----------
- The number of nodes in the list is in the range [0, 5 * 10^4].
- -10^5 <= Node.val <= 10^5

Examples
--------
Example 1:
    Input: head = [4,2,1,3]
    Output: [1,2,3,4]

Example 2:
    Input: head = [-1,5,3,4,0]
    Output: [-1,0,3,4,5]

Example 3:
    Input: head = []
    Output: []

Intuition
---------
The dead-simple approach is to dump every node's value into a Python list, sort that with
Timsort, and rebuild the linked list — correct and O(n log n) time, but it uses O(n) auxiliary
space and doesn't really engage with the linked-list structure at all. The follow-up asks for
O(1) extra space (beyond recursion), which rules out array-based sorting. The insight: merge sort
is a natural fit for linked lists because splitting doesn't require random access (just a
slow/fast pointer to find the middle) and merging two sorted lists is a simple pointer-rewiring
operation — no extra array needed, unlike arrays where merging in place is awkward. So: find the
middle with slow/fast pointers, split the list into two halves, recursively sort each half, then
merge the two sorted halves by relinking nodes.
"""

from typing import List, Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_linked_list(values: List[int]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def linked_list_to_list(head: Optional[ListNode]) -> List[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# ============================================================
# Approach 1: Brute Force (collect into array, sort, rebuild)
# ============================================================
# Idea: read every value into a Python list, sort it, then overwrite the
# node values in order. Simple, correct, ignores the O(1)-space follow-up.
# Time:  O(n log n) — dominated by the sort
# Space: O(n) — the auxiliary array of values
def solve_brute_force(head: Optional[ListNode]) -> Optional[ListNode]:
    values = []
    node = head
    while node:
        values.append(node.val)
        node = node.next
    values.sort()

    node = head
    for v in values:
        node.val = v
        node = node.next
    return head


# ============================================================
# Approach 2: Optimal (true merge sort on the linked list, O(1) extra space)
# ============================================================
# Idea: classic top-down merge sort adapted to a linked list.
#   1. Base case: 0 or 1 nodes is already sorted.
#   2. Find the middle using slow/fast pointers (slow moves 1 step, fast
#      moves 2 — when fast runs out, slow sits at the midpoint).
#   3. Split the list into two halves at the middle, sort each half
#      recursively.
#   4. Merge the two sorted halves by relinking existing nodes (no new
#      nodes allocated) — same technique as Merge Two Sorted Lists.
# The recursion depth is O(log n), which is the only "extra space" used
# beyond pointers — no auxiliary array of values or nodes.
# Dry run: head = [4,2,1,3]
#   split -> slow/fast finds mid: [4,2] | [1,3]
#   recurse [4,2] -> mid splits to [4] | [2] -> merge -> [2,4]
#   recurse [1,3] -> mid splits to [1] | [3] -> merge -> [1,3]
#   merge [2,4] and [1,3] -> compare 2 vs 1 -> 1, 2 vs 3 -> 2, 4 vs 3 -> 3, 4
#   result: [1,2,3,4]
# Time:  O(n log n) — log n levels of splitting, O(n) work merging per level
# Space: O(log n) — recursion call stack only, no auxiliary data structure
def solve_optimal(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None or head.next is None:
        return head

    # Split into two halves using slow/fast pointers.
    prev, slow, fast = None, head, head
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    prev.next = None  # cut the list: prev is the tail of the left half

    left = solve_optimal(head)
    right = solve_optimal(slow)
    return _merge_two_sorted(left, right)


def _merge_two_sorted(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    while a and b:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a else b
    return dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - Merge sort is the natural O(n log n) sort for linked lists: splitting
#   only needs a slow/fast pointer (no random access needed like quicksort
#   partitioning would benefit from), and merging is pure pointer rewiring
#   with zero extra node/array allocation.
# - Common mistake: forgetting to cut the list at the midpoint (`prev.next
#   = None`) before recursing — without it the "left half" recursion never
#   terminates because it still sees the whole list.
# - Related/variant problems to try next: Merge Two Sorted Lists, Merge k
#   Sorted Lists, Insertion Sort List.


if __name__ == "__main__":
    tests = [
        ([4, 2, 1, 3], [1, 2, 3, 4]),
        ([-1, 5, 3, 4, 0], [-1, 0, 3, 4, 5]),
        ([], []),
        ([1], [1]),
        ([2, 1], [1, 2]),
        ([5, 5, 5, 1], [1, 5, 5, 5]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for values, expected in tests:
        for fn in approaches:
            head = build_linked_list(values)
            result_head = fn(head)
            result = linked_list_to_list(result_head)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} values={values!r:25s} -> {result!r}  [{status}]")
