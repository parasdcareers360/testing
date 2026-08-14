# Medium — Linked List Cycle II

**Source**: LeetCode #142
**Pattern**: Fast & Slow Pointers
**Difficulty**: Medium

## Problem Statement
Given the `head` of a singly linked list, return the node where the cycle begins. If there is no cycle, return `null`.

There is a cycle in a linked list if some node in the list can be reached again by continuously following the `next` pointer. Internally, a cycle is represented by an integer `pos` (not passed as a parameter) which denotes the index (0-indexed) of the node the tail's `next` pointer connects to. If `pos` is `-1`, there is no cycle.

You must solve it **without modifying** the linked list, and ideally using O(1) extra memory.

## Constraints
- The number of nodes in the list is in the range `[0, 10^4]`.
- `-10^5 <= Node.val <= 10^5`
- `pos` is `-1` or a valid index in the linked list.

## Examples
**Example 1**
Input: `head = [3, 2, 0, -4]`, `pos = 1` (tail connects to the node with value 2, at index 1)
Output: the node with value `2`
Explanation: There is a cycle where the tail (`-4`) connects to the 2nd node (0-indexed index 1, value 2). The cycle begins at that node.

**Example 2**
Input: `head = [1, 2]`, `pos = 0` (tail connects to node at index 0)
Output: the node with value `1`
Explanation: There is a cycle where the tail connects to the first node.

**Example 3**
Input: `head = [1]`, `pos = -1`
Output: `null`
Explanation: There is no cycle in the linked list.

## Intuition — Why This Pattern
The twist compared to the easy problem in this pattern (Middle of the Linked List): we're no longer just measuring distance, we now need to detect a **cycle** and pinpoint exactly **where it starts** — a strictly harder task.

**Brute force**: traverse the list while storing every visited node in a hash set. If we ever revisit a node already in the set, that node is the cycle's start. This works in O(n) time but uses O(n) extra space — the problem wants O(1) space.

**The Fast & Slow insight (Floyd's Cycle Detection, extended)**: Move `slow` one step and `fast` two steps at a time, same as before. If there's a cycle, `fast` will eventually "lap" `slow` inside the cycle and they will meet at some node — this alone proves a cycle exists (this is phase 1, same as "Linked List Cycle I").

The clever extra insight for finding the **start** of the cycle (phase 2): let the distance from the head to the cycle's start be `a`, and let the distance from the cycle's start to the meeting point (going forward along the cycle) be `b`. It can be proven algebraically (using the fact that `fast` travels exactly twice the distance `slow` does by the time they meet) that the distance remaining from the meeting point back around to the cycle's start (call it `c`, the rest of the cycle) equals `a`. In other words: **if you place one pointer back at `head` and leave the other at the meeting point, then advance both one step at a time, they will meet exactly at the cycle's start.** This second phase needs no extra space and no length pre-computation.

## Approach
1. **Phase 1 — Detect a cycle**: Initialize `slow = head`, `fast = head`. While `fast` and `fast.next` are not `None`: move `slow` by 1, `fast` by 2. If `slow == fast` at any point, a cycle is detected — break out and proceed to Phase 2. If the loop ends naturally (`fast` or `fast.next` becomes `None`), there is no cycle — return `None`.
2. **Phase 2 — Find the cycle start**: Reset one pointer, say `ptr1 = head`; keep the other, `ptr2 = ` the meeting point found in Phase 1. Move both `ptr1` and `ptr2` one step at a time simultaneously. The node where `ptr1 == ptr2` is the start of the cycle. Return that node.

## Dry Run
Input: `head = [3, 2, 0, -4]`, tail (`-4`) connects back to node at index 1 (value `2`).

List structure: `3 -> 2 -> 0 -> -4 -> (back to 2)`. Nodes by index: [0]=3, [1]=2, [2]=0, [3]=-4, and node[3].next = node[1].

**Phase 1** (slow steps by 1, fast steps by 2):
- Start: slow=3(idx0), fast=3(idx0).
- Step 1: slow=2(idx1), fast=0(idx2) [fast moved 3→0→... wait let's be careful: fast = fast.next.next = idx0.next.next = idx1.next = idx2 = 0]. So slow=idx1(2), fast=idx2(0).
- Step 2: slow=idx2(0), fast = idx2.next.next = idx3.next = idx1 (since idx3.next wraps to idx1) = idx1(2). So slow=idx2(0), fast=idx1(2).
- Step 3: slow = idx2.next = idx3(-4). fast = idx1.next.next = idx2.next = idx3(-4). So slow=idx3(-4), fast=idx3(-4). **slow == fast!** Cycle detected, meeting point = idx3 (value -4).

**Phase 2**:
- ptr1 = head = idx0(3). ptr2 = meeting point = idx3(-4).
- Check ptr1 == ptr2? idx0 vs idx3 → no.
- Move both one step: ptr1 = idx0.next = idx1(2). ptr2 = idx3.next = idx1(2) (wraps around).
- Check ptr1 == ptr2? idx1 vs idx1 → **yes!** Both are node idx1 (value 2).

Return node with value `2` — the cycle start, matching the expected output.

## Solution (Python 3)
```python
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    slow, fast = head, head

    # Phase 1: detect whether a cycle exists
    has_cycle = False
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            has_cycle = True
            break

    if not has_cycle:
        return None

    # Phase 2: find the start of the cycle
    ptr1 = head
    ptr2 = slow  # meeting point from phase 1
    while ptr1 != ptr2:
        ptr1 = ptr1.next
        ptr2 = ptr2.next

    return ptr1


def build_cyclic_list(values, pos):
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos != -1 and nodes:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


if __name__ == "__main__":
    head1 = build_cyclic_list([3, 2, 0, -4], 1)
    result1 = detect_cycle(head1)
    print(result1.val if result1 else None)  # Expected: 2

    head2 = build_cyclic_list([1, 2], 0)
    result2 = detect_cycle(head2)
    print(result2.val if result2 else None)  # Expected: 1

    head3 = build_cyclic_list([1], -1)
    result3 = detect_cycle(head3)
    print(result3.val if result3 else None)  # Expected: None
```

## Complexity Analysis
- Time: O(n) — Phase 1 takes O(n) (fast pointer covers at most about 2n steps before either exiting or meeting slow); Phase 2 takes at most O(n) steps (the distance from head to cycle start is at most n). Total remains O(n).
- Space: O(1) — only a constant number of pointers are used; no hash set or extra list needed.

## Key Takeaways
- The "reset one pointer to head, then move both one step at a time" trick for finding the cycle start relies on a clean mathematical proof involving the distances `a` (head to cycle start), `b` (cycle start to meeting point), and the cycle length — worth internalizing the proof once so the trick doesn't feel like magic.
- Common mistakes: forgetting the `fast.next is not None` guard (crashes on lists with no cycle); reusing the same "meeting point" variable incorrectly across phases; assuming the meeting point IS the cycle start (it generally is not — only Phase 2 finds the true start).
- This is a strict generalization of Linked List Cycle I (which only asks "does a cycle exist," answerable with just Phase 1).
- Related/variant problems to try next: **Linked List Cycle I**, **Happy Number** (same Floyd's-cycle idea applied to a sequence of digit-square-sums instead of a linked list).
