"""
LeetCode Top Interview 150 — #54 (LeetCode #155)
Min Stack
Category: Stack | Difficulty: Medium

Problem
-------
Design a stack that supports push, pop, top, and retrieving the minimum element, all in
constant time.

Implement the `MinStack` class:
- `MinStack()` initializes the stack object.
- `void push(int val)` pushes the element `val` onto the stack.
- `void pop()` removes the element on top of the stack.
- `int top()` gets the top element of the stack.
- `int getMin()` retrieves the minimum element in the stack.

You must implement a solution with O(1) time complexity for each function.

Constraints
-----------
- -2^31 <= val <= 2^31 - 1
- Methods pop, top and getMin operations will always be called on non-empty stacks.
- At most 3 * 10^4 calls will be made to push, pop, top, and getMin.

Examples
--------
Example 1:
    Input:
        ["MinStack","push","push","push","getMin","pop","top","getMin"]
        [[],[-2],[0],[-3],[],[],[],[]]
    Output:
        [null,null,null,null,-3,null,0,-2]
    Explanation:
        MinStack minStack = new MinStack();
        minStack.push(-2);
        minStack.push(0);
        minStack.push(-3);
        minStack.getMin(); // return -3
        minStack.pop();
        minStack.top();    // return 0
        minStack.getMin(); // return -2

Intuition
---------
A plain stack gives O(1) push/pop/top for free, but getMin would need an O(n) scan unless we
track the running minimum somewhere. The naive fix (Approach 1) is to just rescan the whole
stack every time getMin is called — correct, but O(n) per call instead of the required O(1).
The key insight for O(1) getMin: the minimum only ever changes when we push a new value that's
<= the current minimum, or pop a value that *was* the current minimum — so if we keep a second,
parallel stack that records "what was the minimum at this point in time," pushing/popping in
lockstep with the main stack, getMin becomes a simple peek at that auxiliary stack's top. An
even leaner variant avoids the second stack's extra memory entirely: store the *actual* minimum
only in a single variable, and whenever we push a new value that becomes the new minimum, push
an "encoded" value into the main stack that lets pop() later reconstruct the previous minimum —
trading a bit of arithmetic trickery for O(1) extra space.
"""

from typing import List, Optional


# ============================================================
# Approach 1: Brute Force (plain stack, O(n) getMin)
# ============================================================
# Idea: use a single Python list as the stack; getMin() scans the whole
# thing on demand. push/pop/top are O(1), but getMin is O(n), which
# violates the problem's O(1)-for-every-op requirement -- included only as
# the naive baseline that "obviously works" before optimizing getMin.
class MinStackBruteForce:
    def __init__(self):
        self._stack: List[int] = []

    def push(self, val: int) -> None:
        self._stack.append(val)

    def pop(self) -> None:
        self._stack.pop()

    def top(self) -> int:
        return self._stack[-1]

    def getMin(self) -> int:  # noqa: N802 (LeetCode's required method name)
        return min(self._stack)  # O(n) scan -- the part we optimize away


# ============================================================
# Approach 2: Optimal (auxiliary min-stack)
# ============================================================
# Idea: maintain a second stack `_mins` in lockstep with the main stack.
# `_mins[i]` always holds the minimum of `_stack[0..i]`. Pushing a value
# also pushes min(val, current_min) onto `_mins`; popping pops both, so
# `_mins[-1]` is always the current minimum in O(1).
# Time:  O(1) for every operation
# Space: O(n) -- one extra int per element for the parallel min-stack
class MinStackAux:
    def __init__(self):
        self._stack: List[int] = []
        self._mins: List[int] = []

    def push(self, val: int) -> None:
        self._stack.append(val)
        new_min = val if not self._mins else min(val, self._mins[-1])
        self._mins.append(new_min)

    def pop(self) -> None:
        self._stack.pop()
        self._mins.pop()

    def top(self) -> int:
        return self._stack[-1]

    def getMin(self) -> int:  # noqa: N802
        return self._mins[-1]


