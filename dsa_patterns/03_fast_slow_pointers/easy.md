# Easy — Middle of the Linked List

**Source**: LeetCode #876
**Pattern**: Fast & Slow Pointers
**Difficulty**: Easy

## Problem Statement
Given the `head` of a singly linked list, return the middle node of the linked list.

If there are two middle nodes (i.e., the list has an even number of nodes), return the **second** middle node.

## Constraints
- The number of nodes in the list is in the range `[1, 100]`.
- `1 <= Node.val <= 100`

## Examples
**Example 1**
Input: `head = [1, 2, 3, 4, 5]`
Output: `[3, 4, 5]` (i.e., the returned node is the node with value 3, and printing from there gives `3 -> 4 -> 5`)
Explanation: The list has 5 nodes; the middle node is the 3rd one (value 3).

**Example 2**
Input: `head = [1, 2, 3, 4, 5, 6]`
Output: `[4, 5, 6]`
Explanation: The list has 6 nodes; there are two middle nodes (values 3 and 4). Since we return the second middle node, we return the node with value 4.

## Intuition — Why This Pattern
The brute-force approach is to traverse the entire list once to count its length `n`, then traverse again from the head for `n // 2` steps to reach the middle. This works but requires **two full passes** over the list (or storing all nodes in an array to index into, which costs O(n) extra space).

The insight behind Fast & Slow Pointers: if one pointer (`fast`) moves twice as fast as another pointer (`slow`), then by the time `fast` has traveled the entire length of the list, `slow` has traveled exactly half that distance — landing precisely on the middle node. This means we only need **one pass**, with two pointers moving at different speeds, to find the middle without ever knowing the length in advance.

## Approach
1. Initialize `slow = head` and `fast = head`.
2. While `fast` is not `None` and `fast.next` is not `None`:
   a. Move `slow` one step: `slow = slow.next`.
   b. Move `fast` two steps: `fast = fast.next.next`.
3. When the loop ends (`fast` is `None` or `fast.next` is `None`), `slow` is at the middle node (the second middle if the list has even length, due to how the loop condition naturally handles it).
4. Return `slow`.

## Dry Run
Input: `head = [1, 2, 3, 4, 5, 6]` (even length, so we expect the second middle, value 4)

| step | slow | fast | fast.next exists? |
|------|------|------|--------------------|
| init | 1 | 1 | yes |
| 1 | 2 | 3 | yes |
| 2 | 3 | 5 | yes |
| 3 | 4 | (fast.next.next: 5.next=6, 6.next=None) → fast=None | loop check: fast is None → stop |

Let's re-trace carefully with node values as position markers (1-indexed list `1,2,3,4,5,6`):
- Initial: slow=1, fast=1.
- Iteration check: fast=1 (not None), fast.next=2 (not None) → enter loop.
  - slow = slow.next = 2.
  - fast = fast.next.next = 1.next.next = 2.next = 3.
- Iteration check: fast=3 (not None), fast.next=4 (not None) → enter loop.
  - slow = slow.next = 3.
  - fast = fast.next.next = 3.next.next = 4.next = 5.
- Iteration check: fast=5 (not None), fast.next=6 (not None) → enter loop.
  - slow = slow.next = 4.
  - fast = fast.next.next = 5.next.next = 6.next = None.
- Iteration check: fast=None → loop stops.

Final `slow` = node with value 4. Output: node 4 (list from there: `4 -> 5 -> 6`), matching the expected second-middle behavior.

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


def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
    slow, fast = head, head

    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    return slow


if __name__ == "__main__":
    head1 = build_linked_list([1, 2, 3, 4, 5])
    print(linked_list_to_list(middle_node(head1)))  # Expected: [3, 4, 5]

    head2 = build_linked_list([1, 2, 3, 4, 5, 6])
    print(linked_list_to_list(middle_node(head2)))  # Expected: [4, 5, 6]
```

## Complexity Analysis
- Time: O(n) — `fast` traverses the list once (roughly n/2 iterations, each moving 2 nodes), a single pass over the list.
- Space: O(1) — only two pointers are used, no auxiliary storage.

## Key Takeaways
- The loop condition `while fast and fast.next` is what automatically makes the algorithm return the *second* middle node for even-length lists — a subtle but important detail; using `while fast.next and fast.next.next` instead would return the *first* middle node for even-length lists.
- Common mistake: not checking `fast is not None` before accessing `fast.next` (causes a `NoneType has no attribute 'next'` crash on odd-length lists).
- This exact fast/slow speed-doubling trick is the foundation for cycle detection (Floyd's algorithm) — see the medium and hard problems in this pattern.
- Related/variant problems to try next: **Palindrome Linked List** (uses this to find the midpoint, then reverses the second half), **Linked List Cycle I**.
