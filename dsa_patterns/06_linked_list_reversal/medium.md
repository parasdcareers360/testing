# Medium — Reverse Linked List II

**Source**: LeetCode #92
**Pattern**: In-Place Linked List Reversal
**Difficulty**: Medium

## Problem Statement
Given the `head` of a singly linked list and two integers `left` and `right` where `left <= right`, reverse the nodes of the list from position `left` to position `right` (1-indexed), and return the reversed list. All other nodes (before `left` and after `right`) must remain in their original order and connect correctly to the reversed sublist.

## Constraints
- The number of nodes in the list is `n`.
- `1 <= n <= 500`
- `-500 <= Node.val <= 500`
- `1 <= left <= right <= n`

## Examples
**Example 1**
Input: `head = [1, 2, 3, 4, 5]`, `left = 2`, `right = 4`
Output: `[1, 4, 3, 2, 5]`
Explanation: Nodes at positions 2 through 4 (values `2, 3, 4`) are reversed to `4, 3, 2`; positions 1 and 5 (values `1` and `5`) stay in place, correctly linked around the reversed section.

**Example 2**
Input: `head = [5]`, `left = 1`, `right = 1`
Output: `[5]`
Explanation: Reversing a single node (left == right) has no visible effect.

## Intuition — Why This Pattern
The twist compared to the easy problem in this pattern: instead of reversing the **entire** list, we must reverse only a **contiguous sublist** in the middle, while leaving everything before and after untouched and correctly connected.

Brute-force idea: extract the values of the sublist `[left, right]` into an array, reverse the array, then walk the sublist again writing the reversed values back into the existing nodes. This works but uses O(right - left) extra space for the array, and it's not truly "rewiring pointers" — it's overwriting values, which is a fine trick sometimes but doesn't scale to problems where nodes carry more complex payloads that must be moved, not copied.

The pointer-rewiring insight: **the exact same reversal loop from the easy problem still applies**, but now we must (a) first walk forward to the node just *before* position `left` (call it the `pre_sub` anchor — the piece that needs to be reconnected afterward), (b) run the standard `prev`/`curr`/`next_temp` reversal loop *only* for the nodes from position `left` to `right`, and (c) afterward, reconnect `pre_sub.next` to the new head of the reversed section (which is the old node at position `right`), and reconnect the new tail of the reversed section (the old node at position `left`, now at the end of the reversed piece) to whatever came after position `right`. This is still a single O(n) pass with O(1) extra space — just with two extra "stitching" pointers to remember the boundary nodes.

