# Hard — Reverse Nodes in k-Group

**Source**: LeetCode #25
**Pattern**: In-Place Linked List Reversal
**Difficulty**: Hard

## Problem Statement
Given the `head` of a linked list, reverse the nodes of the list `k` at a time, and return the modified list.

`k` is a positive integer and is less than or equal to the length of the linked list. If the number of nodes is not a multiple of `k`, then the nodes left over at the end (fewer than `k` of them) should remain in their original order (i.e., they are **not** reversed).

You may not alter the values in the list's nodes (only node pointers may be changed), and you must solve it using only O(1) extra memory (i.e., you cannot copy the list into an array).

## Constraints
- The number of nodes in the list is `n`.
- `1 <= n <= 5000`
- `0 <= Node.val <= 1000`
- `1 <= k <= n`

## Examples
**Example 1**
Input: `head = [1, 2, 3, 4, 5]`, `k = 2`
Output: `[2, 1, 4, 3, 5]`
Explanation: The first group of 2 (`1, 2`) reverses to `2, 1`. The second group of 2 (`3, 4`) reverses to `4, 3`. Only one node (`5`) is left over — fewer than `k=2` — so it stays as-is.

**Example 2**
Input: `head = [1, 2, 3, 4, 5]`, `k = 3`
Output: `[3, 2, 1, 4, 5]`
Explanation: The first group of 3 (`1, 2, 3`) reverses to `3, 2, 1`. Only two nodes (`4, 5`) are left over — fewer than `k=3` — so they stay in original order.

## Intuition — Why This Pattern
This is the hardest problem in this pattern because it **combines two ideas at once**: (1) the sublist-reversal mechanics from the medium problem (reverse a bounded segment, then correctly stitch its boundaries to the rest of the list), applied (2) **repeatedly**, group by group, with the added complication that the **final, possibly-partial group must be detected in advance and left untouched**.

Brute force: this problem explicitly forbids copying values into an array (O(1) space required), so a "collect into array, reverse chunks, write back" approach is disallowed outright — we must rewire pointers directly.

The insight that makes repeated application tractable: process the list group by group using a `dummy` node and a `group_prev` pointer (the node just before the current group, initially the dummy). For each group:
1. **First, check if a full group of `k` nodes actually exists** starting from the current position — walk forward `k` steps without moving pointers permanently, just to confirm there are enough nodes left. If not, stop entirely (leave the remaining partial group untouched).
2. If a full group exists, reverse exactly those `k` nodes using the same `prev`/`curr`/`next_temp` loop from the easy/medium problems.
3. Stitch: connect `group_prev` to the new head of this reversed group (the group's old tail), and connect the new tail of this reversed group (the group's old head) to whatever comes next (the start of the next group, or `None`).
4. Advance `group_prev` to the new tail of the just-reversed group (which is the correct anchor point for stitching the *next* group), and repeat from step 1 for the next group.

Because each node is visited a small constant number of times (once to check group existence, once to reverse), the whole algorithm remains O(n) time and O(1) extra space — no recursion-based value copying, no arrays.

