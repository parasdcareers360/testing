"""
LeetCode Top Interview 150 — #58 (LeetCode #2)
Add Two Numbers
Category: Linked List | Difficulty: Medium

Problem
-------
You are given two non-empty linked lists representing two non-negative integers. The digits are
stored in **reverse order**, and each node contains a single digit. Add the two numbers and
return the sum as a linked list, in the same reverse-digit format.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Constraints
-----------
- The number of nodes in each list is in the range [1, 100].
- 0 <= Node.val <= 9
- It is guaranteed that the list represents a number that does not have leading zeros.

Examples
--------
Example 1:
    Input: l1 = [2,4,3], l2 = [5,6,4]
    Output: [7,0,8]
    Explanation: 342 + 465 = 807, stored reversed as [7,0,8].

Example 2:
    Input: l1 = [0], l2 = [0]
    Output: [0]

Example 3:
    Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
    Output: [8,9,9,9,0,0,0,1]

Intuition
---------
Because the digits are already stored least-significant-digit-first, this maps directly onto how
addition works by hand — no reversal needed first. One valid but "cheating" approach is to lean
on Python's arbitrary-precision integers: decode each list into an int, add, and re-encode the
result as a list; it's O(n) but sidesteps actually simulating the arithmetic (and wouldn't
translate to a language without big integers). The real technique is to walk both lists in
lockstep, summing corresponding digits plus a running carry (0 or 1) at each step, emitting one
result digit per step, and continuing past the shorter list's end (treating missing digits as 0)
until both lists and any final carry are exhausted.
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
# Approach 1: Brute Force (decode to int, add, re-encode)
# ============================================================
# Idea: convert each reversed-digit list into an integer, add them with
# native arithmetic, then split the sum back into reversed digits.
# Time:  O(n + m) to decode/encode   Space: O(n + m) for the digit strings
def solve_brute_force(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    def to_int(node: Optional[ListNode]) -> int:
        digits = []
        while node is not None:
            digits.append(str(node.val))
            node = node.next
        return int("".join(reversed(digits)))

    total = to_int(l1) + to_int(l2)
    return build_linked_list([int(d) for d in reversed(str(total))])


# ============================================================
# Approach 2: Optimal (simulate elementary addition digit-by-digit)
# ============================================================
# Idea: walk l1 and l2 together, at each step adding l1's digit (or 0 if that
# list ran out) + l2's digit (or 0) + carry-in from the previous step;
# emit sum % 10 as the next result node and carry sum // 10 forward. Stop
# once both lists are exhausted and the carry is 0.
# Dry run: l1=[9,9,9,9,9,9,9] (9999999), l2=[9,9,9,9] (9999)
#   step0: 9+9+0=18 -> digit 8, carry 1
#   step1: 9+9+1=19 -> digit 9, carry 1
#   step2: 9+9+1=19 -> digit 9, carry 1
#   step3: 9+9+1=19 -> digit 9, carry 1
#   step4: 9+0+1=10 -> digit 0, carry 1   (l2 exhausted, treated as 0)
#   step5: 9+0+1=10 -> digit 0, carry 1
#   step6: 9+0+1=10 -> digit 0, carry 1
#   step7: 0+0+1=1  -> digit 1, carry 0   (both exhausted, final carry emitted)
#   result: [8,9,9,9,0,0,0,1]
# Time:  O(max(n, m))   Space: O(max(n, m)) for the output list
def solve_optimal(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    carry = 0

    while l1 is not None or l2 is not None or carry:
        d1 = l1.val if l1 is not None else 0
        d2 = l2.val if l2 is not None else 0
        total = d1 + d2 + carry
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        l1 = l1.next if l1 is not None else None
        l2 = l2.next if l2 is not None else None

    return dummy.next


# ============================================================
# Key Takeaways
# ============================================================
# - This is the "add with carry" pattern: emit one digit at a time, thread a
#   carry variable through the loop, and keep looping as long as either
#   input still has digits OR a carry remains — that last carry-only step is
#   the easiest part to forget (e.g. 5 + 5 = [0,1], not [0]).
# - Common mistake: stopping the loop when one list runs out instead of
#   treating its missing digits as 0 and continuing until both are done.
# - Related/variant problems to try next: Add Two Numbers II (digits stored
#   most-significant-first — forces a stack or reversal first), Multiply
#   Strings, Plus One.


if __name__ == "__main__":
    tests = [
        ((build_linked_list([2, 4, 3]), build_linked_list([5, 6, 4])), [7, 0, 8]),
        ((build_linked_list([0]), build_linked_list([0])), [0]),
        (
            (build_linked_list([9, 9, 9, 9, 9, 9, 9]), build_linked_list([9, 9, 9, 9])),
            [8, 9, 9, 9, 0, 0, 0, 1],
        ),
        ((build_linked_list([1]), build_linked_list([9, 9])), [0, 0, 1]),
        ((build_linked_list([5]), build_linked_list([5])), [0, 1]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            l1, l2 = args
            result = linked_list_to_list(fn(l1, l2))
            status = "OK" if result == expected else "FAIL"
            in1, in2 = linked_list_to_list(l1), linked_list_to_list(l2)
            print(f"{fn.__name__:20s} l1={in1!r:20s} l2={in2!r:15s} -> {result!r}  [{status}]")