## Approach
1. Create a `dummy` node pointing to `head` (handles the edge case where `left == 1`, i.e., the reversal starts at the very first node, so there's no "previous" node to stitch).
2. Walk `pre_sub = dummy` forward `left - 1` times, so `pre_sub` ends up at the node immediately before position `left`.
3. Set `curr = pre_sub.next` (this is the node at position `left`, the start of the sublist to reverse). This same node will become the **tail** of the reversed sublist once reversal completes — remember it as `sub_tail_target = curr` conceptually (in code, we just keep `curr`'s reference around, no separate variable strictly needed, but it helps for clarity).
4. Run the standard reversal loop for exactly `right - left + 1` iterations: `prev = None`; then repeat `right - left + 1` times: save `next_temp = curr.next`; set `curr.next = prev`; set `prev = curr`; set `curr = next_temp`.
5. After the loop: `prev` is the new head of the reversed sublist (the old node at position `right`); `curr` is the node immediately after the sublist (the node at position `right + 1`, or `None` if `right == n`).
6. Stitch the pieces together: set `pre_sub.next.next = curr` (the *old* head of the sublist — still referenced via `pre_sub.next`, which hasn't been reassigned yet — is now the tail of the reversed section, so point it forward to whatever comes after the sublist). Then set `pre_sub.next = prev` (connect the node before the sublist to the new head of the reversed section).
7. Return `dummy.next` (the head of the overall list, accounting for the case where `left == 1` changed the actual head).

## Dry Run
Input: `head = [1, 2, 3, 4, 5]`, `left = 2`, `right = 4`

1. `dummy -> 1 -> 2 -> 3 -> 4 -> 5`. `pre_sub = dummy`.
2. Walk `pre_sub` forward `left - 1 = 1` time: `pre_sub = dummy.next = node(1)`.
3. `curr = pre_sub.next = node(2)` (start of sublist to reverse).
4. Reversal loop for `right - left + 1 = 3` iterations, `prev = None`:
   - Iter 1: `next_temp = curr.next = node(3)`. `curr.next = prev` → `node(2).next = None`. `prev = node(2)`. `curr = node(3)`.
   - Iter 2: `next_temp = curr.next = node(4)`. `curr.next = prev` → `node(3).next = node(2)`. `prev = node(3)`. `curr = node(4)`.
   - Iter 3: `next_temp = curr.next = node(5)`. `curr.next = prev` → `node(4).next = node(3)`. `prev = node(4)`. `curr = node(5)`.
5. Loop ends. `prev = node(4)` (new head of reversed section: `4 -> 3 -> 2 -> None`). `curr = node(5)` (node right after the sublist).
6. Stitch:
   - `pre_sub.next.next = curr` → `pre_sub.next` is still `node(2)` (unchanged reference, even though `node(2).next` was already rewired to `None` in iter 1) → `node(2).next = node(5)`.
   - `pre_sub.next = prev` → `node(1).next = node(4)`.
7. Return `dummy.next = node(1)`.

Final list, following pointers from `node(1)`: `1 -> 4 -> 3 -> 2 -> 5 -> None`, matching the expected output `[1, 4, 3, 2, 5]`.

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


def reverse_between(head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
    dummy = ListNode(0)
    dummy.next = head

    pre_sub = dummy
    for _ in range(left - 1):
        pre_sub = pre_sub.next

    curr = pre_sub.next
    prev = None

    for _ in range(right - left + 1):
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp

    pre_sub.next.next = curr
    pre_sub.next = prev

    return dummy.next


if __name__ == "__main__":
    head1 = build_linked_list([1, 2, 3, 4, 5])
    print(linked_list_to_list(reverse_between(head1, 2, 4)))  # Expected: [1, 4, 3, 2, 5]

    head2 = build_linked_list([5])
    print(linked_list_to_list(reverse_between(head2, 1, 1)))  # Expected: [5]

    head3 = build_linked_list([1, 2, 3])
    print(linked_list_to_list(reverse_between(head3, 1, 3)))  # Expected: [3, 2, 1]
```

## Complexity Analysis
- Time: O(n) — walking to `pre_sub` costs O(left), the reversal loop costs O(right - left + 1); together bounded by O(n).
- Space: O(1) — a fixed number of pointers (`dummy`, `pre_sub`, `curr`, `prev`, `next_temp`) regardless of list length or sublist size.

## Key Takeaways
- The `dummy` node trick elegantly handles the "what if the sublist starts at the very head" edge case, avoiding special-casing `left == 1` separately — a broadly reusable technique across linked-list problems.
- Common mistakes: capturing `pre_sub.next` (the old sublist head, now the reversed section's tail) *after* it's already been reassigned in step 6's second line, instead of before — the two stitching lines must happen in the order shown (connect the old head's `.next` first, *then* reassign `pre_sub.next`), otherwise the reference to the old sublist head is lost; off-by-one errors in the loop counts for walking to `pre_sub` (`left - 1` steps) or the reversal loop (`right - left + 1` iterations).
- Related/variant problems to try next: **Reverse Linked List** (the easy problem in this pattern), **Reverse Nodes in k-Group** (the hard problem in this pattern, which applies this exact sublist-reversal logic repeatedly), **Swap Nodes in Pairs**.
