"""
LeetCode Top Interview 150 — #45 (LeetCode #202)
Happy Number
Category: Hashmap | Difficulty: Easy

Problem
-------
Write an algorithm to determine if a number `n` is happy.

A happy number is defined by the following process:
- Starting with any positive integer, replace the number by the sum of the squares of its digits.
- Repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a
  cycle which does not include 1.
- Those numbers for which this process ends in 1 are happy.

Return True if `n` is a happy number, and False if not.

Constraints
-----------
- 1 <= n <= 2^31 - 1

Examples
--------
Example 1:
    Input: n = 19
    Output: true
    Explanation: 1^2 + 9^2 = 82
                 8^2 + 2^2 = 68
                 6^2 + 8^2 = 100
                 1^2 + 0^2 + 0^2 = 1

Example 2:
    Input: n = 2
    Output: false
    Explanation: 2 -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4 -> ... loops forever
    without reaching 1.

Intuition
---------
There's no meaningful "brute force" separate from simulating the digit-square-sum process itself
— that computation is unavoidable and cheap. The real question is *when to stop*: the sequence
either reaches 1 (happy) or enters a cycle that never includes 1 (not happy), and it's a
mathematical fact that it must do one or the other — it can never grow unboundedly, because for
any number with more than 3 digits, the sum of squared digits is strictly smaller than the number
itself. The simplest way to detect "we're stuck in a cycle" is to remember every value we've seen
in a hashset; if we ever compute a value we've already seen, we know we've entered a loop, so it
can't be happy. A cleverer, O(1)-space alternative borrows Floyd's cycle detection ("tortoise and
hare") from linked-list cycle problems: treat "next number in the sequence" as a linked-list
pointer, advance a slow pointer one step and a fast pointer two steps per iteration, and if they
ever meet before either reaches 1, there's a cycle.
"""


def _next_value(n: int) -> int:
    total = 0
    while n > 0:
        digit = n % 10
        total += digit * digit
        n //= 10
    return total


# ============================================================
# Approach 1: Hashset of Seen Values
# ============================================================
# Idea: repeatedly apply the digit-square-sum transform, recording every
# value seen. If we hit 1, it's happy. If we hit a value already in the
# set, we've found a cycle that excludes 1, so it's not happy.
# Dry run: n=19
#   seen={}, n=19 -> next=82, 82 not seen -> seen={19}
#   n=82 -> next=68, not seen -> seen={19,82}
#   n=68 -> next=100, not seen -> seen={19,82,68}
#   n=100 -> next=1, not seen -> seen={19,82,68,100}
#   n=1 -> return True
# Time:  O(log n) per transform step, and the sequence provably reaches 1
#        or a small cycle quickly for any input, so this is treated as O(1)
#        amortized in practice (the state space of reachable sums is small)
# Space: O(k) — k = number of distinct values visited before stopping
def solve_hashset(n: int) -> bool:
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = _next_value(n)
    return n == 1


# ============================================================
# Approach 2: Best (Floyd's Cycle Detection — slow/fast pointers)
# ============================================================
# Idea: treat the digit-square-sum transform as a function defining an
# implicit linked list (each number "points to" its transform). Advance a
# slow pointer one step and a fast pointer two steps at a time; if the
# sequence is happy, fast reaches 1 first; if it's not happy, slow and fast
# eventually land on the same value inside the cycle. This avoids storing
# every visited value, unlike the hashset approach.
# Dry run: n=2 (known unhappy, cycle 4->16->37->58->89->145->42->20->4...)
#   slow=2, fast=2
#   step: slow=next(2)=4, fast=next(next(2))=next(4)=16
#   step: slow=next(4)=16, fast=next(next(16))=next(37)=58
#   ... pointers keep advancing; eventually slow==fast inside the cycle
#   since neither ever equals 1, and slow==fast triggers -> return False
# Time:  O(log n) per step in the transform, same practical bound as above
# Space: O(1) — only two integer pointers, no auxiliary set
def solve_best(n: int) -> bool:
    slow = n
    fast = _next_value(n)
    while fast != 1 and slow != fast:
        slow = _next_value(slow)
        fast = _next_value(_next_value(fast))
    return fast == 1


# ============================================================
# Key Takeaways
# ============================================================
# - "Detect a cycle in an implicit sequence" is a recurring shape: a
#   hashset of seen states is the simple O(space) solution, while Floyd's
#   tortoise-and-hare gives the same answer in O(1) space by exploiting the
#   fact that a cycle means the fast pointer will eventually lap the slow
#   one.
# - Common mistake: forgetting that the "not happy" case doesn't diverge to
#   infinity — it's provably bounded (digit-square-sum shrinks large
#   numbers), so termination is guaranteed either way; no need to cap
#   iterations manually.
# - Related/variant problems to try next: Linked List Cycle (the canonical
#   Floyd's cycle detection problem), Linked List Cycle II (find the cycle
#   start), Find the Duplicate Number (Floyd's applied to an array).


if __name__ == "__main__":
    tests = [
        ((19,), True),
        ((2,), False),
        ((1,), True),
        ((7,), True),
        ((4,), False),
        ((100,), True),
        ((1111111,), True),
    ]

    approaches = [solve_hashset, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")
