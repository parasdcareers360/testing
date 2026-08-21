"""
LeetCode Top Interview 150 — #111 (LeetCode #23)
Merge k Sorted Lists
Category: Divide & Conquer | Difficulty: Hard

Problem
-------
You are given an array `lists` of `k` linked lists, each linked list is sorted in ascending order.

Merge all the linked lists into one sorted linked list and return it.

Constraints
-----------
- k == lists.length
- 0 <= k <= 10^4
- 0 <= lists[i].length <= 500
- -10^4 <= lists[i][j] <= 10^4
- lists[i] is sorted in ascending order
- The sum of lists[i].length will not exceed 10^4

Examples
--------
Example 1:
    Input: lists = [[1,4,5],[1,3,4],[2,6]]
    Output: [1,1,2,3,4,4,5,6]
    Explanation: The linked lists are [1,4,5], [1,3,4], [2,6]. Merging them into one sorted list
    gives 1->1->2->3->4->4->5->6.

Example 2:
    Input: lists = []
    Output: []

Example 3:
    Input: lists = [[]]
    Output: []

Intuition
---------
The simplest correct approach is to dump every node's value into one big list, sort it, and
rebuild a linked list — O(N log N) where N is the total number of nodes, ignoring the fact that
each individual list is already sorted. A smarter approach exploits that structure with a min-heap:
keep one "current" node from each of the k lists in a heap keyed by value, repeatedly pop the
smallest, append it to the result, and push that list's next node — this is the classic k-way
merge and runs in O(N log k) since each of the N nodes is pushed/popped once from a heap of size
at most k. The best approach gets the same O(N log k) bound without a heap at all: **pairwise
divide and conquer**. Merge the k lists two at a time (like the merge step of merge sort) in
rounds — round 1 produces k/2 lists, round 2 produces k/4, and so on, for log k rounds, each
touching all N nodes once. It's simpler to implement than a heap (just repeated 2-list merges) and
has the same complexity, with better cache behavior in practice since it merges pairs sequentially
rather than juggling k heap entries at once.
"""

from typing import List, Optional
import heapq


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
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
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


# ============================================================
# Approach 1: Brute Force (collect all values, sort, rebuild)
# ============================================================
# Idea: walk every list, collect all values into one array, sort it, then
# build a fresh linked list from the sorted array. Ignores that each input
# list is already sorted.
# Time:  O(N log N) where N = total number of nodes, dominated by the sort
# Space: O(N) for the collected values array
def solve_brute_force(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    values = []
    for node in lists:
        while node:
            values.append(node.val)
            node = node.next
    values.sort()
    return build_linked_list(values)


# ============================================================
# Approach 2: Better (min-heap k-way merge)
# ============================================================
# Idea: push the head of each non-empty list into a min-heap keyed by
# value. Repeatedly pop the smallest node, append it to the output, and if
# that node has a next, push it into the heap. The heap always holds at
# most k elements, so each of the N pops/pushes costs O(log k).
# Time:  O(N log k)
# Space: O(k) for the heap
def solve_better(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    heap = []
    # Tie-break with an index counter since ListNode isn't comparable and
    # values can repeat across lists.
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode()
    tail = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


# ============================================================
# Approach 3: Best (pairwise divide and conquer merge)
# ============================================================
# Idea: repeatedly merge the k lists in pairs (list[0] with list[1],
# list[2] with list[3], ...) using the standard 2-list merge, producing
# roughly half as many lists each round. After log2(k) rounds, one list
# remains. Every round touches all N remaining nodes once, and there are
# O(log k) rounds, giving the same O(N log k) bound as the heap approach
# without needing any auxiliary heap structure.
# Dry run: lists = [1->4->5, 1->3->4, 2->6]
#   Round 1: merge(1->4->5, 1->3->4) = 1->1->3->4->4->5; merge(2->6, None) = 2->6
#            -> lists now [1->1->3->4->4->5, 2->6]
#   Round 2: merge(1->1->3->4->4->5, 2->6) = 1->1->2->3->4->4->5->6
#            -> lists now [1->1->2->3->4->4->5->6]  (single list, done)
# Time:  O(N log k)
# Space: O(log k) recursion/iteration overhead (O(1) extra beyond pointers)
def _merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
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


def solve_best(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    lists = list(lists)
    if not lists:
        return None

    while len(lists) > 1:
        merged_round = []
        for i in range(0, len(lists), 2):
            first = lists[i]
            second = lists[i + 1] if i + 1 < len(lists) else None
            merged_round.append(_merge_two(first, second))
        lists = merged_round

    return lists[0]


# ============================================================
# Key Takeaways
# ============================================================
# - Merging k already-sorted sequences is a generalization of the classic
#   2-list merge; a min-heap of "current head per list" is the textbook way
#   to extend it to k sequences in O(N log k).
# - Pairwise divide and conquer achieves the same O(N log k) bound as the
#   heap by repeatedly halving the number of lists via the merge-sort merge
#   step — often preferred in practice for its simplicity and cache
#   locality over managing a heap.
# - Common mistake: comparing ListNode objects directly in a heap tuple
#   without a tie-breaker — Python can't compare nodes, so ties on value
#   raise a TypeError unless an index (or similar) is included in the tuple.
# - Related/variant problems to try next: Merge Two Sorted Lists, Sort
#   List, Kth Smallest Element in a Sorted Matrix (same heap k-way pattern).


if __name__ == "__main__":
    tests = [
        ([[1, 4, 5], [1, 3, 4], [2, 6]], [1, 1, 2, 3, 4, 4, 5, 6]),
        ([], []),
        ([[]], []),
        ([[1], [], [0]], [0, 1]),
        ([[5, 10], [1, 2, 3], [4]], [1, 2, 3, 4, 5, 10]),
    ]

    approaches = [solve_brute_force, solve_better, solve_best]
    for values_lists, expected in tests:
        for fn in approaches:
            lists = [build_linked_list(vals) for vals in values_lists]
            result_head = fn(lists)
            result = linked_list_to_list(result_head)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} lists={values_lists!r:35s} -> {result!r}  [{status}]")
