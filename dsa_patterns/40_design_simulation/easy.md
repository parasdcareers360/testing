# Easy — Min Stack

**Source**: LeetCode #155
**Pattern**: Design / Simulation
**Difficulty**: Easy

## Problem Statement
Design a stack that supports the usual push/pop/top operations, and **additionally** supports retrieving the minimum element in the stack, **all in O(1) time**.

Implement the `MinStack` class:
- `MinStack()` initializes the stack object.
- `push(val)` pushes the element `val` onto the stack.
- `pop()` removes the element on the top of the stack.
- `top()` gets the top element of the stack.
- `getMin()` retrieves the minimum element in the stack, considering only the elements currently on the stack (not elements already popped).

Every one of `push`, `pop`, `top`, and `getMin` must run in **O(1) time**, including `getMin` — you cannot scan the whole stack to find the minimum each time you're asked for it.

## Constraints
- `-2^31 <= val <= 2^31 - 1`
- Methods `pop`, `top`, and `getMin` will always be called on a **non-empty** stack (you don't need to handle popping from / querying an empty stack).
- At most `3 * 10^4` calls will be made in total to `push`, `pop`, `top`, and `getMin`.

## Examples
**Example 1**
```
Input:
["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"]
[[], [-2], [0], [-3], [], [], [], []]

Output:
[null, null, null, null, -3, null, 0, -2]
```
Explanation:
```
MinStack minStack = new MinStack();
minStack.push(-2);
minStack.push(0);
minStack.push(-3);
minStack.getMin();   // return -3 (stack is [-2, 0, -3], minimum is -3)
minStack.pop();      // removes -3, stack is now [-2, 0]
minStack.top();      // return 0 (top of [-2, 0] is 0)
minStack.getMin();   // return -2 (minimum of [-2, 0] is -2)
```

**Example 2**
```
Input:
["MinStack", "push", "push", "getMin", "pop", "getMin"]
[[], [5], [5], [], [], []]

Output:
[null, null, null, 5, null, 5]
```
Explanation: Pushing the same value twice (`5`, then `5` again) means after popping one `5`, the minimum is still `5` because the other `5` remains on the stack — this tests that duplicate values are tracked correctly, not just distinct values.

## Intuition — Why This Pattern
**Naive approach**: Use a plain stack (e.g., a Python list) for `push`/`pop`/`top` (all trivially O(1) with a list's `append`/`pop`/`[-1]`), but for `getMin()`, scan the entire stack with `min(stack)` every time it's called. This is correct, but `min()` over a list of size n is O(n), violating the O(1) requirement for `getMin`.

**What's inefficient**: We're recomputing the minimum from scratch on every query even though the stack only changes by one element (a push or pop) between queries. We should be able to maintain "what is the current minimum" incrementally as elements are pushed and popped, rather than recomputing it.

**The insight (Design/Simulation pattern)**: There's no single classic algorithmic trick here — the solution is to pick the right *combination of data structures* to track exactly the state you need, updated incrementally at each operation. Specifically: maintain a **second, parallel stack** (`min_stack`) that at every position `i` stores "the minimum of the main stack's bottom `i+1` elements as of when position `i` was pushed." Concretely: whenever you push `val` onto the main stack, also push `min(val, current_min)` onto `min_stack` (where `current_min` is `min_stack`'s current top, or `+infinity` if `min_stack` is empty). Whenever you pop from the main stack, also pop from `min_stack`. Now `min_stack[-1]` always equals the minimum of exactly the elements currently in the main stack, in O(1), because it was maintained incrementally alongside every push/pop rather than recomputed.

## Approach
1. Maintain two Python lists as stacks: `stack` (holds the actual values) and `min_stack` (holds the running minimum at each depth).
2. `push(val)`:
   a. Append `val` to `stack`.
   b. Compute `new_min = val` if `min_stack` is empty, else `min(val, min_stack[-1])`.
   c. Append `new_min` to `min_stack`.
3. `pop()`:
   a. Pop (discard) the top of `stack`.
   b. Pop (discard) the top of `min_stack` (they always stay the same length, in lockstep).
4. `top()`: return `stack[-1]`.
5. `getMin()`: return `min_stack[-1]`.
6. All four operations touch only the top of one or both lists, so all are O(1).

## Dry Run
Trace `push(-2)`, `push(0)`, `push(-3)`, `getMin()`, `pop()`, `top()`, `getMin()` (Example 1):

| Operation   | stack (bottom->top) | min_stack (bottom->top) | Returned |
|-------------|----------------------|---------------------------|----------|
| push(-2)    | [-2]                 | [-2]                      | — |
| push(0)     | [-2, 0]              | [-2, min(0,-2)=-2]        | — |
| push(-3)    | [-2, 0, -3]          | [-2, -2, min(-3,-2)=-3]   | — |
| getMin()    | [-2, 0, -3]          | [-2, -2, -3]              | -3 (min_stack[-1]) |
| pop()       | [-2, 0]              | [-2, -2]                  | — (removed -3 / -3) |
| top()       | [-2, 0]              | [-2, -2]                  | 0 (stack[-1]) |
| getMin()    | [-2, 0]              | [-2, -2]                  | -2 (min_stack[-1]) |

Final outputs in order: `-3, 0, -2` — matching Example 1's expected output `[-3, null, 0, -2]` (the `null`s correspond to `pop()` which returns nothing).

## Solution (Python 3)
```python
from typing import List


class MinStack:
    def __init__(self):
        self.stack: List[int] = []
        self.min_stack: List[int] = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if self.min_stack:
            new_min = min(val, self.min_stack[-1])
        else:
            new_min = val
        self.min_stack.append(new_min)

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]


if __name__ == "__main__":
    # Example 1
    minStack = MinStack()
    minStack.push(-2)
    minStack.push(0)
    minStack.push(-3)
    print(minStack.getMin())  # -3
    minStack.pop()
    print(minStack.top())     # 0
    print(minStack.getMin())  # -2

    print("---")

    # Example 2
    s2 = MinStack()
    s2.push(5)
    s2.push(5)
    print(s2.getMin())  # 5
    s2.pop()
    print(s2.getMin())  # 5
```

## Complexity Analysis
- Time: O(1) for every operation (`push`, `pop`, `top`, `getMin`) — each only touches the top of one or two Python lists.
- Space: O(n) total, where n is the number of elements currently on the stack (we maintain two parallel arrays of the same length instead of one).

## Key Takeaways
- The core design idea — "maintain a redundant parallel structure that tracks a running aggregate (min, max, sum) alongside the primary structure, updated incrementally at every mutation" — generalizes far beyond stacks (e.g., a "max stack," a "running median" via two heaps, a Fenwick tree for range sums).
- Common mistake: using a single global variable for the minimum instead of a second stack — that breaks when you `pop()` the current minimum, because you have no way to recover the *previous* minimum without rescanning. The parallel stack solves exactly this by remembering the minimum "as of" each depth.
- Common mistake: comparing `val < min_stack[-1]` and only pushing when smaller (skipping the push when not) — this desynchronizes the two stacks' lengths and breaks the O(1) `pop`. Always push to `min_stack` in lockstep with `stack`, even when the new value doesn't change the minimum.
- Related/variant problems to try next: **Max Stack** (same idea, tracking maximum instead of minimum, sometimes with an additional `popMax()` requirement that needs a more elaborate structure), and **Design Circular Queue/Buffer** in this same pattern folder's theme — both are "pick the right combination of data structures" design exercises with no single algorithmic trick.
