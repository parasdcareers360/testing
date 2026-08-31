# Common Mistakes — Stack & Monotonic Stack

> **Type:** Study notes

- **Popping before checking the stack is non-empty.** `stack.pop()` on an empty list raises
  `IndexError: pop from empty list` — in Valid Parentheses, a string starting with a closer
  (`")("`) hits this immediately. Always guard with `if not stack or ...` (short-circuit order
  matters: check emptiness *before* popping).
- **Returning `True` as soon as the stack is used up, forgetting leftover openers.** Valid
  Parentheses must check `not stack` at the very end too — `"((("` never fails the per-character
  loop (nothing to mismatch), but leaves 3 unmatched openers on the stack, which the final check
  catches.
- **Swapping operand order in RPN evaluation.** `b, a = stack.pop(), stack.pop()` then computing
  `a - b` (not `b - a`) matters because stack order reverses the operands — the *first* value
  popped is the right-hand operand, the second popped is the left-hand operand. Getting this
  backwards silently produces wrong answers only for non-commutative operators (`-`, `/`), which
  means a naive test with only `+`/`*` won't catch the bug.
- **Using regular float division instead of truncation toward zero in RPN.** `a // b` in Python
  floors toward negative infinity, which differs from truncation for negative results
  (`-7 // 2 == -4`, but RPN/LeetCode expects `-3`). Use `int(a / b)` to truncate toward zero, not
  `//`.
- **Pushing values instead of indices onto a monotonic stack.** Next Greater Element and Daily
  Temperatures both need to write into `result[i]` for a specific position, and Daily Temperatures
  additionally needs `i - prev` for the distance — neither works if the stack holds raw values
  instead of indices. Default to pushing indices; look up the value via `nums[stack[-1]]` when
  needed.
- **Getting the comparison direction backwards.** `while stack and nums[stack[-1]] < x` finds the
  *next greater* element; flipping to `>` finds the *next smaller* element instead. Mixing these up
  produces a stack that never triggers the `while` loop correctly and silently returns mostly `-1`s
  — if your output is suspiciously full of `-1`, check the comparison direction first.
- **Assuming the monotonic stack pattern is O(n²) because of the nested `while`.** State explicitly
  (out loud, in an interview) that each index is pushed exactly once and popped at most once across
  the *entire* run, so total pops across all iterations is bounded by n — this is what makes it
  O(n) despite the `while` living inside a `for`. Not saying this leaves the interviewer unsure you
  actually understand the amortized argument versus having memorized the code.
