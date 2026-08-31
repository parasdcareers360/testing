# Linked Lists

> **Type:** Study notes

## Why interviewers ask this

Linked lists test pointer discipline under pressure more than algorithmic insight — most linked
list problems are O(n) either way, so the interviewer is really grading whether you can manipulate
`.next` references without losing a node, creating a cycle by accident, or crashing on `None`. It's
also a common gateway to two-pointer techniques (fast/slow) and to dummy-node bookkeeping, both of
which reappear constantly in later, harder problems (merge k lists, LRU cache, etc.).

## The core idea

A singly linked list is a chain of nodes where each holds a value and a reference to the next node
(`None` terminates the chain). A doubly linked list adds a `prev` reference, trading extra memory
per node for O(1) removal given only a reference to the node (no need to walk from the head to find
its predecessor). Almost every linked-list technique reduces to one of: **rewire pointers in
place**, **use two pointers moving at different speeds/starting points**, or **use a dummy head to
avoid special-casing the first node**.

Recognize this pattern when you see:
- "reverse a linked list" (iterative or recursive pointer rewiring)
- "detect/find the start of a cycle," "find the middle" (fast/slow pointers)
- "merge two/k sorted lists" (repeated smallest-of-front comparison)
- "remove the nth node from the end," "remove duplicates," "partition a list" (dummy head +
  same-direction pointers)

## Key techniques

### 1. Node definition + basic traversal
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def to_list(head: ListNode | None) -> list:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

def from_list(values: list) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next
```
`from_list`/`to_list` aren't interview content themselves, but building them first makes every
other technique testable in isolation — the dummy-head trick used here is the same one used in
technique 4.

### 2. Reversal — iterative and recursive
```python
def reverse_iterative(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        nxt = curr.next      # save before overwriting
        curr.next = prev     # rewire backward
        prev, curr = curr, nxt
    return prev  # new head

def reverse_recursive(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head   # the node after head now points back to head
    head.next = None        # head becomes the new tail
    return new_head
```
Iterative uses O(1) space and three rolling pointers (`prev`, `curr`, `nxt` — `nxt` exists purely
so you don't lose the rest of the list the instant you overwrite `curr.next`). Recursive uses O(n)
call-stack space but mirrors the same rewiring, one level per node, unwinding from the tail
backward.

### 3. Fast/slow pointers — find the middle and detect a cycle (Floyd's algorithm)
```python
def find_middle(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # for even length, this lands on the *second* middle node

def detect_cycle_start(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None  # fast ran off the end -> no cycle
    slow = head
    while slow is not fast:
        slow = slow.next
        fast = fast.next
    return slow  # the cycle's entry node
```
Phase 1 (meeting point) proves a cycle exists. Phase 2 is the non-obvious part: resetting one
pointer to `head` and advancing both one step at a time makes them meet exactly at the cycle's
start — this works because of the distance math (`distance from head to cycle start` equals
`distance from meeting point to cycle start`, walking forward around the cycle). Memorize that
phase 2 exists as a distinct step; don't just return the meeting point when asked for the start.

### 4. Dummy head + merge pattern
```python
def merge_two_sorted(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a if a else b   # attach whichever list has leftovers
    return dummy.next
```
The dummy node sidesteps the "what's the head before I've picked one?" problem — you'd otherwise
need an `if result is None: result = node else: tail.next = node` special case for the first
insertion. Dummy head is also the standard fix for "remove the nth node from the end" / "remove
all nodes with value X" style problems, where the node to remove might be the head itself.

## Complexity to know cold

| Technique | Time | Space | Notes |
|---|---|---|---|
| Traversal / build | O(n) | O(1) (O(n) for `to_list`/`from_list` output) | |
| Reverse (iterative) | O(n) | O(1) | preferred unless recursion is explicitly requested |
| Reverse (recursive) | O(n) | O(n) call stack | risk of stack overflow on very long lists |
| Fast/slow (middle, cycle) | O(n) | O(1) | fast moves 2x, slow moves 1x |
| Merge two sorted lists | O(n + m) | O(1) extra (reuses nodes) | dummy head avoids special-casing |
| Doubly linked list insert/delete (node reference known) | O(1) | O(1) | no need to find `prev` — it's stored |

## Exercises

1. Implement `reverse_iterative` and `detect_cycle_start` from memory, then trace
   `detect_cycle_start` by hand on a 5-node list where node 4 points back to node 1 (0-indexed) —
   confirm phase 2 correctly returns node 1, not the phase-1 meeting point.
2. Using `from_list`/`to_list`, implement "remove the nth node from the end of the list" with a
   dummy head and two pointers offset by `n` steps, in a single pass — verify it correctly removes
   the head node when `n == length`.
