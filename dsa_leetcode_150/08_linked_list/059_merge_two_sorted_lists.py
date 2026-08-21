"""
LeetCode Top Interview 150 — #59 (LeetCode #21)
Merge Two Sorted Lists
Category: Linked List | Difficulty: Easy

Problem
-------
You are given the heads of two sorted (non-decreasing) linked lists, `list1` and `list2`. Merge
the two lists into one sorted list by splicing together the nodes of the two input lists, and
return the head of the merged list.

Constraints
-----------
- The number of nodes in both lists is in the range [0, 50].
- -100 <= Node.val <= 100
- Both `list1` and `list2` are sorted in non-decreasing order.

Examples
--------
Example 1:
    Input: list1 = [1,2,4], list2 = [1,3,4]
    Output: [1,1,2,3,4,4]

Example 2:
    Input: list1 = [], list2 = []
    Output: []

Example 3:
    Input: list1 = [], list2 = [0]
    Output: [0]

Intuition
---------
The naive route ignores that both lists are already sorted: dump every value into an array, sort
it, and rebuild a list from scratch — correct, but wastes the sortedness we were handed for free
and pays an extra O((n+m) log(n+m)). The real insight is this is exactly the "merge" half of
merge sort: walk both lists with one pointer each, always splicing the smaller current node onto
the result, and advancing only that list's pointer. Because we're reusing existing nodes (not
creating new ones), this needs no extra data beyond a dummy head to avoid special-casing the
first node. The same merge step can be written iteratively (a simple loop) or recursively (the
answer for two lists is "smaller head, followed by the merge of the rest") — both run in linear
time but trade off stack space for iteration.
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
# Approach 1: Brute Force (collect, sort, rebuild)
# ============================================================
# Idea: read every value out of both lists into one array, sort it, and
# build a brand-new list from the sorted values — ignores that the inputs
# were already sorted.
# Time:  O((n+m) log(n+m))   Space: O(n+m) for the array + new nodes
def solve_brute_force(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    values = []
    for node in (list1, list2):
        while node is not None:
            values.append(node.val)
            node = node.next
    values.sort()
    return build_linked_list(values)


# ============================================================
# Approach 3: Optimal (iterative two-pointer splice)
# ============================================================
# Idea: use a dummy head so the first real node needs no special case. At
# each step, splice the smaller of list1's/list2's current node onto the
# tail of the result and advance only that pointer. Once one list is
# exhausted, the other is already sorted and can be attached wholesale.
# Dry run: list1=[1,2,4], list2=[1,3,4]
#   1(l1) vs 1(l2) -> tie, take l1's 1 -> result=[1], l1=[2,4]
#   2(l1) vs 1(l2) -> take l2's 1     -> result=[1,1], l2=[3,4]
#   2(l1) vs 3(l2) -> take l1's 2     -> result=[1,1,2], l1=[4]
#   4(l1) vs 3(l2) -> take l2's 3     -> result=[1,1,2,3], l2=[4]
#   4(l1) vs 4(l2) -> tie, take l1's 4 -> result=[1,1,2,3,4], l1=[]
#   l1 exhausted -> attach remaining l2 ([4]) -> [1,1,2,3,4,4]
# Time:  O(n+m) — each node visited once   Space: O(1) — reuses existing nodes
def solve_optimal(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy

    while list1 is not None and list2 is not None:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next

    tail.next = list1 if list1 is not None else list2
    return dummy.next


# ============================================================
# Approach 4: Best / Alternate Optimal (recursive splice)
# ============================================================
# Idea: same merge logic expressed recursively — the merge of two lists is
# "whichever head is smaller, followed by the merge of its tail with the
# other list." Elegant and equally O(n+m) in time, but trades the loop's
# O(1) space for O(n+m) call-stack frames (one per merged node), and can
# hit Python's recursion limit on very long lists.
def solve_best(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    if list1 is None:
        return list2
    if list2 is None:
        return list1
    if list1.val <= list2.val:
        list1.next = solve_best(list1.next, list2)
        return list1
    else:
        list2.next = solve_best(list1, list2.next)
        return list2


# ============================================================
# Key Takeaways
# ============================================================
# - A dummy/sentinel head node is the standard trick to avoid special-casing
#   "is this the first node?" in any linked-list-building loop.
# - Common mistake: forgetting the final "attach whatever's left" step —
#   once one list is exhausted, the other's remaining nodes are already
#   sorted and can be spliced on directly without further comparison.
# - Related/variant problems to try next: Merge k Sorted Lists, Merge Sorted
#   Array (the array analogue), Sort List (merge sort on a linked list).


if __name__ == "__main__":
    tests = [
        ((build_linked_list([1, 2, 4]), build_linked_list([1, 3, 4])), [1, 1, 2, 3, 4, 4]),
        ((build_linked_list([]), build_linked_list([])), []),
        ((build_linked_list([]), build_linked_list([0])), [0]),
        ((build_linked_list([5]), build_linked_list([1, 2, 4])), [1, 2, 4, 5]),
        ((build_linked_list([-3, -1, 0]), build_linked_list([-2, -2, 4])), [-3, -2, -2, -1, 0, 4]),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            l1_vals, l2_vals = linked_list_to_list(args[0]), linked_list_to_list(args[1])
            l1, l2 = build_linked_list(l1_vals), build_linked_list(l2_vals)
            result = linked_list_to_list(fn(l1, l2))
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} l1={l1_vals!r:15s} l2={l2_vals!r:15s} -> {result!r}  [{status}]")
