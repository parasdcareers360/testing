# Stack & Monotonic Stack

> **Type:** Study notes

## Why interviewers ask this

Stack problems test whether you reach for the right structure when the key relationship is
"most recent unmatched thing" rather than reflexively writing recursive or index-chasing code.
Monotonic stack specifically is a favorite interview filter because the brute force ("for each
element, scan the rest of the array") is O(n²) and obviously correct, while the monotonic-stack
trick is O(n) but *not* obvious — it separates candidates who've internalized "each element is
pushed once and popped once" from those pattern-matching without understanding why it's linear.

## The core idea

A stack (LIFO) is the right structure whenever a problem has *nested* or *most-recent-first*
matching: opening/closing brackets, operator precedence, "undo" semantics, or "the next thing that
breaks a trend." A **monotonic stack** additionally keeps its elements in sorted order (increasing
or decreasing) by popping anything that violates the order before pushing the new element — this
turns "find the next greater/smaller element for every position" from O(n²) into O(n), because
each element is pushed and popped at most once across the entire scan.

Recognize this pattern when you see:
- "valid parentheses" / "matching brackets" / nested structure validation
- "evaluate an expression" (calculator, Reverse Polish Notation)
- "next greater/smaller element" for every index
- "daily temperatures" / "span" style problems (how far until a bigger value appears)
- "largest rectangle" / histogram-shaped problems

## Key techniques

### 1. Basic stack — matching/validation (Valid Parentheses)
```python
def is_valid_parentheses(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack  # every opener must have been matched and popped
```
The stack holds unmatched openers. Every closer must match the *most recently* unmatched opener —
that "most recent" requirement is exactly what a stack (not a queue or a counter) gives you for
free.

### 2. Basic stack — expression evaluation (Reverse Polish Notation)
```python
def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    ops = {"+", "-", "*", "/"}
    for tok in tokens:
        if tok in ops:
            b, a = stack.pop(), stack.pop()  # note order: second-popped is the left operand
            result = {
                "+": a + b, "-": a - b, "*": a * b,
                "/": int(a / b),  # truncate toward zero, per RPN convention
            }[tok]
            stack.append(result)
        else:
            stack.append(int(tok))
    return stack[-1]
```
Operands accumulate on the stack; an operator consumes the top two (in the right order — the
*first* popped is the right-hand operand) and pushes the result back. This generalizes to a full
calculator with parentheses by pushing `(` as a marker and evaluating on `)`.

### 3. Monotonic stack — next greater element
```python
def next_greater_element(nums: list[int]) -> list[int]:
    result = [-1] * len(nums)
    stack: list[int] = []  # indices, values kept in decreasing order top-to-bottom... bottom-to-top increasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x   # x is the "next greater" for whatever we just popped
        stack.append(i)
    return result
```
Walk left to right; before pushing the current index, pop every stack index whose value is smaller
than the current value — the current element *is* their next-greater answer. What's left on the
stack has no answer yet (nothing bigger has appeared) and stays for a future pop. Each index is
pushed once and popped at most once, so total work is O(n) even though there's a `while` inside a
`for`.

### 4. Monotonic stack — Daily Temperatures (distance instead of value)
```python
def daily_temperatures(temps: list[int]) -> list[int]:
    result = [0] * len(temps)
    stack: list[int] = []  # indices with temps kept in decreasing order
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            prev = stack.pop()
            result[prev] = i - prev   # distance, not the value itself
        stack.append(i)
    return result
```
Identical shape to technique 3 — the only change is storing `i - prev` (how many days until a
warmer day) instead of the value itself. This is the tell that monotonic stack is really one
template with the payoff swapped out.

### Largest Rectangle in Histogram — intuition only
For each bar, the largest rectangle *using that bar's height* extends left and right until it hits
a shorter bar. A monotonic increasing stack of indices lets you find, for each bar, "the nearest
shorter bar to the left" and "the nearest shorter bar to the right" in one O(n) pass each (or one
combined pass with careful bookkeeping) — same "each index pushed/popped once" argument as next
greater element, just computing a width instead of a next-greater value. Full solution is a
stretch problem — know the shape and the "nearest smaller on both sides" framing; that's usually
enough to make real progress live even if you don't finish.

## Complexity to know cold

| Technique | Time | Space | Key invariant |
|---|---|---|---|
| Valid Parentheses / matching | O(n) | O(n) worst case | stack holds unmatched openers only |
| RPN / expression evaluation | O(n) | O(n) | stack holds operands awaiting an operator |
| Monotonic stack (next greater/smaller) | O(n) amortized | O(n) | each index pushed once, popped once |
| Largest Rectangle in Histogram | O(n) | O(n) | monotonic stack finds nearest-smaller both sides |

## Exercises

1. Implement `is_valid_parentheses` and `next_greater_element` from memory, then trace
   `next_greater_element([2,1,2,4,3])` by hand — expected: `[4,2,4,-1,-1]`.
2. Adapt technique 3 to compute the **next smaller** element instead (flip the comparison), then
   use it to explain, out loud, the "nearest smaller to the left" half of the Largest Rectangle in
   Histogram intuition.
