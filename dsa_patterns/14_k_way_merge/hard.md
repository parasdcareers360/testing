# Hard — Merge k Sorted Lists

**Source**: LeetCode #23
**Pattern**: K-way Merge + Linked Lists
**Difficulty**: Hard

## Problem Statement
You are given an array `lists` of `k` linked-lists, where each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return its head.

Each linked-list node has the structure:
```
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

This escalates the pattern beyond the array/matrix versions: the k sorted sources are now **linked lists** rather than random-access arrays, so "advancing a source" means following a `.next` pointer instead of incrementing an index, and the output itself must be constructed as a linked list (not simply appended to a Python list) — you must correctly wire up new `.next` pointers as you go, and handle the classic linked-list edge cases (empty lists among the k inputs, all lists empty, a single list, etc.) without dereferencing `None`.

## Constraints
- `k == lists.length`
- `0 <= k <= 10^4`
- `0 <= lists[i].length <= 500`
- `-10^4 <= lists[i][j] <= 10^4`
- `lists[i]` is sorted in ascending order.
- The sum of `lists[i].length` will not exceed `10^4`.

## Examples
**Example 1**
Input: `lists = [[1,4,5],[1,3,4],[2,6]]` (each inner array represents a linked list)
Output: `[1,1,2,3,4,4,5,6]`
Explanation: Merging `1->4->5`, `1->3->4`, and `2->6` produces the fully sorted list `1->1->2->3->4->4->5->6`.

**Example 2**
Input: `lists = []`
Output: `[]`
Explanation: No lists at all to merge; the result is an empty list (represented as `None`/head is `None`).

**Example 3**
Input: `lists = [[]]`
Output: `[]`
Explanation: One list is provided, but it is itself empty (its head is `None`); the merged result is still empty.

## Intuition — Why This Pattern
**Brute force**: Traverse every one of the k linked lists, collect all node values into a single Python list (O(N) where N is the total node count), sort that list (O(N log N)), and then build a brand-new linked list from the sorted values (O(N)). This works, but — same story as every K-way Merge problem — it discards the fact that each individual list is already sorted, paying for a full re-sort we don't need.

A second brute-force variant: repeatedly scan the current heads of all k lists to find the smallest, unlink it, and repeat. This avoids the full sort but costs O(N*k) time overall (a linear scan across k candidates for each of the N nodes) — fine for small k, but scales poorly once k grows into the thousands, as this problem's constraints (`k` up to `10^4`) allow.

**What's inefficient**: The O(N*k) "linear scan for the minimum among k heads every time" approach re-does a full k-way comparison from scratch at every single step, when in fact only one of the k candidates changed since the last step (the one we just advanced).

**The insight**: This is exactly the K-way Merge idiom, applied to linked-list heads instead of array indices. Maintain a **min-heap of size k**, seeded with the current head node of every non-empty list. Repeatedly pop the smallest node, splice it onto the output list, and push that same list's *next* node (if it exists) back into the heap. Because the heap only ever holds up to k elements, finding-and-removing the minimum costs O(log k) instead of O(k) — reducing the total time from O(N*k) down to O(N log k).

One implementation subtlety: `ListNode` objects aren't inherently comparable in Python (comparing two nodes directly raises `TypeError` if their values tie), so the heap tuples must include a tie-breaking index (e.g., the list's original index) to guarantee any two tuples are always comparable.

## Approach
1. If `lists` is empty, return `None` immediately.
2. Initialize a min-heap `heap`. For each index `i` in `range(len(lists))`, if `lists[i]` is not `None` (non-empty), push the tuple `(lists[i].val, i, lists[i])` onto the heap — the middle element `i` exists purely as a tie-breaker so two nodes with equal values never cause a direct (unsupported) comparison between `ListNode` objects.
3. Create a dummy sentinel node `dummy = ListNode()` and a pointer `tail = dummy` that always points to the last node appended to the output so far.
4. While `heap` is not empty:
   a. Pop the smallest tuple `(val, i, node)`.
   b. Attach it to the output: `tail.next = node`; then advance `tail = tail.next`.
   c. If `node.next` is not `None`, push `(node.next.val, i, node.next)` onto the heap (advancing list `i`'s source pointer).
5. After the loop, terminate the output list: `tail.next = None` (guards against a dangling stale pointer from whichever list contributed the very last node).
6. Return `dummy.next` (the true head of the merged list, skipping the sentinel).

## Dry Run
Trace `lists` represented as `[1->4->5, 1->3->4, 2->6]` (using linked lists with those values in order).

**Initialization:** heads are `1` (list 0), `1` (list 1), `2` (list 2). Push `(1, 0, node1_a)`, `(1, 1, node1_b)`, `(2, 2, node2)`. Since values tie at `1`, the tie-breaker index (`0` vs `1`) decides pop order: `(1, 0, node1_a)` pops before `(1, 1, node1_b)`.

`dummy -> (empty)`, `tail = dummy`.

| Step | Pop (val, i) | Splice onto output | tail now points to | Push next from list i (if any) |
|------|---------------|----------------------|----------------------|-----------------------------------|
| 1 | (1, 0) | output: 1 | node with val 1 (from list 0) | list 0 next is 4 -> push (4,0,node4_a) |
| 2 | (1, 1) | output: 1 -> 1 | node with val 1 (from list 1) | list 1 next is 3 -> push (3,1,node3) |
| 3 | (2, 2) | output: 1 -> 1 -> 2 | node with val 2 (from list 2) | list 2 next is 6 -> push (6,2,node6) |
| 4 | (3, 1) | output: 1 -> 1 -> 2 -> 3 | node with val 3 (from list 1) | list 1 next is 4 -> push (4,1,node4_b) |
| 5 | (4, 0) | output: ...-> 3 -> 4 | node with val 4 (from list 0, tie broken by index 0 < 1) | list 0 next is 5 -> push (5,0,node5) |
| 6 | (4, 1) | output: ...-> 4 -> 4 | node with val 4 (from list 1) | list 1 next is None -> push nothing |
| 7 | (5, 0) | output: ...-> 4 -> 5 | node with val 5 (from list 0) | list 0 next is None -> push nothing |
| 8 | (6, 2) | output: ...-> 5 -> 6 | node with val 6 (from list 2) | list 2 next is None -> push nothing |

Heap is now empty. `tail.next = None` terminates the list. `dummy.next` is the head of `1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6`, matching the expected output `[1,1,2,3,4,4,5,6]`.

## Solution (Python 3)
```python
import heapq
from typing import List, Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists into one sorted linked list using a
    size-k min-heap keyed on (value, source_index) to avoid comparing
    ListNode objects directly."""
    if not lists:
        return None

    heap = []
    for i, node in enumerate(lists):
        if node is not None:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode()
    tail = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))

    tail.next = None
    return dummy.next


# --- Helpers for testing (not part of the core algorithm) ---
def build_list(values: List[int]) -> Optional[ListNode]:
    head = None
    tail = None
    for v in values:
        node = ListNode(v)
        if head is None:
            head = node
            tail = node
        else:
            tail.next = node
            tail = node
    return head


def list_to_array(head: Optional[ListNode]) -> List[int]:
    out = []
    while head is not None:
        out.append(head.val)
        head = head.next
    return out


if __name__ == "__main__":
    lists1 = [build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]
    print(list_to_array(merge_k_lists(lists1)))  # Expected: [1, 1, 2, 3, 4, 4, 5, 6]

    print(list_to_array(merge_k_lists([])))       # Expected: []

    print(list_to_array(merge_k_lists([None])))   # Expected: []
```

## Complexity Analysis
- Time: O(N log k), where N is the total number of nodes across all k lists. Each node is pushed and popped from the heap exactly once, each operation costing O(log k) since the heap never holds more than k elements at a time.
- Space: O(k) for the heap. (The output list reuses the existing input nodes rather than allocating new ones, so no additional O(N) node-allocation space is needed beyond the heap and a few pointers — though the recursive "divide and conquer, merge pairs of lists" alternative approach to this same problem also achieves O(N log k) time with O(1) extra space beyond recursion stack, at the cost of more complex pairwise-merge bookkeeping.)

## Key Takeaways
- This problem is the "combine with another data structure" escalation of K-way Merge: the underlying heap logic is identical to merging k sorted arrays, but you must additionally manage linked-list mechanics correctly — dummy/sentinel head node, advancing a `tail` pointer, and terminating the list with `tail.next = None` at the end.
- `ListNode` objects are not natively ordered in Python, so any heap of `(node, ...)` tuples must include a tie-breaking field (like the source list's index) placed *before* the raw node in the tuple, otherwise a value tie between two different lists raises `TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'`.
- A common mistake is forgetting to set `tail.next = None` at the end — if the last node spliced in still has a stale `.next` pointer from its original list (which it shouldn't, if it was truly the last node from that list, but is a good defensive habit regardless), leaving it unset can silently create bugs in other contexts; more commonly, forgetting the dummy-head pattern entirely and mishandling the very first append is the classic bug.
- Related/variant problems to try next: **Merge Two Sorted Lists** (LeetCode #21 — the k=2 base case, good warm-up before tackling this) and **Merge k Sorted Arrays** (the array-based version of this exact pattern, a simpler baseline) and **Smallest Range Covering Elements from K Lists** (LeetCode #632 — a genuinely harder variant requiring you to track the current max across all k list-fronts in addition to the heap-tracked min).
