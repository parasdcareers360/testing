"""
Linked Lists — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


class DoublyListNode:
    def __init__(self, val: int = 0):
        self.val = val
        self.prev: Optional["DoublyListNode"] = None
        self.next: Optional["DoublyListNode"] = None


# ---------------------------------------------------------------------------
# Helpers: build/inspect a singly linked list for testing
# ---------------------------------------------------------------------------
def from_list(values: List[int]) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head: Optional[ListNode]) -> List[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# ---------------------------------------------------------------------------
# Shape 1: reversal — iterative and recursive
# ---------------------------------------------------------------------------
def reverse_iterative_template(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev, curr = curr, nxt
    return prev


def reverse_recursive_template(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive_template(head.next)
    head.next.next = head
    head.next = None
    return new_head


# ---------------------------------------------------------------------------
# Shape 2: fast/slow pointers — middle and Floyd's cycle detection
# ---------------------------------------------------------------------------
def find_middle_template(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


def detect_cycle_start_template(head: Optional[ListNode]) -> Optional[ListNode]:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None
    slow = head
    while slow is not fast:
        slow = slow.next
        fast = fast.next
    return slow


# ---------------------------------------------------------------------------
# Shape 3: dummy head + merge pattern
# ---------------------------------------------------------------------------
def merge_two_sorted_template(
    a: Optional[ListNode], b: Optional[ListNode]
) -> Optional[ListNode]:
    dummy = ListNode()
    tail = dummy
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a if a else b
    return dummy.next


# ---------------------------------------------------------------------------
# Shape 4: dummy head + remove-nth-from-end (single pass, offset pointers)
# ---------------------------------------------------------------------------
def remove_nth_from_end_template(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(next=head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next


if __name__ == "__main__":
    assert to_list(from_list([1, 2, 3, 4, 5])) == [1, 2, 3, 4, 5]
    assert to_list(from_list([])) == []

    assert to_list(reverse_iterative_template(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverse_recursive_template(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert reverse_iterative_template(None) is None

    mid = find_middle_template(from_list([1, 2, 3, 4, 5]))
    assert mid.val == 3
    mid_even = find_middle_template(from_list([1, 2, 3, 4]))
    assert mid_even.val == 3  # second of the two middle nodes

    # cycle: 1 -> 2 -> 3 -> 4 -> 2 (start of cycle is node with val 2)
    n1, n2, n3, n4 = ListNode(1), ListNode(2), ListNode(3), ListNode(4)
    n1.next, n2.next, n3.next, n4.next = n2, n3, n4, n2
    cycle_start = detect_cycle_start_template(n1)
    assert cycle_start is n2

    no_cycle = from_list([1, 2, 3])
    assert detect_cycle_start_template(no_cycle) is None

    merged = merge_two_sorted_template(from_list([1, 2, 4]), from_list([1, 3, 4]))
    assert to_list(merged) == [1, 1, 2, 3, 4, 4]

    removed = remove_nth_from_end_template(from_list([1, 2, 3, 4, 5]), 2)
    assert to_list(removed) == [1, 2, 3, 5]
    removed_head = remove_nth_from_end_template(from_list([1]), 1)
    assert to_list(removed_head) == []

    print("All template shapes verified.")