## Approach
1. Create a `dummy` node with `dummy.next = head`. Set `group_prev = dummy`.
2. Loop:
   a. **Check for a full group**: starting from `group_prev.next`, walk a temporary pointer `node_check` forward `k` steps. If at any point `node_check` becomes `None` before completing `k` steps, there is no full group left — break out of the loop entirely (the remaining nodes stay as-is).
   b. If a full group exists: let `group_start = group_prev.next` (the first node of this group, which will become the tail after reversal). Let `group_next = node_check` (the node right after this group, found in step a — this is where the reversed group must reconnect afterward).
   c. Reverse exactly the `k` nodes from `group_start` using the standard `prev = None`, `curr = group_start` loop, run for `k` iterations (save `next_temp`, `curr.next = prev`, `prev = curr`, `curr = next_temp`).
   d. Stitch: `group_prev.next = prev` (new head of reversed group, connect from the previous group's tail). `group_start.next = group_next` (the old group head, now the reversed group's tail, connects forward to the next group).
   e. Advance `group_prev = group_start` (this node is now correctly the tail of the just-reversed group, and the correct anchor for the *next* group's stitching).
   f. Repeat from step a.
3. Return `dummy.next`.

## Dry Run
Input: `head = [1, 2, 3, 4, 5]`, `k = 2`

1. `dummy -> 1 -> 2 -> 3 -> 4 -> 5`. `group_prev = dummy`.

**Group 1:**
- Check for full group of 2 starting at `group_prev.next = node(1)`: walk 2 steps: `node(1)` → `node(2)` → stop (found 2 nodes; `node_check` ends at `node(2)`... let's define precisely: `node_check` starts at `group_prev.next`, and after `k` steps forward `node_check = group_next`). Walking: start `node_check = node(1)`. Step 1: `node_check = node(1).next = node(2)`. Step 2: `node_check = node(2).next = node(3)`. Completed 2 steps without hitting `None` → full group exists. `group_next = node(3)`.
- `group_start = group_prev.next = node(1)`.
- Reverse 2 nodes starting at `node(1)`: `prev=None`, `curr=node(1)`.
  - iter1: `next_temp=node(1).next=node(2)`. `node(1).next=None`. `prev=node(1)`. `curr=node(2)`.
  - iter2: `next_temp=node(2).next=node(3)`. `node(2).next=node(1)`. `prev=node(2)`. `curr=node(3)`.
- Stitch: `group_prev.next = prev` → `dummy.next = node(2)`. `group_start.next = group_next` → `node(1).next = node(3)`.
- Advance: `group_prev = group_start = node(1)`.

Current list so far: `dummy -> 2 -> 1 -> 3 -> 4 -> 5`.

**Group 2:**
- Check full group of 2 starting at `group_prev.next = node(1).next = node(3)`: walk 2 steps: `node_check=node(3)` → step1: `node(3).next=node(4)` → step2: `node(4).next=node(5)`. Completed without hitting `None` → full group exists. `group_next = node(5)`.
- `group_start = group_prev.next = node(3)`.
- Reverse 2 nodes starting at `node(3)`: `prev=None`, `curr=node(3)`.
  - iter1: `next_temp=node(3).next=node(4)`. `node(3).next=None`. `prev=node(3)`. `curr=node(4)`.
  - iter2: `next_temp=node(4).next=node(5)`. `node(4).next=node(3)`. `prev=node(4)`. `curr=node(5)`.
- Stitch: `group_prev.next = prev` → `node(1).next = node(4)`. `group_start.next = group_next` → `node(3).next = node(5)`.
- Advance: `group_prev = group_start = node(3)`.

Current list so far: `dummy -> 2 -> 1 -> 4 -> 3 -> 5`.

**Group 3 (check only):**
- Check full group of 2 starting at `group_prev.next = node(3).next = node(5)`: walk 2 steps: `node_check=node(5)` → step1: `node(5).next=None` → hit `None` before completing 2 steps → no full group → break.

Return `dummy.next = node(2)`. Following pointers: `2 -> 1 -> 4 -> 3 -> 5 -> None`, matching the expected output `[2, 1, 4, 3, 5]`.

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


def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    dummy = ListNode(0)
    dummy.next = head
    group_prev = dummy

    while True:
        # Step a: check whether a full group of k nodes exists
        node_check = group_prev.next
        count = 0
        while node_check is not None and count < k:
            node_check = node_check.next
            count += 1

        if count < k:
            break  # not enough nodes left for a full group; leave them as-is

        group_next = node_check  # node right after this group

        # Step c: reverse exactly k nodes starting at group_prev.next
        group_start = group_prev.next
        prev = None
        curr = group_start
        for _ in range(k):
            next_temp = curr.next
            curr.next = prev
            prev = curr
            curr = next_temp

        # Step d: stitch the reversed group into the list
        group_prev.next = prev
        group_start.next = group_next

        # Step e: advance group_prev to the tail of the just-reversed group
        group_prev = group_start

    return dummy.next


if __name__ == "__main__":
    head1 = build_linked_list([1, 2, 3, 4, 5])
    print(linked_list_to_list(reverse_k_group(head1, 2)))  # Expected: [2, 1, 4, 3, 5]

    head2 = build_linked_list([1, 2, 3, 4, 5])
    print(linked_list_to_list(reverse_k_group(head2, 3)))  # Expected: [3, 2, 1, 4, 5]

    head3 = build_linked_list([1, 2, 3, 4, 5, 6])
    print(linked_list_to_list(reverse_k_group(head3, 2)))  # Expected: [2, 1, 4, 3, 6, 5]
```

## Complexity Analysis
- Time: O(n) — every node is visited a small constant number of times: once during a group's existence check, and once during that group's reversal loop. Total work across all groups sums to O(n).
- Space: O(1) — only a fixed handful of pointers (`dummy`, `group_prev`, `node_check`, `group_start`, `group_next`, `prev`, `curr`, `next_temp`) are used, regardless of `n` or `k`. (A recursive solution to this same problem would use O(n/k) stack space, which is why the iterative version shown here is preferred when strict O(1) space is required.)

## Key Takeaways
- This problem is a direct escalation of the medium problem: instead of reversing one bounded sublist, it repeatedly applies the same reverse-and-stitch mechanics group by group, with an added "look-ahead" check to detect and skip a trailing partial group.
- Common mistakes: reversing a group before confirming it has a full `k` nodes (this would incorrectly reverse the final partial group, or crash on a `None` dereference mid-reversal); forgetting to advance `group_prev` to `group_start` (not to `prev` or `group_next`) after each group — `group_start` is the old head, which becomes the correct tail/anchor after reversal.
- The look-ahead "walk k steps to check, then walk again to actually reverse" approach trades a small constant-factor slowdown for the simplicity of not needing to handle partial reversal and un-reversal on failure — a good general technique when a group-based transformation must be all-or-nothing.
- Related/variant problems to try next: **Reverse Linked List II** (the medium problem in this pattern), **Swap Nodes in Pairs** (the special case `k=2`, often solved with simpler dedicated logic), **Rotate List**.