# ============================================================
# Approach 3: Best / Alternate Optimal (single stack, encoded deltas)
# ============================================================
# Idea: keep only ONE stack and a single `_min` variable instead of a full
# parallel array. When pushing a value `val` that is <= current min, we
# push a specially encoded "flag" value (2*val - old_min) that is always
# strictly less than `val` itself, and update `_min = val`. On pop, if the
# popped raw value is less than `_min`, that value was actually an encoded
# flag -- decode it to recover the *previous* minimum (old_min = 2*_min -
# encoded) before restoring `_min`. This trades a little arithmetic
# trickery for true O(1) extra space (one int) instead of O(n).
# Time:  O(1) for every operation
# Space: O(1) extra (beyond the single required stack of values)
class MinStackEncoded:
    def __init__(self):
        self._stack: List[int] = []
        self._min: Optional[int] = None

    def push(self, val: int) -> None:
        if not self._stack:
            self._stack.append(val)
            self._min = val
            return
        if val <= self._min:
            # Encode: this value is <= old min, so it will always read as
            # "less than" the popped-to min later, signaling "decode me".
            self._stack.append(2 * val - self._min)
            self._min = val
        else:
            self._stack.append(val)

    def pop(self) -> None:
        top = self._stack.pop()
        if top < self._min:
            # top was an encoded flag; recover the previous minimum.
            self._min = 2 * self._min - top
        if not self._stack:
            self._min = None

    def top(self) -> int:
        top = self._stack[-1]
        return self._min if top < self._min else top  # noqa: type: ignore[operator]

    def getMin(self) -> int:  # noqa: N802
        return self._min


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever an aggregate (min, max, sum-so-far) must be queried in O(1)
#   alongside stack push/pop, maintain it incrementally in lockstep with
#   the stack rather than recomputing it -- a parallel "running aggregate"
#   stack is the standard, easy-to-reason-about tool.
# - Common mistake: updating the auxiliary min-stack's top in place instead
#   of pushing/popping it in lockstep with the main stack -- each entry
#   must record the minimum *as of that point in time*, not just "the
#   current global minimum", or popping back through old values breaks.
# - Related/variant problems to try next: Max Stack, Sliding Window
#   Maximum (deque instead of stack), Design a Stack With Increment
#   Operation.


if __name__ == "__main__":
    # Design problems don't fit the plain args-in/expected-out table, so we
    # replay the same sequence of operations against each implementation
    # and assert every observable result matches across all variants.
    operations = [
        ("push", -2), ("push", 0), ("push", -3),
        ("getMin", None), ("pop", None), ("top", None), ("getMin", None),
    ]
    expected_results = [None, None, None, -3, None, 0, -2]

    implementations = [MinStackBruteForce, MinStackAux, MinStackEncoded]
    for cls in implementations:
        obj = cls()
        results = []
        for op, arg in operations:
            if op == "push":
                results.append(obj.push(arg))
            elif op == "pop":
                results.append(obj.pop())
            elif op == "top":
                results.append(obj.top())
            elif op == "getMin":
                results.append(obj.getMin())
        status = "OK" if results == expected_results else "FAIL"
        print(f"{cls.__name__:20s} results={results!r:40s} -> expected={expected_results!r}  [{status}]")

    # A second, longer scenario exercising interleaved pushes/pops that
    # revisit the minimum multiple times (important for Approach 3, where
    # decoding must correctly restore each prior minimum).
    operations2 = [
        ("push", 5), ("push", 3), ("push", 7), ("push", 3), ("push", 1),
        ("getMin", None), ("pop", None), ("getMin", None),
        ("pop", None), ("getMin", None), ("pop", None), ("getMin", None),
        ("top", None), ("pop", None), ("top", None),
    ]
    expected_results2 = [
        None, None, None, None, None,
        1, None, 3,
        None, 3, None, 3,
        3, None, 5,
    ]
    for cls in implementations:
        obj = cls()
        results = []
        for op, arg in operations2:
            if op == "push":
                results.append(obj.push(arg))
            elif op == "pop":
                results.append(obj.pop())
            elif op == "top":
                results.append(obj.top())
            elif op == "getMin":
                results.append(obj.getMin())
        status = "OK" if results == expected_results2 else "FAIL"
        print(f"{cls.__name__:20s} scenario2 results={results!r:50s} -> expected={expected_results2!r}  [{status}]")
