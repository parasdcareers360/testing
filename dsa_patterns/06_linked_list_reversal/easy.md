# Easy — Reverse Linked List

**Source**: LeetCode #206
**Pattern**: In-Place Linked List Reversal
**Difficulty**: Easy

## Problem Statement
Given the `head` of a singly linked list, reverse the list, and return the new head of the reversed list.

## Constraints
- The number of nodes in the list is in the range `[0, 5000]`.
- `-5000 <= Node.val <= 5000`

## Examples
**Example 1**
Input: `head = [1, 2, 3, 4, 5]`
Output: `[5, 4, 3, 2, 1]`
Explanation: Every `next` pointer is flipped, so the list is traversed in the opposite order.

**Example 2**
Input: `head = [1, 2]`
Output: `[2, 1]`
Explanation: The two-node list's pointer direction is reversed: node 2 now points to node 1, and node 1 points to `None`.

## Intuition — Why This Pattern
The brute-force approach would be to traverse the list once, collect all node values (or nodes) into an array, then build a brand-new linked list by iterating the array backward. This works but uses O(n) extra space for the array — unnecessary for a problem that can be solved with a single pass and no auxiliary storage.

The In-Place Reversal insight: reversing a linked list is fundamentally about **redirecting each node's `next` pointer to point backward instead of forward**. If we walk through the list once while keeping track of the node we just came from (`prev`), we can rewire each node's `next` pointer to point to `prev` *before* we lose access to the rest of the original list (which is why we must save `curr.next` into a temporary variable *before* overwriting it). This achieves the reversal in a single O(n) pass with O(1) extra space — no new nodes, no auxiliary array.

## Approach
1. Initialize `prev = None` and `curr = head`.
2. While `curr` is not `None`:
   a. Save `next_temp = curr.next` (remember where to go next, before we overwrite `curr.next`).
   b. Rewire: `curr.next = prev` (point the current node backward).
   c. Advance: `prev = curr`, then `curr = next_temp`.
3. When the loop ends (`curr` is `None`), `prev` holds the new head of the reversed list (it was the last node visited).
4. Return `prev`.

## Dry Run
Input: `head = [1, 2, 3]` (list: `1 -> 2 -> 3 -> None`)

| step | prev | curr | next_temp | action | list state (conceptually) |
|------|------|------|-----------|--------|------------------------------|
| init | None | 1 | — | — | 1->2->3->None |
| 1 | None | 1 | 2 | curr.next=prev (1.next=None); prev=1; curr=2 | None<-1  2->3->None |
| 2 | 1 | 2 | 3 | curr.next=prev (2.next=1); prev=2; curr=3 | None<-1<-2  3->None |
| 3 | 2 | 3 | None | curr.next=prev (3.next=2); prev=3; curr=None | None<-1<-2<-3 |
| end | 3 | None | — | loop stops (curr is None) | — |

Final: `prev = 3`, and following `3 -> 2 -> 1 -> None` gives the reversed list `[3, 2, 1]`, matching the expected reversal.

## Solution (Python 3)
```python
from typing import Optional, List


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_linked_list(values: List[int]) -> Optional[ListNode]:
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


def linked_list_to_list(node: Optional[ListNode]) -> List[int]:
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    curr = head

    while curr is not None:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp

    return prev


if __name__ == "__main__":
    head1 = build_linked_list([1, 2, 3, 4, 5])
    print(linked_list_to_list(reverse_list(head1)))  # Expected: [5, 4, 3, 2, 1]

    head2 = build_linked_list([1, 2])
    print(linked_list_to_list(reverse_list(head2)))  # Expected: [2, 1]

    head3 = build_linked_list([])
    print(linked_list_to_list(reverse_list(head3)))  # Expected: []
```

## Complexity Analysis
- Time: O(n) — a single pass through the list, visiting each node exactly once.
- Space: O(1) — only three pointer variables (`prev`, `curr`, `next_temp`) are used; the reversal is done in place by rewiring existing nodes.

## Key Takeaways
- The three-variable dance (`next_temp`, rewire, advance `prev`/`curr`) is the atomic building block for *every* linked-list reversal problem — memorize this exact sequence, since medium/hard variants just apply it to a sub-portion of the list, possibly multiple times.
- Common mistake: rewiring `curr.next = prev` *before* saving `next_temp = curr.next` — this permanently loses the reference to the rest of the list, since `curr.next` gets overwritten first.
- Related/variant problems to try next: **Reverse Linked List II** (reverse only a sublist — the medium problem in this pattern), **Palindrome Linked List** (uses reversal of the second half as a subroutine).
